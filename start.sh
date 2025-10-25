#!/bin/bash

# Quest Hub - Start Script with Auto-Recovery
# Usage: ./start.sh [--monitor-logs]
# Options:
#   --monitor-logs  Follow logs after successful startup (Ctrl+C to exit)

set -e  # Exit on error

# Parse arguments
MONITOR_LOGS=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --monitor-logs|-m)
            MONITOR_LOGS=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --monitor-logs, -m    Follow logs after startup (Ctrl+C to exit)"
            echo "  --help, -h            Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./start.sh                 # Start services normally"
            echo "  ./start.sh --monitor-logs  # Start and watch logs"
            echo "  ./start.sh -m              # Short version"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Configuration
MAX_RETRIES=3
BACKEND_PORT=8000
FRONTEND_PORT=8080
BACKEND_HEALTH_TIMEOUT=30
FRONTEND_HEALTH_TIMEOUT=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Starting Quest Hub..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function: Check if port is available
check_port_available() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function: Kill process on specific port
kill_port_process() {
    local port=$1
    local process_name=$2
    
    echo -e "${YELLOW}⚠️  Port $port is in use, killing existing process...${NC}"
    
    # Try pkill first (by process pattern)
    pkill -f "$process_name" 2>/dev/null || true
    sleep 1
    
    # Force kill by port if still running
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "   Killing PID $pid on port $port..."
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Function: Wait for service to be healthy
wait_for_service() {
    local url=$1
    local timeout=$2
    local service_name=$3
    local elapsed=0
    
    echo "   Waiting for $service_name to be healthy (timeout: ${timeout}s)..."
    
    while [ $elapsed -lt $timeout ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is healthy!${NC}"
            return 0
        fi
        sleep 1
        elapsed=$((elapsed + 1))
        
        # Show progress every 5 seconds
        if [ $((elapsed % 5)) -eq 0 ]; then
            echo "   Still waiting... (${elapsed}s elapsed)"
        fi
    done
    
    echo -e "${RED}❌ $service_name failed to become healthy after ${timeout}s${NC}"
    return 1
}

# Function: Validate environment
validate_environment() {
    echo "🔍 Validating environment..."
    
    # Check if .env exists
    if [ ! -f .env ]; then
        echo -e "${RED}❌ .env file not found!${NC}"
        echo "   Please create .env file with required variables."
        return 1
    fi
    
    # Load .env
    source .env
    
    # Check critical environment variables
    local missing_vars=()
    
    if [ -z "$SUPABASE_URL" ]; then
        missing_vars+=("SUPABASE_URL")
    fi
    
    if [ -z "$SUPABASE_KEY" ]; then
        missing_vars+=("SUPABASE_KEY")
    fi
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing required environment variables:${NC}"
        for var in "${missing_vars[@]}"; do
            echo "   - $var"
        done
        return 1
    fi
    
    echo -e "${GREEN}✅ Environment validated${NC}"
    return 0
}

# Function: Start backend with retry
start_backend() {
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        echo "� Starting backend API (attempt $attempt/$MAX_RETRIES)..."
        
        # Check and free port if needed
        if ! check_port_available $BACKEND_PORT; then
            kill_port_process $BACKEND_PORT "uvicorn app.api:app"
        fi
        
        # Verify port is now free
        if ! check_port_available $BACKEND_PORT; then
            echo -e "${RED}❌ Port $BACKEND_PORT still in use after cleanup${NC}"
            attempt=$((attempt + 1))
            sleep 3
            continue
        fi
        
        # Start backend
        nohup uvicorn app.api:app --host 0.0.0.0 --port $BACKEND_PORT --reload > backend.log 2>&1 &
        local backend_pid=$!
        echo "   Backend PID: $backend_pid"
        
        # Wait for backend to be healthy
        sleep 3  # Give it a moment to start
        
        if wait_for_service "http://localhost:$BACKEND_PORT/health" $BACKEND_HEALTH_TIMEOUT "Backend API"; then
            echo -e "${GREEN}✅ Backend API is running on http://localhost:$BACKEND_PORT${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Backend failed to start, checking logs...${NC}"
            tail -n 10 backend.log
            
            # Kill the failed process
            kill $backend_pid 2>/dev/null || true
            
            attempt=$((attempt + 1))
            if [ $attempt -le $MAX_RETRIES ]; then
                echo "   Retrying in 5 seconds..."
                sleep 5
            fi
        fi
    done
    
    echo -e "${RED}❌ Failed to start backend after $MAX_RETRIES attempts${NC}"
    return 1
}

# Function: Start frontend with retry
start_frontend() {
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        echo "🌐 Starting frontend (attempt $attempt/$MAX_RETRIES)..."
        
        # Check and free port if needed
        if ! check_port_available $FRONTEND_PORT; then
            kill_port_process $FRONTEND_PORT "python -m http.server $FRONTEND_PORT"
        fi
        
        # Verify port is now free
        if ! check_port_available $FRONTEND_PORT; then
            echo -e "${RED}❌ Port $FRONTEND_PORT still in use after cleanup${NC}"
            attempt=$((attempt + 1))
            sleep 3
            continue
        fi
        
        # Start frontend
        cd frontend
        nohup python -m http.server $FRONTEND_PORT > ../frontend.log 2>&1 &
        local frontend_pid=$!
        cd ..
        echo "   Frontend PID: $frontend_pid"
        
        # Wait for frontend to be healthy
        sleep 2  # Give it a moment to start
        
        if wait_for_service "http://localhost:$FRONTEND_PORT" $FRONTEND_HEALTH_TIMEOUT "Frontend"; then
            echo -e "${GREEN}✅ Frontend is running on http://localhost:$FRONTEND_PORT${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Frontend failed to start, checking logs...${NC}"
            tail -n 10 frontend.log
            
            # Kill the failed process
            kill $frontend_pid 2>/dev/null || true
            
            attempt=$((attempt + 1))
            if [ $attempt -le $MAX_RETRIES ]; then
                echo "   Retrying in 3 seconds..."
                sleep 3
            fi
        fi
    done
    
    echo -e "${RED}❌ Failed to start frontend after $MAX_RETRIES attempts${NC}"
    return 1
}

# Main execution
echo ""

# Step 1: Validate environment
if ! validate_environment; then
    echo -e "${RED}❌ Environment validation failed${NC}"
    exit 1
fi

echo ""

# Step 2: Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn app.api:app" 2>/dev/null || true
pkill -f "python -m http.server $FRONTEND_PORT" 2>/dev/null || true
sleep 2

echo ""

# Step 3: Start backend
if ! start_backend; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ FAILED TO START BACKEND${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "💡 Try running: ./restart.sh"
    exit 1
fi

echo ""

# Step 4: Start frontend
if ! start_frontend; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ FAILED TO START FRONTEND${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "💡 Try running: ./restart.sh"
    exit 1
fi

echo ""

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 QUEST HUB IS RUNNING!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📡 Backend API:    http://localhost:$BACKEND_PORT"
echo "🌐 Frontend:       http://localhost:$FRONTEND_PORT"
echo "📚 API Docs:       http://localhost:$BACKEND_PORT/docs"
echo ""
echo "👤 Test User:      ID 1271737596 (testuser)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop:    ./stop.sh"
echo "🔄 To restart: ./restart.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Monitor logs if requested
if [ "$MONITOR_LOGS" = true ]; then
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📊 MONITORING LOGS (Press Ctrl+C to exit)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Function to handle cleanup on exit
    cleanup_monitor() {
        echo ""
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}📊 Log monitoring stopped${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "Services are still running. Use ./stop.sh to stop them."
        exit 0
    }
    
    # Set trap to handle Ctrl+C gracefully
    trap cleanup_monitor INT TERM
    
    # Check if multitail is available (better log viewer)
    if command -v multitail &> /dev/null; then
        echo -e "${GREEN}Using multitail for enhanced log viewing${NC}"
        echo ""
        multitail -s 2 \
            -l "tail -f backend.log" \
            -l "tail -f frontend.log"
    else
        # Fallback to tail with color coding
        echo -e "${YELLOW}💡 Tip: Install multitail for better log viewing: sudo apt install multitail${NC}"
        echo ""
        echo -e "${GREEN}[BACKEND]${NC} backend.log | ${CYAN}[FRONTEND]${NC} frontend.log"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Use tail -f on both files with prefixes
        (tail -f backend.log 2>/dev/null | sed "s/^/[${GREEN}BACKEND${NC}]  /" &)
        (tail -f frontend.log 2>/dev/null | sed "s/^/[${CYAN}FRONTEND${NC}] /" &)
        
        # Wait for Ctrl+C
        wait
    fi
fi


