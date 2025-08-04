import unittest
import logging
from io import StringIO
import sys
from pathlib import Path
import json
from typing import Dict, Any, Optional, List

# Add the src directory to the Python path if not already there
src_path = Path(__file__).resolve().parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from tracelight.core import log_exception_state, TracedError

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestErrorReturnValues(unittest.TestCase):
    """Test that log_exception_state returns structured data correctly."""
    
    def setUp(self):
        # Create a StringIO object to capture log output
        self.log_output = StringIO()
        self.handler = logging.StreamHandler(self.log_output)
        self.test_logger = logging.getLogger("test_error_return")
        self.test_logger.addHandler(self.handler)
        self.test_logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        self.test_logger.removeHandler(self.handler)
        self.handler.close()
    
    def test_log_exception_state_return_structure(self):
        """Test that log_exception_state returns properly structured data."""
        
        def failing_function():
            local_var = "test_value"
            local_number = 42
            local_list = [1, 2, 3]
            raise ValueError("Test error message")
        
        try:
            failing_function()
        except Exception as e:
            result = log_exception_state(e, self.test_logger)
        
        # Check that result is not None
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        
        # Check required keys
        self.assertIn("error", result)
        self.assertIn("error_type", result)
        self.assertIn("frames", result)
        
        # Check error information
        self.assertEqual(result["error_type"], "ValueError")
        self.assertIn("Test error message", result["error"])
        
        # Check frames structure
        self.assertIsInstance(result["frames"], list)
        self.assertGreater(len(result["frames"]), 0)
        
        # Find the frame that contains the failing_function
        failing_frame = None
        for frame in result["frames"]:
            if frame["function"] == "failing_function":
                failing_frame = frame
                break
        
        self.assertIsNotNone(failing_frame, "Could not find failing_function frame")
        
        # Check frame structure
        self.assertIn("frame_number", failing_frame)
        self.assertIn("function", failing_frame)
        self.assertIn("file", failing_frame)
        self.assertIn("line", failing_frame)
        self.assertIn("locals", failing_frame)
        
        # Check that local variables were captured
        locals_dict = failing_frame["locals"]
        self.assertIn("local_var", locals_dict)
        self.assertIn("local_number", locals_dict)
        self.assertIn("local_list", locals_dict)
        
        # Check variable values
        self.assertEqual(locals_dict["local_var"], "test_value")
        self.assertEqual(locals_dict["local_number"], 42)
        self.assertEqual(locals_dict["local_list"], [1, 2, 3])
    
    def test_multiple_frames_capture(self):
        """Test that multiple stack frames are captured correctly."""
        
        def outer_function(x):
            outer_var = "outer_value"
            return middle_function(x + 1)
        
        def middle_function(y):
            middle_var = "middle_value"
            return inner_function(y * 2)
        
        def inner_function(z):
            inner_var = "inner_value"
            raise RuntimeError(f"Error with value {z}")
        
        try:
            outer_function(5)
        except Exception as e:
            result = log_exception_state(e, self.test_logger)
        
        # Should have multiple frames
        self.assertGreaterEqual(len(result["frames"]), 3)
        
        # Check that each frame has the expected function name and variables
        frame_functions = [frame["function"] for frame in result["frames"]]
        
        self.assertIn("outer_function", frame_functions)
        self.assertIn("middle_function", frame_functions)
        self.assertIn("inner_function", frame_functions)
        
        # Find and check specific frames
        for frame in result["frames"]:
            if frame["function"] == "outer_function":
                self.assertIn("outer_var", frame["locals"])
                self.assertEqual(frame["locals"]["outer_var"], "outer_value")
            elif frame["function"] == "middle_function":
                self.assertIn("middle_var", frame["locals"])
                self.assertEqual(frame["locals"]["middle_var"], "middle_value")
            elif frame["function"] == "inner_function":
                self.assertIn("inner_var", frame["locals"])
                self.assertEqual(frame["locals"]["inner_var"], "inner_value")
    
    def test_excluded_variables(self):
        """Test that excluded variables are not included in the result."""
        
        def function_with_secrets():
            password = "secret123"
            api_key = "abc123xyz"
            public_data = "hello world"
            raise ValueError("Test error")
        
        try:
            function_with_secrets()
        except Exception as e:
            result = log_exception_state(
                e, 
                self.test_logger, 
                exclude_vars=["password", "api_key"]
            )
        
        # Find the frame that contains the function_with_secrets
        secrets_frame = None
        for frame in result["frames"]:
            if frame["function"] == "function_with_secrets":
                secrets_frame = frame
                break
        
        self.assertIsNotNone(secrets_frame, "Could not find function_with_secrets frame")
        
        # Check that excluded variables are not in the result
        frame_locals = secrets_frame["locals"]
        self.assertNotIn("password", frame_locals)
        self.assertNotIn("api_key", frame_locals)
        
        # But public data should be there
        self.assertIn("public_data", frame_locals)
        self.assertEqual(frame_locals["public_data"], "hello world")
    
    def test_json_serializable_output(self):
        """Test that the returned data is JSON serializable."""
        
        def test_function():
            string_var = "test"
            int_var = 42
            float_var = 3.14
            bool_var = True
            none_var = None
            list_var = [1, 2, 3]
            dict_var = {"key": "value"}
            raise ValueError("Test error")
        
        try:
            test_function()
        except Exception as e:
            result = log_exception_state(e, self.test_logger)
        
        # Test that the result can be JSON serialized
        try:
            json_str = json.dumps(result)
            # And deserialized back
            parsed_result = json.loads(json_str)
            
            # Verify structure is preserved
            self.assertEqual(parsed_result["error_type"], "ValueError")
            self.assertIn("frames", parsed_result)
            
        except (TypeError, ValueError) as e:
            self.fail(f"Result is not JSON serializable: {e}")


if __name__ == "__main__":
    unittest.main()