import unittest
import logging
from io import StringIO
import sys
from pathlib import Path
import json
from typing import Dict, Any, Optional

# Add the src directory to the Python path if not already there
src_path = Path(__file__).resolve().parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from tracelight.agent_utils import traced_tool
from tracelight.core import TracedError

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestDecoratorIntegration(unittest.TestCase):
    """Integration tests for decorators and error handling."""
    
    def setUp(self):
        # Create a StringIO object to capture log output
        self.log_output = StringIO()
        self.handler = logging.StreamHandler(self.log_output)
        self.test_logger = logging.getLogger("test_decorator_integration")
        self.test_logger.addHandler(self.handler)
        self.test_logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        self.test_logger.removeHandler(self.handler)
        self.handler.close()
    
    def test_traced_tool_with_complex_data(self):
        """Test traced_tool with complex data structures."""
        
        @traced_tool(logger=self.test_logger)
        def process_complex_data(data: Dict[str, Any]) -> Dict[str, Any]:
            # Simulate complex processing
            user_list = data["users"]  # Will fail if missing
            processed_users = []
            
            for user in user_list:
                processed_user = {
                    "id": user["id"],
                    "name": user["name"].upper(),
                    "age_group": "adult" if user["age"] >= 18 else "minor"
                }
                processed_users.append(processed_user)
            
            return {"processed_users": processed_users, "count": len(processed_users)}
        
        # Test with valid data
        valid_data = {
            "users": [
                {"id": 1, "name": "alice", "age": 25},
                {"id": 2, "name": "bob", "age": 17}
            ]
        }
        
        result = process_complex_data(valid_data)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["result"]["processed_users"]), 2)
        
        # Test with invalid data (missing 'users' key)
        invalid_data = {"members": []}
        
        result = process_complex_data(invalid_data)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "KeyError")
        self.assertIn("users", result["error"])
        
        # Check that the data structure was logged
        output = self.log_output.getvalue()
        self.assertIn("members", output)  # The invalid key should be logged
    
    def test_nested_function_error_tracing(self):
        """Test error tracing through nested function calls."""
        
        @traced_tool(logger=self.test_logger)
        def outer_processor(config: Dict[str, Any]) -> Dict[str, Any]:
            settings = config["settings"]
            return inner_processor(settings)
        
        def inner_processor(settings: Dict[str, Any]) -> Dict[str, Any]:
            # This will fail if 'database_url' is missing
            db_url = settings["database_url"]
            return {"connection": f"Connected to {db_url}"}
        
        # Test with incomplete config
        incomplete_config = {
            "settings": {
                "debug": True,
                "port": 8080
                # Missing 'database_url'
            }
        }
        
        result = outer_processor(incomplete_config)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "KeyError")
        
        # Check that we have frames from both functions
        self.assertGreater(len(result["frames"]), 1)
        
        # Check that local variables from both frames are captured
        frame_functions = [frame["function"] for frame in result["frames"]]
        self.assertIn("outer_processor", frame_functions)
        self.assertIn("inner_processor", frame_functions)
    
    def test_traced_error_context_manager(self):
        """Test TracedError as a context manager."""
        
        def risky_operation():
            with TracedError(logger=self.test_logger):
                sensitive_data = "secret_password_123"
                public_data = "hello_world"
                
                # Simulate an error
                raise ValueError("Something went wrong in risky operation")
        
        with self.assertRaises(ValueError):
            risky_operation()
        
        output = self.log_output.getvalue()
        
        # Check that the error was logged
        self.assertIn("ValueError", output)
        self.assertIn("Something went wrong", output)
        
        # Check that local variables were captured
        self.assertIn("sensitive_data", output)
        self.assertIn("public_data", output)


if __name__ == "__main__":
    unittest.main()