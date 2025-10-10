"""
Background Tasks
===============

Contains all background tasks for the bot including playlist refresh,
playback monitoring, and spontaneous AI messages.
"""

import random
import logging
import asyncio
from datetime import datetime, timezone
from discord import Activity, ActivityType
from discord.ext import commands, tasks

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
                       .replace('🛑', '[STOP]')
                       .replace('⚠️', '[WARNING]')
                       .replace('📊', '[CHART]'))
        getattr(logger, level)(safe_message)
from services.plex_service import PlexService
from services.ai_service import AIService
from models.movie_state import MovieState
from config import (
    PLAYLIST_REFRESH_INTERVAL_HOURS,
    PLAYBACK_CHECK_INTERVAL_MINUTES,
    SPONTANEOUS_AI_INTERVAL_MINUTES,
    SPONTANEOUS_MESSAGE_CHANCE,
    ANNOUNCE_CHANNEL_ID,
    AUTO_SAVE_INTERVAL_MINUTES
)

logger = logging.getLogger(__name__)

# Global references for tasks
playlist_refresh_task = None
playback_check_task = None
spontaneous_ai_task = None
auto_save_task = None

# Services and state references
_bot = None
_plex_service = None
_ai_service = None
_movie_state = None


def setup(bot: commands.Bot, plex_service: PlexService, ai_service: AIService, movie_state: MovieState):
    """Setup all background tasks."""
    global _bot, _plex_service, _ai_service, _movie_state, playlist_refresh_task, playback_check_task, spontaneous_ai_task, auto_save_task
    
    _bot = bot
    _plex_service = plex_service
    _ai_service = ai_service
    _movie_state = movie_state
    
    # Create tasks
    playlist_refresh_task = tasks.loop(hours=PLAYLIST_REFRESH_INTERVAL_HOURS)(refresh_playlist_loop)
    playback_check_task = tasks.loop(minutes=PLAYBACK_CHECK_INTERVAL_MINUTES)(check_playback_loop)
    spontaneous_ai_task = tasks.loop(minutes=SPONTANEOUS_AI_INTERVAL_MINUTES)(spontaneous_ai_loop)
    auto_save_task = tasks.loop(minutes=AUTO_SAVE_INTERVAL_MINUTES)(auto_save_loop)
    
    safe_log(logger, 'info', "✅ Background tasks configured")


def start_all_tasks():
    """Start all background tasks."""
    global playlist_refresh_task, playback_check_task, spontaneous_ai_task, auto_save_task
    
    try:
        if playlist_refresh_task and not playlist_refresh_task.is_running():
            playlist_refresh_task.start()
            safe_log(logger, 'info', "✅ Playlist refresh task started")
        
        if playback_check_task and not playback_check_task.is_running():
            playback_check_task.start()
            safe_log(logger, 'info', "✅ Playback check task started")
        
        if spontaneous_ai_task and not spontaneous_ai_task.is_running():
            spontaneous_ai_task.start()
            safe_log(logger, 'info', "✅ Spontaneous AI task started")
        
        if auto_save_task and not auto_save_task.is_running():
            auto_save_task.start()
            safe_log(logger, 'info', "✅ Auto-save task started")
            
    except Exception as e:
        safe_log(logger, 'error', f"❌ Failed to start background tasks: {e}")


def stop_all_tasks():
    """Stop all background tasks."""
    global playlist_refresh_task, playback_check_task, spontaneous_ai_task, auto_save_task
    
    tasks_to_stop = [
        (playlist_refresh_task, "Playlist refresh"),
        (playback_check_task, "Playback check"),
        (spontaneous_ai_task, "Spontaneous AI"),
        (auto_save_task, "Auto-save")
    ]
    
    for task, name in tasks_to_stop:
        if task and task.is_running():
            task.cancel()
            safe_log(logger, 'info', f"🛑 {name} task stopped")


async def refresh_playlist_loop():
    """Refresh the horror movie playlist from Plex."""
    try:
        if not _plex_service.is_connected():
            logger.warning("Plex not connected - skipping playlist refresh")
            return
        
        new_playlist = await _plex_service.get_horror_movies()
        _movie_state.update_playlist(new_playlist)
        safe_log(logger, 'info', f"✅ Refreshed playlist: {len(new_playlist)} horror movies")
        
    except Exception as e:
        safe_log(logger, 'error', f"❌ Failed to refresh playlist: {e}")


async def check_playback_loop():
    """Monitor Plex sessions and auto-advance to next movie when playback ends."""
    try:
        sessions = _plex_service.get_current_sessions()

        # If no sessions at all, finish tracking and play next movie
        if not sessions:
            safe_log(logger, 'info', "🎬 No active movie sessions found, finishing tracking and starting next movie...")
            
            # Finish badge tracking for the completed movie
            await _finish_movie_tracking()
            
            await _bot.change_presence(activity=None)
            await play_next_movie()
            return

        # Movie is still playing - update Discord status
        session = sessions[0]
        if session.type == "movie":
            # Update Discord status to "Watching <movie>"
            activity = Activity(type=ActivityType.watching, name=session.title)
            await _bot.change_presence(activity=activity)
        else:
            # Session active but not a movie
            await _bot.change_presence(activity=None)

    except Exception as e:
        safe_log(logger, 'error', f"❌ Playback check failed: {e}")


async def spontaneous_ai_loop():
    """Periodically post unsettling AI messages to keep things spooky."""
    # Random chance to post a message
    if random.random() < SPONTANEOUS_MESSAGE_CHANCE:
        channel = _bot.get_channel(ANNOUNCE_CHANNEL_ID)
        if not channel:
            logger.warning("Announce channel not found for spontaneous AI message")
            return

        try:
            message = await _ai_service.generate_spontaneous_message()
            await channel.send(f"🕷️ {message}")
            logger.info("Posted spontaneous AI message")
            
        except Exception as e:
            safe_log(logger, 'error', f"❌ Failed to send spontaneous AI message: {e}")
            try:
                await channel.send(f"❌ Clanker failed to whisper: {e}")
            except:
                pass  # Don't log errors for error messages


async def play_next_movie():
    """Play the next movie based on priority: requests > votes > random."""
    try:
        playlist = _movie_state.playlist
        
        if not playlist:
            logger.warning("Playlist is empty - cannot play next movie")
            return

        movie_title = None

        # First priority: doot requests (top-voted)
        if _movie_state.requests:
            movie_title = _movie_state.get_most_requested_movie()
            _movie_state.remove_movie_request(movie_title)
            logger.info(f"Playing most requested movie: {movie_title}")

        # Second priority: legacy votes
        elif _movie_state.votes:
            movie_title = max(_movie_state.votes, key=_movie_state.votes.get)
            _movie_state.clear_all_votes()
            logger.info(f"Playing most voted movie: {movie_title}")

        # Fallback: random from horror playlist
        else:
            movie_title = random.choice(playlist)
            logger.info(f"Playing random movie: {movie_title}")

        # Play the selected movie with timeout protection
        try:
            result = await asyncio.wait_for(
                _plex_service.play_movie(movie_title),
                timeout=20.0  # Increased to 20 seconds for slow Plex clients
            )
            
            if result['success']:
                _movie_state.set_current_movie(movie_title)
                
                # Start badge tracking for all users in voice channel
                await _start_movie_tracking(movie_title)
                
                # Send announcement
                channel = _bot.get_channel(ANNOUNCE_CHANNEL_ID)
                if channel:
                    await channel.send(f"▶️ Now playing: **{movie_title}** on **{result['client_name']}**")
                    logger.info(f"Announced now playing: {movie_title}")
                    
            else:
                logger.error(f"Failed to play movie: {result['message']}")
                # Try to announce the failure
                channel = _bot.get_channel(ANNOUNCE_CHANNEL_ID) 
                if channel:
                    await channel.send(f"❌ Failed to play **{movie_title}**: {result['message']}")
                    
        except asyncio.TimeoutError:
            # For timeouts, assume the movie might still be starting
            logger.warning(f"Timeout starting movie: {movie_title} - but movie may still be loading...")
            _movie_state.set_current_movie(movie_title)
            
            # Announce with a more positive message
            channel = _bot.get_channel(ANNOUNCE_CHANNEL_ID)
            if channel:
                await channel.send(f"🎬 Starting **{movie_title}** - may take a moment to begin playback...")
                
        except Exception as e:
            logger.error(f"Unexpected error playing movie {movie_title}: {e}")
            # Announce error to users
            channel = _bot.get_channel(ANNOUNCE_CHANNEL_ID)
            if channel:
                await channel.send(f"❌ Error playing **{movie_title}**: {e}")
            
    except Exception as e:
        safe_log(logger, 'error', f"❌ Failed to play next movie: {e}")


async def _start_movie_tracking(movie_title: str):
    """Start tracking movie viewing for users in voice channel."""
    try:
        from config import STREAM_CHANNEL_ID
        
        # Get users in streaming voice channel
        channel = _bot.get_channel(STREAM_CHANNEL_ID)
        if not channel or not hasattr(channel, 'members'):
            return
        
        # Get enhanced session info for position tracking
        session_info = await _plex_service.get_enhanced_session_info()
        
        # Start tracking for each user in the channel
        for member in channel.members:
            if not member.bot:  # Don't track bots
                # Extract movie info and session data
                movie_info = await _plex_service.get_movie_metadata(movie_title)
                genres = movie_info.get('genres', ['Horror']) if movie_info else ['Horror']
                year = movie_info.get('year') if movie_info else None
                director = movie_info.get('director') if movie_info else None
                
                # Get position data for robust tracking
                movie_duration_ms = session_info.get('duration_ms') if session_info else None
                join_position_ms = 0  # Movie just started, so everyone joins at beginning
                
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
                logger.info(f"Started tracking movie for {member.display_name}")
        
    except Exception as e:
        logger.error(f"Failed to start movie tracking: {e}")


async def _finish_movie_tracking():
    """Finish tracking and award badges when movie ends."""
    try:
        # Get current movie sessions to determine completion
        sessions = _plex_service.get_current_sessions()
        
        # Get final movie position for accurate completion calculation
        final_session_info = await _plex_service.get_enhanced_session_info() if _plex_service else None
        final_position_ms = final_session_info.get('duration_ms') if final_session_info else None  # Movie ended naturally
        
        # Award badges to all users who were tracking
        for user_id in list(_movie_state.badge_system.active_watches.keys()):
            new_badges = _movie_state.badge_system.finish_watching(
                user_id=user_id,
                leave_position_ms=final_position_ms  # Use enhanced completion calculation
            )
            
            # Announce new badges earned
            if new_badges:
                try:
                    user = await _bot.fetch_user(user_id)
                    channel = _bot.get_channel(ANNOUNCE_CHANNEL_ID)
                    if channel:
                        badge_names = ", ".join([f"{badge.emoji} {badge.name}" for badge in new_badges])
                        await channel.send(f"🏆 **{user.display_name}** earned new badges: {badge_names}")
                        logger.info(f"User {user.display_name} earned {len(new_badges)} badges")
                except Exception as e:
                    logger.error(f"Failed to announce badges for user {user_id}: {e}")
        
    except Exception as e:
        logger.error(f"Failed to finish movie tracking: {e}")


async def auto_save_loop():
    """Periodically save badge system data and update active watch progress."""
    try:
        # Only save if there are active watches to avoid unnecessary writes
        if not _movie_state or not _movie_state.badge_system:
            return
            
        active_watches_count = len(_movie_state.badge_system.active_watches)
        
        if active_watches_count > 0:
            # Update active watch progress with current movie position
            updates_made = await update_active_watch_progress()
            
            # Save the data (including updated watch history)
            _movie_state.badge_system.save_progress()
            
            if updates_made > 0:
                safe_log(logger, 'info', f"💾 Auto-saved badge data ({active_watches_count} active, {updates_made} updated)")
            else:
                safe_log(logger, 'info', f"💾 Auto-saved badge data ({active_watches_count} active watches)")
        else:
            # No active watches, skip save but log occasionally for debugging
            import random
            if random.randint(1, 12) == 1:  # Log once per hour on average (every 12 * 5 minutes)
                safe_log(logger, 'debug', "⏭️ Auto-save skipped (no active watches)")
            
    except Exception as e:
        safe_log(logger, 'error', f"❌ Auto-save failed: {e}")


async def update_active_watch_progress():
    """Update progress for all active watches based on current movie position."""
    updates_made = 0
    
    try:
        if not _plex_service or not _plex_service.is_connected():
            return updates_made
        
        # Get current session info
        current_session_info = await _plex_service.get_enhanced_session_info()
        if not current_session_info:
            return updates_made
        
        current_position_ms = current_session_info.get('current_position_ms')
        if not current_position_ms:
            return updates_made
        
        current_time = datetime.now(timezone.utc)
        
        # Update each active watch with current progress
        for user_id, active_watch in _movie_state.badge_system.active_watches.items():
            try:
                # Calculate watch duration based on movie position progress
                if active_watch.join_position_ms is not None:
                    # Position-based calculation (most accurate)
                    content_watched_ms = max(0, current_position_ms - active_watch.join_position_ms)
                    duration_minutes = int(content_watched_ms / (1000 * 60))
                else:
                    # Fallback to time-based calculation
                    if active_watch.start_time.tzinfo is None:
                        start_time = active_watch.start_time.replace(tzinfo=timezone.utc)
                    else:
                        start_time = active_watch.start_time
                    
                    duration = current_time - start_time
                    duration_minutes = int(duration.total_seconds() / 60)
                
                # Calculate completion percentage
                completion_percentage = 0.0
                if active_watch.movie_duration_ms and active_watch.movie_duration_ms > 0:
                    if active_watch.join_position_ms is not None:
                        progress_ms = current_position_ms - active_watch.join_position_ms
                    else:
                        progress_ms = current_position_ms
                    completion_percentage = min(100.0, (progress_ms / active_watch.movie_duration_ms) * 100)
                
                # Only update if there's meaningful progress (at least 1 minute)
                if duration_minutes > active_watch.watch_duration_minutes:
                    # Update the active watch progress
                    active_watch.watch_duration_minutes = duration_minutes
                    active_watch.completion_percentage = completion_percentage
                    
                    # Create/update watch history entry
                    _movie_state.badge_system.update_watch_progress(
                        user_id=user_id,
                        duration_minutes=duration_minutes,
                        completion_percentage=completion_percentage
                    )
                    
                    updates_made += 1
                    
            except Exception as e:
                safe_log(logger, 'error', f"Error updating watch progress for user {user_id}: {e}")
        
    except Exception as e:
        safe_log(logger, 'error', f"Error in update_active_watch_progress: {e}")
    
    return updates_made