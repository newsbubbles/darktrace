import unittest
import logging
from io import StringIO
from typing import Dict, Any

from tracelight.agent_utils import traced_tool, format_for_agent


class TestAgentUtils(unittest.TestCase):
    def setUp(self):
        # Create a StringIO object to capture log output
        self.log_output = StringIO()
        self.handler = logging.StreamHandler(self.log_output)
        self.logger = logging.getLogger("test_agent_utils")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
        
    def test_traced_tool_success(self):
        # Test that traced_tool properly wraps successful results
        
        @traced_tool(logger=self.logger)
        def successful_tool(a, b):
            return a + b
        
        result = successful_tool(3, 4)
        
        # Check that it's properly formatted
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 7)
        
        # No logs should be generated on success
        self.assertEqual(self.log_output.getvalue(), "")
        
    def test_traced_tool_error(self):
        # Test that traced_tool handles errors correctly
        
        @traced_tool(logger=self.logger)
        def failing_tool(a, b):
            return a / b  # Will fail if b is 0
        
        result = failing_tool(5, 0)
        
        # Check the error response format
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "ZeroDivisionError")
        self.assertIn("division by zero", result["error"])
        self.assertIn("Traceback", result["traceback"])
        
        # Check that it was logged
        output = self.log_output.getvalue()
        self.assertIn("ZeroDivisionError", output)
        self.assertIn("a = 5", output)
        self.assertIn("b = 0", output)
        
    def test_traced_tool_already_formatted(self):
        # Test that traced_tool doesn't double-wrap results
        
        @traced_tool(logger=self.logger)
        def preformatted_tool():
            # Return an already formatted response
            return {"status": "success", "result": "custom data"}
        
        result = preformatted_tool()
        
        # Should be returned as-is
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], "custom data")
        
    def test_format_for_agent(self):
        # Test the format_for_agent function
        
        # Test dict formatting
        small_dict = {"a": 1, "b": 2}
        large_dict = {f"key{i}": i for i in range(20)}  # Dict with 20 items
        
        # Should format small dict normally
        formatted = format_for_agent("small_dict", small_dict)
        self.assertEqual(formatted, str(small_dict))
        
        # Large dict should be summarized
        formatted = format_for_agent("large_dict", large_dict)
        self.assertIn("Dict with 20 items", formatted)
        self.assertIn("First 5", formatted)
        
        # Test list formatting
        small_list = [1, 2, 3]
        large_list = list(range(20))
        
        # Small list normal formatting
        formatted = format_for_agent("small_list", small_list)
        self.assertEqual(formatted, str(small_list))
        
        # Large list summarized
        formatted = format_for_agent("large_list", large_list)
        self.assertIn("list with 20 items", formatted)
        
        # Test long string
        long_string = "x" * 1000
        formatted = format_for_agent("long_string", long_string)
        self.assertIn("(truncated, length=1000)", formatted)
        

if __name__ == "__main__":
    unittest.main()