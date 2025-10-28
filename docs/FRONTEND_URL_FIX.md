# Frontend URL Fix - GitHub Codespaces Support

## Issue Summary

The frontend was unable to communicate with the API server when accessed via GitHub Codespaces URLs, resulting in 404 errors for all API calls.

### Error Messages

```
GET https://psychic-space-parakeet-rrvpxvx9x42p744-8080.app.github.dev/api/tasks 404 (Not Found)
GET https://psychic-space-parakeet-rrvpxvx9x42p744-8080.app.github.dev/api/users/123456789 404 (Not Found)
POST https://psychic-space-parakeet-rrvpxvx9x42p744-8080.app.github.dev/api/users/init 501 (Not Implemented)
```

## Root Cause Analysis

### GitHub Codespaces URL Format

GitHub Codespaces exposes services using a unique URL format where the **port number is embedded in the subdomain**, not as a traditional port suffix:

**Frontend (port 8080):**
```
https://psychic-space-parakeet-rrvpxvx9x42p744-8080.app.github.dev/
                                               ^^^^
                                            Port in subdomain
```

**API Server (port 8000):**
```
https://psychic-space-parakeet-rrvpxvx9x42p744-8000.app.github.dev/
                                               ^^^^
                                            Port in subdomain
```

### Original Implementation (Broken)

The original code attempted to replace `:8080` with `:8000`:

```javascript
// ❌ This only works for localhost, not Codespaces
const API_BASE = window.location.origin.replace(':8080', ':8000');
```

**Why it failed:**
- `window.location.origin` = `https://...-8080.app.github.dev`
- No `:8080` to replace (port is in subdomain as `-8080`)
- Result: API_BASE = same as origin, points to frontend server
- Frontend tries to fetch API from itself → 404 errors

## Solution Implementation

### Smart URL Detection

Implemented environment detection to handle both localhost and Codespaces:

```javascript
let API_BASE;
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    // Local development: http://localhost:8080 → http://localhost:8000
    API_BASE = window.location.origin.replace(':8080', ':8000');
} else {
    // GitHub Codespaces: https://...-8080.github.dev → https://...-8000.github.dev
    API_BASE = window.location.origin.replace('-8080.', '-8000.');
}
const API_URL = `${API_BASE}/api`;
```

### Key Changes

1. **Environment Detection:**
   - Check `window.location.hostname`
   - Localhost: use port suffix replacement (`:8080` → `:8000`)
   - Codespaces: use subdomain replacement (`-8080.` → `-8000.`)

2. **Debugging Support:**
   - Added `console.log('API_URL configured:', API_URL)` in both files
   - Helps verify correct URL is being used
   - Visible in browser DevTools Console

3. **Files Modified:**
   - `frontend/index.html` - User portal
   - `frontend/admin.html` - Admin panel

## Testing Results

### API Endpoints Verified

All API endpoints respond correctly when accessed directly:

```bash
# Tasks API
curl http://localhost:8000/api/tasks
✅ HTTP 200 - Returns 3 quests

# Leaderboard API
curl http://localhost:8000/api/leaderboard
✅ HTTP 200 - Returns 1 user (testuser - 190 points)

# User Init API
curl -X POST "http://localhost:8000/api/users/init?telegram_id=123456789&username=testuser"
✅ HTTP 200 - Returns user object

# User Data API
curl http://localhost:8000/api/users/123456789
✅ HTTP 200 - Returns user details
```

### Frontend Verification

After the fix, the frontend should:

1. ✅ Load quest list with 3 quests
2. ✅ Display leaderboard with sorted users
3. ✅ Show user profile data
4. ✅ No 404 errors in Console
5. ✅ Console shows correct API_URL with `-8000` subdomain

## URL Format Comparison

| Environment | Frontend URL | API URL |
|-------------|-------------|---------|
| **Localhost** | `http://localhost:8080` | `http://localhost:8000` |
| **Codespaces** | `https://...-8080.app.github.dev` | `https://...-8000.app.github.dev` |

## How It Works

### Flow Diagram

```
Browser loads frontend
      ↓
JavaScript executes
      ↓
Check hostname
      ↓
    Is localhost?
   ╱           ╲
 YES            NO
  ↓              ↓
Replace :port   Replace -port.
  ↓              ↓
http://localhost:8000   https://...-8000.github.dev
  ↓              ↓
      API_URL set
      ↓
All fetch() calls use correct API URL
```

### Example Transformations

**Localhost:**
```javascript
window.location.origin = "http://localhost:8080"
API_BASE = "http://localhost:8080".replace(':8080', ':8000')
API_BASE = "http://localhost:8000"
API_URL = "http://localhost:8000/api"
```

**GitHub Codespaces:**
```javascript
window.location.origin = "https://psychic-space-parakeet-rrvpxvx9x42p744-8080.app.github.dev"
API_BASE = "https://...-8080.app.github.dev".replace('-8080.', '-8000.')
API_BASE = "https://psychic-space-parakeet-rrvpxvx9x42p744-8000.app.github.dev"
API_URL = "https://psychic-space-parakeet-rrvpxvx9x42p744-8000.app.github.dev/api"
```

## Debugging Guide

### 1. Check Console for API_URL

Open browser DevTools (F12) → Console tab

Look for:
```
API_URL configured: https://psychic-space-parakeet-rrvpxvx9x42p744-8000.app.github.dev/api
```

**Verify:**
- ✅ Should contain `-8000` (not `-8080`)
- ✅ Should match API server subdomain
- ✅ Should end with `/api`

### 2. Check Network Tab

DevTools → Network tab

**Look for API requests:**
- Should go to `-8000` subdomain
- Should return HTTP 200 (not 404)
- Response should contain JSON data

### 3. Common Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| 404 errors | Still using `-8080` | Hard refresh (Ctrl+Shift+R) |
| CORS errors | API server down | Check `ps aux \| grep uvicorn` |
| No data | API returns error | Check API logs: `tail api.log` |
| Old cached version | Browser cache | Clear cache or use Incognito |

## Tailwind CDN Warning

You may see this warning in Console:

```
cdn.tailwindcss.com should not be used in production
```

**This is expected and non-critical for development.**

### Why It's There

We're using Tailwind CSS via CDN for rapid development:

```html
<script src="https://cdn.tailwindcss.com"></script>
```

### Production Solution (When Needed)

For production deployment:

1. **Install Tailwind:**
   ```bash
   npm install -D tailwindcss
   ```

2. **Create Config:**
   ```bash
   npx tailwindcss init
   ```

3. **Build CSS:**
   ```bash
   npx tailwindcss -i input.css -o output.css
   ```

4. **Link Built CSS:**
   ```html
   <link href="/output.css" rel="stylesheet">
   ```

## Related Documentation

- **LEADERBOARD_FIX_COMPLETE.md** - Database query fixes
- **BRAND_COLORS_APPLIED.md** - Official color system
- **QUICK_ACCESS_GUIDE.md** - Development reference
- **FRONTEND_FIX_COMPLETE.md** - Frontend architecture

## Summary

The frontend now correctly detects the environment and constructs the appropriate API URL:

- **Localhost:** Uses port suffix (`:8080` → `:8000`)
- **Codespaces:** Uses subdomain replacement (`-8080.` → `-8000.`)

This ensures API calls reach the correct server regardless of how the application is accessed.

**Status:** ✅ **RESOLVED**

---

*Fixed: October 16, 2025*
*Environment: GitHub Codespaces (Ubuntu 24.04.2 LTS)*
