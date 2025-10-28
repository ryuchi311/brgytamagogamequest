# Twitter Quest Auto-Verification Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TWITTER QUEST AUTO-VERIFICATION                   │
│                         (API Method Only)                            │
└─────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  STEP 1: INITIAL STATE                                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Quest Card Shows:                                                 │
│  ┌──────────────────────────────────────────┐                    │
│  │  Follow @TamagoWarriors                   │                    │
│  │  Get 50 points                            │                    │
│  │                                           │                    │
│  │  [🐦 Follow on Twitter]  ← Click here    │                    │
│  └──────────────────────────────────────────┘                    │
│                                                                    │
│  Function Called: openTwitterAndPrepareVerification()             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│  STEP 2: TWITTER OPENS                                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ✓ Twitter page opens in new tab                                  │
│  ✓ User follows the account                                       │
│                                                                    │
│  Quest Card Updates:                                               │
│  ┌──────────────────────────────────────────┐                    │
│  │  Follow @TamagoWarriors                   │                    │
│  │                                           │                    │
│  │  ℹ️ Instructions                          │                    │
│  │  Complete the action on Twitter,          │                    │
│  │  then click "Verify Action" to confirm.   │                    │
│  │                                           │                    │
│  │  [🔍 Verify Action]  ← Click after done  │                    │
│  └──────────────────────────────────────────┘                    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│  STEP 3: VERIFICATION IN PROGRESS                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Function Called: verifyTwitterAction()                            │
│                                                                    │
│  Quest Card Shows:                                                 │
│  ┌──────────────────────────────────────────┐                    │
│  │  Follow @TamagoWarriors                   │                    │
│  │                                           │                    │
│  │  🔄 Checking with Twitter API...          │                    │
│  │     Verifying your action                 │                    │
│  │     (Animated spinner)                    │                    │
│  │                                           │                    │
│  │  [⏳ Checking...]  (disabled)             │                    │
│  └──────────────────────────────────────────┘                    │
│                                                                    │
│  Backend:                                                          │
│  POST /api/tasks/{task_id}/complete                               │
│  → Calls Twitter API to check if followed                         │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                         ↓               ↓
                    SUCCESS          FAILURE
                         ↓               ↓
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  STEP 4A: SUCCESS PATH       │  │  STEP 4B: FAILURE PATH       │
├──────────────────────────────┤  ├──────────────────────────────┤
│                              │  │                              │
│  Quest Card Shows:           │  │  Quest Card Shows:           │
│  ┌────────────────────────┐ │  │  ┌────────────────────────┐ │
│  │  ✅ Action Verified!    │ │  │  │  ❌ Action Not         │ │
│  │  Click "Claim Reward"  │ │  │  │  Completed             │ │
│  │  to get your points.   │ │  │  │                        │ │
│  │                        │ │  │  │  You haven't followed  │ │
│  │  [✅ Claim Reward]     │ │  │  │  the account yet.      │ │
│  └────────────────────────┘ │  │  │                        │ │
│                              │  │  │  [🔍 Verify Again]     │ │
│                              │  │  └────────────────────────┘ │
│                              │  │                              │
│                              │  │  User can retry after        │
│                              │  │  completing the action       │
└──────────────────────────────┘  └──────────────────────────────┘
              ↓
┌────────────────────────────────────────────────────────────────────┐
│  STEP 5: CLAIM REWARD                                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Function Called: handleTwitterClaim()                             │
│                                                                    │
│  Full-Screen Overlay Appears:                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │                       🎉                                   │  │
│  │                                                            │  │
│  │                 Quest Complete!                            │  │
│  │                                                            │  │
│  │                   +50 Points                               │  │
│  │                                                            │  │
│  │          Congratulations! Returning to quests...           │  │
│  │                                                            │  │
│  │         (Blue-to-purple gradient, bouncing)                │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  After 2 seconds:                                                  │
│  ✓ Overlay removed                                                 │
│  ✓ Redirect to quest list (backToQuestList())                     │
│  ✓ Tasks reload to show completed status                          │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════

ACTION TYPE VARIATIONS:

┌────────────────────┬──────────────────────────────────────────┐
│  Action Type       │  Initial Button Label                    │
├────────────────────┼──────────────────────────────────────────┤
│  follow            │  🐦 Follow on Twitter                    │
│  like              │  ❤️ Like Tweet                           │
│  retweet           │  🔄 Retweet                              │
│  quote             │  💬 Quote Tweet                          │
│  reply             │  💬 Reply to Tweet                       │
│  combo             │  ⭐ Complete All Actions                 │
└────────────────────┴──────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════

API ENDPOINTS:

Frontend → Backend:
POST /api/tasks/{task_id}/complete
Body: { "telegram_id": "7988161711" }

Backend → Twitter API:
┌────────────────────┬─────────────────────────────────────────────┐
│  Action Type       │  Twitter API Endpoint                       │
├────────────────────┼─────────────────────────────────────────────┤
│  follow            │  GET /2/users/:id/following                 │
│  like              │  GET /2/tweets/:id/liking_users             │
│  retweet           │  GET /2/tweets/:id/retweeted_by             │
│  quote/reply       │  GET /2/tweets/search/recent                │
│  combo             │  Multiple API calls combined                │
└────────────────────┴─────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════

ERROR HANDLING:

┌─────────────────────────────────────────────────────────────────┐
│  Error Type                    │  User Message                  │
├────────────────────────────────┼────────────────────────────────┤
│  User hasn't completed action  │  "Action not completed yet"    │
│  Twitter API rate limit        │  "Too many requests, try later"│
│  Network error                 │  "Connection error"            │
│  Invalid credentials           │  "Configuration error"         │
│  Deleted tweet                 │  "Tweet no longer available"   │
│  No user ID found              │  "Please reload the app"       │
└────────────────────────────────┴────────────────────────────────┘

All errors show:
- ⚠️ Warning icon
- Yellow/Red background
- "🔄 Try Again" button

═══════════════════════════════════════════════════════════════════════

COMPARISON: MANUAL vs API VERIFICATION

┌─────────────────────────────────────────────────────────────────┐
│  MANUAL VERIFICATION              │  API VERIFICATION           │
├───────────────────────────────────┼─────────────────────────────┤
│  1 button: "Follow on Twitter"    │  4 buttons: Action → Verify │
│  Opens Twitter                    │  → Status → Claim           │
│  User submits completion          │                             │
│  Admin reviews screenshot         │  Auto-check via API         │
│  Admin approves/rejects           │  Instant verification       │
│  No animation                     │  Loading + Success animation│
│  Delay: hours/days                │  Delay: seconds             │
└───────────────────────────────────┴─────────────────────────────┘

═══════════════════════════════════════════════════════════════════════

FUTURE ENHANCEMENTS:

□ Twitter OAuth for direct user authentication
□ Cache verification results (24h cooldown)
□ Rate limit handling with queue system
□ Retry mechanism with exponential backoff
□ Analytics: Track verification success rate
□ Admin override for failed verifications
□ Webhook for real-time Twitter events

```
