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

## Key Features

### Function Decorator

Automate error handling with the `@traced` decorator:

```python
from darktrace import traced

@traced()
def risky_function(x, y):
    complicated_result = process(x)
    return complicated_result[y]  # Might raise KeyError

# All exceptions automatically logged with full variable context!
risky_function("input", "missing_key")
```

### Agent Tool Decorator

Specifically designed for agent systems and MCP servers:

```python
from darktrace.agent_utils import traced_tool

@traced_tool()
def weather_tool(location="New York"):
    # Complex implementation with HTTP calls etc.
    return get_weather_data(location) 

# If anything fails, returns a structured error dict:
# {"status": "error", "error_type": "...", ...}
```

### Context Manager

Easily wrap specific blocks of code:

```python
from darktrace import TracedError

# Automatically logs and preserves original exception
with TracedError(logger=my_logger):
    risky_operation()
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
from darktrace.agent_utils import traced_tool

# Method 1: Wrap entire tool with decorator
@traced_tool()
def agent_tool(params):
    # Complex implementation...
    return process_complex_workflow(params)

# Method 2: Manual integration
def another_tool(params):
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
from darktrace.agent_utils import format_for_agent

# Exclude sensitive variables
log_exception_state(e, logger, exclude_vars=["password", "api_key"])

# Custom formatting for agent consumption
log_exception_state(e, logger, format_var=format_for_agent)

# Customize log level and variable length
log_exception_state(e, logger, 
                   level=logging.ERROR,  # Log level
                   max_var_length=2000)  # Allow longer variable values
```

## License

MIT
