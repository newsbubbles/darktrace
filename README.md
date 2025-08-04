# Darktrace

> Reveal hidden state in Python exceptions with automatic variable tracing

Darktrace exposes the hidden state of your application by automatically logging all local variables in each frame of an exception's traceback. This gives you instant insight into what went wrong without having to add print statements or run in debug mode.

## Installation

```bash
pip install darktrace
```

## Quick Start

```python
import logging
from darktrace import log_exception_state

# Configure your logger however you like
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("exception_logger")

def some_function(x):
    a = x + 1
    b = a * 2
    return b / 0  # Deliberate error

try:
    some_function(5)
except Exception as e:
    # Log all local variables from each frame
    log_exception_state(e, logger)
    # Re-raise if needed
    raise
```

## Use Cases

Darktrace is particularly useful for:

### 1. Data‐Pipeline Breakdowns

**Context**: Multi-stage ETL jobs where a mysterious `KeyError` pops up.

**With Darktrace**: Your logs show the full contents of the record and every local variable—no need to sprinkle `print` calls or guess which field is missing.

### 2. Async Callback Chaos

**Context**: In an `asyncio`-driven system, tasks fire off callbacks and one raises an exception deep inside a helper function.

**With Darktrace**: You get the full context of all local variables in that callback frame—instantly pinpointing the cause.

### 3. Agent-Based Workflows

**Context**: Your LLM‐driven agent orchestrates several tools; one tool call fails with a parsing error.

**With Darktrace**: You immediately see all variables in context, including the raw responses and state data—so you can adjust your tool chain.

## Integration with Agent Systems

Darktrace is designed to work seamlessly with agent-based systems and Model Context Protocol (MCP) servers. It can be integrated as a drop-in error handler to provide rich debugging information when tool calls or agent workflows fail unexpectedly.

```python
from darktrace import log_exception_state

def agent_tool_call(params):
    try:
        # Complex tool implementation
        result = process_complex_workflow(params)
        return {"status": "success", "data": result}
    except Exception as e:
        # Log all variables in each frame of the exception
        log_exception_state(e, logger)
        # Return a graceful error response with helpful context
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
```

## Advanced Usage

```python
from darktrace import log_exception_state

# Customize variable formatting
log_exception_state(e, logger, 
                   level=logging.ERROR,  # Log level
                   max_var_length=2000)  # Allow longer variable values
```

## License

MIT
