#!/bin/bash

# Quest Hub - Stop Script with Thorough Cleanup
# Usage: ./stop.sh

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=8080
GRACEFUL_TIMEOUT=10

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 Stopping Quest Hub..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function: Gracefully stop process
graceful_stop() {
    local process_pattern=$1
    local process_name=$2
    
    echo "🔄 Stopping $process_name..."
    
    # Try graceful shutdown first
    pkill -TERM -f "$process_pattern" 2>/dev/null
    
    # Wait for graceful shutdown
    local elapsed=0
    while [ $elapsed -lt $GRACEFUL_TIMEOUT ]; do
        if ! pgrep -f "$process_pattern" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $process_name stopped gracefully${NC}"
            return 0
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done
    
    # Force kill if still running
    echo -e "${YELLOW}⚠️  $process_name didn't stop gracefully, force killing...${NC}"
    pkill -9 -f "$process_pattern" 2>/dev/null || true
    sleep 1
    
    if ! pgrep -f "$process_pattern" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $process_name stopped (force killed)${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to stop $process_name${NC}"
        return 1
    fi
}

# Function: Kill process on specific port
kill_port() {
    local port=$1
    local service_name=$2
    
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ -z "$pid" ]; then
        echo "   Port $port is already free"
        return 0
    fi
    
    echo "   Killing process on port $port (PID: $pid)..."
    kill -9 $pid 2>/dev/null || true
    sleep 1
    
    # Verify port is free
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ Failed to free port $port${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $port freed${NC}"
        return 0
    fi
}

# Stop backend
graceful_stop "uvicorn app.api:app" "Backend API"

# Stop frontend
graceful_stop "python -m http.server $FRONTEND_PORT" "Frontend"

echo ""
echo "🧹 Cleaning up ports..."

# Ensure ports are freed
kill_port $BACKEND_PORT "Backend"
kill_port $FRONTEND_PORT "Frontend"

echo ""
echo "🗑️  Cleaning up temporary files..."

# Clean up PID files if they exist
rm -f backend.pid frontend.pid 2>/dev/null || true
echo "   Removed PID files"

# Clean up lock files if they exist
rm -f .backend.lock .frontend.lock 2>/dev/null || true
echo "   Removed lock files"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ All services stopped and cleaned up!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
