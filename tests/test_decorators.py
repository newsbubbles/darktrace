import unittest
import logging
from io import StringIO
import sys
from pathlib import Path

# Add the src directory to the Python path if not already there
src_path = Path(__file__).resolve().parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from tracelight.decorators import traced


class TestTracedDecorator(unittest.TestCase):
    def setUp(self):
        # Create a StringIO object to capture log output
        self.log_output = StringIO()
        self.handler = logging.StreamHandler(self.log_output)
        self.logger = logging.getLogger("test_decorators")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
        
    def test_traced_success(self):
        # Test that traced decorator doesn't interfere with successful execution
        
        @traced(logger=self.logger)
        def successful_function(x, y):
            return x + y
        
        result = successful_function(3, 4)
        self.assertEqual(result, 7)
        
        # No logs should be generated on success
        self.assertEqual(self.log_output.getvalue(), "")
        
    def test_traced_error(self):
        # Test that traced decorator logs errors properly
        
        @traced(logger=self.logger)
        def failing_function(x, y):
            return x / y  # Will fail if y is 0
        
        with self.assertRaises(ZeroDivisionError):
            failing_function(5, 0)
        
        output = self.log_output.getvalue()
        
        # Check that variables were logged
        self.assertIn("ZeroDivisionError", output)
        self.assertIn("x = 5", output)
        self.assertIn("y = 0", output)
        
    def test_traced_preserves_function_metadata(self):
        # Test that the decorator preserves function metadata
        
        @traced(logger=self.logger)
        def documented_function(x: int, y: int) -> int:
            """This function adds two numbers."""
            return x + y
        
        # Check that metadata is preserved
        self.assertEqual(documented_function.__name__, "documented_function")
        self.assertEqual(documented_function.__doc__, "This function adds two numbers.")
        self.assertTrue(hasattr(documented_function, '__annotations__'))


if __name__ == "__main__":
    unittest.main()