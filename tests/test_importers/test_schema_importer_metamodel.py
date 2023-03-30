"""Demo version test."""

import unittest

from linkml_runtime.utils.introspection import package_schemaview

from semdsl.importers.schema_importer import SchemaImporter
from semdsl.mapper.mapper import Mapper
from semdsl.writers.lark_writer import LarkWriter


class TestSchemaImporter(unittest.TestCase):
    """Test importing schema."""

    def setUp(self) -> None:
        """Set up."""
        self.schemaview = package_schemaview("linkml_runtime.linkml_model.meta")
        self.importer = SchemaImporter()

    @unittest.skip("Too slow")
    def test_model(self):
        """Generate functional syntax for LinkML metamodel."""
        im = self.importer
        sg = im.convert(self.schemaview.schema)
        writer = LarkWriter()
        print(writer.write(sg))
        mod = writer.compile(sg)
        print(f"Compiled to {mod}")
        mapper = Mapper(schemaview=self.schemaview, schemagrammar=sg)
        print("Parsing: SchemaDefinition(id=x name=y)")
        tree = mod.grammar.parse("SchemaDefinition(id=x name=y)")
        # print(tree.pretty())
