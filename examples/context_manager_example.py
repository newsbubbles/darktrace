import logging
import sys
from pathlib import Path

# Add the src directory to the Python path if not already there (for local development)
src_path = Path(__file__).resolve().parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from tracelight import TracedError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("context_example")

def risky_database_operation(user_id, operation_type):
    """Simulate a database operation that might fail."""
    
    # Use TracedError as a context manager to automatically log state on errors
    with TracedError(logger=logger, level=logging.ERROR):
        connection_string = "postgresql://localhost:5432/mydb"
        query_timeout = 30
        retry_count = 3
        
        # Simulate different types of failures
        if operation_type == "delete" and user_id < 100:
            raise PermissionError(f"Cannot delete user {user_id}: insufficient permissions")
        elif operation_type == "update" and user_id > 1000:
            raise ValueError(f"Invalid user_id {user_id}: user not found")
        elif operation_type == "create" and user_id == 999:
            raise ConnectionError("Database connection timeout")
        
        # If we get here, the operation was successful
        return {"status": "success", "user_id": user_id, "operation": operation_type}

def main():
    print("\n💾 Testing database operations with automatic error tracing\n")
    
    operations = [
        (150, "create"),   # Should succeed
        (50, "delete"),    # Should fail with PermissionError
        (1500, "update"),  # Should fail with ValueError
        (999, "create"),   # Should fail with ConnectionError
    ]
    
    for user_id, operation in operations:
        print(f"Attempting {operation} for user {user_id}...")
        
        try:
            result = risky_database_operation(user_id, operation)
            print(f"✅ Success: {result}")
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            print("🔍 Full error context has been logged with all local variables")
        
        print("-" * 50)
    
    print("\n✅ All operations completed. Check the logs for detailed error context.")

if __name__ == "__main__":
    main()
