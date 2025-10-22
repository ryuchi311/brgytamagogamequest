#!/bin/bash

# Quest Hub - One-Line Startup Script
# Usage: ./start.sh

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎮 Starting Quest Hub..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn app.api:app" 2>/dev/null
pkill -f "python -m http.server 8080" 2>/dev/null
sleep 2

# Start Backend API
echo "🚀 Starting Backend API (port 8000)..."
cd /workspaces/codespaces-blank
nohup uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start. Check backend.log for errors."
    exit 1
fi

# Start Frontend
echo "🚀 Starting Frontend (port 8080)..."
nohup python -m http.server 8080 --directory frontend > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to be ready
sleep 2

# Check if frontend is running
if curl -s -I http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ Frontend is running (PID: $FRONTEND_PID)"
else
    echo "❌ Frontend failed to start. Check frontend.log for errors."
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 QUEST HUB IS RUNNING!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📡 Backend API:    http://localhost:8000"
echo "🌐 Frontend:       http://localhost:8080"
echo "📚 API Docs:       http://localhost:8000/docs"
echo ""
echo "👤 Test User:      ID 1271737596 (testuser)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop: ./stop.sh or pkill -f 'uvicorn|http.server 8080'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
