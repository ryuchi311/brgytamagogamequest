# Quest Hub - Startup Scripts Documentation

## Overview

This project includes four robust scripts for managing the Quest Hub application:
- `start.sh` - Start services with auto-recovery and optional log monitoring
- `stop.sh` - Stop services with thorough cleanup
- `restart.sh` - Diagnose issues and restart cleanly
- `monitor_logs.sh` - Monitor logs in real-time

## Scripts

### 🚀 start.sh - Start with Auto-Recovery

**Features:**
- ✅ Validates environment variables before starting
- ✅ Checks if ports 8000 and 8080 are available
- ✅ Automatically kills zombie processes blocking ports
- ✅ Retries failed starts up to 3 times with backoff
- ✅ Health checks with 30s timeout for backend, 10s for frontend
- ✅ Detailed logging for troubleshooting
- ✅ Color-coded output for better readability
- ✅ **NEW:** Optional log monitoring after startup

**Usage:**
```bash
# Start normally
./start.sh

# Start and monitor logs (press Ctrl+C to exit monitoring)
./start.sh --monitor-logs
./start.sh -m

# Show help
./start.sh --help
```

**What it does:**
1. Validates `.env` file exists and has required variables
2. Checks `SUPABASE_URL` and `SUPABASE_KEY` are set
3. Kills any existing processes on ports 8000/8080
4. Starts backend API (uvicorn) with retry logic
5. Waits for backend health check (up to 30 seconds)
6. Starts frontend (Python HTTP server) with retry logic
7. Waits for frontend to be available (up to 10 seconds)
8. Shows success message with URLs and instructions

**Error Handling:**
- If backend fails after 3 retries, suggests running `./restart.sh`
- If frontend fails after 3 retries, suggests running `./restart.sh`
- Logs last 10 lines of error logs on failure
- Color-coded messages: 🟢 Success, 🔴 Error, 🟡 Warning

### 🛑 stop.sh - Stop with Cleanup

**Features:**
- ✅ Graceful shutdown with 10s timeout
- ✅ Force kill if graceful shutdown fails
- ✅ Frees ports 8000 and 8080
- ✅ Removes PID files and lock files
- ✅ Cleans up temporary files

**Usage:**
```bash
./stop.sh
```

**What it does:**
1. Sends SIGTERM to backend and frontend processes
2. Waits up to 10 seconds for graceful shutdown
3. Force kills (SIGKILL) if processes don't stop
4. Kills any processes still using ports 8000/8080
5. Removes `.pid` and `.lock` files
6. Confirms all services stopped

**Graceful Shutdown:**
- Tries `pkill -TERM` first (allows cleanup)
- Waits 10 seconds for process to exit
- Falls back to `pkill -9` (force kill) if needed
- Verifies ports are freed before completing

### 🔄 restart.sh - Auto-Recovery Restart

**Features:**
- ✅ Comprehensive diagnostics before restart
- ✅ Detects and reports all issues
- ✅ Cleans up zombie processes and ports
- ✅ Clears temporary files and Python cache
- ✅ Validates environment configuration
- ✅ Tests database connectivity
- ✅ Shows recent errors from logs
- ✅ Provides troubleshooting steps if restart fails

**Usage:**
```bash
./restart.sh
```

**What it does:**
1. **Diagnose Issues:**
   - Checks `.env` file exists
   - Validates `SUPABASE_URL` and `SUPABASE_KEY`
   - Detects port conflicts (8000, 8080)
   - Finds zombie processes
   - Shows recent errors from logs
   - Reports log file sizes

2. **Stop Services:**
   - Runs `./stop.sh` for clean shutdown
   - Shows progress and status

3. **Clean Up Zombies:**
   - Force kills all `uvicorn` processes
   - Force kills all `http.server` processes
   - Kills processes by port (8000, 8080)
   - Waits 2 seconds for cleanup

4. **Clear Temporary Files:**
   - Removes `.pid` and `.lock` files
   - Clears Python `__pycache__` directories
   - Deletes `.pyc` bytecode files

5. **Verify Environment:**
   - Checks `.env` file
   - Validates required variables
   - Loads environment into shell

6. **Test Database:**
   - Attempts to reach Supabase URL
   - Reports connection status
   - Continues even if test fails (may be network)

7. **Restart Services:**
   - Runs `./start.sh` with full retry logic
   - Shows final status (success or failure)

**When to use:**
- ✅ When `start.sh` fails to start services
- ✅ When services become unresponsive
- ✅ After making configuration changes
- ✅ When ports are blocked by zombie processes
- ✅ When you need to diagnose startup issues

### 📊 monitor_logs.sh - Log Monitor

**Features:**
- ✅ Real-time log monitoring
- ✅ Monitor backend, frontend, or both logs
- ✅ Color-coded output for easy reading
- ✅ Supports multitail for split-screen viewing
- ✅ Graceful exit with Ctrl+C
- ✅ Auto-cleanup of background processes

**Usage:**
```bash
# Monitor both logs (default)
./monitor_logs.sh
./monitor_logs.sh both

# Monitor only backend
./monitor_logs.sh backend

# Monitor only frontend
./monitor_logs.sh frontend
```

**What it does:**
- Monitors log files in real-time
- Shows color-coded prefixes: [BACKEND] (green), [FRONTEND] (cyan)
- Uses multitail if available for enhanced split-screen view
- Handles Ctrl+C gracefully without stopping services
- Auto-detects missing log files

**Multitail Enhancement:**
```bash
# Install multitail for better viewing (optional)
sudo apt install multitail

# Then run monitor script - will automatically use multitail
./monitor_logs.sh
```

## Troubleshooting

### Port Already in Use

**Error:** `Port 8000 is in use` or `Port 8080 is in use`

**Solution:**
```bash
# Quick fix - use restart.sh
./restart.sh

# Manual fix - kill process on port
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:8080 | xargs kill -9  # Frontend
./start.sh
```

### Environment Variables Missing

**Error:** `Missing required environment variables`

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check contents
cat .env

# Required variables:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-anon-key
# TELEGRAM_BOT_TOKEN=your-bot-token
```

### Backend Won't Start

**Symptoms:**
- Backend fails health check after 30 seconds
- Errors in `backend.log`

**Diagnosis:**
```bash
# Check backend logs
tail -n 50 backend.log

# Look for:
# - ModuleNotFoundError (missing dependencies)
# - Database connection errors
# - Port already in use errors
```

**Common fixes:**
```bash
# Install dependencies
pip install -r requirements.txt

# Check database connectivity
curl -I https://your-project.supabase.co

# Use restart script
./restart.sh
```

### Frontend Won't Start

**Symptoms:**
- Frontend fails availability check after 10 seconds
- Cannot access http://localhost:8080

**Diagnosis:**
```bash
# Check frontend logs
tail -n 50 frontend.log

# Check if port is free
lsof -i :8080
```

**Common fixes:**
```bash
# Kill process on port 8080
pkill -9 -f "http.server 8080"

# Try restart
./restart.sh
```

### Services Keep Crashing

**Symptoms:**
- Services start but crash after a few seconds
- Restart loop

**Diagnosis:**
```bash
# Run diagnostics
./restart.sh  # Shows detailed diagnostics

# Check recent errors
tail -n 100 backend.log | grep -i error
tail -n 100 frontend.log | grep -i error
```

**Common causes:**
- Database connection issues → Check `SUPABASE_URL` and `SUPABASE_KEY`
- Missing dependencies → Run `pip install -r requirements.txt`
- Syntax errors in code → Check logs for traceback
- Port conflicts → Use `restart.sh` to clean up

## Advanced Usage

### Custom Port Configuration

Edit the scripts to change ports:

```bash
# In start.sh, stop.sh, and restart.sh
BACKEND_PORT=8000   # Change this
FRONTEND_PORT=8080  # Change this
```

### Increase Retry Attempts

Edit `start.sh`:

```bash
# Change from 3 to 5 retries
MAX_RETRIES=5
```

### Longer Health Check Timeout

Edit `start.sh`:

```bash
# Change from 30s to 60s for backend
BACKEND_HEALTH_TIMEOUT=60

# Change from 10s to 20s for frontend
FRONTEND_HEALTH_TIMEOUT=20
```

### Disable Auto-Recovery

If you want start.sh to fail immediately without retries:

```bash
# In start.sh
MAX_RETRIES=1  # Only try once
```

## Logs

All scripts create log files:

```bash
# Backend logs
tail -f backend.log

# Frontend logs
tail -f frontend.log

# Follow both logs
tail -f backend.log frontend.log

# Search for errors
grep -i error backend.log
grep -i exception backend.log
```

## Success Indicators

When everything is working, you'll see:

```
✅ Environment validated
✅ Backend API is running on http://localhost:8000
✅ Frontend is running on http://localhost:8080
🎉 QUEST HUB IS RUNNING!
```

## URLs After Startup

- **Backend API:** http://localhost:8000
- **Frontend:** http://localhost:8080
- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **Health Check:** http://localhost:8000/health

## Quick Commands

```bash
# Start services
./start.sh

# Start and monitor logs
./start.sh --monitor-logs
./start.sh -m

# Stop services
./stop.sh

# Restart with diagnostics
./restart.sh

# Monitor logs (standalone)
./monitor_logs.sh              # Both logs
./monitor_logs.sh backend      # Backend only
./monitor_logs.sh frontend     # Frontend only

# Check if services are running
curl http://localhost:8000/health  # Backend
curl http://localhost:8080          # Frontend

# View logs without monitoring
tail -f backend.log    # Backend logs
tail -f frontend.log   # Frontend logs
cat backend.log        # View entire backend log
cat frontend.log       # View entire frontend log

# Search logs
grep -i error backend.log       # Find errors
grep -i exception backend.log   # Find exceptions
tail -n 100 backend.log        # Last 100 lines

# Kill stuck processes
pkill -9 -f "uvicorn|http.server"

# Check ports
lsof -i :8000  # Backend port
lsof -i :8080  # Frontend port
```

## Exit Codes

All scripts use standard exit codes:

- `0` - Success
- `1` - Failure (check logs for details)

You can check the exit code:

```bash
./start.sh
echo $?  # 0 = success, 1 = failure
```

## Integration with Other Tools

### Docker Compose

If using Docker, you can integrate these scripts:

```yaml
# docker-compose.yml
services:
  app:
    command: ["./start.sh"]
    # ...
```

### Systemd Service

Create a systemd service:

```ini
# /etc/systemd/system/questhub.service
[Unit]
Description=Quest Hub Application
After=network.target

[Service]
Type=forking
User=your-user
WorkingDirectory=/path/to/questhub
ExecStart=/path/to/questhub/start.sh
ExecStop=/path/to/questhub/stop.sh
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

### Cron Job

Restart daily:

```cron
# Restart at 3 AM daily
0 3 * * * cd /path/to/questhub && ./restart.sh >> /var/log/questhub-restart.log 2>&1
```

## Best Practices

1. **Always use restart.sh when debugging** - It provides comprehensive diagnostics
2. **Check logs first** - Most issues are visible in logs
3. **Validate .env before starting** - Prevents startup failures
4. **Monitor health endpoints** - Use `/health` to verify backend status
5. **Clean up zombie processes** - Use `restart.sh` regularly if needed
6. **Keep logs rotated** - Prevent log files from growing too large

## Support

If issues persist after using `restart.sh`:

1. Check `backend.log` and `frontend.log` for errors
2. Verify `.env` has correct values
3. Test database connectivity manually
4. Check system resources (disk space, memory)
5. Review recent code changes
