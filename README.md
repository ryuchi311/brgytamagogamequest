# 🎮 Quest Hub - Telegram Mini App# 🎯 Telegram Bot Points Rewards System



A gamified quest platform built with Telegram Mini Apps, featuring multiple quest types including Telegram group verification, Twitter follows, YouTube engagement, and website visits.A comprehensive web application for a Telegram bot that enables users to earn points through completing various tasks. Built with Python, FastAPI, and Supabase PostgreSQL.



## ✨ Features## 🌟 Features



- 🎯 **Multiple Quest Types**: Telegram groups, Twitter follows, YouTube engagement, website visits### User Features

- 👥 **User Management**: Authentication, profiles, and progress tracking- ✅ **Task Completion System** - Complete social media tasks, watch videos, and more

- 💎 **Points & Rewards System**: XP, loot rewards, and progression- 💰 **Points Tracking** - Earn and accumulate points for every task completed

- 📊 **Admin Dashboard**: Quest creation, user management, analytics- 🏆 **Leaderboard** - Compete with other users and see top performers

- 🏆 **Leaderboard**: Real-time rankings and competition- 🎁 **Rewards Redemption** - Redeem points for discounts, gift cards, and exclusive content

- 🎨 **Gaming-Themed UI**: Immersive user experience with branded colors- 🔔 **Real-time Notifications** - Get notified about new tasks and opportunities

- 🤖 **Telegram Bot Integration**: Automated verification and announcements- 📊 **Progress Tracking** - Monitor your points and completed tasks

- 📱 **Telegram Bot Integration** - Interact directly through Telegram

## 🚀 Quick Start

### 📦 Deployment

- The project now ships as a Docker image. Follow [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) to build and run locally.
- For local development you can still use `./start.sh` which spins up backend + frontend with auto-recovery logic.

### Admin Features

### Prerequisites- 📊 **Dashboard Analytics** - View system statistics and user metrics

- Python 3.9+- 👥 **User Management** - Monitor and manage user accounts

- Docker & Docker Compose- 📋 **Task Management** - Create, edit, and delete tasks

- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))- 🎁 **Reward Management** - Configure rewards and pricing

- Supabase Account (free tier available at [supabase.com](https://supabase.com))- ✅ **Task Verification** - Approve or reject user task submissions

- 🚫 **User Moderation** - Ban/unban users as needed

### Installation

## 🏗️ Architecture

1. **Clone and configure:**

```bash```

git clone <repository-url>├── app/

cd quest-hub│   ├── api.py              # FastAPI backend

cp .env.example .env│   ├── models.py           # Database models and Supabase client

# Edit .env with your credentials (see docs/QUICKSTART.md for details)│   └── telegram_bot.py     # Telegram bot implementation

```├── frontend/

│   ├── index.html          # User web interface

2. **Start services:**│   └── admin.html          # Admin dashboard

```bash├── database/

./start.sh│   └── schema.sql          # PostgreSQL database schema

```├── docker-compose.yml      # Docker orchestration

├── Dockerfile              # Docker container configuration

3. **Access the application:**├── requirements.txt        # Python dependencies

- **Frontend**: http://localhost:8080└── .env                    # Environment variables

- **Backend API**: http://localhost:8000```

- **API Docs**: http://localhost:8000/docs

## 🚀 Quick Start

### First-Time Setup

### Prerequisites

1. Create your Telegram bot with [@BotFather](https://t.me/BotFather)

2. Set up Supabase database (see [docs/DATABASE_ARCHITECTURE.md](./docs/DATABASE_ARCHITECTURE.md))- Docker and Docker Compose

3. Configure environment variables in `.env`- Python 3.11+

4. Run `./setup.sh` to initialize the database- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

5. Start services with `./start.sh`- Supabase Account (or local PostgreSQL)



For detailed setup instructions, see [docs/QUICKSTART.md](./docs/QUICKSTART.md).### Installation



## 🛠️ Management Scripts1. **Clone the repository**

```bash

| Script | Description | Usage |git clone <repository-url>

|--------|-------------|-------|cd telegram-bot-points-system

| `./start.sh` | Start all services with auto-recovery | `./start.sh [--monitor-logs]` |```

| `./stop.sh` | Stop all services gracefully | `./stop.sh` |

| `./restart.sh` | Restart with full diagnostics | `./restart.sh` |2. **Set up environment variables**

| `./check_status.sh` | Check system health | `./check_status.sh` |```bash

| `./monitor_logs.sh` | Monitor application logs | `./monitor_logs.sh [backend\|frontend\|both]` |cp .env.example .env

| `./manage_groups.sh` | Manage Telegram groups | `./manage_groups.sh` |```



See [docs/STARTUP_SCRIPTS_GUIDE.md](./docs/STARTUP_SCRIPTS_GUIDE.md) for detailed script documentation.Edit `.env` with your configuration:

```env

## 📖 Documentation# Telegram Bot Configuration

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

All documentation has been organized in the [docs/](./docs/) folder:

# Supabase Configuration

### 🏁 Getting StartedSUPABASE_URL=your_supabase_project_url

- [**Quick Start Guide**](./docs/QUICKSTART.md) - Get up and running in minutesSUPABASE_KEY=your_supabase_anon_key

- [**Quick Launch Checklist**](./docs/QUICK_LAUNCH_CHECKLIST.md) - Pre-deployment checklistSUPABASE_SERVICE_KEY=your_supabase_service_role_key

- [**Development Roadmap**](./docs/DEVELOPMENT_ROADMAP.md) - Project phases and milestones

- [**Project Structure**](./docs/PROJECT_STRUCTURE.md) - Codebase organization# Database Configuration

DATABASE_URL=postgresql://postgres:postgres@postgres:5432/telegram_bot_db

### 🎯 Quest Types & Implementation

- [**Quest Types Guide**](./docs/QUEST_TYPES_GUIDE.md) - Complete overview of all quest types# JWT Configuration

- [**Quest Handlers Implementation**](./docs/QUEST_HANDLERS_IMPLEMENTATION.md) - Backend logicSECRET_KEY=your_secret_key_change_in_production

- [**Quest Management Update**](./docs/QUEST_MANAGEMENT_UPDATE.md) - Admin quest managementALGORITHM=HS256

- [**TapSwap-Inspired Quests**](./docs/TAPSWAP_INSPIRED_QUESTS.md) - Gamification patternsACCESS_TOKEN_EXPIRE_MINUTES=30



### 📱 Telegram Integration# Admin Configuration

- [**Telegram Auth Quick Guide**](./docs/TELEGRAM_AUTH_QUICK_GUIDE.md) - Authentication setupADMIN_USERNAME=admin

- [**Telegram Verification Troubleshooting**](./docs/TELEGRAM_VERIFICATION_TROUBLESHOOTING.md) - Debug guideADMIN_PASSWORD=changeme123

- [**User Guide - Telegram**](./docs/USER_GUIDE_TELEGRAM.md) - User-facing documentation```

- [**Telegram Bot Setup**](./docs/TELEGRAM_BOT_SETUP_GUIDE.md) - Bot configuration

3. **Set up Supabase Database**

### 🐦 Twitter Integration

- [**Twitter API Setup**](./docs/TWITTER_API_SETUP.md) - API credentials and configurationOption A: Using Supabase Cloud

- [**Twitter API Setup Guide**](./docs/TWITTER_API_SETUP_GUIDE.md) - Step-by-step setup- Create a new project on [Supabase](https://supabase.com)

- [**Twitter Verification Methods**](./docs/TWITTER_VERIFICATION_METHODS.md) - Verification strategies- Go to SQL Editor and run the contents of `database/schema.sql`

- Copy your project URL and API keys to `.env`

### 📺 YouTube Integration

- [**YouTube Quick Start**](./docs/YOUTUBE_QUICK_START.md) - Get started with YouTube questsOption B: Using Local PostgreSQL (via Docker)

- [**YouTube Quest Workflow**](./docs/YOUTUBE_QUEST_WORKFLOW.md) - Complete workflow guide- The docker-compose.yml will automatically set up PostgreSQL

- [**YouTube Verification**](./docs/YOUTUBE_VERIFICATION.md) - Verification implementation- Schema will be automatically imported

- [**YouTube Debug Guide**](./docs/YOUTUBE_QUEST_DEBUG_GUIDE.md) - Troubleshooting

4. **Start the application**

### 🌐 Website Quests```bash

- [**Website Link Quest Workflow**](./docs/WEBSITE_LINK_QUEST_WORKFLOW.md) - Implementation guidedocker-compose up -d

- [**Website Quest Manual Verification**](./docs/WEBSITE_QUEST_MANUAL_VERIFICATION.md) - Manual verification```

- [**Website Link Quest Quick Reference**](./docs/WEBSITE_LINK_QUEST_QUICK_REFERENCE.md) - Quick guide

This will start:

### 👨‍💼 Administration- PostgreSQL database (port 5432)

- [**Admin Actions Implementation**](./docs/ADMIN_ACTIONS_IMPLEMENTATION.md) - Admin features- FastAPI backend (port 8000)

- [**Admin Dashboard Fix**](./docs/ADMIN_DASHBOARD_FIX.md) - Dashboard documentation- Telegram bot

- [**Admin Auth Fix**](./docs/ADMIN_AUTH_FIX.md) - Authentication implementation- Nginx web server (port 80)

- [**Quest Creation Update**](./docs/QUEST_CREATION_UPDATE.md) - Creating quests

5. **Access the application**

### 🔧 Operations & Troubleshooting- User Interface: http://localhost

- [**Startup Scripts Guide**](./docs/STARTUP_SCRIPTS_GUIDE.md) - Script documentation- Admin Dashboard: http://localhost/admin

- [**Log Monitoring Feature**](./docs/LOG_MONITORING_FEATURE.md) - Log monitoring guide- API Documentation: http://localhost:8000/docs

- [**System Status**](./docs/SYSTEM_STATUS.md) - Health monitoring- API Base URL: http://localhost:8000/api

- [**Debug Panel Guide**](./docs/DEBUG_PANEL_GUIDE.md) - Debugging tools

### Manual Setup (Without Docker)

### 🚀 Deployment

- [**Deployment Checklist**](./docs/DEPLOYMENT_CHECKLIST.md) - Pre-deployment steps1. **Install dependencies**

- [**Deployment Success**](./docs/DEPLOYMENT_SUCCESS.md) - Post-deployment verification```bash

- [**Supabase Fixes Required**](./docs/SUPABASE_FIXES_REQUIRED.md) - Database considerationspip install -r requirements.txt

```

### 🏗️ Architecture & Development

- [**Database Architecture**](./docs/DATABASE_ARCHITECTURE.md) - Database schema2. **Set up database**

- [**API Examples**](./docs/API_EXAMPLES.md) - API usage examples```bash

- [**Project Summary**](./docs/PROJECT_SUMMARY.txt) - High-level overview# Connect to your PostgreSQL database and run:

- [**Phase 2 Complete**](./docs/PHASE_2_COMPLETE.md) - Development phasespsql -U postgres -d telegram_bot_db -f database/schema.sql

- [**Phase 3 Complete**](./docs/PHASE_3_COMPLETE.md) - Recent updates```



### 📚 Quick References3. **Start the API server**

- [**Quick Reference - Mobile**](./docs/QUICK_REFERENCE_MOBILE.md) - Mobile optimization```bash

- [**Quick Access Guide**](./docs/QUICK_ACCESS_GUIDE.md) - Common taskspython -m uvicorn app.api:app --reload --port 8000

- [**Quest Handlers Quick Reference**](./docs/QUEST_HANDLERS_QUICK_REFERENCE.md) - Handler guide```



## 🏗️ Project Structure4. **Start the Telegram bot**

```bash

```python app/telegram_bot.py

quest-hub/```

├── app/                    # Backend API (FastAPI)

│   ├── api.py             # Main API endpoints5. **Serve frontend** (using Python's HTTP server)

│   └── models.py          # Data models```bash

├── frontend/              # Frontend (HTML/JS)cd frontend

│   ├── index.html         # Main apppython -m http.server 8080

│   ├── admin.html         # Admin dashboard```

│   └── assets/            # Static assets

├── bot/                   # Telegram bot## 📱 Telegram Bot Commands

│   ├── main.py            # Bot main logic

│   └── handlers/          # Command handlers- `/start` - Register and see main menu

├── docs/                  # Documentation- `/help` - Show help message with all commands

├── scripts/               # Utility scripts- `/tasks` - View available tasks

│   ├── start.sh           # Start services- `/profile` - View your profile and points

│   ├── stop.sh            # Stop services- `/leaderboard` - View top users

│   └── restart.sh         # Restart services- `/rewards` - Browse available rewards

└── docker-compose.yml     # Docker configuration

```## 🔧 Configuration



## 🔌 API Endpoints### Task Types



### User Endpoints- `social_follow` - Follow social media accounts

- `GET /api/tasks` - Get all available quests- `like_post` - Like posts

- `POST /api/tasks/:id/verify` - Verify quest completion- `share_post` - Share content

- `GET /api/users/:id` - Get user profile- `watch_video` - Watch videos

- `GET /api/leaderboard` - Get leaderboard rankings- `custom` - Custom tasks



### Admin Endpoints### Supported Platforms

- `POST /api/tasks` - Create new quest

- `PUT /api/tasks/:id` - Update quest- Instagram

- `DELETE /api/tasks/:id` - Delete quest- Twitter

- `GET /api/users` - List all users- Facebook

- YouTube

For complete API documentation, visit http://localhost:8000/docs after starting the services.- TikTok



## 🔍 System Health### Reward Types



Check system status anytime:- `discount` - Discount codes

```bash- `gift_card` - Gift cards

./check_status.sh- `exclusive_content` - Premium content access

```- `custom` - Custom rewards



Monitor logs in real-time:## 📊 API Documentation

```bash

./monitor_logs.sh both     # Monitor both backend and frontend### Authentication

./monitor_logs.sh backend  # Monitor backend only

./monitor_logs.sh frontend # Monitor frontend onlyAdmin endpoints require JWT authentication. Login to get a token:

```

```bash

Or start services with automatic log monitoring:POST /api/auth/login

```bash{

./start.sh --monitor-logs  "username": "admin",

```  "password": "changeme123"

}

## 🐛 Troubleshooting```



### Services won't start?Use the returned token in subsequent requests:

```bash```bash

./restart.sh  # Runs full diagnostics and cleanupAuthorization: Bearer <your_token>

``````



### Telegram verification issues?### Main Endpoints

```bash

./debug_telegram_verification.sh  # Interactive debugging#### Users

```- `GET /api/users` - Get all users

- `GET /api/users/{telegram_id}` - Get user by Telegram ID

### Need to check logs?- `GET /api/users/{telegram_id}/notifications` - Get user notifications

```bash

./monitor_logs.sh both  # Real-time log monitoring#### Tasks

```- `GET /api/tasks` - Get all active tasks

- `GET /api/tasks/{task_id}` - Get task details

For more troubleshooting guides, see:- `POST /api/tasks` - Create task (Admin)

- [Telegram Verification Troubleshooting](./docs/TELEGRAM_VERIFICATION_TROUBLESHOOTING.md)- `PUT /api/tasks/{task_id}` - Update task (Admin)

- [YouTube Debug Guide](./docs/YOUTUBE_QUEST_DEBUG_GUIDE.md)- `DELETE /api/tasks/{task_id}` - Delete task (Admin)

- [System Status Monitoring](./docs/SYSTEM_STATUS.md)

#### Rewards

## 🤝 Contributing- `GET /api/rewards` - Get all active rewards

- `POST /api/rewards` - Create reward (Admin)

We welcome contributions! Please see [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md) for guidelines on:- `PUT /api/rewards/{reward_id}` - Update reward (Admin)

- Code style and standards

- Pull request process#### Leaderboard

- Testing requirements- `GET /api/leaderboard` - Get top users

- Documentation updates

#### Admin

## 📄 License- `GET /api/admin/stats` - Get system statistics (Admin)

- `GET /api/admin/user-tasks` - Get user task submissions (Admin)

This project is licensed under the terms specified in [LICENSE](LICENSE).- `PUT /api/admin/user-tasks/{id}/verify` - Verify task (Admin)

- `PUT /api/admin/users/{id}/ban` - Ban/unban user (Admin)

## 🙏 Acknowledgments

Full API documentation available at: http://localhost:8000/docs

Built with:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework## 🗄️ Database Schema

- [Supabase](https://supabase.com/) - Open source Firebase alternative

- [Telegram Bot API](https://core.telegram.org/bots/api) - Bot platform### Main Tables

- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

- **users** - User accounts and points

---- **tasks** - Available tasks

- **user_tasks** - Task completion tracking

**Need help?** Check the [docs/](./docs/) folder or create an issue on GitHub.- **rewards** - Available rewards

- **user_rewards** - Redemption history
- **notifications** - User notifications
- **admin_users** - Administrator accounts
- **points_transactions** - Points transaction log
- **activity_logs** - User activity tracking

## 🔒 Security

### Admin Password

Default admin credentials:
- Username: `admin`
- Password: `changeme123`

**⚠️ IMPORTANT:** Change the admin password immediately after first login!

To create a new admin user:
```sql
INSERT INTO admin_users (username, password_hash, email, role)
VALUES ('newadmin', '$2b$12$...', 'admin@example.com', 'admin');
```

Use the `passlib` library to hash passwords:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("your_password")
```

### Security Best Practices

1. Use strong, unique passwords for admin accounts
2. Change the `SECRET_KEY` in production
3. Use HTTPS in production
4. Keep Supabase API keys secure
5. Regularly update dependencies
6. Enable rate limiting on API endpoints
7. Validate all user inputs

## 🚀 Deployment

### Deploy to Production

1. **Update environment variables**
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure production database URL
   - Set up proper TELEGRAM_WEBHOOK_URL

2. **Use a reverse proxy (Nginx/Caddy)**
   - Configure SSL certificates
   - Set up proper CORS policies

3. **Deploy options**
   - **Docker Compose** (Recommended)
   - **Kubernetes** (For scaling)
   - **Cloud Platforms** (AWS, Google Cloud, Azure)
   - **Heroku** / **Railway** / **Render**

### Environment-Specific Configuration

Create separate environment files:
- `.env.development`
- `.env.staging`
- `.env.production`

### Health Checks

The API includes a health check endpoint:
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-15T12:00:00"
}
```

## 📈 Monitoring & Logging

### Application Logs

Logs are output to stdout and can be viewed with:
```bash
docker-compose logs -f
```

### Database Monitoring

Monitor using Supabase dashboard or PostgreSQL tools:
```bash
docker-compose exec postgres psql -U postgres -d telegram_bot_db
```

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Manual Testing

1. Test Telegram bot by sending commands
2. Test API using Swagger UI: http://localhost:8000/docs
3. Test frontend by opening in browser

## 🔄 Updates & Maintenance

### Database Migrations

When updating the schema:
1. Create migration SQL file
2. Apply using Supabase dashboard or psql
3. Test thoroughly before production

### Backing Up Data

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres telegram_bot_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres telegram_bot_db < backup.sql
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: your-email@example.com

## 🎉 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Supabase](https://supabase.com/)
- Telegram Bot API: [python-telegram-bot](https://python-telegram-bot.org/)

## 📋 Roadmap

- [ ] Add email notifications
- [ ] Implement WebSocket for real-time updates
- [ ] Add more task types (surveys, referrals)
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Multilingual support
- [ ] Integration with more social platforms
- [ ] Automated task verification using APIs
- [ ] Gamification features (badges, levels)
- [ ] Export data functionality

## 🛠️ Troubleshooting

### Common Issues

**Bot not responding:**
- Check TELEGRAM_BOT_TOKEN is correct
- Verify bot is running: `docker-compose ps`
- Check logs: `docker-compose logs bot`

**Database connection errors:**
- Verify DATABASE_URL or SUPABASE_URL
- Check Supabase project is active
- Ensure network connectivity

**Admin login fails:**
- Verify admin credentials in database
- Check JWT SECRET_KEY configuration
- Clear browser cache/cookies

**Port already in use:**
```bash
# Find and kill process using port
lsof -ti:8000 | xargs kill -9
```

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Contact

For enterprise support or custom development:
- Email: support@example.com
- Website: https://example.com
- Telegram: @yourusername

---

Made with ❤️ by Your Name
