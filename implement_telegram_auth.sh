#!/bin/bash

# Telegram Mini App Authentication Setup Script
# This script helps implement Telegram-only authentication for the Gaming Quest Hub

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   🔐 TELEGRAM MINI APP AUTHENTICATION SETUP                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}This script will guide you through setting up Telegram-only authentication.${NC}"
echo ""

# Step 1: Check for bot token
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Verify Telegram Bot Token"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f .env ]; then
    if grep -q "TELEGRAM_BOT_TOKEN=" .env; then
        BOT_TOKEN=$(grep "TELEGRAM_BOT_TOKEN=" .env | cut -d '=' -f2)
        if [ -n "$BOT_TOKEN" ]; then
            echo -e "${GREEN}✓ Bot token found in .env${NC}"
        else
            echo -e "${RED}✗ Bot token is empty in .env${NC}"
            echo "  Please add your bot token to .env file"
            exit 1
        fi
    else
        echo -e "${RED}✗ TELEGRAM_BOT_TOKEN not found in .env${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ .env file not found${NC}"
    exit 1
fi

# Step 2: Check WebApp URL
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Configure WebApp URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if grep -q "WEBAPP_URL=" .env; then
    WEBAPP_URL=$(grep "WEBAPP_URL=" .env | cut -d '=' -f2)
    echo -e "${GREEN}✓ WebApp URL configured: $WEBAPP_URL${NC}"
else
    echo -e "${YELLOW}⚠ WEBAPP_URL not found in .env${NC}"
    echo ""
    echo "  Your current Codespaces URL is likely:"
    echo "  https://$(hostname)-8080.preview.app.github.dev"
    echo ""
    read -p "  Add this URL to .env now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        WEBAPP_URL="https://$(hostname)-8080.preview.app.github.dev"
        echo "WEBAPP_URL=$WEBAPP_URL" >> .env
        echo -e "${GREEN}✓ Added WEBAPP_URL to .env${NC}"
    fi
fi

# Step 3: Backup current files
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Backup Current Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p backups
cp frontend/index.html "backups/index.html.backup.$(date +%Y%m%d_%H%M%S)"
cp app/api.py "backups/api.py.backup.$(date +%Y%m%d_%H%M%S)"
cp app/telegram_bot.py "backups/telegram_bot.py.backup.$(date +%Y%m%d_%H%M%S)"

echo -e "${GREEN}✓ Backups created in ./backups/${NC}"

# Step 4: Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setup Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Configuration:"
echo "  Bot Token: ✓ Configured"
echo "  WebApp URL: $WEBAPP_URL"
echo "  Backups: ✓ Created"
echo ""
echo "Next Steps:"
echo "  1. Review TELEGRAM_AUTH_IMPLEMENTATION.md for details"
echo "  2. Update frontend/index.html to use Telegram WebApp SDK"
echo "  3. Add validation endpoint to app/api.py"
echo "  4. Update bot to provide WebApp button"
echo "  5. Test authentication flow"
echo ""
echo "Manual Implementation Required:"
echo "  The actual code changes need to be done manually following"
echo "  the guide in TELEGRAM_AUTH_IMPLEMENTATION.md"
echo ""
echo -e "${GREEN}Setup preparation complete!${NC}"
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   📖 Read TELEGRAM_AUTH_IMPLEMENTATION.md for full guide       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
