# Twitter Developer Project Setup

## Issue
You're seeing this error:
```
403 Forbidden
When authenticating requests to the Twitter API v2 endpoints, you must use keys and tokens 
from a Twitter developer App that is attached to a Project.
```

## Solution
Your Twitter App needs to be attached to a Project in the Twitter Developer Portal.

## Steps to Fix

### 1. Go to Twitter Developer Portal
Visit: https://developer.twitter.com/en/portal/dashboard

### 2. Create or Select a Project
- If you don't have a Project, click **"Create Project"**
- Give it a name (e.g., "Gaming Bot Verification")
- Select use case: "Making a bot"
- Provide a description of what your bot does

### 3. Attach Your App to the Project
- In your Project, look for **"Add App"** or **"Attach an App"**
- Select your existing App (the one with your current API keys)
- OR create a new App within the Project

### 4. Get Your App's Credentials
Once your App is attached to a Project:

1. Click on your App name
2. Go to **"Keys and Tokens"** tab
3. You'll see:
   - **API Key** (Consumer Key)
   - **API Secret** (Consumer Secret)
   - **Bearer Token**
   - **Access Token & Secret** (optional)

### 5. Update Your .env File
Replace the credentials in your `.env` file with the new ones:

```bash
# Twitter API v2 Credentials (from Project-attached App)
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAA...
TWITTER_API_KEY=your_new_api_key
TWITTER_API_SECRET=your_new_api_secret
TWITTER_CLIENT_ID=your_client_id  # Optional
TWITTER_CLIENT_SECRET=your_client_secret  # Optional

# Your Twitter Account Info (keep these same)
TWITTER_ACCOUNT_ID=1659517235717890048
TWITTER_USERNAME=@BRGYTamago
```

### 6. Restart the Services
```bash
docker-compose restart api bot
```

### 7. Test Again
```bash
docker-compose exec api python -c "
from app.twitter_client import twitter_client
import json
result = twitter_client.verify_follow('elonmusk')
print(json.dumps(result, indent=2))
"
```

## Expected Result
After fixing, you should see either:
```json
{
  "success": true,
  "is_following": false,
  "api_available": true
}
```
or
```json
{
  "success": true,
  "is_following": true,
  "api_available": true
}
```

## Current Status
✅ Twitter client successfully initialized
✅ Credentials loaded
✅ Container has tweepy library
❌ App not attached to Project (needs fix)

## Notes
- The Twitter API v2 **requires** Apps to be attached to Projects
- This is a Twitter security/organization requirement
- Your credentials (API Key, Secret, Bearer Token) might change after attaching to a Project
- You can have multiple Apps in one Project
- Free tier limits still apply: 100 reads/month, 500 writes/month

## After Setup
Once this is fixed, you'll be able to:
1. Verify Twitter follows automatically
2. Verify tweet likes automatically  
3. Verify retweets automatically
4. All with 24-hour caching to save API quota
