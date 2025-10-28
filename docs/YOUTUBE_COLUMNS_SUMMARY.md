# YouTube Settings Database Columns - Implementation Complete ✅

## Summary

Successfully added 5 dedicated columns to the `tasks` table for YouTube quest settings, providing a structured and type-safe way to store YouTube-specific data.

## New Database Columns

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| `youtube_video_id` | VARCHAR(20) | Auto-extracted YouTube video ID | `dQw4w9WgXcQ` |
| `min_watch_time_seconds` | INTEGER | Minimum watch time before code input | `30` |
| `video_duration_seconds` | INTEGER | Total video duration | `180` |
| `verification_code` | VARCHAR(100) | Code shown in video for verification | `QUEST2025` |
| `code_display_time_seconds` | INTEGER | When code appears in video | `15` |

## Files Created/Updated

### ✅ New Files
1. **`database/migrations/003_youtube_settings_columns.sql`**
   - Complete migration script with:
     - Column additions with IF NOT EXISTS checks
     - Data validation constraints
     - Indexes for performance
     - Helpful comments

2. **`YOUTUBE_SETTINGS_COLUMNS.md`**
   - Comprehensive documentation with:
     - Column descriptions and examples
     - Database constraints
     - Migration instructions (3 methods)
     - Usage examples (SQL, Python, JavaScript)
     - Query examples
     - Backward compatibility guide

3. **`apply_youtube_migration.sh`**
   - Helper script to apply migration
   - Displays instructions for Supabase SQL Editor
   - Shows migration file contents

### ✅ Updated Files
4. **`database/schema.sql`**
   - Updated tasks table definition
   - Added all 5 YouTube columns
   - Added validation constraints
   - Maintained backward compatibility

## Data Validation & Constraints

### Automatic Checks
```sql
✅ min_watch_time_seconds >= 0 (non-negative)
✅ video_duration_seconds > 0 (positive)
✅ code_display_time_seconds >= 0 (non-negative)
✅ code_display_time_seconds <= video_duration_seconds (logical)
```

### Database Indexes
```sql
✅ idx_tasks_youtube_video_id - Fast lookups by video ID
✅ idx_tasks_with_verification_code - Fast lookups for verification codes
```

## How to Apply Migration

### Method 1: Supabase SQL Editor (Recommended) ⭐
```
1. Go to https://supabase.com/dashboard
2. Select your project
3. Navigate to SQL Editor
4. Create new query
5. Copy contents of: database/migrations/003_youtube_settings_columns.sql
6. Click "Run"
```

### Method 2: Using the Helper Script
```bash
./apply_youtube_migration.sh
# This will display the SQL and instructions
```

### Method 3: Direct psql
```bash
# Get connection string from Supabase Dashboard
psql 'postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres' \
  -f database/migrations/003_youtube_settings_columns.sql
```

## Usage Example

### Creating a YouTube Quest
```python
# API endpoint example
POST /api/tasks
{
    "title": "Watch Our Tutorial",
    "description": "Watch and enter the code",
    "task_type": "youtube_watch",
    "platform": "youtube",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "points_reward": 200,
    
    # New YouTube Settings ⬇️
    "youtube_video_id": "dQw4w9WgXcQ",  # Auto-extracted
    "min_watch_time_seconds": 30,       # 30 second timer
    "video_duration_seconds": 180,      # 3 minutes total
    "verification_code": "QUEST2025",   # Secret code
    "code_display_time_seconds": 15,    # Code at 0:15
    
    "is_active": true
}
```

### Frontend Display
```javascript
// Display YouTube quest details
function showYouTubeQuest(task) {
    console.log(`Video ID: ${task.youtube_video_id}`);
    console.log(`Watch for: ${task.min_watch_time_seconds} seconds`);
    console.log(`Code appears at: ${task.code_display_time_seconds}s`);
    console.log(`Enter code: ${task.verification_code}`);
}
```

## Benefits

### ✅ Type Safety
- Integer types ensure numeric values
- VARCHAR prevents data overflow
- Database-level validation

### ✅ Performance
- Dedicated indexes for fast queries
- No JSON parsing required
- Efficient filtering and sorting

### ✅ Data Integrity
- Constraints prevent invalid data
- Logical checks (e.g., code time < video duration)
- Self-documenting schema

### ✅ Developer Experience
- Clear column names
- IDE autocomplete support
- Better error messages

### ✅ Backward Compatible
- `verification_data` JSONB still works
- Can use both approaches
- No breaking changes

## Verification Steps

After applying the migration, verify with:

```sql
-- Check if columns exist
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'tasks'
AND (
    column_name = 'youtube_video_id'
    OR column_name = 'min_watch_time_seconds'
    OR column_name = 'video_duration_seconds'
    OR column_name = 'verification_code'
    OR column_name = 'code_display_time_seconds'
)
ORDER BY column_name;
```

Expected output:
```
column_name              | data_type         | is_nullable
------------------------|-------------------|-------------
code_display_time_seconds| integer          | YES
min_watch_time_seconds  | integer           | YES
verification_code       | character varying | YES
video_duration_seconds  | integer           | YES
youtube_video_id        | character varying | YES
```

## Next Steps

### 1. Apply Migration ⬅️ START HERE
Run the migration in Supabase SQL Editor

### 2. Update API Models
Update `app/api.py`:
```python
class TaskCreate(BaseModel):
    # ... existing fields ...
    youtube_video_id: Optional[str] = None
    min_watch_time_seconds: Optional[int] = None
    video_duration_seconds: Optional[int] = None
    verification_code: Optional[str] = None
    code_display_time_seconds: Optional[int] = None

class TaskResponse(BaseModel):
    # ... existing fields ...
    youtube_video_id: Optional[str] = None
    min_watch_time_seconds: Optional[int] = None
    video_duration_seconds: Optional[int] = None
    verification_code: Optional[str] = None
    code_display_time_seconds: Optional[int] = None
```

### 3. Update Admin Panel
Add form fields for YouTube settings in admin panel

### 4. Update Frontend
Display YouTube settings in quest detail pages

### 5. Test
Create a YouTube quest with the new columns and verify it works

## Support

### Documentation
- **Full Guide**: `YOUTUBE_SETTINGS_COLUMNS.md`
- **Migration File**: `database/migrations/003_youtube_settings_columns.sql`
- **Schema**: `database/schema.sql`

### Quick Reference
```bash
# View migration
cat database/migrations/003_youtube_settings_columns.sql

# View documentation
cat YOUTUBE_SETTINGS_COLUMNS.md

# Run helper script
./apply_youtube_migration.sh
```

---

**Status**: ✅ Ready to apply
**Created**: October 21, 2025
**Migration**: `003_youtube_settings_columns.sql`
