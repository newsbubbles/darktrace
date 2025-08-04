import logging
import traceback
import inspect
from types import FrameType
from typing import Any, Optional, Dict, Union, List, Callable


def log_exception_state(exc: Exception,
                        logger: logging.Logger,
                        level: int = logging.ERROR,
                        *,
                        max_var_length: int = 1000,
                        exclude_vars: Optional[List[str]] = None,
                        format_var: Optional[Callable[[str, Any], str]] = None) -> None:
    """
    Walk the traceback of `exc`, logging each frame's local variables.

    Args:
        exc: The caught exception.
        logger: A logging.Logger (or logger-like) instance.
        level: The log level to use (e.g. logging.ERROR, logging.DEBUG).
        max_var_length: If repr(var) exceeds this, it will be truncated with '...'.
        exclude_vars: List of variable names to exclude from logging (e.g. passwords).
        format_var: Optional function to customize variable formatting: 
                    format_var(var_name, var_value) -> formatted_string
    """
    exclude_vars = exclude_vars or []
    tb = exc.__traceback__
    # Header for context
    logger.log(level, "Logging exception state for: %s: %s",
              type(exc).__name__, exc)
    
    frame_count = 0
    while tb is not None:
        frame: FrameType = tb.tb_frame
        lineno: int = tb.tb_lineno
        func_name: str = frame.f_code.co_name
        filename: str = frame.f_code.co_filename
        
        frame_count += 1
        logger.log(level,
                  "-- Frame %d: %r in %s at line %d --",
                  frame_count, func_name, filename, lineno)

        for var_name, var_val in frame.f_locals.items():
            if var_name in exclude_vars:
                continue
                
            try:
                if format_var is not None:
                    rep = format_var(var_name, var_val)
                else:
                    rep = repr(var_val)
                    # truncate if too long
                    if len(rep) > max_var_length:
                        rep = rep[:max_var_length] + "...<truncated>"
            except Exception as format_err:
                rep = f"<unrepresentable: {type(format_err).__name__}>"

            logger.log(level, "    %s = %s", var_name, rep)

        tb = tb.tb_next
        

class TracedError(Exception):
    """An exception that automatically logs its traceback and all local variables.
    
    This can be raised directly or used as a context manager to automatically catch,
    log, and re-raise exceptions with detailed state information.
    """
    
    def __init__(self, 
                 message: str = "", 
                 logger: Optional[logging.Logger] = None,
                 level: int = logging.ERROR,
                 max_var_length: int = 1000,
                 exclude_vars: Optional[List[str]] = None):
        super().__init__(message)
        self.logger = logger or logging.getLogger(__name__)
        self.level = level
        self.max_var_length = max_var_length
        self.exclude_vars = exclude_vars or []
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            log_exception_state(
                exc_val, 
                self.logger, 
                self.level, 
                max_var_length=self.max_var_length,
                exclude_vars=self.exclude_vars
            )
            # Don't suppress the exception
            return False
        return True
