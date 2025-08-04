import logging
import sys
from darktrace import log_exception_state

# Configure logging to stdout
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("darktrace_example")

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
        # Use darktrace to log all variables in each stack frame
        print("\n🔍 Exception caught! Logging all local variables in each frame:\n")
        log_exception_state(e, logger, level=logging.ERROR)
        print("\n✅ All variables logged. Now we can fix the issue knowing the full context.")

if __name__ == "__main__":
    main()
