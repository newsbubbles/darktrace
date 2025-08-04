#!/usr/bin/env python3

import logging
import sys
import json
from typing import Dict, Any, Optional, List
from tracelight.core import log_exception_state, TracedError

# Set up logging
logger = logging.getLogger("return_test")
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter("%(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


def simulate_complex_error() -> Dict[str, Any]:
    """Simulate a complex error scenario with nested calls and different variable types"""
    try:
        return outer_function()
    except Exception as e:
        # Get structured error data
        structured_data = log_exception_state(e, logger)
        
        print("\nSTRUCTURED ERROR DATA FROM log_exception_state:\n")
        print(json.dumps(structured_data, indent=2))
        
        # Verify data structure
        validate_error_data(structured_data)
        
        return {"status": "error", **structured_data}


def validate_error_data(error_data: Dict[str, Any]):
    """Validate that the error data has the expected structure"""
    # Check required fields
    assert "error" in error_data, "Missing 'error' field"
    assert "error_type" in error_data, "Missing 'error_type' field"
    assert "frames" in error_data, "Missing 'frames' field"
    
    # Check frames structure
    frames = error_data["frames"]
    assert isinstance(frames, list), "'frames' must be a list"
    
    if frames:
        first_frame = frames[0]
        # Check frame structure
        assert "frame_number" in first_frame, "Frame missing 'frame_number'"
        assert "function" in first_frame, "Frame missing 'function'"
        assert "file" in first_frame, "Frame missing 'file'"
        assert "line" in first_frame, "Frame missing 'line'"
        assert "locals" in first_frame, "Frame missing 'locals'"
    
    print("✓ Error data structure validation passed")


def outer_function() -> str:
    """Function with various variable types that calls a function that fails"""
    outer_var = "This is a string in the outer function"
    numeric_list = [1, 2, 3, 4, 5]
    complex_dict = {
        "name": "example",
        "values": numeric_list,
        "nested": {
            "a": 1,
            "b": 2
        }
    }
    
    # Tuple and set examples
    tuple_example = (1, "two", 3.0)
    set_example = {"a", "b", "c"}
    
    # Create a custom object
    class CustomObject:
        def __init__(self, name):
            self.name = name
    
    custom = CustomObject("test_object")
    
    # Call the function that will eventually fail
    return middle_function(numeric_list, complex_dict, custom)


def middle_function(numbers: List[int], data: Dict[str, Any], obj: Any) -> str:
    """Middle function that passes data to the inner function that will fail"""
    middle_var = "This is a string in the middle function"
    multiplier = 10
    
    if not isinstance(numbers, list):
        raise TypeError("'numbers' must be a list")
    
    # Function that will fail
    return inner_function(numbers, multiplier, data, obj)


def inner_function(numbers: List[int], multiplier: int, 
                  data: Dict[str, Any], obj: Any) -> str:
    """Inner function that will fail with KeyError and IndexError"""
    try:
        # This will fail with KeyError
        missing_key = data["non_existent_key"]
        
        # We'll never get here
        return f"Value: {missing_key * multiplier}"
    except KeyError:
        # Handle the KeyError but then hit an IndexError
        try:
            # This will fail with IndexError
            out_of_bounds = numbers[len(numbers) + 5] 
            return f"Fallback value: {out_of_bounds}"
        except IndexError as idx_err:
            # Add some context to the error
            raise IndexError(f"Failed to access numbers: {idx_err}")


if __name__ == "__main__":
    print("\n=== TESTING log_exception_state RETURN VALUES ===\n")
    
    # Run the test and print results
    result = simulate_complex_error()
    
    print(f"\nFinal result status: {result.get('status')}")
    print(f"Error type: {result.get('error_type')}")
    print(f"Error message: {result.get('error')}")
    
    print("\n=== TEST COMPLETE ===\n")
