# Auto-Save Enhancement Summary

## What We Added

### 1. Auto-Save Background Task
- **File**: `bot/tasks/background_tasks.py`
- **Function**: `auto_save_loop()`
- **Interval**: Every 5 minutes (configurable in `config.py`)
- **Behavior**: 
  - Only saves when there are active watch sessions
  - Prevents unnecessary file writes when idle
  - Includes smart logging (reduced spam)

### 2. Configuration
- **File**: `config.py`
- **Setting**: `AUTO_SAVE_INTERVAL_MINUTES = 5`
- **Purpose**: Configurable interval for auto-save frequency

### 3. Active Watch Status Command
- **Command**: `!activewatches`
- **Purpose**: Show current in-memory tracking sessions
- **Features**:
  - Lists all users currently being tracked
  - Shows watch duration and join position
  - Displays current movie
  - Shows auto-save interval info

### 4. Enhanced Manual Recovery
- **File**: `manual_recovery.py`
- **Purpose**: Manually start tracking if startup detection fails
- **Features**: Simulation mode with real user ID guidance

## How It Works

### Data Persistence Timeline

1. **Startup Detection** → Users added to `active_watches` (memory only)
2. **Auto-Save Task** → Every 5 minutes, saves user stats/badges (preserves progress)
3. **Session End** → Complete watch record saved to `watch_history.json`

### File Update Events

| Event | Files Updated | When |
|-------|---------------|------|
| `start_watching()` | None | Users added to memory only |
| `auto_save_loop()` | `user_stats.json`, `user_badges.json` | Every 5 min if active watches |
| `finish_watching()` | All 3 files | When user leaves or movie ends |
| Manual `!savedata` | All 3 files | On command |

### Memory vs Persistence

- **Memory Only**: `active_watches` (current tracking sessions)  
- **Persisted**: `user_stats`, `user_badges`, `watch_history`
- **Recovery**: Startup detection rebuilds `active_watches` from Plex

## Benefits

1. **Data Safety**: Progress saved every 5 minutes during active sessions
2. **Efficiency**: Only saves when necessary (active watchers present)
3. **Transparency**: `!activewatches` shows real-time status
4. **Recovery**: Manual tools if startup detection fails
5. **Configurable**: Easy to adjust save interval

## Commands for Users

- `!activewatches` - Show current tracking status
- `!savedata` - Manual save (admin only)
- `!starttracking` - Manual recovery (admin only)
- `!moviestats` - Show movie data (works with active sessions)

## Production Monitoring

The auto-save task logs:
- `💾 Auto-saved badge data (X active watches)` - Every save
- `⏭️ Auto-save skipped (no active watches)` - Occasionally when idle
- `❌ Auto-save failed: error` - On errors

This ensures your tracking data is preserved even if the bot crashes during active movie sessions!