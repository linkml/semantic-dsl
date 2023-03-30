from dataclasses import dataclass
from io import StringIO
from typing import List, Optional, TextIO, Union

import inflection
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import (
    ClassDefinition,
    Element,
    EnumDefinition,
    SchemaDefinition,
    TypeDefinition,
)

from semdsl.datamodel.semdsl_model import (
    AtomicSequence,
    Disjunction,
    NonTerminal,
    ProductionRule,
    SchemaGrammar,
    Terminal,
)
from semdsl.importers.importer import Importer

required_multivalued_to_card = {
    (False, False): "?",
    (False, True): "*",
    (True, False): "",
    (True, True): "+",
}


def _snakify(s: str) -> str:
    return inflection.underscore(str(s)).replace(" ", "_")


@dataclass
class SchemaImporter(Importer):
    """
    An importer that imports from a LinkML schema
    """

    def convert(
        self, input: Union[str, TextIO, SchemaDefinition], starts: List[str] = None, **kwargs
    ) -> SchemaGrammar:
        """
        Convert input to a SchemaGrammar
        :param input: input to convert
        :param kwargs: additional arguments
        :return: SchemaGrammar
        """
        if isinstance(input, str):
            input = StringIO(input)
        if isinstance(input, TextIO):
            input = input.read()
        schemaview = SchemaView(input)
        sg = SchemaGrammar(parser="lalr")
        sg.pragmas = ["ignore WS"]
        if starts is None:
            # starts = [x.name for x in schemaview.all_classes().values() if x.tree_root]
            starts = [x.name for x in schemaview.all_classes().values()]

        sg.start_symbols = [self._class_symbol(s) for s in starts]
        for cls in schemaview.all_classes().values():
            self._add_class(sg, cls, schemaview)
        for typ in schemaview.all_types().values():
            self._add_type(sg, typ, schemaview)
        for enum in schemaview.all_enums().values():
            self._add_enum(sg, enum)
        return sg

    def _add_class(self, sg: SchemaGrammar, cls: ClassDefinition, schemaview: SchemaView):
        abstract = cls.abstract or cls.mixin
        if abstract:
            return self._add_abstract_class(sg, cls, schemaview)
        sym = self._class_symbol(cls.name)
        rule = ProductionRule(lhs_symbol=sym)
        rule.source_class = cls.name
        seq = AtomicSequence(elements=[])
        rule.rhs = seq
        sg.rules.append(rule)
        seq_str = self._get_sequence_from_annotations(cls)
        if seq_str:
            rule.rhs.serialized = seq_str
            for slot in schemaview.class_induced_slots(cls.name):
                slot_production = self._get_sequence_from_annotations(slot)
                if not slot_production:
                    continue
                slot_sym = _snakify(slot.name)
                slot_rule = ProductionRule(lhs_symbol=slot_sym)
                slot_rule.rhs = AtomicSequence(serialized=slot_production)
                sg.rules.append(slot_rule)
            return
        # For example:
        # >>> my_class: "MyClass(" ...
        self._add_terminal(seq, f"{inflection.camelize(cls.name)}(")
        slots = []
        for s in schemaview.class_induced_slots(cls.name):
            slot_sym = self._slot_symbol(s.name, cls.name)
            slots.append((slot_sym, s))
            if not s.required:
                card = "?"
            else:
                card = ""
            self._add_non_terminal(seq, slot_sym, card)
        self._add_terminal(seq, ")")
        for slot_sym, slot in slots:
            self._add_slot(sg, slot, slot_sym, schemaview)

    def _add_abstract_class(self, sg: SchemaGrammar, cls: ClassDefinition, schemaview: SchemaView):
        sym = self._class_symbol(cls.name)
        rule = ProductionRule(lhs_symbol=sym)
        disj = Disjunction(operands=[])
        for child in schemaview.class_children(cls.name):
            child_sym = self._class_symbol(child)
            seq = AtomicSequence(elements=[])
            self._add_non_terminal(seq, child_sym)
            disj.operands.append(seq)
        rule.rhs = disj
        sg.rules.append(rule)

    def _add_slot(
        self, sg: SchemaGrammar, slot: ClassDefinition, slot_sym: str, schemaview: SchemaView = None
    ):
        """
        Generates a production rule for a slot in the context of a class.

        For example:

        .. code ::

            Person_address : "address=" Address

        If the slot is multivalued:


        .. code ::

            Person_addresses : "addresses=" "[" Address* "]"

        """
        rule = ProductionRule(lhs_symbol=slot_sym)
        seq = AtomicSequence(elements=[])
        self._add_terminal(seq, f"{_snakify(str(slot.name))}=")
        if slot.multivalued:
            self._add_terminal(seq, "[")
        card = required_multivalued_to_card[(slot.required or False, slot.multivalued or False)]
        if card == "?":
            # optionality previously accounted for
            card = ""
        unions = [r for r in schemaview.slot_range_as_union(slot) if r is not None]
        if not slot.range and unions:
            if card and card != "?":
                raise NotImplementedError(
                    f"TODO; union ranges for multivalued; slot c={card} {slot.name} => {unions}"
                )
            atomic_ranges = [self._atomic_range_as_symbol(r, schemaview) for r in unions if r]
            disj = Disjunction(operands=[])
            for r in atomic_ranges:
                inner_seq = AtomicSequence(elements=[])
                self._add_non_terminal(inner_seq, r)
                disj.operands.append(inner_seq)
            seq.elements.append(disj)
        else:
            sym = self._atomic_range_as_symbol(slot.range, schemaview)
            self._add_non_terminal(seq, sym, card)
        if slot.multivalued:
            self._add_terminal(seq, "]")
        rule.rhs = seq
        rule.source_slot = slot.name
        sg.rules.append(rule)

    def _atomic_range_as_symbol(self, range: str, schemaview: SchemaView = None):
        if range is None:
            range = "string"
        if range in schemaview.all_classes():
            sym = self._class_symbol(range)
        elif range in schemaview.all_types():
            sym = self._type_symbol(range)
        elif range in schemaview.all_enums():
            sym = self._enum_symbol(range)
        else:
            raise ValueError(f"The range {range} is not defined")
        return sym

    def _add_enum(self, sg: SchemaGrammar, enum: EnumDefinition):
        sym = self._enum_symbol(enum.name)
        rule = ProductionRule(is_terminal=True, lhs_symbol=sym)
        disj = Disjunction(operands=[])
        for text in enum.permissible_values.keys():
            seq = AtomicSequence(elements=[])
            self._add_terminal(seq, text)
            disj.operands.append(seq)
        rule.rhs = disj
        sg.rules.append(rule)

    def _add_type(self, sg: SchemaGrammar, typ: TypeDefinition, schemaview: SchemaView = None):
        induced_type = schemaview.induced_type(typ.name)
        sym = self._type_symbol(typ.name)
        rule = ProductionRule(is_terminal=True, lhs_symbol=sym)
        seq = AtomicSequence(elements=[])
        # terminal = "quoted_string_literal"
        terminal = "ESCAPED_STRING"
        xsd_type = induced_type.uri
        if xsd_type == "xsd:integer":
            terminal = "NUMBER"
        elif xsd_type == "xsd:float":
            terminal = "FLOAT"
        elif xsd_type == "xsd:double":
            terminal = "FLOAT"
        elif induced_type.base == "Curie":
            terminal = "CURIE"
        elif induced_type.base == "URI":
            terminal = "URIORCURIE"
        elif induced_type.base == "URIorCURIE":
            terminal = "URIORCURIE"
        self._add_non_terminal(seq, terminal)
        rule.rhs = seq
        sg.rules.append(rule)

    def _class_symbol(self, class_name: str) -> str:
        return f"class_{_snakify(str(class_name))}"

    def _enum_symbol(self, class_name: str) -> str:
        return f"ENUM{_snakify(str(class_name)).upper()}"

    def _slot_symbol(self, slot_name: str, class_name: str) -> str:
        if class_name:
            pfx = f"{_snakify(str(class_name))}__"
        else:
            pfx = ""
        return f"slot_{pfx}{_snakify(str(slot_name))}"

    def _type_symbol(self, type_name: str) -> str:
        return f"TYPE_{_snakify(str(type_name)).upper()}"
        # return f"type_{_snakify(str(type_name))}"

    def _add_terminal(self, seq: AtomicSequence, value: str):
        seq.elements.append(Terminal(value=value))

    def _add_non_terminal(self, seq: AtomicSequence, name: str, repetitions=None):
        seq.elements.append(NonTerminal(name=name, repetitions=repetitions))

    def _get_sequence_from_annotations(self, element: Element) -> Optional[str]:
        if "grammar.main" in element.annotations:
            return element.annotations["grammar.main"].value
