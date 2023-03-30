import sys
from abc import abstractmethod
from dataclasses import dataclass, field
from io import StringIO
from types import ModuleType
from typing import Any, TextIO

from linkml_runtime.utils.compile_python import compile_python

from semdsl.datamodel.semdsl_model import SchemaGrammar


@dataclass
class Writer:
    """
    Base class for all writers
    """

    file: TextIO = field(default=sys.stdout)

    @abstractmethod
    def write(self, sg: SchemaGrammar, **kwargs):
        raise NotImplementedError

    def dumps(self, sg: SchemaGrammar, **kwargs):
        io = StringIO()
        self.file = io
        self.write(sg, **kwargs)
        return io.getvalue()

    def compile(self, sg: SchemaGrammar, **kwargs) -> ModuleType:
        return compile_python(self.dumps(sg, **kwargs))

    def emit(self, s: Any = None):
        self.file.write(str(s))
