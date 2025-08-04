import functools
import logging
from typing import Any, Callable, Optional, List, TypeVar, cast, Union

from tracelight.core import log_exception_state

# Type variable for decorator to preserve function signature
F = TypeVar('F', bound=Callable[..., Any])

def traced(logger: Optional[logging.Logger] = None,
           level: int = logging.ERROR,
           max_var_length: int = 1000,
           exclude_vars: Optional[List[str]] = None,
           reraise: bool = True) -> Callable[[F], F]:
    """
    Decorator that catches exceptions and logs all local variables in the traceback.
    
    Args:
        logger: Logger to use (creates one if None)
        level: Log level to use
        max_var_length: Maximum length for variable representations
        exclude_vars: Variable names to exclude from logs
        reraise: Whether to re-raise the exception after logging
    
    Examples:
        @traced()
        def my_function(x, y):
            return x / y  # Will log all context if y is 0
            
        @traced(logger=my_logger, level=logging.WARNING, reraise=False)
        def safe_operation():
            # Exceptions will be logged with variables but not propagated
            risky_call()
    """
    _logger = logger or logging.getLogger(__name__)
    _exclude_vars = exclude_vars or []
    
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_exception_state(
                    e, 
                    _logger, 
                    level, 
                    max_var_length=max_var_length,
                    exclude_vars=_exclude_vars
                )
                if reraise:
                    raise
                return None  # If not reraising
                
        return cast(F, wrapper)
    return decorator
