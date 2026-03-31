#!/bin/bash
# run_tests.sh

# Activate virtual environment
source venv/bin/activate

# Run tests with python -m pytest to ensure project root is in sys.path
python -m pytest tests/ "$@"
