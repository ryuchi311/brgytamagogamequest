#!/bin/bash
# Simple Docker run script for BRGY TAMAGO Quest Hub on port 8080

set -e

echo "🚀 Starting BRGY TAMAGO Quest Hub on port 8080..."
echo "=================================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Creating default..."
    cat > .env << 'ENVEOF'
# Database Configuration
DATABASE_URL=postgresql://user:pass@host/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key

# Application Secret
SECRET_KEY=dev-secret-key-change-in-production

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Twitter API (optional)
TWITTER_BEARER_TOKEN=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=
ENVEOF
    echo "✅ Created .env file. Please update it with your credentials!"
    echo ""
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.8080.yml down 2>/dev/null || true

# Build and start
echo "📦 Building Docker image..."
docker-compose -f docker-compose.8080.yml build

echo ""
echo "🚀 Starting container..."
docker-compose -f docker-compose.8080.yml up -d

echo ""
echo "✅ BRGY TAMAGO Quest Hub is running!"
echo "=================================================="
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:8080"
echo "   API: http://localhost:8080/api"
echo "   Health: http://localhost:8080/health"
echo ""
echo "📊 View logs:"
echo "   docker-compose -f docker-compose.8080.yml logs -f"
echo ""
echo "🛑 Stop the application:"
echo "   docker-compose -f docker-compose.8080.yml down"
echo ""
