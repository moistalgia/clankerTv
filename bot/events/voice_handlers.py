"""
Voice State Event Handlers
==========================

Handles voice channel join/leave events for streaming notifications and watch tracking.
"""

import logging
from discord.ext import commands
from config import STREAM_CHANNEL_ID, NOTIFY_USER_ID

logger = logging.getLogger(__name__)

# Service references for watch tracking
_plex_service = None
_movie_state = None
_hit_list = None


def setup(bot: commands.Bot, plex_service=None, movie_state=None, hit_list=None):
    """Setup voice state event handlers."""
    global _plex_service, _movie_state, _hit_list
    
    _plex_service = plex_service
    _movie_state = movie_state
    _hit_list = hit_list
    
    @bot.event
    async def on_voice_state_update(member, before, after):
        """Handle voice channel join/leave events for streaming notifications and watch tracking."""
        
        # Get user to notify
        try:
            notify_user = await bot.fetch_user(NOTIFY_USER_ID)
        except Exception as e:
            logger.error(f"Failed to fetch notify user: {e}")
            return

        def get_current_watchers(channel_id):
            """Get all current members in the streaming channel."""
            channel = bot.get_channel(channel_id)
            if channel:
                return [m.name for m in channel.members]
            return []

        # Someone joined the streaming channel
        if after.channel and after.channel.id == STREAM_CHANNEL_ID:
            if not before.channel or before.channel.id != STREAM_CHANNEL_ID:
                watchers = get_current_watchers(STREAM_CHANNEL_ID)
                
                # Send notification
                try:
                    await notify_user.send(
                        f"👀 {member.name} just joined the streaming channel.\n"
                        f"Current watchers: {', '.join(watchers)}"
                    )
                    logger.info(f"{member.name} joined streaming channel")
                except Exception as e:
                    logger.error(f"Failed to send join notification: {e}")
                
                # Start watch tracking if there's a movie currently playing
                await _start_tracking_for_new_joiner(member)
                
                # Check for hit list suggestions when users join
                await _check_hit_list_suggestions(after.channel)

        # Someone left the streaming channel
        if before.channel and before.channel.id == STREAM_CHANNEL_ID:
            if not after.channel or after.channel.id != STREAM_CHANNEL_ID:
                watchers = get_current_watchers(STREAM_CHANNEL_ID)
                
                # Send notification
                try:
                    await notify_user.send(
                        f"⚠️ {member.name} just left the streaming channel.\n"
                        f"Current watchers: {', '.join(watchers) if watchers else 'No one left!'}"
                    )
                    logger.info(f"{member.name} left streaming channel")
                except Exception as e:
                    logger.error(f"Failed to send leave notification: {e}")
                
                # Finish watch tracking for the user who left
                await _finish_tracking_for_leaver(member)


async def _start_tracking_for_new_joiner(member):
    """Start watch tracking for a user who joined during an active movie."""
    if not _plex_service or not _movie_state or member.bot:
        return
    
    try:
        # Check if there's currently a movie playing
        sessions = _plex_service.get_current_sessions()
        if not sessions:
            logger.debug(f"No active movie sessions - not starting tracking for {member.display_name}")
            return
        
        # Check if user is already being tracked
        if member.id in _movie_state.badge_system.active_watches:
            logger.debug(f"User {member.display_name} already being tracked")
            return
        
        # Get current movie info
        current_movie = _movie_state.current_movie
        if not current_movie:
            # Try to get movie title from Plex session
            movie_session = next((s for s in sessions if s.type == "movie"), None)
            if movie_session:
                current_movie = movie_session.title
            else:
                logger.debug("No current movie found for late joiner tracking")
                return
        
        # Get movie metadata and current session info for position tracking
        movie_info = await _plex_service.get_movie_metadata(current_movie)
        session_info = await _plex_service.get_enhanced_session_info()
        
        genres = movie_info.get('genres', ['Horror']) if movie_info else ['Horror']
        year = movie_info.get('year') if movie_info else None
        director = movie_info.get('director') if movie_info else None
        
        # Get position data for robust completion calculation
        movie_duration_ms = session_info.get('duration_ms') if session_info else None
        join_position_ms = session_info.get('current_position_ms') if session_info else None
        
        # Start tracking with enhanced position data
        _movie_state.badge_system.start_watching(
            user_id=member.id,
            username=member.display_name,
            movie_title=current_movie,
            genres=genres,
            year=year,
            director=director,
            movie_duration_ms=movie_duration_ms,
            join_position_ms=join_position_ms
        )
        
        logger.info(f"Started watch tracking for late joiner: {member.display_name} - {current_movie}")
        
    except Exception as e:
        logger.error(f"Failed to start tracking for new joiner {member.display_name}: {e}")


async def _finish_tracking_for_leaver(member):
    """Finish watch tracking for a user who left the channel."""
    if not _movie_state or member.bot:
        return
    
    try:
        # Check if user was being tracked
        if member.id not in _movie_state.badge_system.active_watches:
            return
        
        # Get current movie position when user leaves for accurate completion
        session_info = await _plex_service.get_enhanced_session_info() if _plex_service else None
        leave_position_ms = session_info.get('current_position_ms') if session_info else None
        
        # Finish their watch session with enhanced completion calculation
        new_badges = _movie_state.badge_system.finish_watching(
            user_id=member.id,
            leave_position_ms=leave_position_ms  # Let system calculate accurate completion
        )
        
        logger.info(f"Finished watch tracking for leaver: {member.display_name} (earned {len(new_badges)} badges)")
        
        # Optionally announce badges (you could add this to a channel)
        if new_badges:
            logger.info(f"User {member.display_name} earned badges: {[badge.name for badge in new_badges]}")
        
    except Exception as e:
        logger.error(f"Failed to finish tracking for leaver {member.display_name}: {e}")


async def _check_hit_list_suggestions(voice_channel):
    """Check if users in voice channel have shared movie interests and suggest them."""
    if not _hit_list or not voice_channel:
        return
    
    try:
        # Don't spam suggestions
        if not _hit_list.should_suggest_now():
            return
        
        # Get all non-bot users in voice channel
        voice_users = [member.id for member in voice_channel.members if not member.bot]
        
        if len(voice_users) < 2:
            return  # Need at least 2 users for suggestions
        
        # Find shared movie interests
        shared_movies = _hit_list.find_shared_interests(voice_users)
        
        if not shared_movies:
            return  # No shared interests
        
        # Mark that we're making a suggestion to prevent spam
        _hit_list.mark_suggestion_made()
        
        # Sort by most interested users first
        sorted_movies = sorted(shared_movies.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Build suggestion message
        import discord
        embed = discord.Embed(
            title="👻 Séance Detected!",
            description="Users in voice chat have movies on their hit lists:",
            color=discord.Color.purple()
        )
        
        suggestion_text = []
        for movie, interested_user_ids in sorted_movies[:3]:  # Top 3 suggestions
            # Get usernames
            usernames = []
            for user_id in interested_user_ids:
                try:
                    user = voice_channel.guild.get_member(user_id)
                    if user:
                        usernames.append(user.display_name)
                    else:
                        usernames.append(f"User {user_id}")
                except:
                    usernames.append(f"User {user_id}")
            
            suggestion_text.append(f"🎬 **{movie}** _{', '.join(usernames)}_")
        
        embed.add_field(
            name="Suggested Movies",
            value="\n".join(suggestion_text),
            inline=False
        )
        
        embed.add_field(
            name="Ready to Watch?",
            value="Use `!vote <movie>` to start a poll or `!play <movie>` to begin immediately!",
            inline=False
        )
        
        # Send to the text channel associated with the voice channel or a default channel
        text_channel = None
        
        # Try to find an associated text channel or use general
        for channel in voice_channel.guild.channels:
            if channel.type == discord.ChannelType.text:
                if ("movie" in channel.name.lower() or 
                    "stream" in channel.name.lower() or 
                    "general" in channel.name.lower()):
                    text_channel = channel
                    break
        
        if not text_channel:
            # Fallback to first text channel
            text_channel = next((c for c in voice_channel.guild.channels 
                               if c.type == discord.ChannelType.text), None)
        
        if text_channel:
            await text_channel.send(embed=embed)
            logger.info(f"Sent hit list suggestions for {len(voice_users)} users in voice")
        
    except Exception as e:
        logger.error(f"Failed to check hit list suggestions: {e}")