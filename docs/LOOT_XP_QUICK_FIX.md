# 🎯 Quick Fix Reference: Loot Rewards XP

## Issue
"undefined XP" displayed in Loot Rewards tab

## Solution (1 Line Change!)
```javascript
// File: frontend/index.html
// Line: 771

// Change this:
${reward.points_required} XP

// To this:
${reward.points_cost || 0} XP
```

## Why?
- Database field is `points_cost` (not `points_required`)
- JavaScript couldn't find the field → returned `undefined`
- Now using correct field name → shows actual XP cost

## Test
1. Open web app
2. Go to Rewards tab
3. See XP costs like "500 XP", "1000 XP" instead of "undefined XP"

## Status
✅ **FIXED** - Ready to test!

---

**One-line fix for a big improvement!** 💎
