import logging
import sys
from pathlib import Path

# Add the src directory to the Python path if not already there (for local development)
src_path = Path(__file__).resolve().parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from tracelight import log_exception_state

# Configure logging to stdout
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("tracelight_example")

# Example function that will raise an exception
def calculate_value(x, y):
    intermediate = x * 2
    result = intermediate / y  # Will raise ZeroDivisionError if y is 0
    return result

def main():
    try:
        # Call a function that will fail
        value = calculate_value(42, 0)
        print(f"Calculated value: {value}")  # This won't execute
    except Exception as e:
        # Use tracelight to log all variables in each stack frame
        print("\n🔍 Exception caught! Logging all local variables in each frame:\n")
        log_exception_state(e, logger, level=logging.ERROR)
        print("\n✅ All variables logged. Now we can fix the issue knowing the full context.")

if __name__ == "__main__":
    main()
