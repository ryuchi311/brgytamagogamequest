#!/bin/bash
# Telegram Bot Manager Script
# Ensures only one bot instance runs at a time

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_SCRIPT="$SCRIPT_DIR/app/telegram_bot.py"
PID_FILE="$SCRIPT_DIR/bot.pid"
LOG_FILE="$SCRIPT_DIR/bot.log"

start_bot() {
    echo "🤖 Starting Telegram Bot..."
    
    # Check if bot is already running
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            echo "❌ Bot is already running (PID: $OLD_PID)"
            echo "   Use './manage_bot.sh stop' to stop it first"
            return 1
        else
            echo "⚠️  Stale PID file found, removing..."
            rm "$PID_FILE"
        fi
    fi
    
    # Kill any orphaned bot processes
    pkill -f "telegram_bot.py" 2>/dev/null
    sleep 1
    
    # Start bot in background
    cd "$SCRIPT_DIR"
    nohup python3 "$BOT_SCRIPT" > "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    echo $NEW_PID > "$PID_FILE"
    
    sleep 2
    
    # Verify bot started
    if ps -p "$NEW_PID" > /dev/null 2>&1; then
        echo "✅ Bot started successfully!"
        echo "   PID: $NEW_PID"
        echo "   Logs: tail -f $LOG_FILE"
    else
        echo "❌ Bot failed to start. Check logs:"
        tail -20 "$LOG_FILE"
        rm "$PID_FILE"
        return 1
    fi
}

stop_bot() {
    echo "🛑 Stopping Telegram Bot..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            sleep 2
            
            # Force kill if still running
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "⚠️  Bot didn't stop gracefully, force killing..."
                kill -9 "$PID"
            fi
            
            echo "✅ Bot stopped (PID: $PID)"
        else
            echo "⚠️  Bot not running (stale PID file)"
        fi
        rm "$PID_FILE"
    else
        echo "⚠️  No PID file found"
    fi
    
    # Kill any remaining bot processes
    pkill -f "telegram_bot.py" 2>/dev/null && echo "✅ Killed orphaned bot processes"
}

status_bot() {
    echo "📊 Telegram Bot Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ Status: RUNNING"
            echo "   PID: $PID"
            echo "   Started: $(ps -p $PID -o lstart= 2>/dev/null)"
            echo "   Memory: $(ps -p $PID -o rss= 2>/dev/null | awk '{print int($1/1024) "MB"}')"
        else
            echo "❌ Status: STOPPED (stale PID file)"
            echo "   Last PID: $PID"
        fi
    else
        echo "❌ Status: STOPPED"
        echo "   No PID file found"
    fi
    
    # Check for orphaned processes
    ORPHANS=$(ps aux | grep "telegram_bot.py" | grep -v grep | wc -l)
    if [ "$ORPHANS" -gt 0 ]; then
        echo "⚠️  Warning: $ORPHANS orphaned bot process(es) found"
        ps aux | grep "telegram_bot.py" | grep -v grep
    fi
    
    echo ""
    echo "📝 Recent logs (last 10 lines):"
    if [ -f "$LOG_FILE" ]; then
        tail -10 "$LOG_FILE"
    else
        echo "   No log file found"
    fi
}

restart_bot() {
    echo "🔄 Restarting Telegram Bot..."
    stop_bot
    sleep 2
    start_bot
}

logs_bot() {
    if [ -f "$LOG_FILE" ]; then
        echo "📝 Tailing bot logs (Ctrl+C to stop)..."
        tail -f "$LOG_FILE"
    else
        echo "❌ Log file not found: $LOG_FILE"
    fi
}

# Main command handler
case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        status_bot
        ;;
    logs)
        logs_bot
        ;;
    *)
        echo "🤖 Telegram Bot Manager"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the Telegram bot"
        echo "  stop     - Stop the Telegram bot"
        echo "  restart  - Restart the Telegram bot"
        echo "  status   - Check bot status"
        echo "  logs     - View bot logs (real-time)"
        echo ""
        echo "Examples:"
        echo "  $0 start          # Start the bot"
        echo "  $0 status         # Check if running"
        echo "  $0 logs           # Watch logs"
        echo "  $0 restart        # Restart the bot"
        exit 1
        ;;
esac
