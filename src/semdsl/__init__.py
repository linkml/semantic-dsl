"""semdsl package."""
import importlib_metadata

try:
    __version__ = importlib_metadata.version(__name__)
except importlib_metadata.PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"  # pragma: no cover

from semdsl.datamodel.semdsl_model import *
from semdsl.dsl_engine import DSLEngine

__all__ = [
    "DSLEngine",
]
