"""Demo version test."""

import unittest

from lark import UnexpectedCharacters, UnexpectedToken

from semdsl import DSLEngine
from tests.input.examples.arithmetic import ARITHMETIC_MODEL

CLUE_SCHEMA = """
id: https://example.org/clue
name: clue
prefixes:
  linkml: https://w3id.org/linkml/
imports:
  - linkml:types
classes:
  ClueHypothesis:
    tree_root: true
    attributes:
      person:   # e.g. Colonel Mustard
        annotations:
          grammar.main: "WORD WORD"
      location: # e.g. Kitchen
        annotations:
          grammar.main: "WORD"
      weapon:   # e.g. Candlestick
        annotations:
          grammar.main: "WORD"
    annotations:
      grammar.main: >-
        "<" person "in the" location "with the" weapon ">" 
"""


class TestSchemaImporter(unittest.TestCase):
    """Test importing schema."""

    def setUp(self) -> None:
        """Set up."""
        engine = DSLEngine()
        engine.load_schema(ARITHMETIC_MODEL)
        self.engine = engine

    # @unittest.skip("in progress")
    def test_schema_auto_importer(self):
        """Generate functional syntax for Test model."""
        engine = self.engine
        engine.generate_grammar()
        obj = engine.parse_as_object(
            "CompoundExpression(operator=+ left=Constant(value=1) right=Constant(value=1))",
            target_class="CompoundExpression",
        )
        self.assertEqual(2, obj.left.value + obj.right.value)

    def test_schema_guided(self):
        """Generate functional syntax for Test model."""
        engine = DSLEngine()
        engine.load_schema(CLUE_SCHEMA)
        cases = [
            (
                True,
                "<Colonel Mustard in the Kitchen with the Candlestick>",
                "ClueHypothesis",
                {"person": "Colonel Mustard", "location": "Kitchen", "weapon": "Candlestick"},
            ),
            (
                False,
                "<Mustard in the Kitchen with the Candlestick>",
                "ClueHypothesis",
                {"person": "Colonel Mustard", "location": "Kitchen", "weapon": "Candlestick"},
            ),
            (
                False,
                "Colonel Mustard in the Kitchen with the Candlestick",
                "ClueHypothesis",
                None,
            ),
            (
                False,
                "<Colonel Mustard in the Kitchen with Candlestick>",
                "ClueHypothesis",
                None,
            ),
        ]
        for case in cases:
            passes, ser, target_class, expected = case
            if not passes:
                with self.assertRaises((UnexpectedCharacters, UnexpectedToken)) :
                    obj = engine.parse_as_object(ser, target_class=target_class)
                continue
            obj = engine.parse_as_object(ser, target_class=target_class)
            self.assertEqual(expected, obj.dict())
