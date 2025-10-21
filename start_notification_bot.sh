#!/bin/bash

# Telegram Bot - Notification Only - Quick Start Script

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🤖 Telegram Notification Bot - Quick Start                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Please create .env file with:"
    echo "  TELEGRAM_BOT_TOKEN=your_token_here"
    echo "  WEBAPP_URL=your_webapp_url_here"
    exit 1
fi

# Check if TELEGRAM_BOT_TOKEN is set
if ! grep -q "TELEGRAM_BOT_TOKEN=" .env; then
    echo "❌ ERROR: TELEGRAM_BOT_TOKEN not found in .env!"
    echo "Add this line to .env:"
    echo "  TELEGRAM_BOT_TOKEN=your_token_here"
    exit 1
fi

# Check if WEBAPP_URL is set
if ! grep -q "WEBAPP_URL=" .env; then
    echo "⚠️  WARNING: WEBAPP_URL not found in .env!"
    echo "Add this line to .env:"
    echo "  WEBAPP_URL=your_webapp_url_here"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Environment check passed!"
echo ""

# Show menu
echo "Choose deployment option:"
echo ""
echo "1. Replace current bot (Recommended)"
echo "2. Run side-by-side with old bot (Testing)"
echo "3. Run directly (Development)"
echo "4. Cancel"
echo ""
read -p "Enter option (1-4): " option

case $option in
    1)
        echo ""
        echo "📦 Option 1: Replace current bot"
        echo ""
        
        # Backup old bot if exists
        if [ -f app/telegram_bot.py ]; then
            echo "💾 Backing up old bot..."
            cp app/telegram_bot.py app/telegram_bot_old.py
            echo "✅ Backup created: app/telegram_bot_old.py"
        fi
        
        # Copy new bot
        echo "📋 Copying new notification bot..."
        cp app/telegram_bot_notification_only.py app/telegram_bot.py
        echo "✅ New bot copied to app/telegram_bot.py"
        
        echo ""
        echo "🚀 Starting bot..."
        python -m app.telegram_bot
        ;;
        
    2)
        echo ""
        echo "📦 Option 2: Run side-by-side"
        echo ""
        echo "⚠️  Make sure old bot is still running!"
        echo "⚠️  This will start the new bot on the same token"
        echo "⚠️  Only one bot instance can run per token!"
        echo ""
        read -p "Are you sure? (y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        
        echo ""
        echo "🚀 Starting notification bot..."
        python app/telegram_bot_notification_only.py
        ;;
        
    3)
        echo ""
        echo "📦 Option 3: Run directly (Development)"
        echo ""
        echo "🚀 Starting bot in development mode..."
        python app/telegram_bot_notification_only.py
        ;;
        
    4)
        echo ""
        echo "👋 Cancelled."
        exit 0
        ;;
        
    *)
        echo ""
        echo "❌ Invalid option!"
        exit 1
        ;;
esac
