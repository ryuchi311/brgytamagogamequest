#!/bin/bash

# Script to apply social media username columns migration
# Run this to add twitter_username, instagram_username, discord_username columns

echo "🔄 Applying social media username migration..."
echo ""

# Check if Supabase CLI is available
if command -v supabase &> /dev/null; then
    echo "✅ Using Supabase CLI"
    supabase db push database/migrations/add_social_usernames.sql
else
    echo "⚠️ Supabase CLI not found. Please run the SQL manually in your Supabase dashboard."
    echo ""
    echo "📋 Steps to apply migration manually:"
    echo "1. Go to your Supabase project dashboard"
    echo "2. Navigate to SQL Editor"
    echo "3. Copy and paste the contents of database/migrations/add_social_usernames.sql"
    echo "4. Click 'Run' to execute the migration"
    echo ""
    echo "Or you can use psql:"
    echo "psql -h your-db-host -U postgres -d postgres -f database/migrations/add_social_usernames.sql"
fi

echo ""
echo "✅ Migration file location: database/migrations/add_social_usernames.sql"
