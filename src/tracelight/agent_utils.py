import logging
import functools
import traceback
from typing import Any, Dict, Callable, TypeVar, Optional, List, Union, cast

from tracelight.core import log_exception_state

# Type variable for generic function
F = TypeVar('F', bound=Callable[..., Any])

def traced_tool(logger: Optional[logging.Logger] = None,
                level: int = logging.ERROR,
                max_var_length: int = 1000,
                exclude_vars: Optional[List[str]] = None) -> Callable[[F], F]:
    """
    Decorator for agent tool functions that ensures they return a response dict
    with detailed error information when exceptions occur.
    
    Perfect for wrapping MCP Server tool implementations to ensure they never
    crash the agent and always return useful debugging information.
    
    Args:
        logger: Logger to use (creates one if None)
        level: Log level to use
        max_var_length: Maximum length for variable representations
        exclude_vars: Variable names to exclude from logs
        
    Return value format on success:
        {"status": "success", "result": <original return value>}
        
    Return value format on error:
        {
            "status": "error",
            "error_type": "ExceptionClassName",
            "error": "Error message", 
            "traceback": "Formatted traceback"
        }
    """
    _logger = logger or logging.getLogger(__name__)
    _exclude_vars = exclude_vars or []
    
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            try:
                result = func(*args, **kwargs)
                # If already a dict with status, return as is
                if isinstance(result, dict) and "status" in result:
                    return result
                # Otherwise wrap the result
                return {"status": "success", "result": result}
            except Exception as e:
                # Log the detailed state
                log_exception_state(
                    e, 
                    _logger, 
                    level, 
                    max_var_length=max_var_length,
                    exclude_vars=_exclude_vars
                )
                
                # Return a structured error response
                return {
                    "status": "error",
                    "error_type": type(e).__name__,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                
        return cast(F, wrapper)
    return decorator


def format_for_agent(var_name: str, var_value: Any) -> str:
    """
    Formats variables in a way that's more readable for agents/LLMs.
    
    This is a utility function you can pass to log_exception_state
    as the format_var parameter when you want the output to be
    easily parsed by an agent.
    
    Args:
        var_name: Name of the variable
        var_value: Value of the variable
        
    Returns:
        A formatted string representation optimized for LLM comprehension
    """
    try:
        # Special handling for common types
        if isinstance(var_value, dict):
            if len(var_value) > 10:
                # For large dicts, summarize
                preview = {k: var_value[k] for k in list(var_value.keys())[:5]}
                return f"Dict with {len(var_value)} items. First 5: {preview} ..."
            return str(var_value)
        
        elif isinstance(var_value, (list, tuple, set)):
            if len(var_value) > 10:
                # For large sequences, summarize
                preview = list(var_value)[:5]
                return f"{type(var_value).__name__} with {len(var_value)} items. First 5: {preview} ..."
            return str(var_value)
            
        elif isinstance(var_value, str) and len(var_value) > 500:
            # For long strings, truncate in the middle
            return f"{var_value[:200]}... (truncated, length={len(var_value)}) ...{var_value[-200:]}"
            
        else:
            # Default representation
            return repr(var_value)
            
    except Exception:
        return f"<unrepresentable {type(var_value).__name__}>"
