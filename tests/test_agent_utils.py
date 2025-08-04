import unittest
import logging
from io import StringIO
from typing import Dict, Any

from darktrace.agent_utils import traced_tool, format_for_agent

class TestAgentUtils(unittest.TestCase):
    def setUp(self):
        # Capture log output
        self.log_capture = StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.logger = logging.getLogger("test_agent_utils")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
    
    def test_traced_tool_success(self):
        @traced_tool(logger=self.logger)
        def my_tool(x, y):
            return x * y
        
        # Call with valid inputs
        result = my_tool(5, 10)
        
        # Should return a success dict
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 50)
        
        # No logs should be present
        self.assertEqual(self.log_capture.getvalue(), "")
    
    def test_traced_tool_error(self):
        @traced_tool(logger=self.logger)
        def my_tool(x, y):
            return x / y  # Will raise ZeroDivisionError if y is 0
        
        # Call with invalid inputs
        result = my_tool(10, 0)
        
        # Should return an error dict
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "ZeroDivisionError")
        self.assertIn("division by zero", result["error"])
        self.assertIn("Traceback", result["traceback"])
        
        # Should log the error
        log_output = self.log_capture.getvalue()
        self.assertIn("Logging exception state for: ZeroDivisionError", log_output)
        self.assertIn("x = 10", log_output)
        self.assertIn("y = 0", log_output)
    
    def test_format_for_agent(self):
        # Test with different variable types
        self.assertEqual(format_for_agent("x", 42), "42")
        
        # Test with long string
        long_str = "a" * 1000
        formatted = format_for_agent("long_str", long_str)
        self.assertLess(len(formatted), 1000)  # Should be shortened
        self.assertIn("truncated", formatted)
        
        # Test with large dict
        large_dict = {f"key{i}": i for i in range(20)}
        formatted = format_for_agent("large_dict", large_dict)
        self.assertIn("Dict with 20 items", formatted)
        
        # Test with large list
        large_list = list(range(20))
        formatted = format_for_agent("large_list", large_list)
        self.assertIn("list with 20 items", formatted)

if __name__ == "__main__":
    unittest.main()
