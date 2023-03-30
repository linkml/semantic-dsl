from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

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
