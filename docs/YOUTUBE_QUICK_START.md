# YouTube Settings Columns - Quick Start Guide

## 🎯 What Was Added

5 new columns to the `tasks` table for YouTube quest settings:

```
┌─────────────────────────────┬──────────────┬────────────────────────────┐
│ Column Name                 │ Type         │ Purpose                    │
├─────────────────────────────┼──────────────┼────────────────────────────┤
│ youtube_video_id            │ VARCHAR(20)  │ Video ID (e.g., dQw4w9W..│
│ min_watch_time_seconds      │ INTEGER      │ Timer duration (30s)       │
│ video_duration_seconds      │ INTEGER      │ Total video length (180s)  │
│ verification_code           │ VARCHAR(100) │ Secret code (QUEST2025)    │
│ code_display_time_seconds   │ INTEGER      │ When code appears (15s)    │
└─────────────────────────────┴──────────────┴────────────────────────────┘
```

## 🚀 Quick Apply (3 Steps)

### Step 1: Copy the SQL
```bash
# View the migration file
cat database/migrations/003_youtube_settings_columns.sql
```

### Step 2: Open Supabase SQL Editor
1. Go to https://supabase.com/dashboard
2. Select your project
3. Click **"SQL Editor"** in left sidebar
4. Click **"New query"**

### Step 3: Run Migration
1. Paste the SQL from `003_youtube_settings_columns.sql`
2. Click **"Run"** button
3. ✅ Done!

## 📊 Visual Example

### Before Migration
```sql
CREATE TABLE tasks (
    id UUID,
    title VARCHAR(255),
    task_type VARCHAR(50),
    url TEXT,
    points_reward INTEGER,
    verification_data JSONB  -- ❌ Everything in JSON
);
```

### After Migration
```sql
CREATE TABLE tasks (
    id UUID,
    title VARCHAR(255),
    task_type VARCHAR(50),
    url TEXT,
    points_reward INTEGER,
    
    -- ✅ Dedicated YouTube columns
    youtube_video_id VARCHAR(20),
    min_watch_time_seconds INTEGER,
    video_duration_seconds INTEGER,
    verification_code VARCHAR(100),
    code_display_time_seconds INTEGER,
    
    verification_data JSONB  -- Still available
);
```

## 💡 Usage Example

### Creating a YouTube Quest

**Before (using JSONB):**
```python
task = {
    "title": "Watch Tutorial",
    "task_type": "youtube_watch",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "points_reward": 200,
    "verification_data": {  # ❌ Nested in JSON
        "method": "time_delay_code",
        "code": "QUEST2025",
        "min_watch_time_seconds": 30,
        "video_duration_seconds": 180,
        "code_display_time_seconds": 15
    }
}
```

**After (using dedicated columns):**
```python
task = {
    "title": "Watch Tutorial",
    "task_type": "youtube_watch",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "points_reward": 200,
    
    # ✅ Direct columns (type-safe, indexed, validated)
    "youtube_video_id": "dQw4w9WgXcQ",
    "min_watch_time_seconds": 30,
    "video_duration_seconds": 180,
    "verification_code": "QUEST2025",
    "code_display_time_seconds": 15
}
```

## 🎮 How It Works in Your App

### Admin Panel Flow
```
1. Admin creates YouTube quest
   ↓
2. Enters YouTube URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ↓
3. System auto-extracts video ID: dQw4w9WgXcQ
   ↓
4. Admin sets:
   - Min watch time: 30 seconds
   - Video duration: 180 seconds (3 minutes)
   - Verification code: QUEST2025
   - Code appears at: 15 seconds
   ↓
5. Data saved in dedicated columns ✅
```

### User Quest Flow
```
1. User opens YouTube quest
   ↓
2. Video loads using youtube_video_id
   ↓
3. Timer starts: min_watch_time_seconds (30s)
   ↓
4. Hint shown: "Code appears at 0:15"
   ↓
5. After 30s → Code input appears
   ↓
6. User enters: verification_code (QUEST2025)
   ↓
7. Correct code → Points awarded! 🎉
```

## 🔍 Verification After Migration

Run this SQL to check if columns were added:

```sql
SELECT column_name, data_type 
FROM information_schema.columns
WHERE table_name = 'tasks'
AND column_name IN (
    'youtube_video_id',
    'min_watch_time_seconds',
    'video_duration_seconds',
    'verification_code',
    'code_display_time_seconds'
)
ORDER BY column_name;
```

**Expected result (5 rows):**
```
✅ code_display_time_seconds  | integer
✅ min_watch_time_seconds     | integer
✅ verification_code          | character varying
✅ video_duration_seconds     | integer
✅ youtube_video_id           | character varying
```

## 📦 Files Created

```
✅ database/migrations/003_youtube_settings_columns.sql
   └─ Migration script to add columns

✅ database/schema.sql (updated)
   └─ Updated schema with new columns

✅ YOUTUBE_SETTINGS_COLUMNS.md
   └─ Full documentation

✅ YOUTUBE_COLUMNS_SUMMARY.md
   └─ Implementation summary

✅ apply_youtube_migration.sh
   └─ Helper script

✅ YOUTUBE_QUICK_START.md (this file)
   └─ Quick reference
```

## ⚡ Benefits

| Feature | Before (JSONB) | After (Columns) |
|---------|----------------|-----------------|
| **Type Safety** | ❌ No validation | ✅ Database types |
| **Queries** | ❌ JSON parsing | ✅ Direct SQL |
| **Indexes** | ❌ Generic | ✅ Specific |
| **Validation** | ❌ Application | ✅ Database |
| **Performance** | 🐢 Slower | 🚀 Faster |
| **IDE Support** | ❌ Limited | ✅ Full autocomplete |

## 🆘 Troubleshooting

### ❓ "Column already exists"
✅ Migration uses `IF NOT EXISTS` - safe to run multiple times

### ❓ "Constraint violation"
✅ Check that:
- `min_watch_time_seconds` >= 0
- `video_duration_seconds` > 0
- `code_display_time_seconds` <= `video_duration_seconds`

### ❓ "Can't connect to database"
✅ Use Supabase SQL Editor (no connection needed)

## 📚 Full Documentation

- **Complete Guide**: `YOUTUBE_SETTINGS_COLUMNS.md`
- **Summary**: `YOUTUBE_COLUMNS_SUMMARY.md`
- **Migration File**: `database/migrations/003_youtube_settings_columns.sql`

---

**Ready to apply?** → Copy SQL from `database/migrations/003_youtube_settings_columns.sql` and paste into Supabase SQL Editor

**Need help?** → See `YOUTUBE_SETTINGS_COLUMNS.md` for detailed instructions
