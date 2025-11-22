#!/bin/bash
# Startup script for Cloud Run compatibility
# Uses PORT environment variable provided by Cloud Run (defaults to 8080 for local)

PORT=${PORT:-8080}
echo "Starting server on port $PORT..."

exec python -m uvicorn app.api:app --host 0.0.0.0 --port $PORT
