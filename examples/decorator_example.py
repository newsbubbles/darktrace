import logging
import sys
from darktrace.decorators import traced

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("darktrace_decorator")

# Use the @traced decorator to automatically log variable state on exception
@traced(logger=logger, level=logging.DEBUG)
def process_record(record):
    """Example function that processes a record and might fail."""
    # Extract ID (this will fail if 'id' is missing)
    record_id = record["id"]
    
    # Transform some values (will fail if values aren't the expected type)
    transformed = {
        "id": record_id,
        "value_squared": record["value"] ** 2,
        "name_upper": record["name"].upper()
    }
    
    # More processing...
    return transformed

# Use the @traced decorator with different options
@traced(logger=logger, reraise=False)  # Won't re-raise the exception
def safe_process(record):
    """This function catches and logs exceptions but doesn't propagate them."""
    return process_record(record)  # This calls the other function

def main():
    # Example of a good record
    good_record = {"id": 1, "value": 5, "name": "test"}
    
    # Example of a bad record
    bad_record1 = {"value": 10, "name": "missing_id"}
    bad_record2 = {"id": 2, "value": "not_a_number", "name": "type_error"}
    
    print("\n🔍 Testing @traced decorator\n")
    
    # Process good record
    print("Processing valid record...")
    result = process_record(good_record)
    print(f"Result: {result}")
    
    # This will raise an exception and log all variables
    print("\nProcessing record with missing ID...")
    try:
        process_record(bad_record1)
    except Exception as e:
        print(f"Caught exception: {type(e).__name__}: {e}")
        print("✅ All variables were automatically logged")
    
    # This uses the safe version that won't raise
    print("\nSafely processing bad record (using @traced with reraise=False)...")
    result = safe_process(bad_record2)
    print(f"Result: {result}")
    print("✅ Exception was logged but not raised")

if __name__ == "__main__":
    main()
