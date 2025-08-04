#!/usr/bin/env python3

import logging
import sys
from pydantic import BaseModel, Field
from tracelight.agent_utils import traced_tool
from tracelight.core import log_exception_state

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
    return items[value] * mapping["multiplier"]

# Run tests
if __name__ == "__main__":
    print("\n=== RUNNING TRACELIGHT TESTS ===\n")
    
    # Test 1: Validation Error
    print("\nTest 1: Pydantic Validation Error")
    try:
        result = function_with_validation_error({"optional_field": "test"})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Caught exception: {e}")
    
    # Test 2: Runtime Error
    print("\nTest 2: Division by Zero")
    try:
        result = function_with_runtime_error(10, 0)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Caught exception: {e}")
    
    # Test 3: Nested Error with multiple frames
    print("\nTest 3: Nested Function with Multiple Frames")
    try:
        result = outer_function(10)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Caught exception: {e}")
    
    print("\n=== TEST COMPLETE ===\n")
    print(f"Check logs/tracelight_test.log for full trace output")