# 🚀 Quick Start Guide

## Get Started in 5 Minutes!

### Step 1: Get Your Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Set Up Supabase (Free)

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Go to **SQL Editor** and run the contents of `database/schema.sql`
4. Go to **Settings** → **API** and copy:
   - Project URL
   - `anon` public key
   - `service_role` secret key

### Step 3: Configure Environment

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your credentials:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here
SECRET_KEY=generate_a_random_string_here
```

### Step 4: Run the Application

**Option A: Using Docker (Recommended)**
```bash
./setup.sh
```

**Option B: Manual Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Start API
python -m uvicorn app.api:app --reload --port 8000 &

# Start Telegram Bot
python app/telegram_bot.py &

# Start frontend (in another terminal)
cd frontend && python -m http.server 8080
```

### Step 5: Access the Application

- 🌐 **User Interface**: http://localhost (or http://localhost:8080)
- 🛠️ **Admin Dashboard**: http://localhost/admin
- 📚 **API Docs**: http://localhost:8000/docs
- 📱 **Telegram Bot**: Search your bot name on Telegram

### Step 6: Login to Admin Dashboard

Default credentials:
- Username: `admin`
- Password: `changeme123`

**⚠️ IMPORTANT: Change this password immediately!**

## First Steps After Setup

### 1. Create Your First Task

Go to Admin Dashboard → Tasks → Add Task:
- Title: "Follow us on Instagram"
- Description: "Follow our Instagram account"
- Task Type: Social Follow
- Platform: Instagram
- URL: Your Instagram URL
- Points Reward: 50
- Click "Create Task"

### 2. Create a Reward

Go to Admin Dashboard → Rewards → Add Reward:
- Title: "$5 Gift Card"
- Description: "Redeem for a $5 Amazon gift card"
- Reward Type: Gift Card
- Points Cost: 500
- Quantity: 10
- Click "Create Reward"

### 3. Test with Telegram

1. Open Telegram and search for your bot
2. Send `/start` to register
3. Send `/tasks` to see available tasks
4. Send `/profile` to check your points
5. Send `/rewards` to browse rewards

## 🎉 You're All Set!

Your Telegram bot points system is now running!

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- View API documentation at http://localhost:8000/docs
- Check logs: `docker-compose logs -f`

## Common Issues

**Bot not responding?**
- Make sure you copied the correct bot token
- Restart the bot: `docker-compose restart bot`

**Can't access admin dashboard?**
- Make sure services are running: `docker-compose ps`
- Check if port 80 is available

**Database connection error?**
- Verify your Supabase credentials
- Check if schema.sql was imported correctly

## Next Steps

1. ✅ Change admin password
2. ✅ Add more tasks
3. ✅ Configure rewards
4. ✅ Customize the frontend
5. ✅ Share your bot with users!

Happy building! 🚀
