"""Demo version test."""

import unittest

import yaml
from lark import Token
from linkml_runtime import SchemaView

from semdsl.datamodel.semdsl_model import SchemaGrammar
from semdsl.dsl_engine import DSLEngine
from semdsl.mapper.mapper import Mapper
from semdsl.writers.lark_writer import LarkWriter
from tests.input.examples.arithmetic import ARITHMETIC_DSL, ARITHMETIC_MODEL
from tests.input.examples.arithmetic.model_arithmetic import (
    CompoundExpression,
    Constant,
    Container,
    Variable,
)
from tests.input.examples.clue import CLUE_MODEL_SEMANTIC

EXAMPLES = [
    (
        None,
        CLUE_MODEL_SEMANTIC,
        [
            (
                None,
                "< clue:ColonelMustard in the clue:Kitchen with the clue:Candlestick >",
                None,
                [
                    ("clue:ColonelMustard", lambda obj: obj.person),
                    ("clue:Kitchen", lambda obj: obj.location),
                    ("clue:Candlestick", lambda obj: obj.weapon),
                ],
            )
        ],
    ),
    (
        ARITHMETIC_DSL,
        ARITHMETIC_MODEL,
        [
            (
                "constant",
                "0",
                Constant,
                [
                    (0, lambda obj: obj.value),
                ],
            ),
            (
                "variable",
                "x",
                Variable,
                [
                    ("x", lambda obj: obj.name),
                ],
            ),
            (
                "expr",
                "1+1",
                CompoundExpression,
                [
                    (2, lambda obj: int(obj.left.value + obj.right.value)),
                    ("+", lambda obj: obj.operator),
                ],
            ),
            (
                "expr",
                "(1+1)",
                CompoundExpression,
                [(2, lambda obj: int(obj.left.value + obj.right.value))],
            ),
            (
                "expr",
                " (   1 + 1\n)\n\n",
                CompoundExpression,
                [(2, lambda obj: int(obj.left.value + obj.right.value))],
            ),
            (
                "expr",
                "((1+1))",
                CompoundExpression,
                [(2, lambda obj: int(obj.left.value + obj.right.value))],
            ),
            (
                "expr",
                "((1))",
                Constant,
                [(1, lambda obj: int(obj.value))],
            ),
            (
                "container",
                "EXPRESSIONS: (1+1)",
                Container,
                [
                    (
                        2,
                        lambda obj: int(
                            obj.expressions[0].left.value + obj.expressions[0].right.value
                        ),
                    )
                ],
            ),
            (
                "container",
                "EXPRESSIONS: (1+1)(2+2)",
                Container,
                [
                    (
                        2,
                        lambda obj: int(
                            obj.expressions[0].left.value + obj.expressions[0].right.value
                        ),
                    ),
                    (
                        4,
                        lambda obj: int(
                            obj.expressions[1].left.value + obj.expressions[1].right.value
                        ),
                    ),
                ],
            ),
        ],
    ),
]


class TestModel(unittest.TestCase):
    """Test version."""

    def setUp(self) -> None:
        """Set up."""
        self.writer = LarkWriter()
        schema_path = ARITHMETIC_MODEL
        sv = SchemaView(schema_path)
        grammar_path = ARITHMETIC_DSL
        engine = DSLEngine()
        engine.load_schema(schema_path)
        engine.load_grammar(grammar_path)
        with open(grammar_path) as f:
            obj = yaml.safe_load(f)
            self.grammar = SchemaGrammar.parse_obj(obj)
            self.mapper = Mapper(schemaview=sv, schemagrammar=self.grammar)

    def test_introspect(self):
        mapper = self.mapper
        t, _seq = mapper.lookup_token_value(Token("x", "compound_expr"))
        self.assertEqual(t, None)
        t, _seq = mapper.lookup_token_value(Token("x", "main_expression"))
        self.assertEqual(t, "CompoundExpression")

    def test_examples(self):
        w = self.writer
        for e in EXAMPLES:
            grammar_path, schema_path, sers = e
            engine = DSLEngine()
            engine.load_schema(str(schema_path))
            if grammar_path:
                engine.load_grammar(grammar_path)
                with open(grammar_path) as f:
                    obj = yaml.safe_load(f)
                    g = SchemaGrammar.parse_obj(obj)
                    # test writer
                    w.write(g)
                    mod = w.compile(g)
                    mapper = self.mapper
                    mapper.schemagrammar = g
            for start, ser, typ, eq_tests in sers:
                obj = engine.parse_as_object(ser, start=start, target_class=typ)
                for expected, func in eq_tests:
                    self.assertEqual(expected, func(obj))
                # g = engine.parse_as_rdf_graph(ser, start)
