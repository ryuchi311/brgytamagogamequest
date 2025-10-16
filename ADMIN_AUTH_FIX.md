# Admin Authentication Issue - 401 Unauthorized

## ❌ Problem
Getting `401 Unauthorized` error when trying to create a quest:
```
POST /api/tasks 401 (Unauthorized)
Failed to create quest: Invalid authentication credentials
```

## 🔍 Root Cause
The authentication token in `localStorage` is either:
1. **Expired** - JWT tokens expire after a certain time
2. **Invalid** - Token from an old session
3. **Missing** - No admin user logged in

## ✅ Solution Applied

### Fix 1: Added Authentication Error Handler
Added `handleAuthError()` function that:
- Clears the invalid token
- Shows the login screen
- Alerts user that session expired

### Fix 2: Enhanced Token Validation
Updated `window.onload` to validate the token before showing dashboard:
```javascript
window.onload = async function() {
    const token = localStorage.getItem('authToken');
    if (token) {
        // Validate token with API call
        const response = await fetch(`${API_URL}/tasks`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.status === 401) {
            handleAuthError(); // Auto-logout if invalid
        }
    }
}
```

### Fix 3: Auto-Logout on 401 Errors
Updated `submitTask()` to detect 401 and force re-login:
```javascript
if (response.status === 401) {
    handleAuthError();
    return;
}
```

## 🔑 How to Fix Your Issue NOW

### Option 1: Clear Cache and Re-login (Recommended)
1. Open the admin dashboard: http://localhost/admin.html
2. Open browser DevTools (F12)
3. Go to Console tab
4. Run: `localStorage.clear()`
5. Refresh the page (F5)
6. Login with:
   - **Username**: `admin`
   - **Password**: `changeme123`

### Option 2: Hard Refresh
1. Close all browser tabs with admin dashboard
2. Open new tab
3. Go to: http://localhost/admin.html
4. Press `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac) for hard refresh
5. Login with credentials above

### Option 3: Use Incognito/Private Window
1. Open incognito/private browsing window
2. Go to: http://localhost/admin.html
3. Login with credentials above
4. This ensures no cached token

## 🔐 Admin Credentials

**Default credentials** (from `.env` file):
```
Username: admin
Password: changeme123
```

## 🧪 Verify It's Working

After logging in fresh:
1. You should see the admin dashboard
2. Try creating a quest
3. If successful → Problem solved! ✅
4. If still getting 401 → See troubleshooting below

## 🔧 Troubleshooting

### Still Getting 401?

#### Check 1: Verify Admin User Exists in Database
```bash
docker-compose exec postgres psql -U postgres -d telegram_bot_db -c "SELECT username, email, role FROM admin_users;"
```

**Expected output:**
```
 username |       email        |     role     
----------+--------------------+--------------
 admin    | admin@example.com  | super_admin
```

#### Check 2: Verify API is Running
```bash
docker-compose ps api
```

Should show `Up` status.

#### Check 3: Check API Logs
```bash
docker-compose logs api --tail=50 | grep -i "auth\|login\|401"
```

Look for authentication errors.

#### Check 4: Test Login API Directly
```bash
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme123"}'
```

**Expected output:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "token_type": "bearer"
}
```

If you get an error, the admin user password might be wrong.

#### Check 5: Reset Admin Password

If the password doesn't work, create a new admin user:

```bash
docker-compose exec api python -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
hashed = pwd_context.hash('changeme123')
print(f'Hashed password: {hashed}')
"
```

Then update the database:
```bash
docker-compose exec postgres psql -U postgres -d telegram_bot_db -c \
  "UPDATE admin_users SET password_hash='PASTE_HASH_HERE' WHERE username='admin';"
```

## 📊 What Changed in the Code

### Files Modified:
1. **`frontend/admin.html`**
   - Added `handleAuthError()` function
   - Enhanced token validation on page load
   - Auto-logout on 401 errors in all API calls

### Features Added:
- ✅ Automatic token validation
- ✅ Session expiry detection
- ✅ User-friendly error messages
- ✅ Auto-redirect to login when token expires

## 💡 Best Practices Going Forward

1. **Always use fresh login** if you haven't used admin panel in a while
2. **Clear localStorage** if you see unexpected auth errors
3. **Check browser console** for detailed error messages
4. **Token expires after 30 minutes** of inactivity (default)

## 🎯 Quick Commands Reference

```bash
# Clear localStorage (in browser console)
localStorage.clear()

# Check admin users in database
docker-compose exec postgres psql -U postgres -d telegram_bot_db \
  -c "SELECT * FROM admin_users;"

# Restart API (if needed)
docker-compose restart api

# View API logs
docker-compose logs api -f
```

## ✅ Summary

**Problem**: 401 Unauthorized when creating quest  
**Cause**: Expired or invalid authentication token  
**Solution**: Clear localStorage and login again  
**Prevention**: Auto-logout on 401 errors now implemented

---

**Try this now:**
1. Go to admin dashboard
2. Open console (F12)
3. Run: `localStorage.clear()`
4. Refresh page
5. Login with `admin` / `changeme123`
6. Try creating a quest again

It should work! 🎉
