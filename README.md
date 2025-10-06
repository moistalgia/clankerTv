# ClankerTV Discord Bot - Modular Structure

A horror movie marathon Discord bot with Plex integration, AI personality, and interactive movie queue management.

## 🏗️ Project Structure

```
clankerTV/
├── main.py              # Main entry point
├── config.py            # Configuration management
├── clankerTV.py         # Original monolithic file (legacy)
├── bot/
│   ├── __init__.py      # Bot package initialization
│   ├── bot_instance.py  # Bot instance creation
│   ├── commands/        # Command modules
│   │   ├── __init__.py
│   │   ├── movie_commands.py     # Movie browsing and requests
│   │   ├── playback_commands.py  # Playback control
│   │   └── ai_commands.py        # AI and personality
│   ├── events/          # Event handlers
│   │   ├── __init__.py
│   │   ├── message_handlers.py   # Message events and AI responses
│   │   └── voice_handlers.py     # Voice channel notifications
│   ├── tasks/           # Background tasks
│   │   ├── __init__.py
│   │   └── background_tasks.py   # Playlist refresh, playback monitoring
│   └── ui/              # Discord UI components
│       ├── __init__.py
│       ├── list_view.py          # Paginated movie lists
│       └── playback_view.py      # Playback controls
├── services/            # External service integrations
│   ├── __init__.py
│   ├── plex_service.py          # Plex Media Server operations
│   └── ai_service.py            # OpenAI integration
└── models/              # Data models and state
    ├── __init__.py
    └── movie_state.py           # Movie queue and state management
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Discord bot token
- Plex Media Server
- OpenAI API key
- qBittorrent (optional)

### Installation

1. **Install dependencies:**
   ```bash
   pip install discord.py plexapi openai qbittorrent-api requests
   ```

2. **Configure the bot:**
   - Edit `config.py` with your tokens and settings
   - Or set environment variables (recommended for production):
     ```bash
     export DISCORD_TOKEN="your_discord_token"
     export PLEX_TOKEN="your_plex_token"
     export OPENAI_API_KEY="your_openai_key"
     ```

3. **Run the bot:**
   ```bash
   python main.py
   ```

## 🎯 Features

### Movie Management
- Browse Plex horror movie library
- Interactive paginated movie lists
- Movie request system (doots)
- Automated queue management

### Playback Control
- Play/pause/restart controls
- Interactive Discord UI for movie controls
- Automatic subtitle downloading

### Horror Bingo Game 🎰
- **AI-Generated Cards:** Movie-specific tropes using OpenAI
- **Interactive UI:** 25-button Discord interface
- **Real-time Detection:** Automatic bingo line detection
- **Badge Integration:** Special achievement rewards
- **Persistent Progress:** Cards saved across bot restarts
- **Multi-user Support:** Each user gets unique cards

### Badge & Achievement System 🏆
- **25+ Unique Badges** across 6 categories
- **Automatic Tracking** of user progress
- **Gamification Elements** to encourage engagement
- **Leaderboards** and progress visualization
- **Data Persistence** with automatic backups
- Seek forward/backward
- Subtitle management
- Auto-advance to next movie

### AI Personality
- Configurable personality sliders (creepiness, humor, violence, mystery)
- Dynamic AI responses to chat messages
- Movie recommendations and analysis
- Threatening DMs for bot trigger words

### Background Tasks
- Automatic playlist refresh from Plex
- Playback monitoring and auto-advance
- Spontaneous creepy AI messages
- Voice channel join/leave notifications

## 🔧 Configuration

### Environment Variables (Recommended)
```bash
DISCORD_TOKEN=your_discord_bot_token
PLEX_TOKEN=your_plex_token
OPENAI_API_KEY=your_openai_api_key
QB_USER=your_qbittorrent_username
QB_PASS=your_qbittorrent_password
```

### Direct Configuration
Edit values in `config.py` (not recommended for production):
- Discord bot token and guild settings
- Plex server URL and authentication
- OpenAI API configuration
- qBittorrent connection details

## 📝 Commands

### Movie Commands
- `!list [query]` - Show horror movie playlist (filterable)
- `!listview` - Interactive paginated movie list
- `!doot <movie>` - Request a movie
- `/dootdoot` - Slash command with autocomplete
- `!dootlist` - Show pending requests
- `!seed <movie>` - Preload movie without voting

### Playbook Commands
- `!nowplaying` - Current movie with interactive controls
- `!timeleft` - Remaining time in current movie
- `!restart` - Restart current movie
- `!subtitles` - Download and apply subtitles
- `!clients` - List available Plex clients

### Horror Bingo 🎰
- `!bingo` - Create bingo card for current movie
- `!bingo <movie>` - Create bingo card for specific movie
- `!mybingo` - Show your current bingo card
- `!clearbingo` - Clear your current bingo card
- `!bingostats` - Show Horror Bingo statistics

### Movie History 📚
- `!history` - Show recent movies played by the bot
- `!history <user>` - Show movies watched by specific user
- `!moviestats` - Show comprehensive movie statistics
- `!topwatchers` - Show leaderboard of top watchers

### AI Commands
- `!lobotomize <settings>` - Adjust AI personality
- `!movieslike <movie>` - Get similar movie recommendations
- `!vibe <description>` - Get movies matching a vibe
- `!whatdidijustwatch [movie]` - Movie analysis and trivia
- `!catchmeup` - Get AI synopsis at current timestamp
- `!endinganalysis [movie]` - Deep dive into ending interpretations and theories

### Admin Commands
- `!play <movie>` - Force play a specific movie
- `!removedoot <movie>` - Remove specific request
- `!cleardoots` - Clear all requests
- `!start_marathon` - Begin marathon mode

## 🏛️ Architecture Benefits

### Modularity
- **Separation of Concerns:** Each module has a specific responsibility
- **Easy Testing:** Individual components can be tested in isolation
- **Maintainability:** Changes to one feature don't affect others

### Scalability
- **Service Layer:** External integrations are abstracted
- **State Management:** Centralized state with clear data models
- **Event Handling:** Organized event system with proper error handling

### Developer Experience
- **Type Hints:** Better IDE support and code clarity
- **Logging:** Comprehensive logging for debugging
- **Configuration:** Environment-based configuration for security
- **Documentation:** Clear docstrings and comments

## 🚦 Migration from Original

The original monolithic `clankerTV.py` file has been split into focused modules:

1. **Configuration** → `config.py`
2. **Commands** → `bot/commands/`
3. **Event Handlers** → `bot/events/`
4. **Background Tasks** → `bot/tasks/`
5. **UI Components** → `bot/ui/`
6. **Service Integrations** → `services/`
7. **Data Models** → `models/`

The bot functionality remains the same, but the code is now:
- More maintainable and readable
- Easier to test and debug
- Better organized for team development
- More secure with environment variable support

## 🎰 Horror Bingo System

### How It Works
1. **Generate Card:** Use `!bingo` or `!bingo <movie>` to create a personalized bingo card
2. **AI-Generated Tropes:** OpenAI creates 25 movie-specific horror tropes
3. **Interactive Play:** Click buttons in Discord to mark squares when tropes occur
4. **Real-time Bingo:** Automatic detection of completed lines (rows, columns, diagonals)
5. **Badge Rewards:** Earn "Horror Bingo Master" badge for your first bingo

### Example Horror Tropes
Different movies generate different tropes:
- **Slasher Films:** "Killer calls victim", "Car won't start", "Group splits up"
- **Supernatural:** "Lights flicker", "Voice whispers", "Mirror reflection"
- **Psychological:** "Reality questioned", "Unreliable narrator", "Mind games"

### Bingo Card Features
- **5x5 Grid:** 25 unique tropes per movie
- **Visual Progress:** Real-time completion tracking
- **Persistent Storage:** Cards saved across bot restarts
- **Multiple Lines:** Can complete multiple bingos per card
- **Clear Option:** Reset card anytime with confirmation

### Demo
Run the included demo to see how it works:
```bash
python demo_horror_bingo.py
```

## 🔍 Troubleshooting

```

### Common Issues

1. **Import Errors:** Ensure you're running from the project root directory
2. **Plex Connection:** Check Plex server URL and token
3. **Discord Permissions:** Verify bot has necessary permissions in your server
4. **Environment Variables:** Make sure all required variables are set

### Logging

The bot creates a `clanker.log` file with detailed information about:
- Service connections
- Command executions  
- Error messages
- Background task activities

## 🤝 Contributing

The modular structure makes it easy to contribute:

1. **Adding Commands:** Create new command files in `bot/commands/`
2. **New Services:** Add service classes in `services/`
3. **UI Components:** Create reusable UI elements in `bot/ui/`
4. **Background Tasks:** Add scheduled tasks in `bot/tasks/`

Each module is self-contained with clear interfaces and documentation.