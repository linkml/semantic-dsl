"""Command line interface for semdsl."""
import json
import logging
import sys
from typing import Union

import click
import yaml
from pydantic import BaseModel

from semdsl import DSLEngine, __version__

__all__ = [
    "main",
]


logger = logging.getLogger(__name__)


def _dumps(obj: Union[dict, BaseModel], format: str = "yaml", **kwargs) -> str:
    if not isinstance(obj, dict):
        obj = obj.dict(exclude_unset=True)
    json_str = json.dumps(obj, sort_keys=False, indent=2)
    if format == "json":
        return json_str
    return yaml.dump(yaml.safe_load(json_str), sort_keys=False)


schema_option = click.option(
    "--schema",
    "-s",
    help="Path to schema specified as LinkML yaml",
)
output_option = click.option(
    "--output",
    "-o",
    type=click.File("w"),
    default=sys.stdout,
    help="Path to output file",
)
output_format_option = click.option(
    "--output-format",
    "-O",
    help="Output format. Inferred from output suffix if not specified",
)
grammar_option = click.option(
    "--grammar",
    "-g",
    help="Path to grammar specified as Lark yaml",
)
validate_option = click.option(
    "--validate/--no-validate",
    default=True,
    help="Validate the output",
)


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
@click.version_option(__version__)
def main(verbose: int, quiet: bool):
    """CLI for semdsl.

    :param verbose: Verbosity while running.
    :param quiet: Boolean to be quiet or verbose.
    """
    if verbose >= 2:
        logger.setLevel(level=logging.DEBUG)
    elif verbose == 1:
        logger.setLevel(level=logging.INFO)
    else:
        logger.setLevel(level=logging.WARNING)
    if quiet:
        logger.setLevel(level=logging.ERROR)


@main.command()
@schema_option
@output_option
@grammar_option
@validate_option
def export_grammar(schema, grammar, validate, output):
    """
    Exports grammar from a LinkML schema.
    """
    engine = DSLEngine()
    if schema:
        engine.load_schema(schema)
    if grammar:
        engine.load_grammar(grammar)
    if validate:
        engine.compiled_grammar_module
    output.write(engine.lark_serialization)


@main.command()
@schema_option
@grammar_option
@output_option
@output_format_option
@click.option("--tree/--no-tree")
@click.argument("input", type=click.File("r"))
def parse(input, grammar, schema, tree, output, output_format):
    """
    Exports grammar from a LinkML schema.
    """
    engine = DSLEngine()
    engine.load_schema(schema)
    if grammar:
        engine.load_grammar(grammar)
    s = input.read()
    if tree:
        tree_obj = engine.parse_tree(s)
        print(tree_obj.pretty("  "))
    obj = engine.parse_as_object(s)
    output.write(_dumps(obj, output_format))


if __name__ == "__main__":
    main()
