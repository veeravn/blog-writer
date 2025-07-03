#!/bin/bash

cd /app
echo "Starting the FastAPI application..."
echo "Setting PYTHONPATH to current directory..."
export PYTHONPATH=$(pwd)
echo "Python version: $(python --version)"
echo "Checking main.py module..."
python -m py_compile main.py || { echo "main.py has syntax errors"; exit 1; }

exec python -m main