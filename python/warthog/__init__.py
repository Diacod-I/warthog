"""Warthog: a deep learning library built from scratch in Python and Rust."""

from importlib.metadata import version

from ._warthog import sum_as_string

__version__ = version("warthog")
__all__ = ["sum_as_string", "__version__"]
