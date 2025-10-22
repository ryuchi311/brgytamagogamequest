#!/bin/bash

# Quest Hub - Stop Script
# Usage: ./stop.sh

echo "🛑 Stopping Quest Hub..."

# Kill backend
pkill -f "uvicorn app.api:app"
echo "✅ Backend stopped"

# Kill frontend
pkill -f "python -m http.server 8080"
echo "✅ Frontend stopped"

echo "✅ All services stopped!"
