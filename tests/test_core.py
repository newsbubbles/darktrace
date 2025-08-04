import unittest
import logging
from io import StringIO

from tracelight.core import log_exception_state, TracedError


class TestLogExceptionState(unittest.TestCase):
    def setUp(self):
        # Create a StringIO object to capture log output
        self.log_output = StringIO()
        self.handler = logging.StreamHandler(self.log_output)
        self.logger = logging.getLogger("test")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
        
    def test_log_exception_state_basic(self):
        # Test that log_exception_state logs the basic info
        try:
            x = 1
            y = 0
            z = x / y
        except Exception as e:
            log_exception_state(e, self.logger)
        
        output = self.log_output.getvalue()
        
        # Check basic exception info
        self.assertIn("Logging exception state for: ZeroDivisionError:", output)
        self.assertIn("division by zero", output)
        
        # Check frame info
        self.assertIn("Frame", output)
        self.assertIn("test_log_exception_state_basic", output)
        
        # Check variable contents
        self.assertIn("x = 1", output)
        self.assertIn("y = 0", output)
        
    def test_exclude_vars(self):
        # Test that variables can be excluded
        try:
            password = "secret123"  # sensitive data
            api_key = "abc123xyz"    # sensitive data
            public_var = "hello"     # non-sensitive
            raise ValueError("Test error")
        except Exception as e:
            log_exception_state(e, self.logger, exclude_vars=["password", "api_key"])
        
        output = self.log_output.getvalue()
        
        # Ensure excluded vars aren't present
        self.assertNotIn("password = ", output)
        self.assertNotIn("secret123", output)
        self.assertNotIn("api_key = ", output)
        self.assertNotIn("abc123xyz", output)
        
        # But public var should be there
        self.assertIn("public_var = ", output)
        self.assertIn("hello", output)
        
    def test_max_var_length(self):
        # Test that variables are truncated
        try:
            long_string = "x" * 2000  # Very long string
            raise ValueError("Test error")
        except Exception as e:
            log_exception_state(e, self.logger, max_var_length=50)  # Short max length
        
        output = self.log_output.getvalue()
        
        # Check truncation
        self.assertIn("long_string = ", output)
        self.assertIn("...<truncated>", output)
        self.assertNotIn("x" * 60, output)  # Shouldn't have 60 consecutive x's


class TestTracedError(unittest.TestCase):
    def setUp(self):
        # Create a StringIO object to capture log output
        self.log_output = StringIO()
        self.handler = logging.StreamHandler(self.log_output)
        self.logger = logging.getLogger("test_traced_error")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
        
    def test_as_context_manager(self):
        # Test TracedError as a context manager
        
        with self.assertRaises(ZeroDivisionError):
            with TracedError(logger=self.logger):
                x = 10
                y = 0
                z = x / y  # This will raise ZeroDivisionError
        
        output = self.log_output.getvalue()
        
        # Check that variables were logged
        self.assertIn("ZeroDivisionError", output)
        self.assertIn("x = 10", output)
        self.assertIn("y = 0", output)


if __name__ == "__main__":
    unittest.main()