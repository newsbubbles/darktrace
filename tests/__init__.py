"""Tests package for Tracelight."""

import sys
import os
from pathlib import Path

def setup_tracelight_path():
    """Add the src directory to the Python path for local development."""
    # Add the src directory to the Python path
    src_path = Path(__file__).resolve().parent.parent / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        return True
    return False

# Automatically set up the path when this module is imported
setup_tracelight_path()
