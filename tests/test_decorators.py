import unittest
import logging
from io import StringIO

from darktrace.decorators import traced

class TestTracedDecorator(unittest.TestCase):
    def setUp(self):
        # Capture log output
        self.log_capture = StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.logger = logging.getLogger("test_decorator")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
    
    def test_traced_reraise(self):
        @traced(logger=self.logger)
        def function_with_error(x, y):
            result = x / y  # Will raise if y is 0
            return result
        
        # Should raise and log
        with self.assertRaises(ZeroDivisionError):
            function_with_error(10, 0)
            
        log_output = self.log_capture.getvalue()
        self.assertIn("Logging exception state for: ZeroDivisionError", log_output)
        self.assertIn("x = 10", log_output)
        self.assertIn("y = 0", log_output)
    
    def test_traced_no_reraise(self):
        @traced(logger=self.logger, reraise=False)
        def safe_function(x, y):
            return x / y  # Will raise if y is 0
        
        # Should not raise but still log
        result = safe_function(10, 0)
        self.assertIsNone(result)
        
        log_output = self.log_capture.getvalue()
        self.assertIn("Logging exception state for: ZeroDivisionError", log_output)
        self.assertIn("x = 10", log_output)
        self.assertIn("y = 0", log_output)
        
    def test_traced_success(self):
        @traced(logger=self.logger)
        def working_function(x, y):
            return x * y
        
        # Should work normally with no logging
        result = working_function(5, 6)
        self.assertEqual(result, 30)
        
        # No exception logs should appear
        log_output = self.log_capture.getvalue()
        self.assertEqual(log_output, "")

if __name__ == "__main__":
    unittest.main()
