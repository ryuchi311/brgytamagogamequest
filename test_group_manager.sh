#!/bin/bash
echo "Testing Telegram Group Manager..."
echo ""
echo "This tool will help you:"
echo "✅ Add Telegram groups"
echo "✅ Store group details (ID, username, title, members)"
echo "✅ Export quest configurations"
echo ""
echo "To use:"
echo "  ./manage_groups.sh"
echo ""
echo "Example stored data:"
cat telegramgroups.example.json | jq '.'
