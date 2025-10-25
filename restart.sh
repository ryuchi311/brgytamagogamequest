#!/bin/bash

# Quest Hub - Restart Script with Auto-Recovery
# This script diagnoses issues and restarts services cleanly
# Usage: ./restart.sh

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=8080

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 Quest Hub - Auto-Recovery Restart"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function: Check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function: Diagnose issues
diagnose_issues() {
    echo "🔍 Running diagnostics..."
    echo ""
    
    local issues_found=0
    
    # Check 1: Environment file
    if [ ! -f .env ]; then
        echo -e "${RED}❌ Issue found: .env file is missing${NC}"
        echo "   Solution: Create .env file with required variables"
        issues_found=$((issues_found + 1))
    else
        echo -e "${GREEN}✅ .env file exists${NC}"
        
        # Check critical variables
        source .env
        if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
            echo -e "${RED}❌ Issue found: Missing SUPABASE_URL or SUPABASE_KEY in .env${NC}"
            issues_found=$((issues_found + 1))
        else
            echo -e "${GREEN}✅ Required environment variables set${NC}"
        fi
    fi
    
    # Check 2: Port conflicts
    if check_port $BACKEND_PORT; then
        echo -e "${YELLOW}⚠️  Issue found: Port $BACKEND_PORT is in use${NC}"
        local pid=$(lsof -ti:$BACKEND_PORT 2>/dev/null)
        if [ ! -z "$pid" ]; then
            echo "   PID: $pid"
            echo "   Will be killed during restart"
        fi
        issues_found=$((issues_found + 1))
    else
        echo -e "${GREEN}✅ Port $BACKEND_PORT is free${NC}"
    fi
    
    if check_port $FRONTEND_PORT; then
        echo -e "${YELLOW}⚠️  Issue found: Port $FRONTEND_PORT is in use${NC}"
        local pid=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
        if [ ! -z "$pid" ]; then
            echo "   PID: $pid"
            echo "   Will be killed during restart"
        fi
        issues_found=$((issues_found + 1))
    else
        echo -e "${GREEN}✅ Port $FRONTEND_PORT is free${NC}"
    fi
    
    # Check 3: Zombie processes
    if pgrep -f "uvicorn app.api:app" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Issue found: Zombie backend processes detected${NC}"
        echo "   Will be killed during restart"
        issues_found=$((issues_found + 1))
    else
        echo -e "${GREEN}✅ No zombie backend processes${NC}"
    fi
    
    if pgrep -f "python -m http.server $FRONTEND_PORT" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Issue found: Zombie frontend processes detected${NC}"
        echo "   Will be killed during restart"
        issues_found=$((issues_found + 1))
    else
        echo -e "${GREEN}✅ No zombie frontend processes${NC}"
    fi
    
    # Check 4: Log files
    if [ -f backend.log ]; then
        local log_size=$(du -h backend.log | cut -f1)
        echo -e "${BLUE}ℹ️  Backend log size: $log_size${NC}"
        
        # Check for recent errors in backend log
        if tail -n 50 backend.log 2>/dev/null | grep -i "error\|exception\|failed" >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  Recent errors found in backend.log${NC}"
            echo "   Last 5 error lines:"
            tail -n 50 backend.log | grep -i "error\|exception\|failed" | tail -n 5 | sed 's/^/   │ /'
        fi
    fi
    
    if [ -f frontend.log ]; then
        local log_size=$(du -h frontend.log | cut -f1)
        echo -e "${BLUE}ℹ️  Frontend log size: $log_size${NC}"
    fi
    
    echo ""
    
    if [ $issues_found -eq 0 ]; then
        echo -e "${GREEN}✅ No critical issues detected${NC}"
    else
        echo -e "${YELLOW}⚠️  Found $issues_found issue(s) - will attempt to fix${NC}"
    fi
    
    echo ""
}

# Function: Clean up zombie processes
cleanup_zombies() {
    echo "🧹 Cleaning up zombie processes..."
    
    # Kill all uvicorn processes
    pkill -9 -f "uvicorn app.api:app" 2>/dev/null || true
    
    # Kill all Python HTTP server processes on frontend port
    pkill -9 -f "python -m http.server $FRONTEND_PORT" 2>/dev/null || true
    
    # Force kill by port
    for port in $BACKEND_PORT $FRONTEND_PORT; do
        local pid=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$pid" ]; then
            echo "   Killing PID $pid on port $port..."
            kill -9 $pid 2>/dev/null || true
        fi
    done
    
    sleep 2
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    echo ""
}

# Function: Clear temporary files
clear_temp_files() {
    echo "🗑️  Clearing temporary files..."
    
    # Remove PID files
    rm -f backend.pid frontend.pid 2>/dev/null || true
    
    # Remove lock files
    rm -f .backend.lock .frontend.lock 2>/dev/null || true
    
    # Clear Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ Temporary files cleared${NC}"
    echo ""
}

# Function: Verify environment
verify_environment() {
    echo "🔍 Verifying environment..."
    
    if [ ! -f .env ]; then
        echo -e "${RED}❌ .env file not found${NC}"
        echo ""
        echo "Please create .env file with the following variables:"
        echo "  SUPABASE_URL=your_supabase_url"
        echo "  SUPABASE_KEY=your_supabase_key"
        echo "  TELEGRAM_BOT_TOKEN=your_bot_token"
        echo ""
        return 1
    fi
    
    source .env
    
    if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
        echo -e "${RED}❌ Missing required environment variables${NC}"
        echo "   Required: SUPABASE_URL, SUPABASE_KEY"
        return 1
    fi
    
    echo -e "${GREEN}✅ Environment verified${NC}"
    echo ""
    return 0
}

# Function: Test database connectivity
test_database() {
    echo "🔌 Testing database connectivity..."
    
    if [ -z "$SUPABASE_URL" ]; then
        echo -e "${YELLOW}⚠️  Cannot test - SUPABASE_URL not set${NC}"
        echo ""
        return 0
    fi
    
    # Try to reach Supabase
    if curl -s --max-time 5 "$SUPABASE_URL" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Database connection OK${NC}"
    else
        echo -e "${YELLOW}⚠️  Cannot reach database (may be network issue)${NC}"
    fi
    
    echo ""
}

# Main execution
echo ""

# Step 1: Diagnose issues
diagnose_issues

# Step 2: Stop existing services
echo "🛑 Stopping existing services..."
./stop.sh
echo ""

# Step 3: Clean up zombies
cleanup_zombies

# Step 4: Clear temp files
clear_temp_files

# Step 5: Verify environment
if ! verify_environment; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ RESTART FAILED - Environment issues${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi

# Step 6: Test database
test_database

# Step 7: Wait a moment
echo "⏳ Waiting for cleanup to complete..."
sleep 3
echo ""

# Step 8: Start services
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Starting services with auto-recovery..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if ./start.sh; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✅ RESTART SUCCESSFUL!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📡 Backend API:    http://localhost:$BACKEND_PORT"
    echo "🌐 Frontend:       http://localhost:$FRONTEND_PORT"
    echo "📚 API Docs:       http://localhost:$BACKEND_PORT/docs"
    echo ""
    echo "📝 Monitor logs:"
    echo "   Backend:  tail -f backend.log"
    echo "   Frontend: tail -f frontend.log"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${RED}❌ RESTART FAILED${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🔍 Troubleshooting steps:"
    echo ""
    echo "1. Check logs for errors:"
    echo "   tail -n 50 backend.log"
    echo "   tail -n 50 frontend.log"
    echo ""
    echo "2. Verify environment variables:"
    echo "   cat .env"
    echo ""
    echo "3. Check if ports are still in use:"
    echo "   lsof -i :$BACKEND_PORT"
    echo "   lsof -i :$FRONTEND_PORT"
    echo ""
    echo "4. Try manual cleanup:"
    echo "   pkill -9 -f 'uvicorn|http.server'"
    echo "   ./restart.sh"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi
