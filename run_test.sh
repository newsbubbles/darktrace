#!/bin/bash
# Run tests with correct Python path

# Get the absolute path to the project root
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Make sure logs directory exists
mkdir -p "$ROOT_DIR/logs"

# Make sure all scripts have executable permissions
chmod +x "$ROOT_DIR/tests/basic.py"

# Add the src directory to PYTHONPATH
export PYTHONPATH="$ROOT_DIR/src:$PYTHONPATH"

# Print environment information for debugging
echo "================================"
echo "Running tracelight test with:"
echo "  Root directory: $ROOT_DIR"
echo "  Python path: $PYTHONPATH"
echo "  Python version: $(python3 --version)"
echo "================================"

# Run the specified test or default to basic.py
TEST_FILE=${1:-"tests/basic.py"}

# Run the test with added verbosity
python3 -vv "$ROOT_DIR/$TEST_FILE"

# Show the result code
RESULT=$?
echo "\nTest completed with exit code: $RESULT"

# If log file exists, show the last few lines
LOG_FILE="$ROOT_DIR/logs/tracelight_test.log"
if [ -f "$LOG_FILE" ]; then
    echo "\nLast 20 lines of log file:"
    tail -n 20 "$LOG_FILE"
fi

exit $RESULT
