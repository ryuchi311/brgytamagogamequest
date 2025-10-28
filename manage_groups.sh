#!/bin/bash

# Telegram Group Manager - Easy wrapper script

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 Telegram Group Manager"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "   Please create .env with TELEGRAM_BOT_TOKEN"
    exit 1
fi

# Run the Python script
python3 manage_telegram_groups.py
