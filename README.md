# 🎯 Telegram Bot Points Rewards System

A comprehensive web application for a Telegram bot that enables users to earn points through completing various tasks. Built with Python, FastAPI, and Supabase PostgreSQL.

## 🌟 Features

### User Features
- ✅ **Task Completion System** - Complete social media tasks, watch videos, and more
- 💰 **Points Tracking** - Earn and accumulate points for every task completed
- 🏆 **Leaderboard** - Compete with other users and see top performers
- 🎁 **Rewards Redemption** - Redeem points for discounts, gift cards, and exclusive content
- 🔔 **Real-time Notifications** - Get notified about new tasks and opportunities
- 📊 **Progress Tracking** - Monitor your points and completed tasks
- 📱 **Telegram Bot Integration** - Interact directly through Telegram

### Admin Features
- 📊 **Dashboard Analytics** - View system statistics and user metrics
- 👥 **User Management** - Monitor and manage user accounts
- 📋 **Task Management** - Create, edit, and delete tasks
- 🎁 **Reward Management** - Configure rewards and pricing
- ✅ **Task Verification** - Approve or reject user task submissions
- 🚫 **User Moderation** - Ban/unban users as needed

## 🏗️ Architecture

```
├── app/
│   ├── api.py              # FastAPI backend
│   ├── models.py           # Database models and Supabase client
│   └── telegram_bot.py     # Telegram bot implementation
├── frontend/
│   ├── index.html          # User web interface
│   └── admin.html          # Admin dashboard
├── database/
│   └── schema.sql          # PostgreSQL database schema
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Docker container configuration
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Supabase Account (or local PostgreSQL)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd telegram-bot-points-system
```

2. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/telegram_bot_db

# JWT Configuration
SECRET_KEY=your_secret_key_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme123
```

3. **Set up Supabase Database**

Option A: Using Supabase Cloud
- Create a new project on [Supabase](https://supabase.com)
- Go to SQL Editor and run the contents of `database/schema.sql`
- Copy your project URL and API keys to `.env`

Option B: Using Local PostgreSQL (via Docker)
- The docker-compose.yml will automatically set up PostgreSQL
- Schema will be automatically imported

4. **Start the application**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- FastAPI backend (port 8000)
- Telegram bot
- Nginx web server (port 80)

5. **Access the application**
- User Interface: http://localhost
- Admin Dashboard: http://localhost/admin
- API Documentation: http://localhost:8000/docs
- API Base URL: http://localhost:8000/api

### Manual Setup (Without Docker)

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up database**
```bash
# Connect to your PostgreSQL database and run:
psql -U postgres -d telegram_bot_db -f database/schema.sql
```

3. **Start the API server**
```bash
python -m uvicorn app.api:app --reload --port 8000
```

4. **Start the Telegram bot**
```bash
python app/telegram_bot.py
```

5. **Serve frontend** (using Python's HTTP server)
```bash
cd frontend
python -m http.server 8080
```

## 📱 Telegram Bot Commands

- `/start` - Register and see main menu
- `/help` - Show help message with all commands
- `/tasks` - View available tasks
- `/profile` - View your profile and points
- `/leaderboard` - View top users
- `/rewards` - Browse available rewards

## 🔧 Configuration

### Task Types

- `social_follow` - Follow social media accounts
- `like_post` - Like posts
- `share_post` - Share content
- `watch_video` - Watch videos
- `custom` - Custom tasks

### Supported Platforms

- Instagram
- Twitter
- Facebook
- YouTube
- TikTok

### Reward Types

- `discount` - Discount codes
- `gift_card` - Gift cards
- `exclusive_content` - Premium content access
- `custom` - Custom rewards

## 📊 API Documentation

### Authentication

Admin endpoints require JWT authentication. Login to get a token:

```bash
POST /api/auth/login
{
  "username": "admin",
  "password": "changeme123"
}
```

Use the returned token in subsequent requests:
```bash
Authorization: Bearer <your_token>
```

### Main Endpoints

#### Users
- `GET /api/users` - Get all users
- `GET /api/users/{telegram_id}` - Get user by Telegram ID
- `GET /api/users/{telegram_id}/notifications` - Get user notifications

#### Tasks
- `GET /api/tasks` - Get all active tasks
- `GET /api/tasks/{task_id}` - Get task details
- `POST /api/tasks` - Create task (Admin)
- `PUT /api/tasks/{task_id}` - Update task (Admin)
- `DELETE /api/tasks/{task_id}` - Delete task (Admin)

#### Rewards
- `GET /api/rewards` - Get all active rewards
- `POST /api/rewards` - Create reward (Admin)
- `PUT /api/rewards/{reward_id}` - Update reward (Admin)

#### Leaderboard
- `GET /api/leaderboard` - Get top users

#### Admin
- `GET /api/admin/stats` - Get system statistics (Admin)
- `GET /api/admin/user-tasks` - Get user task submissions (Admin)
- `PUT /api/admin/user-tasks/{id}/verify` - Verify task (Admin)
- `PUT /api/admin/users/{id}/ban` - Ban/unban user (Admin)

Full API documentation available at: http://localhost:8000/docs

## 🗄️ Database Schema

### Main Tables

- **users** - User accounts and points
- **tasks** - Available tasks
- **user_tasks** - Task completion tracking
- **rewards** - Available rewards
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
