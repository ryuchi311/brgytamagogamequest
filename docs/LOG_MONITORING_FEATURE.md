# Log Monitoring Feature Added ✅

## Summary

Added optional log monitoring capabilities to the startup scripts for real-time debugging and observation.

## New Features

### 1. **start.sh** - Monitor Logs Option

**New Usage:**
```bash
# Start normally (no monitoring)
./start.sh

# Start and monitor logs automatically
./start.sh --monitor-logs
./start.sh -m

# Show help
./start.sh --help
```

**What happens with `--monitor-logs`:**
1. Services start normally with all retry logic
2. After successful startup, automatically begins monitoring logs
3. Shows both backend.log and frontend.log in real-time
4. Press Ctrl+C to exit monitoring (services keep running)
5. Uses multitail if available, otherwise falls back to color-coded tail

**Example Output:**
```
✅ QUEST HUB IS RUNNING!

📡 Backend API:    http://localhost:8000
🌐 Frontend:       http://localhost:8080

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 MONITORING LOGS (Press Ctrl+C to exit)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[BACKEND]  INFO:     Uvicorn running on http://0.0.0.0:8000
[BACKEND]  INFO:     Application startup complete
[FRONTEND] 127.0.0.1 - - [25/Oct/2025 22:47:13] "GET / HTTP/1.1" 200 -
[BACKEND]  INFO:     127.0.0.1:43210 - "GET /health HTTP/1.1" 200 OK
```

### 2. **monitor_logs.sh** - Standalone Monitor Script

**New Script:** `monitor_logs.sh` for monitoring logs anytime

**Usage:**
```bash
# Monitor both backend and frontend (default)
./monitor_logs.sh
./monitor_logs.sh both

# Monitor only backend
./monitor_logs.sh backend

# Monitor only frontend
./monitor_logs.sh frontend
```

**Features:**
- ✅ Real-time log streaming
- ✅ Color-coded prefixes ([BACKEND] green, [FRONTEND] cyan)
- ✅ Supports multitail for split-screen viewing
- ✅ Graceful Ctrl+C handling (doesn't stop services)
- ✅ Auto-detects missing log files
- ✅ Shows helpful tips if multitail not installed

**When to use:**
- Debugging issues while services are running
- Watching API requests in real-time
- Monitoring error logs during testing
- Observing application behavior

## Implementation Details

### start.sh Changes

**Added:**
- Command-line argument parsing (`--monitor-logs`, `-m`, `--help`)
- Help message showing usage and examples
- Post-startup log monitoring with cleanup handler
- Trap for INT/TERM signals to exit gracefully
- Fallback to basic tail if multitail not available

**Key Functions:**
```bash
# Parse arguments
MONITOR_LOGS=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --monitor-logs|-m) MONITOR_LOGS=true ;;
        --help|-h) show_help ;;
    esac
done

# After successful startup
if [ "$MONITOR_LOGS" = true ]; then
    # Setup cleanup trap
    trap cleanup_monitor INT TERM
    
    # Monitor logs with multitail or tail
    if command -v multitail &> /dev/null; then
        multitail -s 2 -l "tail -f backend.log" -l "tail -f frontend.log"
    else
        # Fallback to colored tail
        tail -f backend.log | sed "s/^/[BACKEND]  /" &
        tail -f frontend.log | sed "s/^/[FRONTEND] /" &
        wait
    fi
fi
```

### monitor_logs.sh Features

**Capabilities:**
- Select which logs to monitor (backend/frontend/both)
- Validates log files exist before monitoring
- Shows helpful error messages if logs missing
- Cleans up background processes on exit
- Suggests installing multitail for better experience

**Modes:**
1. **Backend only:** `./monitor_logs.sh backend`
   - Shows only backend.log
   - Good for API debugging

2. **Frontend only:** `./monitor_logs.sh frontend`
   - Shows only frontend.log
   - Good for HTTP request monitoring

3. **Both (default):** `./monitor_logs.sh` or `./monitor_logs.sh both`
   - Shows both logs interleaved
   - Best for full application monitoring

## Enhanced Multitail Support

If `multitail` is installed:
- ✅ Split-screen view (one log per pane)
- ✅ Color-coded by log source
- ✅ Better scrolling and navigation
- ✅ Search functionality (press '/')
- ✅ Pause/resume (press 'space')

**Install multitail:**
```bash
sudo apt install multitail
```

## Use Cases

### Development Workflow
```bash
# Start with monitoring during development
./start.sh --monitor-logs

# Make code changes...
# Watch logs for errors...
# Press Ctrl+C to stop monitoring (services keep running)
```

### Debugging Issues
```bash
# Start services normally
./start.sh

# Later, attach log monitor to debug
./monitor_logs.sh

# Or monitor just the problematic service
./monitor_logs.sh backend
```

### Testing API Calls
```bash
# Monitor only backend during API testing
./monitor_logs.sh backend

# In another terminal, make API calls
curl http://localhost:8000/api/users/123

# Watch real-time logs of the request
```

### Production Monitoring
```bash
# Monitor both logs in production
./monitor_logs.sh

# Or use multitail for better viewing
multitail backend.log frontend.log
```

## Comparison

| Feature | Before | After |
|---------|--------|-------|
| **Start & Monitor** | ❌ Not possible | ✅ `./start.sh -m` |
| **Standalone Monitor** | ❌ Manual tail commands | ✅ `./monitor_logs.sh` |
| **Select Logs** | ❌ Monitor all or none | ✅ Choose backend/frontend/both |
| **Color Coding** | ❌ No | ✅ Yes |
| **Multitail Support** | ❌ No | ✅ Yes |
| **Graceful Exit** | ❌ Ctrl+C stops services | ✅ Ctrl+C exits monitoring only |
| **Help/Usage** | ❌ No help text | ✅ `--help` flag |

## Examples

### Example 1: Development Session
```bash
# Start and watch logs during development
$ ./start.sh --monitor-logs

🚀 Starting Quest Hub...
✅ Environment validated
✅ Backend API is running
✅ Frontend is running
🎉 QUEST HUB IS RUNNING!

📊 MONITORING LOGS (Press Ctrl+C to exit)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[BACKEND]  INFO: Application startup complete
[FRONTEND] Serving HTTP on 0.0.0.0 port 8080
[BACKEND]  INFO: 127.0.0.1:52341 - "GET /health HTTP/1.1" 200 OK
```

### Example 2: Debug Specific Service
```bash
# Monitor only backend for API debugging
$ ./monitor_logs.sh backend

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 MONITORING LOGS - Quest Hub
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Monitoring: backend.log
Press Ctrl+C to exit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: 127.0.0.1:43210 - "POST /api/tasks/5/complete" - 200 OK
```

### Example 3: Stop Monitoring, Keep Services Running
```bash
# Monitoring logs...
[BACKEND]  INFO: Processing request...
[FRONTEND] GET / HTTP/1.1" 200

# Press Ctrl+C
^C

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Log monitoring stopped
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Services are still running. Use ./stop.sh to stop them.
```

## Files Modified/Created

1. **start.sh** - Enhanced with:
   - Argument parsing for `--monitor-logs` flag
   - Help message with `--help` flag
   - Post-startup monitoring logic
   - Graceful exit handling
   - Multitail detection and fallback

2. **monitor_logs.sh** - NEW standalone script:
   - 130+ lines of monitoring logic
   - Multiple viewing modes
   - Error handling and validation
   - Color-coded output
   - Multitail integration

3. **STARTUP_SCRIPTS_GUIDE.md** - Updated with:
   - monitor_logs.sh documentation
   - New start.sh usage examples
   - Enhanced quick commands section
   - Log monitoring use cases

## Quick Reference

```bash
# Start Normally
./start.sh                        # Start without monitoring
./start.sh --help                 # Show help

# Start with Monitoring
./start.sh --monitor-logs         # Start and monitor logs
./start.sh -m                     # Short version

# Monitor Anytime
./monitor_logs.sh                 # Monitor both logs
./monitor_logs.sh backend         # Backend only
./monitor_logs.sh frontend        # Frontend only

# Exit Monitoring
Press Ctrl+C                      # Stops monitoring, keeps services running

# Stop Services
./stop.sh                         # Stop all services
```

## Benefits

✅ **Faster debugging** - See logs immediately after startup  
✅ **Better development experience** - Watch app behavior in real-time  
✅ **Flexible monitoring** - Choose which logs to watch  
✅ **Non-intrusive** - Exit monitoring without stopping services  
✅ **Enhanced with multitail** - Better viewing if installed  
✅ **Production-ready** - Safe for production use  
✅ **Easy to use** - Simple command-line options  

## Next Steps

### Optional: Install multitail for better viewing
```bash
sudo apt install multitail
```

### Try it out
```bash
# Start with monitoring
./start.sh --monitor-logs

# Or monitor existing services
./monitor_logs.sh
```

---

**Log monitoring is now integrated and ready to use! 📊**
