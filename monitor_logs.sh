#!/bin/bash

# Quest Hub - Log Monitor Script
# Usage: ./monitor_logs.sh [backend|frontend|both]
# Default: both

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse argument
MODE="${1:-both}"

# Validate mode
if [[ ! "$MODE" =~ ^(backend|frontend|both)$ ]]; then
    echo -e "${RED}Invalid option: $MODE${NC}"
    echo ""
    echo "Usage: ./monitor_logs.sh [backend|frontend|both]"
    echo ""
    echo "Options:"
    echo "  backend   - Monitor only backend.log"
    echo "  frontend  - Monitor only frontend.log"
    echo "  both      - Monitor both logs (default)"
    echo ""
    echo "Examples:"
    echo "  ./monitor_logs.sh              # Monitor both logs"
    echo "  ./monitor_logs.sh backend      # Monitor only backend"
    echo "  ./monitor_logs.sh frontend     # Monitor only frontend"
    exit 1
fi

# Check if log files exist
if [ "$MODE" = "backend" ] || [ "$MODE" = "both" ]; then
    if [ ! -f backend.log ]; then
        echo -e "${YELLOW}⚠️  backend.log not found${NC}"
        echo "   Make sure services are running: ./start.sh"
        if [ "$MODE" = "backend" ]; then
            exit 1
        fi
    fi
fi

if [ "$MODE" = "frontend" ] || [ "$MODE" = "both" ]; then
    if [ ! -f frontend.log ]; then
        echo -e "${YELLOW}⚠️  frontend.log not found${NC}"
        echo "   Make sure services are running: ./start.sh"
        if [ "$MODE" = "frontend" ]; then
            exit 1
        fi
    fi
fi

# Function to handle cleanup on exit
cleanup_monitor() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📊 Log monitoring stopped${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Kill background tail processes
    jobs -p | xargs -r kill 2>/dev/null
    
    exit 0
}

# Set trap to handle Ctrl+C gracefully
trap cleanup_monitor INT TERM

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}📊 MONITORING LOGS - Quest Hub${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

case "$MODE" in
    backend)
        echo -e "${GREEN}Monitoring: backend.log${NC}"
        echo "Press Ctrl+C to exit"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        tail -f backend.log
        ;;
    
    frontend)
        echo -e "${CYAN}Monitoring: frontend.log${NC}"
        echo "Press Ctrl+C to exit"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        tail -f frontend.log
        ;;
    
    both)
        echo -e "Monitoring: ${GREEN}backend.log${NC} + ${CYAN}frontend.log${NC}"
        echo "Press Ctrl+C to exit"
        echo ""
        
        # Check if multitail is available
        if command -v multitail &> /dev/null; then
            echo -e "${GREEN}✅ Using multitail for enhanced viewing${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            multitail -s 2 \
                -ci green -l "tail -f backend.log" \
                -ci cyan -l "tail -f frontend.log"
        else
            echo -e "${YELLOW}💡 Tip: Install multitail for split-screen viewing${NC}"
            echo -e "${YELLOW}   Command: sudo apt install multitail${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo -e "${GREEN}[BACKEND]${NC} backend.log | ${CYAN}[FRONTEND]${NC} frontend.log"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            
            # Use tail -f on both files with color-coded prefixes
            (tail -f backend.log 2>/dev/null | while IFS= read -r line; do
                echo -e "${GREEN}[BACKEND]${NC}  $line"
            done) &
            
            (tail -f frontend.log 2>/dev/null | while IFS= read -r line; do
                echo -e "${CYAN}[FRONTEND]${NC} $line"
            done) &
            
            # Wait for background processes
            wait
        fi
        ;;
esac
