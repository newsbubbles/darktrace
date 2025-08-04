import logging
import sys
from tracelight import TracedError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("tracelight_context")

# Function that will raise an error
def parse_complex_data(data):
    # Some complex data parsing that might fail
    parsed = {}
    for key, value in data.items():  # Will raise AttributeError if data is not a dict
        parsed[key.upper()] = int(value)  # Will raise ValueError if value not convertible to int
    return parsed

def main():
    # Example data that will cause an error
    input_data = "not a dict"  # This will cause AttributeError in parse_complex_data
    
    print("\n🔍 Using TracedError as a context manager\n")
    
    # Use the context manager approach
    try:
        with TracedError("Error processing data", logger=logger):
            # This will fail but the TracedError will log all variables
            result = parse_complex_data(input_data)
            print(f"Processed result: {result}")  # Won't execute
    except Exception as e:
        print(f"\nCaught exception: {type(e).__name__}: {e}")
        print("✅ All variables were automatically logged")

if __name__ == "__main__":
    main()
