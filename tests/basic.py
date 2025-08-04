#!/usr/bin/env python3

import logging
import sys
import json
import os
from pathlib import Path

# Add the src directory to the Python path if not already there
src_path = Path(__file__).resolve().parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
    print(f"Added {src_path} to Python path")
else:
    print(f"{src_path} already in Python path")

# Import after adjusting Python path
import tracelight
from pydantic import BaseModel, Field
from tracelight.agent_utils import traced_tool
from tracelight.core import log_exception_state

print(f"Imported tracelight.core from {tracelight.core.__file__}")

# Set up visible logging to both file and console
logger = logging.getLogger("tracelight_test")
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler("logs/tracelight_test.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter("%(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Example class used in validation errors
class TestRequest(BaseModel):
    required_field: str = Field(..., description="A required field")
    optional_field: str = Field(None, description="An optional field")

# The traced tool decorator will catch and log the exception
@traced_tool(logger=logger, level=logging.INFO)
def function_with_validation_error(request_data):
    """Function that will fail with pydantic validation"""
    # This will raise a validation error if required_field is missing
    request = TestRequest(**request_data)
    return {"message": f"Successfully processed {request.required_field}"}

# Another function that will raise a different kind of error
@traced_tool(logger=logger)
def function_with_runtime_error(a, b):
    """Function that will fail with a division error"""
    # This will raise a ZeroDivisionError if b is 0
    return a / b

# A function nested deeper to show stack trace capabilities
@traced_tool(logger=logger)
def outer_function(x):
    """Function that calls another function which fails"""
    # Some local variables for demonstration
    some_list = [1, 2, 3, 4, 5]
    some_dict = {"a": 1, "b": 2, "x": x}
    
    # This will eventually fail
    return inner_function(x, some_list, some_dict)

def inner_function(value, items, mapping):
    """Inner function that will fail with an index error"""
    # This will raise an IndexError if value >= len(items)
    return items[value] * mapping.get("multiplier", 1)

# A function that directly uses log_exception_state to demonstrate the return value
def demo_log_exception_state(x):
    """Demonstrate log_exception_state's structured return value"""
    try:
        result = inner_function(x, [1, 2, 3], {"a": 1})
        return {"status": "success", "result": result}
    except Exception as e:
        # Capture and return the structured error data
        structured_data = log_exception_state(
            e, logger, logging.ERROR,
            max_var_length=500
        )
        print("\nSTRUCTURED ERROR DATA:\n")
        print(json.dumps(structured_data, indent=2) if structured_data else "None returned")
        return {"status": "error", **(structured_data or {})}

# Run tests
if __name__ == "__main__":
    print("\n=== RUNNING TRACELIGHT TESTS ===\n")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Test 1: Validation Error with traced_tool
    print("\nTest 1: Pydantic Validation Error")
    result = function_with_validation_error({"optional_field": "test"})
    print(f"Result status: {result['status']}")
    print(f"Error type: {result.get('error_type')}")
    print(f"Error message: {result.get('error')}")
    print(f"Number of stack frames: {len(result.get('frames', []))}")
    
    # Test 2: Runtime Error with traced_tool
    print("\nTest 2: Division by Zero")
    result = function_with_runtime_error(10, 0)
    print(f"Result status: {result['status']}")
    print(f"Error type: {result.get('error_type')}")
    print(f"Error message: {result.get('error')}")
    # Check if frames is present and has at least one frame
    if result.get('frames') and len(result['frames']) > 0:
        print(f"First frame function: {result['frames'][0].get('function')}")
    else:
        print("No frames or empty frames list")
    
    # Test 3: Nested Error with multiple frames
    print("\nTest 3: Nested Function with Multiple Frames")
    result = outer_function(10)
    print(f"Result status: {result['status']}")
    print(f"Error type: {result.get('error_type')}")
    print(f"Error message: {result.get('error')}")
    # Safely get frame functions
    if 'frames' in result and result['frames']:
        frame_functions = [frame.get('function') for frame in result['frames']]
        print(f"Stack frames: {frame_functions}")
        if result['frames'][0].get('locals'):
            print(f"Local variables in first frame: {list(result['frames'][0]['locals'].keys())}")
        else:
            print("No locals in first frame")
    else:
        print("No frames available")
    
    # Test 4: Direct use of log_exception_state
    print("\nTest 4: Direct Use of log_exception_state")
    result = demo_log_exception_state(5)
    print(f"Result status: {result['status']}")
    if result['status'] == 'error':
        print(f"Error type: {result.get('error_type')}")
        print(f"Error message: {result.get('error')}")
        if 'frames' in result and result['frames']:
            print(f"Frame count: {len(result['frames'])}")
            print(f"First frame function: {result['frames'][0].get('function')}")
    
    print("\n=== TEST COMPLETE ===\n")
    print(f"Check logs/tracelight_test.log for full trace output")