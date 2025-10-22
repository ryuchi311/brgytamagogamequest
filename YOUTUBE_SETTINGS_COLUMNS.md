# YouTube Settings Columns - Database Update

## Overview
The `tasks` table has been updated with dedicated columns for YouTube quest settings. This provides a structured way to store YouTube-specific data alongside the existing `verification_data` JSONB column.

## New Columns Added

### 1. **youtube_video_id** (VARCHAR(20))
- **Description**: Auto-extracted YouTube video ID
- **Example**: `dQw4w9WgXcQ` (from `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
- **Usage**: Automatically extracted when YouTube URL is provided
- **Nullable**: Yes (only required for YouTube quests)

### 2. **min_watch_time_seconds** (INTEGER)
- **Description**: Minimum time user must watch before code input appears
- **Example**: `120` (2 minutes)
- **Constraint**: Must be >= 0 if provided
- **Default**: NULL
- **Usage**: Timer duration before showing code input field

### 3. **video_duration_seconds** (INTEGER)
- **Description**: Total duration of the YouTube video
- **Example**: `300` (5 minutes)
- **Constraint**: Must be > 0 if provided
- **Default**: NULL
- **Usage**: For progress tracking and validation

### 4. **verification_code** (VARCHAR(100))
- **Description**: Code shown in video that user must enter to verify watching
- **Example**: `"QUEST2025"`, `"SECRET_CODE"`, `"WATCH_ME"`
- **Default**: NULL
- **Usage**: User enters this code after watching to claim reward

### 5. **code_display_time_seconds** (INTEGER)
- **Description**: Timestamp in video when verification code is displayed
- **Example**: `30` (code appears at 0:30 in the video)
- **Constraint**: Must be >= 0 and <= video_duration_seconds
- **Default**: NULL
- **Usage**: Hint for users where to find the code

## Database Constraints

### Validation Rules
```sql
-- Minimum watch time must be non-negative
CHECK (min_watch_time_seconds IS NULL OR min_watch_time_seconds >= 0)

-- Video duration must be positive
CHECK (video_duration_seconds IS NULL OR video_duration_seconds > 0)

-- Code display time must be non-negative
CHECK (code_display_time_seconds IS NULL OR code_display_time_seconds >= 0)

-- Code display time cannot exceed video duration
CHECK (
    code_display_time_seconds IS NULL 
    OR video_duration_seconds IS NULL 
    OR code_display_time_seconds <= video_duration_seconds
)
```

### Indexes
- `idx_tasks_youtube_video_id` - Fast lookups by video ID
- `idx_tasks_with_verification_code` - Fast lookups for tasks with verification codes

## Migration Instructions

### Apply Migration to Supabase

**Option 1: Using Supabase SQL Editor**
1. Go to your Supabase Dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `database/migrations/003_youtube_settings_columns.sql`
4. Click "Run"

**Option 2: Using psql Command Line**
```bash
# Set your Supabase connection string
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres"

# Run the migration
psql $DATABASE_URL -f database/migrations/003_youtube_settings_columns.sql
```

**Option 3: Using Supabase CLI**
```bash
# If you have Supabase CLI installed
supabase db push
```

## Usage Examples

### Creating a YouTube Quest (Admin Panel)

**Using the Admin Panel:**
When creating a YouTube quest, fill in the YouTube Settings section:
- **YouTube URL**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- **Minimum Watch Time**: `30` seconds
- **Video Duration**: `180` seconds
- **Verification Code**: `QUEST2025`
- **Code Display Time**: `15` seconds (appears at 0:15)

**Direct SQL Insert:**
```sql
INSERT INTO tasks (
    title,
    description,
    task_type,
    platform,
    url,
    points_reward,
    youtube_video_id,
    min_watch_time_seconds,
    video_duration_seconds,
    verification_code,
    code_display_time_seconds,
    is_active
) VALUES (
    'Watch Tutorial Video',
    'Watch our tutorial video and enter the secret code',
    'youtube_watch',
    'youtube',
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    200,
    'dQw4w9WgXcQ',  -- Auto-extracted
    30,              -- 30 seconds minimum watch time
    180,             -- 3 minutes total duration
    'QUEST2025',     -- Verification code
    15,              -- Code appears at 0:15
    true
);
```

### Using API (Python/FastAPI)

**Update the TaskCreate model:**
```python
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str
    platform: Optional[str] = None
    url: Optional[str] = None
    points_reward: int
    
    # YouTube Settings
    youtube_video_id: Optional[str] = None
    min_watch_time_seconds: Optional[int] = None
    video_duration_seconds: Optional[int] = None
    verification_code: Optional[str] = None
    code_display_time_seconds: Optional[int] = None
    
    verification_data: Optional[dict] = None
    is_active: Optional[bool] = True
```

**Update the TaskResponse model:**
```python
class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    task_type: str
    platform: Optional[str]
    url: Optional[str]
    points_reward: int
    
    # YouTube Settings
    youtube_video_id: Optional[str] = None
    min_watch_time_seconds: Optional[int] = None
    video_duration_seconds: Optional[int] = None
    verification_code: Optional[str] = None
    code_display_time_seconds: Optional[int] = None
    
    verification_data: Optional[dict] = None
    is_active: bool
```

**Creating a task via API:**
```python
@app.post("/api/tasks")
async def create_task(task: TaskCreate):
    # Auto-extract YouTube video ID from URL
    if task.url and 'youtube.com/watch?v=' in task.url:
        task.youtube_video_id = task.url.split('v=')[1].split('&')[0]
    
    # Insert into database
    result = supabase.table("tasks").insert({
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type,
        "platform": task.platform,
        "url": task.url,
        "points_reward": task.points_reward,
        "youtube_video_id": task.youtube_video_id,
        "min_watch_time_seconds": task.min_watch_time_seconds,
        "video_duration_seconds": task.video_duration_seconds,
        "verification_code": task.verification_code,
        "code_display_time_seconds": task.code_display_time_seconds,
        "verification_data": task.verification_data,
        "is_active": task.is_active
    }).execute()
    
    return result.data[0]
```

## Frontend Integration

### Displaying YouTube Settings in Quest Details
```javascript
function displayYouTubeQuest(task) {
    const questHtml = `
        <div class="quest-details">
            <h2>${task.title}</h2>
            <p>${task.description}</p>
            
            <!-- YouTube Video -->
            <iframe 
                src="https://www.youtube.com/embed/${task.youtube_video_id}"
                width="100%" 
                height="315" 
                frameborder="0"
            ></iframe>
            
            <!-- Instructions -->
            <div class="instructions">
                <p>⏱️ Watch for at least ${task.min_watch_time_seconds} seconds</p>
                <p>💡 The verification code appears at ${formatTime(task.code_display_time_seconds)}</p>
                <p>🎥 Total video duration: ${formatTime(task.video_duration_seconds)}</p>
            </div>
            
            <!-- Timer (shows after clicking Watch) -->
            <div id="timer" class="hidden"></div>
            
            <!-- Code Input (shows after timer) -->
            <div id="codeInput" class="hidden">
                <input type="text" placeholder="Enter verification code" />
                <button onclick="submitCode()">Submit</button>
            </div>
        </div>
    `;
    
    document.getElementById('questContainer').innerHTML = questHtml;
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}
```

## Backward Compatibility

### verification_data JSONB Column
The existing `verification_data` JSONB column is **still supported** for:
- Flexibility for other verification methods
- Storing additional metadata
- Complex verification logic

**You can use both approaches:**
```python
# Option 1: Use dedicated columns (recommended for YouTube)
task.youtube_video_id = "dQw4w9WgXcQ"
task.min_watch_time_seconds = 30
task.verification_code = "SECRET"

# Option 2: Use JSONB (still works)
task.verification_data = {
    "method": "time_delay_code",
    "code": "SECRET",
    "min_watch_time_seconds": 30
}

# Option 3: Use both (most comprehensive)
# Dedicated columns for quick queries
# JSONB for additional metadata
```

## Query Examples

### Find all YouTube quests with codes
```sql
SELECT id, title, youtube_video_id, verification_code, points_reward
FROM tasks
WHERE verification_code IS NOT NULL
AND task_type = 'youtube_watch'
AND is_active = true;
```

### Find quests by video ID
```sql
SELECT * FROM tasks
WHERE youtube_video_id = 'dQw4w9WgXcQ';
```

### Find quests with short watch time (< 1 minute)
```sql
SELECT title, min_watch_time_seconds, points_reward
FROM tasks
WHERE min_watch_time_seconds < 60
AND task_type = 'youtube_watch';
```

## Benefits of Dedicated Columns

### ✅ Advantages
1. **Type Safety**: Integer/VARCHAR types vs. JSON parsing
2. **Direct SQL Queries**: Easy filtering and indexing
3. **Database Validation**: Constraints enforce data integrity
4. **Better Performance**: Indexes on specific columns
5. **Clearer Schema**: Self-documenting structure
6. **IDE Support**: Better autocomplete and type hints

### 🔄 When to Use JSONB Instead
- Complex nested data structures
- Frequently changing verification methods
- Additional metadata that doesn't warrant a column
- Temporary experimental features

## Verification

### Check if migration was successful
```sql
-- List all YouTube-related columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'tasks'
AND column_name LIKE '%youtube%' 
   OR column_name LIKE '%watch%'
   OR column_name LIKE '%video%'
   OR column_name LIKE '%verification_code%'
   OR column_name LIKE '%code_display%';
```

### Expected Output
```
column_name              | data_type         | is_nullable
------------------------|-------------------|-------------
youtube_video_id        | character varying | YES
min_watch_time_seconds  | integer           | YES
video_duration_seconds  | integer           | YES
verification_code       | character varying | YES
code_display_time_seconds| integer          | YES
```

## Next Steps

1. ✅ Apply migration to Supabase database
2. ✅ Update API models (TaskCreate, TaskResponse)
3. ✅ Update admin panel form to include new fields
4. ✅ Update frontend to display YouTube settings
5. ✅ Test creating YouTube quests with new columns
6. ✅ Verify constraints and indexes work correctly

---

**Migration File**: `database/migrations/003_youtube_settings_columns.sql`
**Schema File**: `database/schema.sql` (updated)
**Created**: October 21, 2025
