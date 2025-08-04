import unittest
import logging
from io import StringIO

from darktrace.core import log_exception_state, TracedError

class TestLogExceptionState(unittest.TestCase):
    def setUp(self):
        # Capture log output
        self.log_capture = StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.logger = logging.getLogger("test")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
    
    def test_basic_logging(self):
        # Create an exception to log
        try:
            x = 42
            y = 0
            result = x / y  # This will raise ZeroDivisionError
        except Exception as e:
            log_exception_state(e, self.logger)
        
        # Assert expected output appeared in the log
        log_output = self.log_capture.getvalue()
        self.assertIn("Logging exception state for: ZeroDivisionError", log_output)
        self.assertIn("x = 42", log_output)
        self.assertIn("y = 0", log_output)
    
    def test_exclude_vars(self):
        try:
            password = "secret123"
            token = "abcd1234"
            raise ValueError("Test error")
        except Exception as e:
            log_exception_state(e, self.logger, exclude_vars=["password"])
            
        log_output = self.log_capture.getvalue()
        self.assertNotIn("password = ", log_output)  # Should be excluded 
        self.assertIn("token = ", log_output)  # Should be included

class TestTracedError(unittest.TestCase):
    def setUp(self):
        # Capture log output
        self.log_capture = StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.logger = logging.getLogger("test_traced")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
    
    def test_context_manager(self):
        with self.assertRaises(ValueError):
            with TracedError(logger=self.logger):
                a = 1
                b = 2
                raise ValueError("Test error in context manager")
                
        log_output = self.log_capture.getvalue()
        self.assertIn("Logging exception state for: ValueError", log_output)
        self.assertIn("a = 1", log_output)
        self.assertIn("b = 2", log_output)

if __name__ == "__main__":
    unittest.main()
