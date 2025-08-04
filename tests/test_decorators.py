import unittest
import logging
from io import StringIO

from tracelight.decorators import traced


class TestTracedDecorator(unittest.TestCase):
    def setUp(self):
        # Create a StringIO object to capture log output
        self.log_output = StringIO()
        self.handler = logging.StreamHandler(self.log_output)
        self.logger = logging.getLogger("test_traced")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
        
    def test_traced_decorator_with_exception(self):
        # Test the @traced decorator when an exception occurs
        
        @traced(logger=self.logger)
        def example_function(a, b):
            x = a + 1
            y = b - 1
            return x / y  # This will raise if y is 0
        
        with self.assertRaises(ZeroDivisionError):
            example_function(5, 1)  # This will cause y to be 0
        
        output = self.log_output.getvalue()
        
        # Check that the exception and variables were logged
        self.assertIn("ZeroDivisionError", output)
        self.assertIn("example_function", output)
        self.assertIn("a = 5", output)
        self.assertIn("b = 1", output)
        self.assertIn("x = 6", output)
        self.assertIn("y = 0", output)
        
    def test_traced_decorator_no_exception(self):
        # Test that @traced doesn't interfere when no exception occurs
        
        @traced(logger=self.logger)
        def add(a, b):
            return a + b
        
        result = add(3, 4)
        
        # Function should work normally
        self.assertEqual(result, 7)
        
        # No logs should have been written
        self.assertEqual(self.log_output.getvalue(), "")
        
    def test_traced_decorator_no_reraise(self):
        # Test that @traced with reraise=False swallows exceptions
        
        @traced(logger=self.logger, reraise=False)
        def example_function(a, b):
            return a / b  # This will raise if b is 0
        
        # No exception should propagate, but the function returns None
        result = example_function(5, 0)
        self.assertIsNone(result)
        
        # But it should still log the exception
        output = self.log_output.getvalue()
        self.assertIn("ZeroDivisionError", output)
        self.assertIn("a = 5", output)
        self.assertIn("b = 0", output)


if __name__ == "__main__":
    unittest.main()