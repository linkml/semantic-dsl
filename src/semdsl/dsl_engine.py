import logging
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Optional, TextIO, Type, Union

import yaml
from lark import Tree
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime.processing.referencevalidator import ReferenceValidator
from linkml_runtime.utils.compile_python import compile_python
from linkml_runtime.utils.formatutils import camelcase
from pydantic import BaseModel

from semdsl.datamodel.semdsl_model import Disjunction, SchemaGrammar
from semdsl.importers.schema_importer import SchemaImporter
from semdsl.mapper.mapper import Mapper
from semdsl.writers.lark_writer import LarkWriter

logger = logging.getLogger(__name__)


@dataclass
class DSLEngine:
    """
    Engine for generating DSLs from LinkML Schemas and for parsing serialization to these DSLs.

    >>> from semdsl import DSLEngine
    >>> engine = DSLEngine()
    >>> engine.load_schema("examples/clue/model_clue.yaml")  ## Annotated LinkML schema
    >>> obj = engine.parse_as_dict("< Colonel Mustard in the Kitchen with the Candlestick >")
    >>> print(obj)
    {'person': 'Colonel Mustard', 'location': 'Kitchen', 'weapon': 'Candlestick'}

    This works as follows:

    - The LinkML schema is loaded from a YAML source
    - A Lark grammar is generated from the LinkML schema, using annotations in the schema
    - The Lark grammar is used to parse the input into a tree
    - The tree is automatically transformed into an object conformant with the schema

    """

    schemaview: Optional[SchemaView] = None
    """Wrapper onto a LinkML schema"""

    _grammar: Optional[SchemaGrammar] = None
    _lark_serialization: Optional[str] = None
    _compiled_grammar_module: Optional[ModuleType] = None
    _compiled_datamodel: Optional[ModuleType] = None

    normalizer: Optional[ReferenceValidator] = None
    """Uses to normalize object structures prior to object initialization"""

    def load_schema(self, schema: Union[str, TextIO, SchemaDefinition]) -> None:
        """Load a schema from a LinkML schema source.

        >>> from semdsl import DSLEngine
        >>> engine = DSLEngine()
        >>> engine.load_schema("examples/clue/model_clue.yaml")

        :param schema: path to a schema or a schema object
        """
        self.schemaview = SchemaView(schema)

    def parse_as_dict(self, input: str, start=None, target_class=None) -> dict:
        """
        Parses input string to a raw object/dict.

        >>> from semdsl import DSLEngine
        >>> engine = DSLEngine()
        >>> engine.load_schema("examples/clue/model_clue.yaml")
        >>> obj = engine.parse_as_dict("< Colonel Mustard in the Kitchen with the Candlestick >")
        >>> print(obj)
        {'person': 'Colonel Mustard', 'location': 'Kitchen', 'weapon': 'Candlestick'}

        :param input: input string to parse
        :param start: start symbol in grammar
        :param target_class: target data model class for parsing
        :return: input parsed into a dict object conforming to the schema/data model
        """

        if start is None:
            start = self._get_start_symbol(target_class)
        mod = self.compiled_grammar_module
        tree = mod.grammar.parse(input, start=start)
        mapper = Mapper(schemaview=self.schemaview, schemagrammar=self.grammar)
        return mapper.transform(tree)

    def parse_as_object(
        self, input: str, start=None, target_class: Optional[Union[str, Type]] = None
    ) -> BaseModel:
        """
        Parses the input string into a pydantic BaseModel.

        .. note ::

            this requires EITHER that the main linkml package is installed, OR that
            the module for the pydantic data model is set using :ref:`compiled_datamodel`


        >>> from semdsl import DSLEngine
        >>> engine = DSLEngine()
        >>> engine.load_schema("examples/clue/model_clue.yaml")
        >>> obj = engine.parse_as_object("< Colonel Mustard in the Kitchen with the Candlestick >")
        >>> print(type(obj))
        <class 'test.ClueHypothesis'>
        >>> print(obj.weapon)
        Candlestick
        >>> print(obj.dict())
        {'person': 'Colonel Mustard', 'location': 'Kitchen', 'weapon': 'Candlestick'}

        :param input: input string to parse
        :param start: start symbol in grammar
        :param target_class: target data model class for parsing
        :return: pydantic object representing the parsed input
        """
        if target_class is None:
            if len(self.schemaview.all_classes()) == 1:
                candidates = list(self.schemaview.all_classes().values())
            else:
                candidates = [x for x in self.schemaview.all_classes().values() if x.tree_root]
            target_class = candidates[0].name
        d = self.parse_as_dict(input, start=start, target_class=target_class)
        module = self.compiled_datamodel
        if isinstance(target_class, str):
            py_class = module.__dict__[camelcase(target_class)]
        else:
            py_class = target_class
        if self.grammar.normalize_collections:
            if self.normalizer is None:
                self.normalizer = ReferenceValidator(self.schemaview)
            d = self.normalizer.normalize(d)
        # print(f"Creating {py_class} from dict: {d}")
        return py_class(**d)

    @property
    def grammar(self) -> SchemaGrammar:
        """Access the grammar object.

        .. note ::

            for most purposes, you do not need to access the grammar object directly.

        If the grammar object is not explicitly set, this will
        generate a grammar from the schema, using annotations if
        present, and auto-generating otherwise.


        >>> from semdsl import DSLEngine
        >>> engine = DSLEngine()
        >>> engine.load_schema("examples/clue/model_clue.yaml")
        >>> grammar = engine.grammar
        >>> print(grammar.rules[0].lhs_symbol)
        class_clue_hypothesis

        :return: a SchemaGrammar object
        """
        if self._grammar is None:
            self.generate_grammar()
        return self._grammar

    def load_grammar(self, grammar: Union[str, Path, TextIO, SchemaGrammar]) -> None:
        """Load a grammar from a DSL YAML file.


        >>> from semdsl import DSLEngine
        >>> engine = DSLEngine()
        >>> engine.load_grammar("examples/linkml_lite/linkml_model_lite.semdsl.yaml")
        >>> grammar = engine.grammar
        >>> print(grammar.rules[0].lhs_symbol)
        schema
        >>> print(engine.lark_serialization)
        from lark import Lark
        ...
        schema : schema_id schema_name description? (comment|import|prefix|class|slot|type|enum)*
        class : "class" class_name is_a? mixins? "{" description? class_uri? (comment|attribute|slot_usage|slots)* "}"
        slot : "slot" slot_block
        ...

        :param grammar: path to a YAML file containing the grammar using the semdsl metamodel
        """
        if not isinstance(grammar, SchemaGrammar):
            with open(grammar) as f:
                obj = yaml.safe_load(f)
                grammar = SchemaGrammar.parse_obj(obj)
        self._grammar = grammar

    def generate_grammar(self) -> None:
        """Generate a grammar from the current schema.

        This will use annotations if present, and auto-generate otherwise.

        .. note ::

            if the grammar has previously been set, this will overwrite it.
        """
        importer = SchemaImporter()
        self._grammar = importer.convert(self.schemaview.schema)

    @property
    def lark_serialization(self) -> str:
        """Serialize as a lark program.

        >>> from semdsl import DSLEngine
        >>> engine = DSLEngine()
        >>> engine.load_schema("examples/clue/model_clue.yaml")
        >>> print(engine.lark_serialization)
        from lark import Lark
        ...
        class_clue_hypothesis : "<" person "in the" location "with the" weapon ">"
        person : WORD WORD
        location : WORD
        weapon : WORD
        ...

        :return: a string containing the lark program
        """
        if self._lark_serialization is None:
            writer = LarkWriter()
            self._lark_serialization = writer.dumps(self.grammar)
        return self._lark_serialization

    @property
    def compiled_grammar_module(self) -> ModuleType:
        """Get the python module for the compiled grammar.

        Note that most clients do not need to use this directly.
        """
        if self._compiled_grammar_module is None:
            ser = self.lark_serialization
            self._compiled_grammar_module = compile_python(ser)
        return self._compiled_grammar_module

    @property
    def compiled_datamodel(self) -> ModuleType:
        """Get the pydantic module for the current data model."""
        if self._compiled_datamodel is None:
            from linkml.generators.pydanticgen import PydanticGenerator

            ser = PydanticGenerator(self.schemaview.schema).serialize()
            self._compiled_datamodel = compile_python(ser)
        return self._compiled_datamodel

    @compiled_datamodel.setter
    def compiled_datamodel(self, module: ModuleType) -> None:
        """
        Set the compiled pydantic datamodel module.

        :param module:
        :return:
        """
        self._compiled_datamodel = module

    def parse_tree(self, input: str, start=None, target_class=None) -> Tree:
        """
        Generates Lark parse tree using grammar from input string.

        :param input:
        :param start:
        :param target_class:
        :return:
        """

        if start is None:
            start = self._get_start_symbol(target_class)
        mod = self.compiled_grammar_module
        return mod.grammar.parse(input, start=start)

    def _get_start_symbol(self, target_class: Optional[Union[str, Type]] = None) -> str:
        if len(self.grammar.start_symbols) == 1:
            return self.grammar.start_symbols[0]
        if target_class is None:
            [target_class] = [x.name for x in self.schemaview.all_classes().values() if x.tree_root]
        if not isinstance(target_class, str):
            target_class = target_class.__name__
        for rule in self.grammar.rules:
            if rule.source_class == target_class:
                return rule.lhs_symbol
            if isinstance(rule.rhs, Disjunction):
                for op in rule.rhs.operands:
                    if op.source_class == target_class:
                        return rule.lhs_symbol
        for rule in self.grammar.rules:
            if rule.lhs_symbol == target_class:
                return rule.lhs_symbol
        raise ValueError(f"Cannot find start symbol for {target_class}")
