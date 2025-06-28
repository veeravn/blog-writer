#!/bin/bash

cd /app
echo "Starting the FastAPI application..."
echo "Setting PYTHONPATH to current directory..."
export PYTHONPATH=.
ls -al 
python -c "import main"
exec uvicorn main:app --host 0.0.0.0 --port 5001