"""Darktrace: Reveal hidden state in Python exceptions with automatic variable tracing.

Provides tools to automatically log all local variables in each frame of an exception's
traceback, giving you instant insight into what went wrong without having to add print
statements or run in debug mode.
"""

from darktrace.core import log_exception_state, TracedError
from darktrace.decorators import traced

__version__ = "0.1.0"
__all__ = ["log_exception_state", "TracedError", "traced"]
