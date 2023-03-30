import sys
from abc import abstractmethod
from dataclasses import dataclass, field
from io import StringIO
from types import ModuleType
from typing import Any, TextIO

from linkml_runtime.utils.compile_python import compile_python

from semdsl.datamodel.semdsl_model import SchemaGrammar


@dataclass
class Importer:
    """
    Base class for all importers
    """

    @abstractmethod
    def convert(self, input: Any, **kwargs) -> SchemaGrammar:
        """
        Convert input to a SchemaGrammar
        :param input: input to convert
        :param kwargs: additional arguments
        :return: SchemaGrammar
        """
        raise NotImplementedError
