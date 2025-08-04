import logging
import sys
import json
from typing import Dict, Any
from pathlib import Path

# Add the src directory to the Python path if not already there (for local development)
src_path = Path(__file__).resolve().parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from tracelight.agent_utils import traced_tool

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("agent_tools")

# Example function representing an agent tool
@traced_tool(logger=logger)
def process_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Example of a tool that processes user data."""
    # Let's simulate complex processing that might fail
    username = user_data["name"]  # This will fail if 'name' is missing
    age = int(user_data["age"])   # This will fail if 'age' isn't convertible to int
    
    # More processing logic...
    processed_result = {
        "username": username.lower(),
        "age_category": "adult" if age >= 18 else "minor",
        "can_receive_marketing": age >= 18 and user_data.get("marketing_opt_in", False)
    }
    
    return processed_result

def simulate_mcp_server():
    print("\n🤖 Simulating an MCP Server with error handling\n")
    
    # Example of well-formed input
    good_input = {"name": "Alice", "age": "30", "marketing_opt_in": True}
    
    # Example of malformed input that will cause errors
    bad_input = {"user": "Bob", "age": "not_a_number"}
    
    # Process good input
    print("Processing valid user data...")
    result1 = process_user_data(good_input)
    print(f"Result: {json.dumps(result1, indent=2)}")
    
    # Process bad input - this will cause errors but won't crash
    print("\nProcessing invalid user data...")
    result2 = process_user_data(bad_input)
    print(f"Result: {json.dumps(result2, indent=2)}")
    print("\n✅ Notice how the function returns a structured error response rather than crashing")
    print("🔍 And detailed variable state was logged for debugging")

if __name__ == "__main__":
    simulate_mcp_server()
