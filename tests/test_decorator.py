#!/usr/bin/env python3

import logging
import sys
import json
from typing import Dict, Any, Optional
from tracelight.agent_utils import traced_tool
from tracelight.core import TracedError

# Set up logging
logger = logging.getLogger("decorator_test")
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter("%(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Define some example tools that might be used in an agent system

@traced_tool(logger=logger)
def weather_tool(location: str = "New York") -> Dict[str, Any]:
    """Simulated weather tool that would normally make API calls"""
    if not location:
        raise ValueError("Location cannot be empty")
    
    if location.lower() == "error":
        # Simulate deeper error
        return process_location(location)
    
    # Simulate successful API call
    return {"temperature": 72, "condition": "sunny", "location": location}


def process_location(loc: str) -> Dict[str, Any]:
    """Process location string - will fail for certain inputs"""
    locations_db = {"new york": {"lat": 40.7, "lng": -74.0}}
    
    # Convert to lowercase for lookup
    loc_key = loc.lower()
    
    # This will raise KeyError if location not in our simple DB
    coords = locations_db[loc_key]
    
    # This will cause IndexError
    some_list = [1, 2, 3]
    impossible_index = len(some_list) + 10
    value = some_list[impossible_index]  # This will fail
    
    return {"coords": coords, "data": value}


@traced_tool(logger=logger)
def divide_numbers(a: Optional[float] = None, b: Optional[float] = None) -> Dict[str, Any]:
    """Simulated calculation tool showing different error types"""
    if a is None or b is None:
        raise ValueError("Both 'a' and 'b' parameters are required")
        
    # This will raise ZeroDivisionError if b is 0
    result = a / b
    
    return {"result": result, "operation": "division"}


@traced_tool(logger=logger)
async def async_tool(query: str) -> Dict[str, Any]:
    """Demonstrate that traced_tool works with async functions too"""
    # Simulate async operation
    if not query:
        raise ValueError("Query cannot be empty")
        
    if query.lower() == "error":
        raise RuntimeError("Simulated async error")
        
    # Return success
    return {"results": [f"Result for {query}"], "count": 1}


def run_tool_and_print_result(tool_func, *args, **kwargs):
    """Helper to run a tool and print its result nicely"""
    print(f"\nRunning {tool_func.__name__} with args={args}, kwargs={kwargs}")
    try:
        result = tool_func(*args, **kwargs)
        print(f"Result status: {result.get('status')}")
        
        if result.get('status') == 'error':
            # Print error details
            print(f"Error type: {result.get('error_type')}")
            print(f"Error message: {result.get('error')}")
            print(f"Frames captured: {len(result.get('frames', []))}")
            
            # Show the first frame's details
            if result.get('frames'):
                first_frame = result.get('frames')[0]
                print(f"\nFirst frame details:")
                print(f"  Function: {first_frame.get('function')}")
                print(f"  File: {first_frame.get('file')}")
                print(f"  Line: {first_frame.get('line')}")
                print(f"  Local variables: {list(first_frame.get('locals', {}).keys())}")
        else:
            # Print success result
            print(f"Result data: {result.get('result')}")
    except Exception as e:
        print(f"Unexpected exception: {type(e).__name__}: {e}")


# Run tests
if __name__ == "__main__":
    print("\n=== TESTING TRACED_TOOL DECORATOR ===\n")
    
    # Test successful case
    run_tool_and_print_result(weather_tool, location="Seattle")
    
    # Test ValueError
    run_tool_and_print_result(weather_tool, location="")
    
    # Test nested error (KeyError -> IndexError)
    run_tool_and_print_result(weather_tool, location="Error")
    
    # Test division error
    run_tool_and_print_result(divide_numbers, a=10, b=0)
    
    # Test missing parameter
    run_tool_and_print_result(divide_numbers, a=10)
    
    print("\n=== TESTS COMPLETE ===\n")
