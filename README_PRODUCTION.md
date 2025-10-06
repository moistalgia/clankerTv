# ClankerTV Discord Bot 🎬🤖

A sophisticated Discord bot for managing horror movie marathons with Plex integration, AI personality, and interactive features.

## ✨ Features

### 🎭 AI Personality System
- **Clanker**: A dark, knowledgeable horror AI with adjustable personality sliders
- Responds to horror movie discussions with witty, creepy commentary
- Personality traits: Creepiness, Humor, Violence, Mystery (0-10 scale)

### 🎬 Movie Management
- **Plex Integration**: Browse your horror movie library
- **Interactive Queue**: Vote on movies with doot system
- **Smart Recommendations**: AI-powered movie suggestions
- **Watch History**: Track viewing stats and user badges

### 🎮 Interactive Commands
- `!nextup` - Interactive movie voting polls
- `!list` / `!listview` - Browse movie library (text/interactive)
- `!catchmeup` - AI-generated plot summaries at current timestamp
- `!analyze` - Deep AI analysis of current movie
- `!personality` - Adjust Clanker's behavior

### 🏆 Gamification
- **Badge System**: Earn badges for movie activities
- **User Stats**: Track movies watched, votes cast, etc.
- **Horror Bingo**: Interactive horror trope bingo game

### 🎛️ Playback Control
- Real-time Plex playback monitoring
- Automatic notifications for movie start/end
- Timestamp-based AI summaries
- qBittorrent integration for downloads

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Discord Bot Token
- Plex Media Server
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd clankerTV
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (never commit this!):

```env
# Discord
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_discord_server_id
STREAM_CHANNEL_ID=your_voice_channel_id
NOTIFY_USER_ID=your_user_id

# Plex
PLEX_URL=http://localhost:32400
PLEX_TOKEN=your_plex_token
PLEX_LIBRARY=Movies

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# qBittorrent (optional)
QB_HOST=localhost:8080
QB_USER=admin
QB_PASS=your_password
DOWNLOAD_PATH=C:\Downloads\Movies
```

### Getting API Keys

#### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Create bot and copy token

#### Plex Token
1. Log into Plex Web UI
2. Go to Settings → Account → Privacy
3. Show Advanced → Get Token

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com)
2. Create account and add payment method
3. Go to API Keys section and create new key

## 📁 Project Structure

```
clankerTV/
├── main.py                    # Entry point
├── config_secure.py           # Secure configuration
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── bot/                      # Bot modules
│   ├── commands/             # Command handlers
│   │   ├── movie_commands.py      # Movie browsing/voting
│   │   ├── playback_commands.py   # Playback control
│   │   ├── ai_commands.py         # AI interactions
│   │   ├── utility_commands.py    # General utilities
│   │   └── badge_commands.py      # Badge system
│   ├── events/               # Event handlers
│   │   ├── message_handlers.py    # Chat monitoring
│   │   └── voice_handlers.py      # Voice events
│   ├── tasks/                # Background tasks
│   │   └── background_tasks.py    # Monitoring loops
│   └── ui/                   # Discord UI components
│       ├── list_view.py           # Paginated lists
│       ├── nextup_view.py         # Voting interface
│       └── playback_view.py       # Media controls
├── services/                 # Core services
│   ├── ai_service.py              # OpenAI integration
│   └── plex_service.py            # Plex API wrapper
├── models/                   # Data models
│   ├── movie_state.py             # Movie queue state
│   ├── badge_system.py           # User achievements
│   └── horror_bingo.py           # Bingo game logic
└── data/                     # Persistent data (git-ignored)
    ├── user_stats.json           # User statistics
    ├── watch_history.json        # Viewing history
    └── movie_ratings.json        # Movie ratings
```

## 🎯 Commands Reference

### Movie Commands
- `!list [query]` - List movies (with optional search)
- `!listview [query]` - Interactive paginated movie list
- `!next` - Show next movie in queue
- `!nextup` - Interactive voting poll for next movie
- `!play <title>` - Queue specific movie
- `!seed <title>` - Add movie to doot list
- `!removedoot <title>` - Remove from doot list
- `!cleardoots` - Clear all doot votes
- `!showdoots` - Show current doot list

### AI Commands
- `!ask <question>` - Ask Clanker about horror movies
- `!analyze` - AI analysis of current movie
- `!catchmeup` - Get plot summary up to current timestamp
- `!personality` - View/adjust personality sliders
- `!roast <movie>` - Get AI roast of a movie

### Utility Commands
- `!stats [user]` - View user statistics
- `!badges [user]` - View earned badges
- `!help` - Show command help
- `!fetch <magnet>` - Download torrent (if configured)
- `!status` - Show bot/service status

### Playback Commands
- `!current` - Show what's currently playing
- `!skip` - Skip current movie (admin only)
- `!pause` / `!resume` - Playback control

## 🛡️ Security Notes

- **Never commit** `.env` files or `config.py` with real tokens
- Use environment variables for all sensitive data
- The bot includes config validation to prevent startup with placeholder values
- Consider using Discord's slash commands for improved security

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Bot not responding**
- Check Discord token is valid
- Verify bot has proper permissions in server
- Check console for error messages

**Plex integration not working**
- Verify Plex server is running and accessible
- Check Plex token is valid
- Ensure library name matches exactly

**AI commands failing**
- Verify OpenAI API key is valid and has credits
- Check internet connection
- Review API usage limits

**qBittorrent integration issues**
- Ensure qBittorrent is running with Web UI enabled
- Check login credentials
- Verify download path exists and is writable

### Getting Help

1. Check the logs in `clanker.log`
2. Verify all environment variables are set correctly
3. Test individual components (Plex, OpenAI, Discord)
4. Open an issue with full error details

## 🎬 Enjoy Your Horror Movie Marathons! 🎭