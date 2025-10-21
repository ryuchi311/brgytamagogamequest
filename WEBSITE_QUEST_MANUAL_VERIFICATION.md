# 🌐 Website Quest Manual Verification Guide

## Overview

Manual verification for Website Link Quests allows admins to review user-submitted proof before awarding XP. This is useful for quests that require specific actions on your website.

---

## 📋 How It Works

### **User Flow:**

1. **User clicks quest** in Telegram bot
   - Quest displays: "Visit Website" button
   - Opens website URL in new browser tab

2. **User completes action** on website
   - Reads article
   - Signs up for newsletter
   - Makes purchase
   - Downloads file
   - etc.

3. **User submits proof**
   - Clicks "Submit for Review" button
   - Bot asks: "Please provide proof (screenshot link, transaction ID, etc.)"
   - User sends text proof (e.g., "I signed up with email: user@example.com")

4. **User waits for review**
   - Status shows: "⏳ Pending Review"
   - User receives notification when reviewed

---

### **Admin Flow:**

1. **Admin receives notification**
   - New pending review appears in dashboard
   - Badge counter updates

2. **Admin reviews proof**
   - Go to **Admin Panel** > **User Tasks** tab
   - Filter: "Pending" status
   - See user submission with proof text

3. **Admin makes decision**
   - **APPROVE** ✅ → User receives XP + success notification
   - **REJECT** ❌ → User receives rejection notice

---

## 🎯 Use Cases for Manual Verification

### **Good Use Cases:**
- ✅ Newsletter signups (user provides email)
- ✅ Account registrations (user provides username)
- ✅ Purchases (user provides transaction ID)
- ✅ Form submissions (user provides confirmation code)
- ✅ Content reading (user answers quiz question)

### **Bad Use Cases:**
- ❌ Simple page visits (use **Auto-Complete** instead)
- ❌ Video views (use **Timer-Based** instead)
- ❌ Link clicks (use **Auto-Complete** instead)

---

## 🔧 Configuration

### **Creating Manual Website Quest:**

```javascript
// Quest Data Structure
{
  title: "Sign Up for Newsletter",
  description: "Subscribe to our newsletter and submit your email as proof",
  points_reward: 100,
  is_active: true,
  task_type: 'visit',
  platform: 'website',
  url: 'https://example.com/newsletter',
  verification_required: true,  // Must be true for manual
  verification_data: {
    method: 'manual'
  }
}
```

### **In Admin Panel:**
1. Go to **Create Website Quest**
2. Select verification type: **"Manual Verification (Proof Required)"**
3. Yellow instructions box will appear explaining the process
4. Fill in quest details
5. Click **Create Quest**

---

## 📱 User Interface (Telegram Bot)

### **Quest Display:**
```
🌐 Website Quest
━━━━━━━━━━━━━━━━
📌 Sign Up for Newsletter
Subscribe to our newsletter and submit your email as proof

🔗 URL: https://example.com/newsletter
🏆 Reward: 100 XP
📊 Status: Active
✅ Type: Manual Review Required

[🌐 Visit Website] [📤 Submit Proof]
```

### **After User Clicks "Visit Website":**
- Opens URL in new browser tab
- User completes action on website
- User returns to Telegram

### **After User Clicks "Submit Proof":**
```
Bot: Please provide proof of completion
     (e.g., email used, transaction ID, screenshot link)

User: I signed up with email: user@example.com

Bot: ✅ Proof submitted successfully!
     Status: ⏳ Pending Admin Review
     You'll be notified when reviewed.
```

---

## 🎛️ Admin Dashboard Integration

### **Location:**
Admin Panel > **User Tasks** Tab

### **View Pending Reviews:**
```
📋 Pending Verifications
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User: @john_doe
Quest: Sign Up for Newsletter
Proof: "I signed up with email: john@example.com"
Submitted: 2 hours ago
Points: 100 XP

[✅ Approve] [❌ Reject]
```

### **Approval Actions:**

**✅ Approve:**
```python
# Backend automatically:
1. Awards 100 XP to user
2. Updates user's total_earned_points
3. Sets user_task status to 'completed'
4. Sends notification to user
5. Logs approval in admin_actions table
```

**❌ Reject:**
```python
# Backend automatically:
1. Sets user_task status to 'rejected'
2. Sends rejection notification to user
3. No XP awarded
4. User can retry quest if allowed
```

---

## 🔄 Backend Handler (WebsiteLinkQuestHandler)

### **Manual Verification Flow:**

```python
# In app/quest_handlers/website_link_quest.py

async def handle_manual_submission(self, query, task_id):
    """Handle manual verification submission"""
    
    # Ask user for proof
    await query.edit_message_text(
        "📤 **Submit Proof**\n\n"
        "Please send proof of completion:\n"
        "• Screenshot link\n"
        "• Transaction ID\n"
        "• Email address used\n"
        "• Confirmation code\n\n"
        "Send your proof in the next message:"
    )
    
    # Wait for user proof text
    # Store in database with status 'pending'
    # Notify admin of new submission
```

### **Admin Review API:**

```python
# POST /api/user-tasks/{user_task_id}/verify
{
  "approved": true  # or false
}

# Response:
{
  "success": true,
  "message": "User task approved",
  "xp_awarded": 100
}
```

---

## 📊 Database Schema

### **user_tasks Table:**

```sql
CREATE TABLE user_tasks (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  task_id UUID REFERENCES tasks(id),
  status VARCHAR(20),  -- 'pending', 'completed', 'rejected'
  proof_text TEXT,      -- User-submitted proof
  reviewed_by UUID,     -- Admin who reviewed
  reviewed_at TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### **Status Values:**
- `pending` - Awaiting admin review
- `completed` - Approved by admin, XP awarded
- `rejected` - Rejected by admin, no XP

---

## 🎨 UI Improvements

### **Frontend (create-website-quest.html):**

1. **Dynamic Form:**
   - Shows timer input for timer_based
   - Shows manual instructions for manual
   - Hides irrelevant options

2. **Manual Config Box:**
   ```html
   <div id="manualConfig" class="bg-yellow-500/10 border-2 border-yellow-500/30">
     <h4>📋 Manual Verification Process:</h4>
     <ol>
       <li>User clicks quest → Opens website</li>
       <li>User takes action → Notes proof</li>
       <li>User submits proof → Stored in DB</li>
       <li>Admin reviews → Dashboard > User Tasks</li>
       <li>Admin approves/rejects → User gets XP/notice</li>
     </ol>
   </div>
   ```

3. **Helper Text:**
   - Explains full workflow
   - Shows where to review submissions
   - Clarifies admin responsibility

---

## ✅ Best Practices

### **For Admins:**

1. **Review Regularly**
   - Check dashboard daily
   - Don't leave users waiting too long
   - Set up notification preferences

2. **Clear Requirements**
   - In quest description, specify exactly what proof is needed
   - Example: "Submit your email address" (not just "sign up")

3. **Fair Decisions**
   - Accept reasonable proof
   - Reject obvious spam/fake submissions
   - Be consistent with standards

4. **Communication**
   - If rejecting, consider adding rejection reason feature
   - Update quest description if users consistently misunderstand

### **For Quest Creation:**

1. **Be Specific**
   ```
   ❌ Bad: "Visit our website"
   ✅ Good: "Sign up for newsletter and submit the email you used"
   ```

2. **Set Appropriate Rewards**
   ```
   Auto-Complete: 10-20 XP (easy, instant)
   Timer-Based: 20-50 XP (medium effort)
   Manual: 50-200 XP (requires proof, admin time)
   ```

3. **Test First**
   - Create a test quest
   - Submit proof yourself
   - Review in admin panel
   - Verify notification flow

---

## 🚀 Quick Setup Checklist

- [ ] Create website quest with manual verification
- [ ] Test quest appears in Telegram bot
- [ ] Test "Visit Website" opens correct URL
- [ ] Test "Submit Proof" accepts text input
- [ ] Check submission appears in Admin > User Tasks
- [ ] Test approve button awards XP
- [ ] Test reject button doesn't award XP
- [ ] Verify user receives notification
- [ ] Check XP balance updates correctly
- [ ] Test with multiple users

---

## 🔍 Troubleshooting

### **Quest doesn't show "Submit Proof" button:**
- Check `verification_required: true` in quest data
- Check `verification_data.method: 'manual'`
- Verify WebsiteLinkQuestHandler detects quest

### **Proof submission doesn't save:**
- Check database connection
- Verify user_tasks table exists
- Check bot has write permissions

### **Admin doesn't see pending reviews:**
- Check User Tasks tab in admin panel
- Filter by "pending" status
- Verify query includes verification_required=true

### **XP not awarded after approval:**
- Check API endpoint /api/user-tasks/{id}/verify
- Verify admin has approval permissions
- Check user's points balance query

---

## 📚 Related Files

- **Backend Handler:** `app/quest_handlers/website_link_quest.py`
- **Frontend Form:** `frontend/create-website-quest.html`
- **API Endpoint:** `app/api.py` (verify_user_task)
- **Admin Panel:** `frontend/admin.html` (User Tasks tab)

---

## 🎉 Summary

Manual verification provides a flexible way to verify user actions that require human review. The system:

✅ Allows users to submit text proof
✅ Stores submissions in database
✅ Shows pending reviews in admin dashboard
✅ Provides approve/reject buttons
✅ Automatically handles XP awards
✅ Sends notifications to users
✅ Logs all actions for audit trail

Perfect for quests requiring account creation, purchases, form submissions, or any action where automatic verification isn't possible!

---

**Last Updated:** October 21, 2025
**Status:** ✅ Complete and Ready to Use
