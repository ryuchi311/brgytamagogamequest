# 🚀 Quick Launch Checklist - Telegram Mini App

## ⚡ 5-Minute Setup

Follow these steps to launch your Gaming Quest Hub as a Telegram Mini App:

---

## Step 1️⃣: Create Bot (2 minutes)

- [ ] Open Telegram app
- [ ] Search for: **@BotFather**
- [ ] Send: `/newbot`
- [ ] Choose bot name: `Gaming Quest Hub`
- [ ] Choose username: `your_name_bot` (must end with "bot")
- [ ] **Save the bot token** (you'll need this for your .env file)

**Result**: You now have a bot! Example: @gamequesthub_bot

---

## Step 2️⃣: Configure Mini App (2 minutes)

- [ ] Still in @BotFather, send: `/newapp`
- [ ] Select your bot from the list
- [ ] **Title**: Gaming Quest Hub
- [ ] **Description**: Complete quests, earn XP, and claim awesome rewards!
- [ ] **Photo**: Upload a 640x640px image (your app icon)
- [ ] **Demo** (optional): Skip or upload a GIF
- [ ] **Web App URL**: Enter your frontend URL:
  
  For Codespaces:
  ```
  https://psychic-space-parakeet-rrvpxvx9x42p744-8080.app.github.dev/index.html
  ```
  
  For custom domain:
  ```
  https://yourdomain.com/index.html
  ```

- [ ] **Short name**: `questhub` (or your choice, lowercase, no spaces)

**Result**: Your mini app is created!

---

## Step 3️⃣: Add Menu Button (1 minute)

- [ ] In @BotFather, send: `/mybots`
- [ ] Select your bot
- [ ] Click: **Bot Settings**
- [ ] Click: **Menu Button**
- [ ] Click: **Configure Menu Button**
- [ ] **Button text**: 🎮 Play Game
- [ ] **URL**: Same as your Web App URL above

**Result**: Users can now tap the menu button to open your game!

---

## Step 4️⃣: Test It! (1 minute)

- [ ] Search for your bot in Telegram (e.g., @gamequesthub_bot)
- [ ] Click **Start** (or send `/start`)
- [ ] Look for the menu button (≡) in bottom-left
- [ ] Tap the menu button
- [ ] Your mini app should open! 🎉
- [ ] Try completing a quest

**Expected**: 
- ✅ App loads in Telegram
- ✅ Your account auto-created
- ✅ Can see quests
- ✅ Can earn XP

**Troubleshooting**:
- ❌ App doesn't load → Check URL is correct and servers are running
- ❌ "Telegram Required" message → Good! This means direct browser access is blocked
- ❌ Menu button not showing → Refresh @BotFather menu button settings

---

## Step 5️⃣: Update Bot Token (if needed)

If you created a new bot, update your `.env` file:

- [ ] Open `.env` file in your project
- [ ] Find line: `TELEGRAM_BOT_TOKEN=your_token_here`
- [ ] Replace with your new token from @BotFather
- [ ] Save the file
- [ ] Restart your bot:
  ```bash
  pkill -f telegram_bot.py
  nohup python app/telegram_bot.py > bot.log 2>&1 &
  ```

---

## ✅ Launch Complete!

Your Gaming Quest Hub is now live as a Telegram Mini App! 🎮

### Share With Users

**Option 1: Direct Link**
```
https://t.me/YOUR_BOT_USERNAME/YOUR_SHORT_NAME
```

Example:
```
https://t.me/gamequesthub_bot/questhub
```

**Option 2: Bot Username**
Just tell users:
1. Search for `@YOUR_BOT_USERNAME` in Telegram
2. Tap "Start"
3. Tap the menu button (≡)
4. Play!

---

## 📊 Verify Everything Works

Run this checklist to ensure everything is configured correctly:

### Frontend Checklist
- [ ] Telegram SDK loads (check browser console)
- [ ] Browser access shows "Telegram Required" message
- [ ] Telegram access works and loads user data
- [ ] User's name appears correctly
- [ ] XP points display

### Backend Checklist
- [ ] Frontend server running (port 8080)
- [ ] API server running (port 8000)
- [ ] Database connected
- [ ] Users auto-register on first access
- [ ] Quest verification works

### Bot Checklist
- [ ] Bot responds to `/start`
- [ ] Bot responds to `/help`
- [ ] Menu button appears
- [ ] Menu button opens mini app
- [ ] User data syncs between bot and mini app

---

## 🎯 Your URLs Reference

**Web App URL** (for @BotFather):
```
https://psychic-space-parakeet-rrvpxvx9x42p744-8080.app.github.dev/index.html
```

**Admin Panel** (desktop only):
```
https://psychic-space-parakeet-rrvpxvx9x42p744-8080.app.github.dev/admin.html
```

**API Endpoint**:
```
https://psychic-space-parakeet-rrvpxvx9x42p744-8000.app.github.dev
```

**Direct Mini App Link** (replace with your bot):
```
https://t.me/YOUR_BOT_USERNAME/YOUR_SHORT_NAME
```

---

## 💡 Quick Tips

1. **Test Before Sharing**: Make sure everything works with your own Telegram account first

2. **Add Sample Quests**: Create some quests in the admin panel before inviting users

3. **Customize Welcome Message**: Edit the bot's `/start` message in `app/telegram_bot.py`

4. **Monitor Users**: Check the admin panel to see new registrations

5. **Update Bot Avatar**: Send a photo to @BotFather with `/setuserpic`

6. **Set Bot Commands**: Use `/setcommands` in @BotFather to show available commands

---

## 🆘 Common Issues

### Issue: Menu button doesn't appear
**Fix**: 
1. Go to @BotFather
2. Send `/mybots` → select bot → Bot Settings → Menu Button
3. Make sure it's configured with your URL

### Issue: App shows "Telegram Required"
**Fix**: This is CORRECT when accessing via browser. Access through Telegram instead.

### Issue: User data not loading
**Fix**: 
1. Check if API server is running: `ps aux | grep uvicorn`
2. Check if database is connected
3. Check browser console for errors

### Issue: Bot doesn't respond
**Fix**:
1. Check if bot is running: `ps aux | grep telegram_bot`
2. Restart bot: `nohup python app/telegram_bot.py > bot.log 2>&1 &`
3. Check bot token in `.env` is correct

---

## 📚 Need More Help?

Read the full guides:
- **TELEGRAM_MINI_APP_SETUP.md** - Technical setup details
- **USER_GUIDE_TELEGRAM.md** - User instructions
- **README.md** - Project overview

---

## 🎉 You're Ready!

✅ Bot created
✅ Mini app configured  
✅ Menu button set
✅ Tested and working
✅ Ready to share!

**Start inviting users and watch them complete quests! 🚀**
