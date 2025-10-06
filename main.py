"""
ClankerTV Discord Bot - Main Entry Point
=======================================

A horror movie marathon Discord bot with Plex integration, AI personality,
and interactive movie queue management.

Usage:
    python main.py

Author: [Your Name]
Version: 2.0 (Modular Structure)
Date: 2025
"""

import asyncio
import logging
import sys
from pathlib import Path
import discord

# Configure Windows-safe logging
def setup_logging():
    """Setup logging with Windows encoding safety."""
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File handler with UTF-8
    file_handler = logging.FileHandler('clanker.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Console handler with safe encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Try to set UTF-8 encoding for console, fallback to errors='replace'
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

# Initialize logging
setup_logging()

def safe_log(logger, level, message):
    """Safely log message with emoji fallback for Windows."""
    try:
        getattr(logger, level)(message)
    except UnicodeEncodeError:
        # Fallback: replace emojis with text
        safe_message = (message
                       .replace('🎃', '[PUMPKIN]')
                       .replace('✅', '[CHECK]')
                       .replace('❌', '[X]')
                       .replace('🤖', '[BOT]')
                       .replace('🔧', '[WRENCH]')
                       .replace('🎬', '[MOVIE]')
                       .replace('⚠️', '[WARNING]')
                       .replace('📊', '[CHART]'))
        getattr(logger, level)(safe_message)

logger = logging.getLogger(__name__)

# Import all necessary components
from config import TOKEN, GUILD_ID
from bot.bot_instance import bot
from services.plex_service import PlexService
from services.ai_service import AIService
from models.movie_state import MovieState

# Import command modules
from bot.commands import movie_commands, playback_commands, ai_commands, utility_commands, badge_commands

# Import event handlers and tasks
from bot.events import message_handlers, voice_handlers
from bot.tasks import background_tasks

# Global service references for startup checks
_plex_service = None
_movie_state = None


async def setup_bot():
    """Initialize and configure the bot with all components."""
    global _plex_service, _movie_state
    logger.info("Starting ClankerTV Bot setup...")
    
    # Initialize services
    plex_service = PlexService()
    ai_service = AIService()
    movie_state = MovieState()
    
    # Store global references for startup checks
    _plex_service = plex_service
    _movie_state = movie_state
    
    # Connect AI service to badge system for tracking interactions
    ai_service.set_badge_system(movie_state.badge_system)
    
    # Check service connections
    if not plex_service.is_connected():
        logger.warning("Plex service not connected - some features may not work")
    
    # Setup command cogs
    try:
        await movie_commands.setup(bot, plex_service, movie_state)
        await playback_commands.setup(bot, plex_service, movie_state)
        await ai_commands.setup(bot, ai_service, movie_state, plex_service)
        await utility_commands.setup(bot, plex_service, ai_service, movie_state, movie_state.badge_system)
        await badge_commands.setup(bot, movie_state.badge_system, plex_service)
        safe_log(logger, 'info', "✅ All command cogs loaded successfully")
    except Exception as e:
        safe_log(logger, 'error', f"❌ Failed to load command cogs: {e}")
        return False
    
    # Setup event handlers
    try:
        message_handlers.setup(bot, ai_service)
        voice_handlers.setup(bot, plex_service, movie_state)
        safe_log(logger, 'info', "✅ Event handlers registered successfully")
    except Exception as e:
        safe_log(logger, 'error', f"❌ Failed to setup event handlers: {e}")
        return False
    
    # Setup background tasks
    try:
        background_tasks.setup(bot, plex_service, ai_service, movie_state)
        safe_log(logger, 'info', "✅ Background tasks configured successfully")
    except Exception as e:
        safe_log(logger, 'error', f"❌ Failed to setup background tasks: {e}")
        return False
    
    return True


async def check_startup_movie_session():
    """Check for existing movie sessions on startup and start tracking current watchers."""
    global _plex_service, _movie_state
    from config import STREAM_CHANNEL_ID
    
    # Check if services are available
    if not _plex_service or not _movie_state:
        safe_log(logger, 'warning', "⚠️ Services not initialized - skipping startup session check")
        return
    
    # Check if Plex is connected
    if not _plex_service.is_connected():
        safe_log(logger, 'info', "🔌 Plex not connected - skipping startup session check")
        return
    
    try:
        # Check for active Plex sessions
        sessions = _plex_service.get_current_sessions()
        if not sessions:
            safe_log(logger, 'info', "📺 No active Plex sessions found on startup")
            return
        
        # Find movie sessions
        movie_sessions = [s for s in sessions if s.type == "movie"]
        if not movie_sessions:
            safe_log(logger, 'info', "🎬 No movie sessions found on startup")
            return
        
        # Get the first movie session
        current_movie_session = movie_sessions[0]
        movie_title = current_movie_session.title
        
        safe_log(logger, 'info', f"🎬 Found active movie session: {movie_title}")
        
        # Set current movie in state
        _movie_state.set_current_movie(movie_title)
        
        # Get users currently in the streaming voice channel
        channel = bot.get_channel(STREAM_CHANNEL_ID)
        if not channel or not hasattr(channel, 'members'):
            safe_log(logger, 'info', f"📢 Voice channel {STREAM_CHANNEL_ID} not found or has no members")
            return
        
        current_watchers = [m for m in channel.members if not m.bot]
        if not current_watchers:
            safe_log(logger, 'info', "👥 No users in voice channel on startup")
            return
        
        safe_log(logger, 'info', f"👥 Found {len(current_watchers)} users in voice channel: {[m.display_name for m in current_watchers]}")
        
        # Get enhanced session info for robust position tracking
        session_info = await _plex_service.get_enhanced_session_info()
        
        # Start tracking for all current watchers
        for member in current_watchers:
            try:
                # Get movie metadata
                movie_info = await _plex_service.get_movie_metadata(movie_title)
                genres = movie_info.get('genres', ['Horror']) if movie_info else ['Horror']
                year = movie_info.get('year') if movie_info else None
                director = movie_info.get('director') if movie_info else None
                
                # Get position data for accurate tracking (they joined at current movie position)
                movie_duration_ms = session_info.get('duration_ms') if session_info else None
                join_position_ms = session_info.get('current_position_ms') if session_info else None
                
                # Start tracking with enhanced position data
                _movie_state.badge_system.start_watching(
                    user_id=member.id,
                    username=member.display_name,
                    movie_title=movie_title,
                    genres=genres,
                    year=year,
                    director=director,
                    movie_duration_ms=movie_duration_ms,
                    join_position_ms=join_position_ms
                )
                
                safe_log(logger, 'info', f"✅ Started tracking for existing watcher: {member.display_name}")
                
            except Exception as e:
                safe_log(logger, 'error', f"❌ Failed to start tracking for {member.display_name}: {e}")
        
        safe_log(logger, 'info', f"🎯 Startup tracking initiated for {len(current_watchers)} watchers of '{movie_title}'")
        
    except Exception as e:
        safe_log(logger, 'error', f"❌ Error during startup session check: {e}")


@bot.event
async def on_ready():
    """Bot ready event handler."""
    safe_log(logger, 'info', f"🤖 {bot.user} has connected to Discord!")
    safe_log(logger, 'info', f"🔧 Bot is in {len(bot.guilds)} guilds")
    
    # Sync slash commands
    try:
        guild = discord.Object(id=GUILD_ID)
        await bot.tree.sync(guild=guild)
        
        # Fetch and log registered commands
        commands_list = await bot.tree.fetch_commands(guild=guild)
        command_names = [cmd.name for cmd in commands_list]
        safe_log(logger, 'info', f"✅ Synced {len(command_names)} slash commands: {', '.join(command_names)}")
        
    except Exception as e:
        safe_log(logger, 'error', f"❌ Failed to sync slash commands: {e}")
    
    # Start background tasks
    try:
        background_tasks.start_all_tasks()
        safe_log(logger, 'info', "✅ Background tasks started")
    except Exception as e:
        safe_log(logger, 'error', f"❌ Failed to start background tasks: {e}")
    
    # Check for existing movie sessions and start tracking current watchers
    try:
        await check_startup_movie_session()
        safe_log(logger, 'info', "✅ Startup session check completed")
    except Exception as e:
        safe_log(logger, 'error', f"❌ Failed startup session check: {e}")
    
    safe_log(logger, 'info', "🎬 ClankerTV Bot is ready for the horror marathon!")


async def main():
    """Main function to run the bot."""
    safe_log(logger, 'info', "🎃 Starting ClankerTV Horror Bot...")
    
    # Setup bot components
    setup_success = await setup_bot()
    if not setup_success:
        safe_log(logger, 'error', "❌ Bot setup failed - exiting")
        return
    
    # Start the bot
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        safe_log(logger, 'info', "🛑 Bot stopped by user")
    except Exception as e:
        safe_log(logger, 'error', f"❌ Bot crashed: {e}")
    finally:
        # Stop background tasks before closing bot
        try:
            background_tasks.stop_all_tasks()
            safe_log(logger, 'info', "🛑 Background tasks stopped")
        except Exception as e:
            safe_log(logger, 'error', f"Error stopping background tasks: {e}")
        
        await bot.close()
        safe_log(logger, 'info', "👋 Bot shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOP] Bot stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"[X] Fatal error: {e}")
        try:
            logging.exception("Fatal error occurred")
        except UnicodeEncodeError:
            print("[ERROR] Fatal error occurred (unicode logging failed)")