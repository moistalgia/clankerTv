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
- `!lobotomize` - Adjust Clanker's personality traits
- `!bingo` - Interactive horror movie bingo game

### 🏆 Gamification
- **Badge System**: Earn badges for movie activities
- **User Stats**: Track movies watched, votes cast, etc.
- **Horror Bingo**: Interactive horror trope bingo game

### 🎃 October Horror Experience
- **Progressive Corruption**: Clanker's AI deteriorates throughout October
- **Spontaneous Events**: Random corruption manifestations with cinematic effects
- **Recovery System**: Interactive minigames to combat the decay
- **ARG Elements**: Hidden fragments and mysterious transmissions

### 🎛️ Playback Control
- Real-time Plex playback monitoring
- Automatic notifications for movie start/end
- Timestamp-based AI summaries
- qBittorrent integration for downloads

## ⚠️ Important Disclaimers

### 🎥 Discord Streaming Compliance
**This bot does NOT stream content directly.** To comply with Discord's Terms of Service:
- The bot **controls** a Discord user account that manually streams via screen share
- **You** are responsible for manually starting Discord streaming
- The bot only **coordinates** and **monitors** what you're already streaming
- All content streaming is done through **your** Discord account, not the bot

### 🖥️ Supported Plex Clients
The bot **only works with specific Plex clients** that support proper session reporting:
- ✅ **Plex Media Player** (Desktop)
- ✅ **Roku** Plex app
- ✅ **Apple TV** Plex app
- ✅ **Smart TV** apps (Samsung, LG, etc.)
- ❌ **Web Player** (limited session data)
- ❌ **Mobile apps** (inconsistent reporting)

### 🎬 Discord Streaming Setup
For Discord streaming compatibility, you need **Plex Media Player**:
1. **Download older installer**: [Plex Media Player v2.58.0](https://downloads.plex.tv/plexmediaplayer/) (or compatible version)
2. **Install on streaming computer**
3. **Configure for fullscreen playback**
4. **Use Discord screen share** to stream to your server

### 🚨 Torrent Security Warning
**The `!fetch` command has NO input sanitization:**
- ⚠️ **Only provide access to trusted users**
- ⚠️ **Malicious magnets can download malware**
- ⚠️ **No content filtering** (could download inappropriate material)
- ⚠️ **Downloads directly to your system**
- 🔒 **Consider disabling if unsure** (comment out in utility_commands.py)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Discord Bot Token
- Plex Media Server
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/moistalgia/clankerTv.git
   cd clankerTv
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
   # Windows
   copy .env.example .env
   # Linux/Mac
   cp .env.example .env
   
   # Edit .env with your actual values using any text editor
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```
   
   **Note:** If running without virtual environment, you may need:
   ```bash
   pip install python-dotenv
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

### ⚡ Slash Commands (Recommended)
*Modern Discord commands with autocomplete and better UX*

**Movie Commands:**
- `/play <title>` - Play specific movie immediately (with autocomplete)
- `/doot <title>` - Vote for a movie (with playlist autocomplete)
- `/dootlist` - Show current voting results
- `/undoot <title>` - Remove your vote from a movie (with autocomplete)
- `/seed <title>` - Preload movie into dootlist without voting (with autocomplete)
- `/list [query]` - Browse movie collection with search (with autocomplete)

**AI Analysis:**
- `/movieslike <movie>` - Get similar horror movie suggestions (flexible autocomplete)
- `/whatdidijustwatch [movie]` - Get AI analysis and facts about a movie (with autocomplete)
- `/endinganalysis [movie]` - Deep dive into movie ending analysis (with autocomplete)

**Ratings & Games:**
- `/rate <movie> <rating>` - Rate a movie 1-10 (with movie autocomplete)
- `/ratings [movie]` - View movie ratings (individual or aggregate)
- `/bingo [movie]` - Generate horror bingo card for a movie

**Playback:**
- `/timeleft` - Show remaining time for current movie
- `/nowplaying` - Show what's currently playing
- `/clients` - Show active Plex clients and status
- `/subtitles` - Download and apply subtitles to current movie

### 🔤 Classic Text Commands
*Legacy commands still available*

**Movie Commands:**
- `!list [query]` - List movies (with optional search)
- `!listview [query]` - Interactive paginated movie list
- `!next` - Show next movie in queue
- `!nextup` - Interactive voting poll for next movie
- `!removedoot <title>` - Remove movie from doot list
- `!cleardoots` - Clear all doot votes
- `!showdoots` - Show current doot list

**AI Commands:**
- `!lobotomize <traits>` - Set personality sliders (e.g., `creepiness=8 humor=2`)
- `!vibe <description>` - Get movie suggestions based on your mood/vibe
- `!catchmeup` - Get plot summary up to current timestamp (DM)

**Utility Commands:**
- `!commands` - Show comprehensive help with all commands
- `!fetch <magnet>` - Download torrent ⚠️ **TRUSTED USERS ONLY**
- `!downloads` / `!dl` - Show qBittorrent download status
- `!check_perms` - Check bot permissions in current channel

**Playback Commands:**
- `!restart` - Restart current movie from beginning
- `!subtitles` - Toggle subtitles for current session

### Statistics & History
- `!stats [user]` - View user statistics and watch time
- `!history [user]` - View watch history
- `!moviestats <movie>` - Detailed stats for specific movie
- `!topwatchers` - Show leaderboard of top watchers
- `!activewatches` - Show currently active viewing sessions
- `!starttracking` - Begin tracking your watch session

### Rating System
- `!rate <movie> <rating>` - Rate a movie (1-10)
- `!ratings <movie>` - View all ratings for a movie
- `!myratings` - View your personal movie ratings
- `!addmovie <title>` - Add movie to database for rating

### Badge System
- `!badges [user]` - View earned badges
- `!allbadges` - View all available badges and requirements
- `!leaderboard` - Badge leaderboard
- `!progress` - View your badge progress
- `!badgestats` - Overall badge statistics
- `!savedata` / `!backupdata` - Backup badge data

### Horror Bingo
- `!bingo` - Start/join horror movie bingo game
- `!mybingo` - View your current bingo card
- `!clearbingo` - Clear your bingo progress
- `!bingostats` - View bingo game statistics

### 🎃 Corruption System (October Horror Features)
- `!status` / `!corruption` / `!sanity` - Check Clanker's corruption level
- `!recover` - Participate in recovery minigames to reduce corruption
- `!purge` - Emergency corruption reset (admin only)

### Admin/Maintenance
- `!repair` - Repair data inconsistencies (admin only)
- `!trigger_event [level]` - Manually trigger corruption event (admin only)

## 🛡️ Security & Compliance Notes

### 🔐 Configuration Security
- **Never commit** `.env` files or `config.py` with real tokens
- Use environment variables for all sensitive data
- The bot includes config validation to prevent startup with placeholder values
- Consider using Discord's slash commands for improved security

### 🚨 Torrent Safety Warning
- **`!fetch` command is UNSANITIZED** - only give access to trusted users
- **No malware protection** - malicious magnets can harm your system
- **No content filtering** - inappropriate material could be downloaded
- **Recommended**: Disable torrent features for public bots

### ⚖️ Legal & ToS Compliance
- **Bot does not stream content** - only coordinates manual Discord streaming
- **You are responsible** for all streamed content and copyright compliance
- **Discord ToS compliance** - streaming is done via your user account, not the bot
- **Content responsibility** - ensure you have rights to stream any content

### 🔒 Access Control Recommendations
- Use **private Discord server** for movie nights with trusted friends
- **Restrict bot permissions** to necessary channels only
- **Monitor command usage** - check logs for suspicious activity
- **Regular security updates** - keep dependencies updated

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