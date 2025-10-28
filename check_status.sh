#!/bin/bash

# Quest Hub - System Status Check
# Quick health check for all services

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏥 Quest Hub - System Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check API Server
echo -n "API Server: "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')
    if [ "$STATUS" = "healthy" ]; then
        echo "✅ ONLINE"
    else
        echo "⚠️  $STATUS"
    fi
else
    echo "❌ OFFLINE"
fi

# Check Database
echo -n "Database: "
TASKS=$(curl -s http://localhost:8000/api/tasks 2>/dev/null | jq 'length' 2>/dev/null)
if [ ! -z "$TASKS" ] && [ "$TASKS" -ge 0 ]; then
    echo "✅ CONNECTED ($TASKS tasks)"
else
    echo "❌ DISCONNECTED"
fi

# Check Frontend
echo -n "Frontend: "
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ ONLINE"
else
    echo "❌ OFFLINE"
fi

# Check Backend Process
echo -n "Backend Process: "
if pgrep -f "uvicorn app.api:app" > /dev/null; then
    PID=$(pgrep -f "uvicorn app.api:app")
    echo "✅ Running (PID: $PID)"
else
    echo "❌ Not Running"
fi

# Check Frontend Process
echo -n "Frontend Process: "
if pgrep -f "http.server 8080" > /dev/null; then
    PID=$(pgrep -f "http.server 8080")
    echo "✅ Running (PID: $PID)"
else
    echo "❌ Not Running"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if any service is down
if ! curl -s http://localhost:8000/health > /dev/null 2>&1 || \
   ! curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "⚠️  Some services are offline"
    echo ""
    echo "To restart:"
    echo "  ./restart.sh"
    echo ""
else
    echo "✅ All systems operational"
    echo ""
    echo "URLs:"
    echo "  Backend:  http://localhost:8000"
    echo "  Frontend: http://localhost:8080"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
