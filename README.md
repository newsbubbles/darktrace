# Tracelight

> Reveal hidden state in Python exceptions with automatic variable tracing

Tracelight exposes the hidden state of your application by automatically logging all local variables in each frame of an exception's traceback. This gives you instant insight into what went wrong without having to add print statements or run in debug mode.

## Installation

```bash
pip install tracelight
```

## Quick Start

```python
import logging
from tracelight import log_exception_state

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
from tracelight import traced

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
from tracelight.agent_utils import traced_tool

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
from tracelight import TracedError

# Automatically logs and preserves original exception
with TracedError(logger=my_logger):
    risky_operation()
```

## Use Cases

Tracelight is particularly useful for:

### 1. Data‐Pipeline Breakdowns

**Context**: Multi-stage ETL jobs where a mysterious `KeyError` pops up.

**With Tracelight**: Your logs show the full contents of the record and every local variable—no need to sprinkle `print` calls or guess which field is missing.

### 2. Async Callback Chaos

**Context**: In an `asyncio`-driven system, tasks fire off callbacks and one raises an exception deep inside a helper function.

**With Tracelight**: You get the full context of all local variables in that callback frame—instantly pinpointing the cause.

### 3. Agent-Based Workflows

**Context**: Your LLM‐driven agent orchestrates several tools; one tool call fails with a parsing error.

**With Tracelight**: You immediately see all variables in context, including the raw responses and state data—so you can adjust your tool chain.

## Integration with Agent Systems

Tracelight is designed to work seamlessly with agent-based systems and Model Context Protocol (MCP) servers. It can be integrated as a drop-in error handler to provide rich debugging information when tool calls or agent workflows fail unexpectedly.

```python
from tracelight import log_exception_state
from tracelight.agent_utils import traced_tool

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

## FastMCP Integration Example

Tracelight integrates seamlessly with FastMCP servers for rich error handling in MCP tools:

```python
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field
from tracelight.agent_utils import traced_tool
import logging

# Setup logging
logger = logging.getLogger("mcp-server")

# Create FastMCP server
mcp = FastMCP("TracelightExample")

# Define request model
class WeatherRequest(BaseModel):
    city: str = Field(..., description="City to get weather for")
    country_code: str = Field(None, description="Optional 2-letter country code")

# Define response models
class WeatherResponse(BaseModel):
    temperature: float
    condition: str
    humidity: int

class ErrorResponse(BaseModel):
    status: str = "error"
    error_type: str
    error: str
    context: dict = None

# Create traced tool with automatic error handling
@mcp.tool()
@traced_tool(logger=logger)
async def get_weather(request: WeatherRequest, ctx: Context):
    """Get current weather with automatic error tracing."""
    # This will automatically log all variables if an exception occurs
    # and return a properly formatted error response
    
    if request.city.lower() == "atlantis":
        raise ValueError("City not found: Atlantis is a fictional city")  
        
    # Simulate API call
    weather_data = await fetch_weather_api(request.city)  # Would raise on failure
    
    # The decorator automatically handles any exceptions and returns
    # a structured error response that works with FastMCP
    return WeatherResponse(
        temperature=23.5,
        condition="sunny",
        humidity=65
    )
```

When the tool fails, Tracelight logs the complete variable state and returns a structured error response that works perfectly with FastMCP's tool response format, making it easy for agents to handle errors gracefully.

## Advanced Usage

```python
from tracelight import log_exception_state
from tracelight.agent_utils import format_for_agent

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
