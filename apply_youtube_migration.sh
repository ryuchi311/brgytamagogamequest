#!/bin/bash

# YouTube Settings Migration Script
# Applies the 003_youtube_settings_columns.sql migration to Supabase

echo "🎬 YouTube Settings Columns Migration"
echo "======================================"
echo ""

# Check if migration file exists
if [ ! -f "database/migrations/003_youtube_settings_columns.sql" ]; then
    echo "❌ Error: Migration file not found!"
    echo "   Expected: database/migrations/003_youtube_settings_columns.sql"
    exit 1
fi

echo "📋 This migration will add the following columns to the tasks table:"
echo "   1. youtube_video_id (VARCHAR) - Auto-extracted video ID"
echo "   2. min_watch_time_seconds (INTEGER) - Minimum watch time"
echo "   3. video_duration_seconds (INTEGER) - Total video duration"
echo "   4. verification_code (VARCHAR) - Code for verification"
echo "   5. code_display_time_seconds (INTEGER) - When code appears"
echo ""

# Check for Supabase credentials
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "⚠️  Warning: SUPABASE_URL or SUPABASE_KEY not set"
    echo ""
    echo "📖 To apply this migration, you have 3 options:"
    echo ""
    echo "Option 1: Use Supabase SQL Editor (Recommended)"
    echo "  1. Go to https://supabase.com/dashboard"
    echo "  2. Select your project"
    echo "  3. Go to SQL Editor"
    echo "  4. Create a new query"
    echo "  5. Copy and paste: database/migrations/003_youtube_settings_columns.sql"
    echo "  6. Click 'Run'"
    echo ""
    echo "Option 2: Use psql Command Line"
    echo "  1. Get your connection string from Supabase Dashboard → Settings → Database"
    echo "  2. Run: psql 'postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres'"
    echo "  3. Copy and paste the migration SQL"
    echo ""
    echo "Option 3: Set environment variables and re-run this script"
    echo "  export SUPABASE_URL='https://[PROJECT].supabase.co'"
    echo "  export SUPABASE_KEY='your-service-role-key'"
    echo "  ./apply_youtube_migration.sh"
    echo ""
    
    # Display the migration file contents
    echo "📄 Migration file contents:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    cat database/migrations/003_youtube_settings_columns.sql
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ Copy the above SQL and paste it into Supabase SQL Editor"
    
else
    echo "✅ Supabase credentials found"
    echo "🔄 Attempting to apply migration..."
    echo ""
    
    # Note: Actual execution would require a database connection tool
    # For now, we'll display instructions
    echo "⚠️  Automatic migration not yet implemented"
    echo "📋 Please use Supabase SQL Editor to run the migration"
    echo ""
    echo "Migration file: database/migrations/003_youtube_settings_columns.sql"
fi

echo ""
echo "📚 For detailed documentation, see: YOUTUBE_SETTINGS_COLUMNS.md"
echo ""
