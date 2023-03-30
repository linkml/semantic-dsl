import json
import unittest
from pathlib import Path

import yaml
from click.testing import CliRunner
from linkml_runtime import SCHEMA_DIRECTORY, SchemaView

from semdsl.cli import main
from tests import EXAMPLE_CLUE_DIR, EXAMPLE_DIR, OUTPUT_DIR
from tests.input.examples.arithmetic import ARITHMETIC_DSL, ARITHMETIC_EXAMPLE, ARITHMETIC_MODEL
from tests.input.examples.clue import CLUE_MODEL
from tests.input.examples.linkml_lite import LINKML_DSL, LINKML_EXAMPLE


class CliTestSuite(unittest.TestCase):
    """
    Tests command line interfaces
    """

    def setUp(self) -> None:
        runner = CliRunner(mix_stderr=False)
        self.runner = runner
        Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    def test_help(self):
        result = self.runner.invoke(main, ["--help"])
        self.assertEqual(0, result.exit_code)
        out = result.stdout
        self.assertEqual(0, result.exit_code)
        self.assertIn("parse", out)

    def test_export_grammar(self):
        outfile = OUTPUT_DIR / "test-clue.lark"
        result = self.runner.invoke(main, ["export-grammar", "-s", CLUE_MODEL, "-o", outfile])
        self.assertEqual(0, result.exit_code)
        self.assertIn("class_clue_hypothesis : ", open(outfile).read())

    def test_export_grammar_auto(self):
        outfile = OUTPUT_DIR / "test-auto.lark"
        result = self.runner.invoke(main, ["export-grammar", "-s", ARITHMETIC_MODEL, "-o", outfile])
        self.assertEqual(0, result.exit_code)
        self.assertIn("class_compound_expression", open(outfile).read())

    def test_export_grammar_from_yaml(self):
        outfile = OUTPUT_DIR / "test-arithmetic.lark"
        result = self.runner.invoke(
            main,
            [
                "export-grammar",
                "-s",
                ARITHMETIC_MODEL,
                "-g",
                ARITHMETIC_DSL,
                "-o",
                outfile,
            ],
        )
        self.assertEqual(0, result.exit_code)
        out = open(outfile).read()
        self.assertIn("compound_expr : left operator right -> main_expression", out)

    def test_parse(self):
        outfile = f"{OUTPUT_DIR}/parse-output.yaml"
        result = self.runner.invoke(
            main,
            [
                "parse",
                "-s",
                ARITHMETIC_MODEL,
                "-g",
                ARITHMETIC_DSL,
                ARITHMETIC_EXAMPLE,
                "-o",
                outfile,
                "-O",
                "json",
            ],
        )
        self.assertEqual(0, result.exit_code)
        out = open(outfile).read()
        obj = json.loads(out)
        self.assertEqual(1, int(obj["expressions"][0]["left"]["value"]))

    def test_linkml_dsl(self):
        outfile = f"{OUTPUT_DIR}/test-schema.yaml"
        metamodel = SCHEMA_DIRECTORY / "meta.yaml"
        grammar = LINKML_DSL
        src = LINKML_EXAMPLE
        result = self.runner.invoke(
            main, ["parse", "-s", metamodel, "-g", grammar, src, "-o", outfile]
        )
        self.assertEqual(0, result.exit_code)
        out = open(outfile).read()
        obj = yaml.safe_load(out)
        # TODO: aliases in pydantic
        obj["slots"] = obj["slot_definitions"]
        del obj["slot_definitions"]
        sv = SchemaView(yaml.dump(obj))
        self.assertGreater(len(sv.all_classes()), 0)
        self.assertGreater(len(sv.all_slots()), 0)
        self.assertGreater(len(sv.all_enums()), 0)
