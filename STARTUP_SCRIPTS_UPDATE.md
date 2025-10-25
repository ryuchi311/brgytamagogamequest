# Startup Scripts Update - Complete ✅

## Summary

Successfully updated all startup scripts with robust error handling, retry logic, and auto-recovery mechanisms.

## Changes Made

### 1. **start.sh** - Enhanced with Auto-Recovery
- ✅ **Environment Validation**: Checks `.env` file and required variables before starting
- ✅ **Port Conflict Detection**: Automatically detects if ports 8000/8080 are in use
- ✅ **Zombie Process Cleanup**: Kills blocking processes before starting
- ✅ **Retry Logic**: Up to 3 retry attempts for both backend and frontend
- ✅ **Health Checks**: Waits up to 30s for backend, 10s for frontend to be healthy
- ✅ **Detailed Logging**: Shows progress, errors, and suggestions
- ✅ **Color-Coded Output**: Green (success), Red (error), Yellow (warning)

**Key Functions Added:**
- `check_port_available()` - Verifies port is free
- `kill_port_process()` - Kills process blocking a port
- `wait_for_service()` - Polls health endpoint with timeout
- `validate_environment()` - Checks .env and required variables
- `start_backend()` - Starts backend with retry logic
- `start_frontend()` - Starts frontend with retry logic

### 2. **stop.sh** - Enhanced with Thorough Cleanup
- ✅ **Graceful Shutdown**: Sends SIGTERM first, waits 10 seconds
- ✅ **Force Kill**: Falls back to SIGKILL if graceful fails
- ✅ **Port Cleanup**: Ensures ports 8000 and 8080 are freed
- ✅ **File Cleanup**: Removes PID files and lock files
- ✅ **Verification**: Confirms all processes stopped

**Key Functions Added:**
- `graceful_stop()` - Tries graceful shutdown with fallback
- `kill_port()` - Frees specific port by force

### 3. **restart.sh** - NEW Auto-Recovery Script
- ✅ **Comprehensive Diagnostics**: Checks environment, ports, zombies, logs
- ✅ **Issue Detection**: Identifies all problems before restarting
- ✅ **Zombie Cleanup**: Force kills all related processes
- ✅ **Temporary File Cleanup**: Removes PIDs, locks, Python cache
- ✅ **Environment Verification**: Validates .env configuration
- ✅ **Database Test**: Attempts to reach Supabase
- ✅ **Smart Restart**: Runs stop.sh + cleanup + start.sh
- ✅ **Troubleshooting Guide**: Shows steps if restart fails

**Key Functions Added:**
- `diagnose_issues()` - Scans for all potential problems
- `cleanup_zombies()` - Force kills all related processes
- `clear_temp_files()` - Removes temp files and cache
- `verify_environment()` - Validates configuration
- `test_database()` - Tests Supabase connectivity

## Configuration

All scripts use these configurable variables:

```bash
# Ports
BACKEND_PORT=8000
FRONTEND_PORT=8080

# Retry settings
MAX_RETRIES=3
BACKEND_HEALTH_TIMEOUT=30  # seconds
FRONTEND_HEALTH_TIMEOUT=10  # seconds
GRACEFUL_TIMEOUT=10  # seconds for graceful shutdown
```

## Usage

### Normal Startup
```bash
./start.sh
```

### Stop Services
```bash
./stop.sh
```

### Restart with Diagnostics (Recommended when issues occur)
```bash
./restart.sh
```

## What Happens When start.sh Fails

**Old Behavior:**
- Failed immediately with exit 1
- Left zombie processes running
- Didn't clean up ports
- No retry logic
- Minimal error information

**New Behavior:**
1. Validates environment first (prevents wasted startup attempts)
2. Checks and cleans up port conflicts automatically
3. Tries to start backend up to 3 times with delays
4. Waits up to 30 seconds for backend health (not just 3 seconds)
5. Shows last 10 lines of logs if failure occurs
6. Tries to start frontend up to 3 times with delays
7. Waits up to 10 seconds for frontend availability
8. Suggests running `./restart.sh` if all retries fail
9. Color-coded output for easy diagnosis

## What restart.sh Does

This is the **"fix everything"** script that you should use when things go wrong:

### Phase 1: Diagnosis
```
🔍 Running diagnostics...
✅ .env file exists
✅ Required environment variables set
⚠️  Issue found: Port 8000 is in use
   PID: 12345
   Will be killed during restart
⚠️  Issue found: Zombie backend processes detected
   Will be killed during restart
⚠️  Recent errors found in backend.log
   Last 5 error lines: [shows errors]

⚠️  Found 3 issue(s) - will attempt to fix
```

### Phase 2: Stop
```
🛑 Stopping existing services...
[Runs ./stop.sh with graceful shutdown]
```

### Phase 3: Cleanup
```
🧹 Cleaning up zombie processes...
   Killing PID 12345 on port 8000...
✅ Cleanup complete

🗑️  Clearing temporary files...
✅ Temporary files cleared
```

### Phase 4: Verify
```
🔍 Verifying environment...
✅ Environment verified

🔌 Testing database connectivity...
✅ Database connection OK
```

### Phase 5: Restart
```
🚀 Starting services with auto-recovery...
[Runs ./start.sh with full retry logic]

✅ RESTART SUCCESSFUL!
```

## Retry Logic in Detail

### Backend Start Retry
```
Attempt 1:
- Check port 8000 available
- Kill process if needed
- Start uvicorn
- Wait 3 seconds
- Health check (up to 30 seconds)
- ✅ Success or ❌ Show logs and retry

Attempt 2:
- Same as above
- Wait 5 seconds before retry

Attempt 3:
- Same as above
- Final attempt
- ❌ Suggest restart.sh if fails
```

### Frontend Start Retry
```
Attempt 1:
- Check port 8080 available
- Kill process if needed
- Start http.server
- Wait 2 seconds
- Availability check (up to 10 seconds)
- ✅ Success or ❌ Show logs and retry

Attempt 2:
- Same as above
- Wait 3 seconds before retry

Attempt 3:
- Same as above
- Final attempt
- ❌ Suggest restart.sh if fails
```

## Error Messages and What They Mean

### ❌ Port already in use
**Meaning:** Another process is using port 8000 or 8080  
**Solution:** Script automatically kills it, or use `./restart.sh`

### ❌ Missing required environment variables
**Meaning:** .env file missing or incomplete  
**Solution:** Create/update .env with SUPABASE_URL and SUPABASE_KEY

### ❌ Failed to start backend after 3 attempts
**Meaning:** Backend crashes or won't start  
**Solution:** Check `backend.log` for errors, verify dependencies installed

### ❌ Backend failed to become healthy after 30s
**Meaning:** Backend started but health check fails  
**Solution:** Check database connection, verify .env variables

### ⚠️ Zombie processes detected
**Meaning:** Old processes still running from previous start  
**Solution:** Script cleans them automatically, or use `./restart.sh`

## Troubleshooting Flow

```
Problem: Services won't start
    ↓
Step 1: Try ./restart.sh
    ↓
Still fails?
    ↓
Step 2: Check logs
    $ tail -n 50 backend.log
    $ tail -n 50 frontend.log
    ↓
Step 3: Verify environment
    $ cat .env
    $ source .env
    $ echo $SUPABASE_URL
    ↓
Step 4: Check dependencies
    $ pip install -r requirements.txt
    ↓
Step 5: Manual cleanup
    $ pkill -9 -f "uvicorn|http.server"
    $ lsof -i :8000
    $ lsof -i :8080
    ↓
Step 6: Try again
    $ ./restart.sh
```

## Testing Scenarios

### Test 1: Port Already in Use
```bash
# Start services
./start.sh

# Try to start again (should handle gracefully)
./start.sh
# Expected: Kills old processes, starts fresh
```

### Test 2: Missing Environment
```bash
# Rename .env temporarily
mv .env .env.bak

# Try to start
./start.sh
# Expected: ❌ .env file not found! Please create .env...

# Restore .env
mv .env.bak .env
```

### Test 3: Backend Crash
```bash
# Start services
./start.sh

# Kill backend manually
pkill -9 -f uvicorn

# Use restart to recover
./restart.sh
# Expected: Detects issue, cleans up, restarts successfully
```

### Test 4: Zombie Processes
```bash
# Create zombie process
nohup python -m http.server 8080 &

# Try to start
./start.sh
# Expected: Detects port in use, kills zombie, starts fresh
```

## Benefits of New Approach

| Feature | Old Scripts | New Scripts |
|---------|-------------|-------------|
| Environment validation | ❌ No | ✅ Yes, before starting |
| Port conflict handling | ❌ Fails | ✅ Auto-kills and retries |
| Retry logic | ❌ No | ✅ 3 attempts with backoff |
| Health check timeout | ❌ 3 seconds | ✅ 30 seconds backend, 10 seconds frontend |
| Error logging | ❌ Minimal | ✅ Detailed with log excerpts |
| Zombie cleanup | ❌ Manual | ✅ Automatic |
| Graceful shutdown | ❌ Kill immediately | ✅ Try graceful first |
| Diagnostics | ❌ None | ✅ Comprehensive via restart.sh |
| Color output | ❌ No | ✅ Yes, for clarity |
| Recovery guidance | ❌ None | ✅ Suggests next steps |

## Files Changed

1. **start.sh** - Completely rewritten (68 lines → 282 lines)
2. **stop.sh** - Enhanced (18 lines → 96 lines)
3. **restart.sh** - NEW (235 lines)
4. **STARTUP_SCRIPTS_GUIDE.md** - NEW (comprehensive documentation)

## Next Steps

### Immediate Use
```bash
# Make sure all scripts are executable
chmod +x start.sh stop.sh restart.sh

# Test restart.sh (safest option)
./restart.sh
```

### When to Use Each Script

**Use `./start.sh` when:**
- Starting fresh after reboot
- First time setup
- You know services are stopped

**Use `./stop.sh` when:**
- Shutting down for maintenance
- Need to free ports
- Want clean shutdown

**Use `./restart.sh` when:**
- Services won't start
- Something is broken
- Need diagnostics
- After code changes
- Zombie processes present
- Want comprehensive recovery

## Success Indicators

When restart.sh succeeds, you'll see:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ RESTART SUCCESSFUL!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📡 Backend API:    http://localhost:8000
🌐 Frontend:       http://localhost:8080
📚 API Docs:       http://localhost:8000/docs

📝 Monitor logs:
   Backend:  tail -f backend.log
   Frontend: tail -f frontend.log

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Documentation

Full documentation available in:
- **STARTUP_SCRIPTS_GUIDE.md** - Comprehensive guide with troubleshooting

## Summary

✅ All scripts updated with auto-recovery  
✅ Retry logic implemented (3 attempts per service)  
✅ Environment validation added  
✅ Port conflict auto-resolution  
✅ Graceful shutdown with force-kill fallback  
✅ NEW restart.sh with comprehensive diagnostics  
✅ Color-coded output for clarity  
✅ Detailed error logging with suggestions  
✅ Complete documentation created  

**The scripts are now production-ready and handle failures gracefully!**
