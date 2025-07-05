#!/bin/bash

echo "🚀 Starting FastAPI app..."

# Optional: Load environment variables
if [ -f ".env" ]; then
    echo "🔑 Loading .env file"
    export $(grep -v '^#' .env | xargs)
fi

# Start the app
uvicorn main:app --host 0.0.0.0 --port 8000
