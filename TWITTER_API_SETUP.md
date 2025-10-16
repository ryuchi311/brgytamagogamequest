# Twitter API v2 Free Tier Implementation Guide

## 🐦 What You Get with Free Tier

**Limits:**
- 100 posts/month (reads) - Check follows, likes, retweets
- 500 posts/month (writes) - Post tweets, retweets
- Basic v2 endpoints access
- Login with X (OAuth 2.0)

**Perfect For:**
- Small to medium communities (~50 verified tasks/month)
- Mix of manual + automated verification
- Growing your bot gradually

---

## 📋 Setup Steps

### 1. Get Twitter API Credentials

1. Go to https://developer.twitter.com/
2. Sign up for Developer Account (Free)
3. Create a new App
4. Get your credentials:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Bearer Token
   - Client ID & Client Secret (for OAuth 2.0)

### 2. Add to .env File

```env
# Twitter API v2 Credentials
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_CLIENT_ID=your_client_id_here
TWITTER_CLIENT_SECRET=your_client_secret_here

# Your Twitter Account Info
TWITTER_ACCOUNT_ID=your_twitter_user_id
TWITTER_USERNAME=YourTwitterHandle
```

---

## 🛠️ Implementation

### Files to Create/Modify:
1. `app/twitter_client.py` - Twitter API integration
2. `app/api.py` - Add Twitter verification endpoints
3. `app/telegram_bot.py` - Update Twitter task handlers
4. `requirements.txt` - Add tweepy library
5. `database/migrations/002_twitter_auth.sql` - Twitter auth storage

---

## 📊 Verification Flow

### User Experience:
1. User clicks Twitter quest (follow/like/retweet)
2. Bot asks for Twitter username
3. User submits Twitter handle (@username)
4. Bot verifies via Twitter API
5. If verified → Points awarded immediately
6. If not verified → Shows helpful error

### Rate Limit Management:
- Cache verification results (24 hours)
- Batch verifications when possible
- Fall back to manual verification if quota exceeded
- Priority: High-value tasks first

---

## 🎯 What Can Be Verified

### ✅ Fully Automated (with free tier):
- **Follow**: Check if user follows your account
- **Like**: Check if user liked specific tweet
- **Retweet**: Check if user retweeted specific tweet

### ⚠️ Limited:
- **Comment**: Can search but limited queries
- **Quote Tweet**: Requires more API calls

### ❌ Not Available (free tier):
- Post new tweets (needs write access)
- DM verification

---

## 💡 Smart Rate Limit Strategy

With 100 reads/month:
- Reserve 20 for follows (most common)
- Reserve 30 for likes
- Reserve 30 for retweets
- Reserve 20 for error retries

Average: ~3 automated verifications per day

For more users: Mix automated + manual verification

---

## 📝 Ready to Implement?

Files will be created:
- Twitter API client wrapper
- Verification endpoints
- Bot handlers for Twitter username collection
- Database migration for OAuth tokens
- Rate limit tracking

Estimated time: 2-3 hours
