#!/bin/bash

# Start Telegram Group Manager Bot
# This bot manages groups via Telegram commands

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 Starting Telegram Group Manager Bot"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

# Check .env
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    exit 1
fi

# Check if python-telegram-bot is installed
echo "📦 Checking dependencies..."
if ! python3 -c "import telegram" 2>/dev/null; then
    echo "⚠️  python-telegram-bot not installed"
    echo "📥 Installing python-telegram-bot..."
    pip install python-telegram-bot --quiet
    if [ $? -eq 0 ]; then
        echo "✅ Installed successfully"
    else
        echo "❌ Failed to install. Please run manually:"
        echo "   pip install python-telegram-bot"
        exit 1
    fi
else
    echo "✅ Dependencies OK"
fi

echo ""
echo "🚀 Starting bot..."
echo ""

# Run bot
python3 telegram_group_bot.py
