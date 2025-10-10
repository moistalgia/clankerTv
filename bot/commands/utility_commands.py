"""
Utility Commands
===============

General utility commands like help, status, and bot information.
"""

import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional
import subprocess
import os
import tempfile

from config import GUILD_ID, AUTO_SAVE_INTERVAL_MINUTES, QB_HOST, QB_USER, QB_PASS, DOWNLOAD_PATH, NOTIFY_USER_ID

from services.plex_service import PlexService
# Import qBittorrent for fetch and status commands
try:
    import qbittorrentapi
    QB_AVAILABLE = True
except ImportError:
    QB_AVAILABLE = False
    qbittorrentapi = None
from services.ai_service import AIService
from models.movie_state import MovieState
from models.horror_bingo import HorrorBingoSystem, BingoView
from models.hit_list import HitListSystem


class UtilityCommands(commands.Cog):
    """Cog containing utility and help commands."""
    
    def __init__(self, bot: commands.Bot, plex_service: PlexService, ai_service: AIService, movie_state: MovieState, badge_system=None):
        self.bot = bot
        self.plex_service = plex_service
        self.ai_service = ai_service
        self.movie_state = movie_state
        self.horror_bingo = HorrorBingoSystem(ai_service, badge_system)
        self.hit_list = HitListSystem()
        
        # Initialize qBittorrent client
        self.qb = None
        if QB_AVAILABLE:
            try:
                self.qb = qbittorrentapi.Client(host=QB_HOST, username=QB_USER, password=QB_PASS)
                self.qb.auth_log_in()
            except Exception as e:
                print(f"qBittorrent connection failed: {e}")
                pass  # qBittorrent not available

    @commands.command(name="fetch")
    async def fetch_magnet(self, ctx: commands.Context, *, magnet_link: str):
        """Add a magnet link to qBittorrent for downloading."""
        if not self.qb:
            await ctx.send("❌ qBittorrent is not available or not configured.")
            return
        
        try:
            # Add the torrent with the custom save path from config
            self.qb.torrents_add(urls=magnet_link, save_path=DOWNLOAD_PATH)
            await ctx.send(f"🎬 Magnet added to qBittorrent successfully!\n📂 Saved to: {DOWNLOAD_PATH}")
        except Exception as e:
            await ctx.send(f"❌ Failed to add magnet: {e}")

    @commands.command(name="downloads", aliases=["dl", "download_status"])
    async def download_status(self, ctx: commands.Context):
        """Show status of active qBittorrent downloads."""
        if not QB_AVAILABLE:
            await ctx.send("❌ qBittorrent API library not installed. Run: `pip install qbittorrent-api`")
            return
            
        if not self.qb:
            await ctx.send(f"❌ qBittorrent connection failed. Check if qBittorrent is running at {QB_HOST} with Web UI enabled.")
            return
        
        try:
            torrents = self.qb.torrents_info()
            if not torrents:
                await ctx.send("📭 No torrents found.")
                return

            active_states = ["downloading", "stalledDL", "queuedDL"]
            active_torrents = [t for t in torrents if t.state in active_states]

            if not active_torrents:
                await ctx.send("📭 No torrents are actively downloading.")
                return

            embed = discord.Embed(
                title="📊 Active Downloads",
                color=discord.Color.blue()
            )
            
            for i, t in enumerate(active_torrents[:10]):  # Limit to 10
                progress = f"{t.progress * 100:.1f}%" if hasattr(t, 'progress') else "N/A"
                speed = f"{t.dlspeed / 1024 / 1024:.1f} MB/s" if hasattr(t, 'dlspeed') and t.dlspeed > 0 else "0 MB/s"
                
                embed.add_field(
                    name=f"🎬 {t.name[:40]}{'...' if len(t.name) > 40 else ''}",
                    value=f"Progress: {progress}\nSpeed: {speed}\nState: {t.state}",
                    inline=True
                )
            
            if len(active_torrents) > 10:
                embed.set_footer(text=f"Showing 10 of {len(active_torrents)} active downloads")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Failed to get download status: {e}")

    @commands.command(name="commands")
    async def custom_help(self, ctx: commands.Context):
        """Display comprehensive help information with all available commands."""
        embed = discord.Embed(
            title="📖 Available Commands",
            description="Here's what Clanker can do during the marathon:",
            color=discord.Color.red()
        )

        # Playback Controls
        embed.add_field(
            name="🎬 Playback Controls",
            value=(
                "`!nowplaying` — Playback control and info for the current film\n"
                "`!start_marathon` — Start the horror marathon\n"
                "`!stop` — Stop current movie (when you're last viewer)\n"
                "`!seek <time>` — Jump to timestamp (1h23m45s, 23:45, 1:23:45)\n"
                "`!play <movie>` — Admin override — immediately play a movie\n"
                "`!restart` — Restart the current movie from the beginning\n"
                "`!timeleft` — Show remaining time in the current movie\n"
                "`!subtitles` — Download the top-ranked OpenSubtitles subtitle and apply it\n"
                "`!next` — Play the next movie from requests, votes, or random"
            ),
            inline=False
        )

        # Requests & Voting
        embed.add_field(
            name="🗳️ Requests & Voting",
            value=(
                "`!nextup` — Voting UI for the next movie\n"
                "`!doot <movie>` [DEPRECATED - use /dootdoot] — Request (doot) a movie to be reviewed\n"
                "`/dootdoot` — Movie request via autocomplete dropdown\n"
                "`!dootlist` — List all pending movie doots (requests)\n"
                "`!removedoot <movie>` — Remove a movie request\n"
                "`!cleardoots` — Clear all requests\n"
                "`!showdoots` — Show current votes for movies\n"
                "`!seed <movie>` — Preload a movie without voting"
            ),
            inline=False
        )

        # AI & Analysis
        embed.add_field(
            name="🤖 AI & Analysis",
            value=(
                "`!catchmeup` — Get AI summary of current movie up to timestamp (DM)\n"
                "`!movieslike <movie>` — 5 horror movie recommendations (AI)\n"
                "`!vibe <words>` — Get horror suggestions matching a vibe\n"
                "`!whatdidijustwatch [movie]` — Provide synopsis and trivia for the film\n"
                "`!endinganalysis [movie]` — Deep dive into ending interpretations and theories\n"
                "`!lobotomize` — Set bot personality traits. Example: 'Turn mystery to 10 and creepiness to 10'"
            ),
            inline=False
        )

        # Badge System
        embed.add_field(
            name="🏆 Badge System",
            value=(
                "`!badges [@user]` — View earned badges (yours or another user's)\n"
                "`!stats [@user]` — Detailed watch statistics and achievements\n"
                "`!leaderboard [category]` — Rankings: movies, time, streak, badges\n"
                "`!progress` — Progress towards next badges\n"
                "`!allbadges` — View all available badges and requirements"
            ),
            inline=False
        )

        # Library & Clients
        embed.add_field(
            name="📚 Library & Clients",
            value=(
                "`!list <optional movie name>` — Show the full horror playlist (filterable)\n"
                "`!listview` — Interactive paginated movie list with navigation\n"
                "`!clients` — List controllable Plex clients (devices)\n"
                "`!refresh` — Refresh Plex library and update horror playlist"
            ),
            inline=False
        )

        # Horror Bingo
        embed.add_field(
            name="🎰 Horror Bingo",
            value=(
                "`!bingo` — Start a Horror Bingo card for the current movie\n"
                "`!bingo <movie>` — Start a custom Horror Bingo card\n"
                "`!mybingo` — Show your current bingo card\n"
                "`!clearbingo` — Clear your current bingo card"
            ),
            inline=False
        )

        # Corruption System (October Horror Features)
        embed.add_field(
            name="🎃 Corruption System",
            value=(
                "`!status` / `!corruption` / `!sanity` — Check Clanker's corruption level\n"
                "`!recover [type]` — Play recovery minigames (memory/circuit/static/debug/binary)\n"
                "`!reboot` — Attempt emergency system reboot\n"
                "`!diagnostics` — Run full system diagnostic\n"
                "`!fragment` — Retrieve ARG memory fragment\n"
                "`!recovery_help` — Show recovery system help"
            ),
            inline=False
        )

        # Movie History & Ratings
        embed.add_field(
            name="📚 Movie History & Ratings",
            value=(
                "`!history` — Show recent movies played by the bot\n"
                "`!history <user>` — Show movies watched by specific user\n"
                "`!moviestats` — Show overall movie statistics\n"
                "`!topwatchers` — Show users with most movies watched\n"
                "`!rate <1-10> <movie>` — Rate a movie you've watched\n"
                "`!ratings [movie]` — Show ratings for movie or all movies\n"
                "`!myratings` — Show your personal movie ratings\n"
                "`!addmovie <movie info>` — Manually add movie to your history\n"
                "`!repair <movie>` — Add movie from Plex library to your history"
            ),
            inline=False
        )

        # Admin & Debug
        embed.add_field(
            name="⚙️ Admin & Debug",
            value=(
                "`!activewatches` — Show current active tracking sessions\n"
                "`!starttracking` — Manually start tracking (admin only)\n"
                "`!savedata` — Manually save badge data (admin only)"
            ),
            inline=False
        )

        # Hit List
        embed.add_field(
            name="🎯 Hit List",
            value=(
                "`!hitlist` — Show your hit list of movies you want to watch\n"
                "`/hitlist <movie>` — Add a movie to your hit list (with autocomplete!) 🌟\n"
                "`!hitlist remove <movie>` — Remove a movie from your hit list\n"
                "`!hitlist show [movie]` — Show all hit list movies or who wants a specific movie"
            ),
            inline=False
        )

        # Misc
        embed.add_field(
            name="🧩 Misc",
            value=(
                "`!fetch <magnet link>` — Add a magnet link to qBittorrent (for media you own)\n"
                "`!downloads` / `!dl` — Show status of active qBittorrent downloads\n"
                "`!ahk [script_name]` — Execute AutoHotkey script (admin only)\n"
                "`!commands` — Show this help message\n"
                "`!check_perms` — Check bot permissions in server"
            ),
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command(name="refresh")
    async def refresh_library(self, ctx: commands.Context):
        """Refresh Plex library and update horror movie playlist."""
        if not self.plex_service.is_connected():
            await ctx.send("❌ Plex service is not connected.")
            return
        
        try:
            # Refresh the Plex library
            await ctx.send("🔄 Refreshing Plex library...")
            
            # Get the library section and refresh it
            library = self.plex_service.library
            if library:
                library.update()
                
                # Wait a moment then get updated movie count
                await ctx.send("📚 Library refresh initiated. Fetching updated horror movies...")
                
                # Get fresh horror movie list
                horror_movies = await self.plex_service.get_horror_movies()
                
                embed = discord.Embed(
                    title="✅ Library Refreshed",
                    description=f"Found **{len(horror_movies)}** horror movies in library",
                    color=discord.Color.green()
                )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Could not access Plex library for refresh.")
                
        except Exception as e:
            await ctx.send(f"❌ Error refreshing library: {e}")

    @commands.command(name="start_marathon")
    async def start_marathon(self, ctx: commands.Context):
        """Start the horror marathon - begins playback of movies from the queue."""
        
        if not self.plex_service or not self.plex_service.is_connected():
            await ctx.send("❌ Plex service is not connected. Cannot start marathon.")
            return
        
        # Check if there's already a movie playing
        try:
            sessions = self.plex_service.get_current_sessions()
            movie_sessions = [s for s in sessions if s.type == "movie"]
            
            if movie_sessions:
                current_movie = movie_sessions[0].title
                await ctx.send(f"🎬 Marathon is already running! Currently playing: **{current_movie}**\n"
                             f"Use `!nowplaying` for playback controls.")
                return
        except Exception as e:
            print(f"Error checking current sessions: {e}")
        
        # Try to start the next movie from the queue
        try:
            # Get the next movie to play (this would typically be from a queue/playlist)
            # For now, we'll check if there are any doots (requests) or fall back to library
            
            # Check for pending requests first
            if hasattr(self.movie_state, 'doots') and self.movie_state.doots:
                # Get the most voted movie or first in queue
                next_movie = list(self.movie_state.doots.keys())[0]
                await ctx.send(f"🎬 Starting marathon with requested movie: **{next_movie}**")
            else:
                # Fall back to a random horror movie from the library
                try:
                    horror_movies = await self.plex_service.get_horror_movies()
                    if horror_movies:
                        import random
                        next_movie = random.choice(horror_movies)  # horror_movies already contains strings
                        await ctx.send(f"🎬 Starting marathon with random movie: **{next_movie}**")
                    else:
                        await ctx.send("❌ No horror movies found in library to start marathon.")
                        return
                except Exception as e:
                    await ctx.send(f"❌ Could not access movie library: {e}")
                    return
            
            # Attempt to play the movie
            success = await self.plex_service.play_movie(next_movie)
            
            if success:
                # Set current movie state
                self.movie_state.set_current_movie(next_movie)
                
                embed = discord.Embed(
                    title="🎃 Horror Marathon Started!",
                    description=f"Now playing: **{next_movie}**",
                    color=discord.Color.dark_red()
                )
                embed.add_field(
                    name="🎮 Controls", 
                    value="Use `!nowplaying` for playback controls\nUse `/dootdoot` to request movies", 
                    inline=False
                )
                embed.add_field(
                    name="🏆 Features",
                    value="• Badge tracking active\n• Horror Bingo available with `!bingo`\n• Movie ratings with `!rate`",
                    inline=False
                )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Failed to start playback of **{next_movie}**. Check Plex server and client connections.")
                
        except Exception as e:
            await ctx.send(f"❌ Error starting marathon: {e}")

    @commands.command(name="testplay")
    @commands.has_permissions(administrator=True)
    async def test_play_movie(self, ctx: commands.Context, *, movie_title: str = "The Thing (1982)"):
        """Test playing a specific movie to debug Plex client issues."""
        
        if not self.plex_service or not self.plex_service.is_connected():
            await ctx.send("❌ Plex service is not connected.")
            return
        
        loading_msg = await ctx.send(f"🧪 Testing playback of **{movie_title}**...")
        
        try:
            # Get available clients
            clients = await self.plex_service.get_available_clients()
            
            embed = discord.Embed(
                title="🧪 Plex Client Test",
                color=discord.Color.blue()
            )
            
            if not clients:
                embed.add_field(name="❌ No Clients", value="No Plex clients found", inline=False)
            else:
                client_list = "\n".join([f"• **{c['title']}** ({c['platform']})" for c in clients])
                embed.add_field(name="📱 Available Clients", value=client_list, inline=False)
            
            # Try to play the movie
            result = await self.plex_service.play_movie(movie_title)
            
            if result['success']:
                embed.add_field(
                    name="✅ Playback Result", 
                    value=f"Success! {result['message']}", 
                    inline=False
                )
                embed.color = discord.Color.green()
            else:
                embed.add_field(
                    name="❌ Playback Result", 
                    value=f"Failed: {result['message']}", 
                    inline=False
                )
                embed.color = discord.Color.red()
            
            await loading_msg.edit(content=None, embed=embed)
            
        except Exception as e:
            await loading_msg.edit(content=f"❌ Test failed with error: {e}")

    @commands.command(name="stop")
    async def stop_playback(self, ctx: commands.Context):
        """Stop current movie playback when you're the last person viewing."""
        
        if not self.plex_service or not self.plex_service.is_connected():
            await ctx.send("❌ Plex service is not connected.")
            return
        
        try:
            # Check if there's currently a movie playing
            sessions = self.plex_service.get_current_sessions()
            movie_sessions = [s for s in sessions if s.type == "movie"]
            
            if not movie_sessions:
                await ctx.send("⏹️ No movie is currently playing.")
                return
            
            current_session = movie_sessions[0]
            movie_title = current_session.title
            
            # Check voice channel for active viewers
            from config import STREAM_CHANNEL_ID
            voice_channel = ctx.bot.get_channel(STREAM_CHANNEL_ID)
            
            if voice_channel and hasattr(voice_channel, 'members'):
                # Count non-bot members in voice channel
                real_viewers = [m for m in voice_channel.members if not m.bot]
                
                if len(real_viewers) > 1:
                    await ctx.send(f"⚠️ Cannot stop **{movie_title}** - {len(real_viewers)} people are still in the voice channel.")
                    return
            
            # Get client and stop playback
            client = self.plex_service.get_first_controllable_client()
            if not client:
                await ctx.send("❌ No controllable Plex client found.")
                return
            
            # Stop the playback
            client.stop()
            
            # Clear current movie state
            self.movie_state.set_current_movie(None)
            
            await ctx.send(f"⏹️ Stopped **{movie_title}**. Marathon can be restarted with `!start_marathon`.")
            
        except Exception as e:
            await ctx.send(f"❌ Error stopping playback: {e}")

    @commands.command(name="seek")
    async def seek_to_timestamp(self, ctx: commands.Context, *, timestamp: str):
        """Seek to a specific timestamp. Format: 1h23m45s, 23:45, or 1:23:45"""
        
        if not self.plex_service or not self.plex_service.is_connected():
            await ctx.send("❌ Plex service is not connected.")
            return
        
        try:
            # Parse timestamp to milliseconds
            def parse_timestamp(ts):
                """Parse various timestamp formats to milliseconds."""
                ts = ts.lower().strip()
                
                # Format: 1h23m45s
                if 'h' in ts or 'm' in ts or 's' in ts:
                    import re
                    hours = int(re.search(r'(\d+)h', ts).group(1)) if 'h' in ts else 0
                    minutes = int(re.search(r'(\d+)m', ts).group(1)) if 'm' in ts else 0
                    seconds = int(re.search(r'(\d+)s', ts).group(1)) if 's' in ts else 0
                    return (hours * 3600 + minutes * 60 + seconds) * 1000
                
                # Format: 23:45 or 1:23:45
                parts = ts.split(':')
                if len(parts) == 2:  # mm:ss
                    minutes, seconds = map(int, parts)
                    return (minutes * 60 + seconds) * 1000
                elif len(parts) == 3:  # hh:mm:ss
                    hours, minutes, seconds = map(int, parts)
                    return (hours * 3600 + minutes * 60 + seconds) * 1000
                else:
                    raise ValueError("Invalid timestamp format")
            
            seek_ms = parse_timestamp(timestamp)
            
            # Check for active session
            sessions = self.plex_service.get_current_sessions()
            movie_sessions = [s for s in sessions if s.type == "movie"]
            
            if not movie_sessions:
                await ctx.send("❌ No movie is currently playing.")
                return
            
            # Get client and seek
            client = self.plex_service.get_first_controllable_client()
            if not client:
                await ctx.send("❌ No controllable Plex client found.")
                return
            
            # Perform seek
            client.seekTo(seek_ms)
            
            # Format response
            hours = seek_ms // (3600 * 1000)
            minutes = (seek_ms % (3600 * 1000)) // (60 * 1000)
            seconds = (seek_ms % (60 * 1000)) // 1000
            
            if hours > 0:
                time_str = f"{hours}h {minutes}m {seconds}s"
            else:
                time_str = f"{minutes}m {seconds}s"
            
            await ctx.send(f"⏭️ Seeked to **{time_str}**")
            
        except ValueError as e:
            await ctx.send(f"❌ Invalid timestamp format. Use: `1h23m45s`, `23:45`, or `1:23:45`")
        except Exception as e:
            await ctx.send(f"❌ Error seeking to timestamp: {e}")

    @commands.command(name="check_perms")
    async def check_permissions(self, ctx: commands.Context):
        """Check bot permissions in the current guild and channel."""
        guild = ctx.guild
        bot_member = guild.me  # the bot's member object in this guild

        # Global guild permissions
        guild_perms = bot_member.guild_permissions
        guild_perm_list = [perm for perm, value in guild_perms if value]
        missing_guild_perms = [perm for perm, value in guild_perms if not value]

        # Channel-specific permissions
        channel = ctx.channel
        channel_perms = channel.permissions_for(bot_member)
        channel_perm_list = [perm for perm, value in channel_perms if value]
        missing_channel_perms = [perm for perm, value in channel_perms if not value]

        msg = f"**Guild permissions:**\n✅ {', '.join(guild_perm_list)}\n❌ {', '.join(missing_guild_perms)}\n\n"
        msg += f"**Channel permissions for #{channel.name}:**\n✅ {', '.join(channel_perm_list)}\n❌ {', '.join(missing_channel_perms)}"
        
        await ctx.send(msg)

    @commands.command(name="ahk")
    async def run_autohotkey(self, ctx: commands.Context, script_name: str = "discord_automation"):
        """Execute an AutoHotkey script."""
        
        # Security check - only allow specific users or roles
        if not (ctx.author.guild_permissions.administrator or ctx.author.id in [NOTIFY_USER_ID]):
            await ctx.send("❌ You don't have permission to run AutoHotkey scripts.")
            return
        
        try:
            # Define script directory
            scripts_dir = os.path.join(os.getcwd(), "autohotkey_scripts")
            script_path = os.path.join(scripts_dir, f"{script_name}.ahk")
            
            # Check if script exists
            if not os.path.exists(script_path):
                # Create default Discord automation script if it doesn't exist
                if script_name == "discord_automation":
                    await self._create_default_discord_script(scripts_dir, script_path)
                else:
                    await ctx.send(f"❌ Script `{script_name}.ahk` not found in `autohotkey_scripts/` folder.")
                    return
            
            # Try to find AutoHotkey executable
            ahk_paths = [
                r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
                r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
                "AutoHotkey.exe"  # If in PATH
            ]
            
            ahk_exe = None
            for path in ahk_paths:
                if os.path.exists(path) or path == "AutoHotkey.exe":
                    ahk_exe = path
                    break
            
            if not ahk_exe:
                await ctx.send("❌ AutoHotkey not found. Please install AutoHotkey first.")
                return
            
            # Execute the script
            result = subprocess.run([ahk_exe, script_path], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            
            if result.returncode == 0:
                await ctx.send(f"✅ AutoHotkey script `{script_name}` executed successfully!")
            else:
                await ctx.send(f"❌ Script execution failed. Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            await ctx.send("⏰ Script execution timed out (30s limit).")
        except Exception as e:
            await ctx.send(f"❌ Error executing script: {e}")

    async def _create_default_discord_script(self, scripts_dir: str, script_path: str):
        """Create a default Discord automation script."""
        os.makedirs(scripts_dir, exist_ok=True)
        
        default_script = '''
; Discord Automation Script
; Generated by ClankerTV Bot
; Press Ctrl+D to run, F1 to get coordinates, Esc to exit

; Define your click coordinates here (replace with actual coordinates)
Click1X := 400
Click1Y := 300
Click2X := 600
Click2Y := 500

^d::
    ; Activate Discord window
    WinActivate, ahk_exe Discord.exe
    WinWaitActive, ahk_exe Discord.exe, , 3
    
    ; Make Discord fullscreen
    Send, {F11}
    Sleep, 1000
    
    ; First click
    Click, %Click1X%, %Click1Y%
    Sleep, 500
    
    ; Second click
    Click, %Click2X%, %Click2Y%
    
    ; Optional: Exit fullscreen after 2 seconds
    Sleep, 2000
    Send, {F11}
return

; Press F1 to get current mouse coordinates
F1::
MouseGetPos, xpos, ypos
MsgBox, Discord Coordinates: X=%xpos% Y=%ypos%
return

; Press Esc to stop script
Esc::ExitApp
'''
        
        with open(script_path, 'w') as f:
            f.write(default_script)

    @commands.command(name="bingo")
    async def horror_bingo(self, ctx: commands.Context, *, movie_title: str = None):
        """Start a Horror Bingo card for a movie."""
        
        # Determine movie title
        if not movie_title:
            # Use current movie if available
            if self.movie_state.current_movie:
                movie_title = self.movie_state.current_movie
            else:
                await ctx.send("❌ No movie specified and no movie currently playing. Use `!bingo <movie title>`")
                return
        
        # Check if user already has an active card
        if self.horror_bingo.has_active_card(ctx.author.id):
            existing_card = self.horror_bingo.get_user_card(ctx.author.id)
            await ctx.send(
                f"⚠️ You already have an active bingo card for **{existing_card.movie_title}**!\n"
                f"Use `!mybingo` to view it or `!clearbingo` to start fresh."
            )
            return
        
        # Show loading message
        loading_msg = await ctx.send(f"🎰 Generating Horror Bingo card for **{movie_title}**... This may take a moment!")
        
        try:
            # Get movie info if available
            movie_genre = None
            if self.plex_service and hasattr(self.plex_service, 'get_movie_info'):
                try:
                    movie_info = await self.plex_service.get_movie_info(movie_title)
                    if movie_info and hasattr(movie_info, 'genres'):
                        movie_genre = movie_info.genres[0] if movie_info.genres else None
                except:
                    pass  # Continue without genre info
            
            # Create bingo card
            card = await self.horror_bingo.create_bingo_card(ctx.author.id, movie_title, movie_genre)
            
            # Create embed and view
            embed = self.horror_bingo.create_card_embed(card)
            view = BingoView(card, self.horror_bingo)
            
            # Update loading message with bingo card
            await loading_msg.edit(content=None, embed=embed, view=view)
            
        except Exception as e:
            await loading_msg.edit(content=f"❌ Failed to create bingo card: {e}")

    @commands.command(name="mybingo")
    async def show_my_bingo(self, ctx: commands.Context):
        """Show your current bingo card."""
        
        card = self.horror_bingo.get_user_card(ctx.author.id)
        if not card:
            await ctx.send("❌ You don't have an active bingo card. Use `!bingo` to create one!")
            return
        
        # Create embed and view
        embed = self.horror_bingo.create_card_embed(card)
        view = BingoView(card, self.horror_bingo)
        
        await ctx.send(embed=embed, view=view)

    @commands.command(name="clearbingo")
    async def clear_bingo(self, ctx: commands.Context):
        """Clear your current bingo card."""
        
        if not self.horror_bingo.has_active_card(ctx.author.id):
            await ctx.send("❌ You don't have an active bingo card to clear.")
            return
        
        card = self.horror_bingo.get_user_card(ctx.author.id)
        
        # Confirmation
        embed = discord.Embed(
            title="⚠️ Clear Bingo Card",
            description=f"Are you sure you want to clear your bingo card for **{card.movie_title}**?\n\nThis action cannot be undone!",
            color=discord.Color.orange()
        )
        
        view = BingoClearConfirmView(ctx.author.id, self.horror_bingo)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="bingostats")
    async def bingo_stats(self, ctx: commands.Context):
        """Show Horror Bingo statistics."""
        
        active_cards = len(self.horror_bingo.active_cards)
        
        if active_cards == 0:
            await ctx.send("📊 No active bingo cards right now. Start one with `!bingo`!")
            return
        
        embed = discord.Embed(
            title="📊 Horror Bingo Statistics",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="🎰 Active Cards",
            value=f"{active_cards} players have active bingo cards",
            inline=False
        )
        
        # Show some active cards
        if active_cards <= 10:
            card_info = []
            for user_id, card in self.horror_bingo.active_cards.items():
                try:
                    user = self.bot.get_user(user_id)
                    username = user.display_name if user else f"User {user_id}"
                    progress = sum(card.marked)
                    bingo_status = "🎉 BINGO!" if card.has_bingo() else f"{progress}/25"
                    card_info.append(f"**{username}** - {card.movie_title} ({bingo_status})")
                except:
                    continue
            
            if card_info:
                embed.add_field(
                    name="📋 Active Cards",
                    value="\n".join(card_info),
                    inline=False
                )
        
        await ctx.send(embed=embed)

    @commands.command(name="history")
    async def movie_history(self, ctx: commands.Context, *, user_mention: str = None):
        """Show movie watch history for bot or specific user."""
        
        if not hasattr(self.movie_state, 'badge_system') or not self.movie_state.badge_system:
            await ctx.send("❌ Badge system not available - movie history not tracked.")
            return
        
        badge_system = self.movie_state.badge_system
        
        if user_mention:
            # Parse user mention or username
            user = None
            if ctx.message.mentions:
                user = ctx.message.mentions[0]
            else:
                # Try to find user by username - check if we have access to guild
                if ctx.guild and ctx.guild.members:
                    for member in ctx.guild.members:
                        if member.display_name.lower() == user_mention.lower() or member.name.lower() == user_mention.lower():
                            user = member
                            break
                
                # If no guild access, try to find user by searching user stats
                if not user:
                    # Look through user stats for matching username
                    matching_users = []
                    for user_id, user_stats in badge_system.user_stats.items():
                        if hasattr(user_stats, 'username') and user_stats.username and user_stats.username.lower() == user_mention.lower():
                            matching_users.append((user_id, user_stats.username))
                    
                    if len(matching_users) == 1:
                        # Found exactly one matching user
                        user_id, username = matching_users[0]
                        # Create a mock user object with the ID for lookups
                        class MockUser:
                            def __init__(self, user_id, username):
                                self.id = user_id
                                self.display_name = username
                        
                        user = MockUser(user_id, username)
                    elif len(matching_users) > 1:
                        await ctx.send(f"❌ Multiple users found with name '{user_mention}'. Try using @mention instead.")
                        return
            
            if not user:
                await ctx.send(f"❌ User '{user_mention}' not found.")
                return
            
            # Show history for specific user
            user_watches = [watch for watch in badge_system.watch_history if watch.user_id == user.id]
            
            if not user_watches:
                await ctx.send(f"📚 No movie history found for {user.display_name}")
                return
            
            # Sort by most recent
            user_watches.sort(key=lambda x: x.start_time, reverse=True)
            
            embed = discord.Embed(
                title=f"📚 Movie History - {user.display_name}",
                color=discord.Color.blue()
            )
            
            history_text = ""
            for i, watch in enumerate(user_watches[:15]):  # Show last 15
                completion_emoji = "✅" if watch.is_completed else "⏸️"
                date_str = watch.start_time.strftime("%m/%d")
                duration = f"{watch.watch_duration_minutes}m" if watch.watch_duration_minutes > 0 else "N/A"
                
                history_text += f"{completion_emoji} **{watch.movie_title}** - {date_str} ({duration})\n"
            
            embed.description = history_text or "No movies watched yet."
            
            # Add stats
            total_watches = len(user_watches)
            completed_watches = len([w for w in user_watches if w.is_completed])
            total_time = sum(w.watch_duration_minutes for w in user_watches)
            
            embed.add_field(
                name="📊 Stats",
                value=f"**{total_watches}** movies watched\n**{completed_watches}** completed\n**{total_time//60:.0f}h {total_time%60}m** total time",
                inline=True
            )
            
        else:
            # Show overall bot history
            if not badge_system.watch_history:
                await ctx.send("📚 No movie history available yet.")
                return
            
            # Get unique movies sorted by most recent watch
            movie_watches = {}
            for watch in badge_system.watch_history:
                if watch.movie_title not in movie_watches or watch.start_time > movie_watches[watch.movie_title].start_time:
                    movie_watches[watch.movie_title] = watch
            
            recent_movies = sorted(movie_watches.values(), key=lambda x: x.start_time, reverse=True)
            
            embed = discord.Embed(
                title="📚 Recent Movies Played by Bot",
                description="Movies watched during marathons",
                color=discord.Color.purple()
            )
            
            history_text = ""
            for i, watch in enumerate(recent_movies[:20]):  # Show last 20 unique movies
                date_str = watch.start_time.strftime("%m/%d/%y")
                year_str = f" ({watch.year})" if watch.year else ""
                
                # Count total watchers for this movie
                watchers = len([w for w in badge_system.watch_history if w.movie_title == watch.movie_title])
                watcher_text = f" - {watchers} watcher{'s' if watchers != 1 else ''}"
                
                history_text += f"**{watch.movie_title}**{year_str} - {date_str}{watcher_text}\n"
            
            embed.description = history_text
            
            # Add overall stats
            total_unique_movies = len(movie_watches)
            total_watch_sessions = len(badge_system.watch_history)
            
            embed.add_field(
                name="📊 Overall Stats",
                value=f"**{total_unique_movies}** unique movies\n**{total_watch_sessions}** total watch sessions",
                inline=True
            )
        
        await ctx.send(embed=embed)

    @commands.command(name="moviestats")
    async def movie_statistics(self, ctx: commands.Context):
        """Show comprehensive movie statistics."""
        
        if not hasattr(self.movie_state, 'badge_system') or not self.movie_state.badge_system:
            await ctx.send("❌ Badge system not available - movie statistics not tracked.")
            return
        
        badge_system = self.movie_state.badge_system
        
        if not badge_system.watch_history:
            await ctx.send("📊 No movie data available yet.")
            return
        
        embed = discord.Embed(
            title="📊 ClankerTV Movie Statistics",
            color=discord.Color.gold()
        )
        
        # Limit data processing to prevent freezing - only process last 1000 watches
        watch_data = badge_system.watch_history[-1000:] if len(badge_system.watch_history) > 1000 else badge_system.watch_history
        
        # Basic stats
        total_watches = len(watch_data)
        
        # Build all stats in one pass to ensure consistency
        unique_plays = set()
        unique_movies = set()
        unique_watchers = set()
        movie_play_counts = {}
        genre_counts = {}
        year_counts = {}
        
        completed_watches = 0
        total_minutes = 0
        
        for watch in watch_data:
            # Track basic stats
            unique_movies.add(watch.movie_title)
            unique_watchers.add(watch.user_id)
            
            if watch.is_completed:
                completed_watches += 1
            
            if watch.watch_duration_minutes and watch.watch_duration_minutes > 0:
                total_minutes += watch.watch_duration_minutes
            
            # Group simultaneous watches as one "play"
            play_key = f"{watch.movie_title}-{watch.start_time.strftime('%Y%m%d%H%M')}"
            
            if play_key not in unique_plays:
                unique_plays.add(play_key)
                
                # Count movie plays
                movie_play_counts[watch.movie_title] = movie_play_counts.get(watch.movie_title, 0) + 1
                
                # Count genres (only once per unique play)
                for genre in watch.genres:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
                
                # Count decades (only once per unique play)
                if watch.year:
                    decade = (watch.year // 10) * 10
                    year_counts[f"{decade}s"] = year_counts.get(f"{decade}s", 0) + 1
        
        unique_movie_count = len(unique_movies)
        unique_movie_plays = len(unique_plays)
        unique_watcher_count = len(unique_watchers)
        completion_rate = (completed_watches / total_watches * 100) if total_watches > 0 else 0
        
        embed.add_field(
            name="🎬 Movies",
            value=f"**{unique_movie_count}** unique movies\n**{unique_movie_plays}** times played\n**{total_watches}** total watches\n**{completion_rate:.1f}%** completion rate",
            inline=True
        )
        
        embed.add_field(
            name="👥 Users",
            value=f"**{unique_watcher_count}** unique watchers\n**{total_minutes//60:.0f}h {total_minutes%60}m** total watched",
            inline=True
        )
        
        # Most watched movie
        if movie_play_counts:
            most_watched = max(movie_play_counts.items(), key=lambda x: x[1])
            embed.add_field(
                name="🏆 Most Watched",
                value=f"**{most_watched[0]}**\n({most_watched[1]} times)",
                inline=True
            )
        
        if genre_counts:
            top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            genre_text = "\n".join([f"**{genre}**: {count}" for genre, count in top_genres])
            embed.add_field(
                name="🎭 Top Genres",
                value=genre_text,
                inline=True
            )
        
        # Year breakdown (already calculated in single pass above)
        if year_counts:
            top_decades = sorted(year_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            decade_text = "\n".join([f"**{decade}**: {count}" for decade, count in top_decades])
            embed.add_field(
                name="📅 Top Decades",
                value=decade_text,
                inline=True
            )
        
        # Recent activity
        recent_watches = sorted(watch_data, key=lambda x: x.start_time, reverse=True)[:3]
        if recent_watches:
            recent_text = ""
            for watch in recent_watches:
                date_str = watch.start_time.strftime("%m/%d")
                recent_text += f"**{watch.movie_title}** - {date_str}\n"
            
            embed.add_field(
                name="📅 Recent Activity",
                value=recent_text,
                inline=True
            )
        
        # Add note if data was limited
        if len(badge_system.watch_history) > 1000:
            embed.set_footer(text=f"Showing stats from last 1000 watches (of {len(badge_system.watch_history)} total)")
        
        await ctx.send(embed=embed)

    @commands.command(name="topwatchers")
    async def top_watchers(self, ctx: commands.Context):
        """Show leaderboard of top movie watchers."""
        
        if not hasattr(self.movie_state, 'badge_system') or not self.movie_state.badge_system:
            await ctx.send("❌ Badge system not available - watcher data not tracked.")
            return
        
        badge_system = self.movie_state.badge_system
        
        if not badge_system.user_stats:
            await ctx.send("👥 No watcher data available yet.")
            return
        
        # Get leaderboard from badge system
        leaderboard = badge_system.get_leaderboard("total_movies", limit=10)
        
        if not leaderboard:
            await ctx.send("👥 No watcher statistics available yet.")
            return
        
        embed = discord.Embed(
            title="🏆 Top Movie Watchers",
            description="Users who have watched the most movies",
            color=discord.Color.gold()
        )
        
        leaderboard_text = ""
        for i, (user_stats, rank) in enumerate(leaderboard):
            # Get user object for display name
            user = self.bot.get_user(user_stats.user_id)
            username = user.display_name if user else user_stats.username
            
            # Medal emojis for top 3
            if rank == 1:
                emoji = "🥇"
            elif rank == 2:
                emoji = "🥈"  
            elif rank == 3:
                emoji = "🥉"
            else:
                emoji = f"{rank}."
            
            # Stats
            movies = user_stats.total_movies
            hours = user_stats.total_watch_time_hours
            completion = user_stats.average_completion_rate
            
            leaderboard_text += f"{emoji} **{username}**\n"
            leaderboard_text += f"    {movies} movies • {hours:.1f}h • {completion:.0f}% completion\n\n"
        
        embed.description = leaderboard_text
        
        await ctx.send(embed=embed)

    @commands.command(name="starttracking")
    @commands.has_permissions(administrator=True)
    async def start_tracking_current(self, ctx: commands.Context):
        """Manually start tracking current watchers if startup detection failed."""
        
        if not self.plex_service.is_connected():
            await ctx.send("❌ Plex is not connected")
            return
        
        # Check for active movie sessions
        try:
            sessions = self.plex_service.get_current_sessions()
            movie_sessions = [s for s in sessions if s.type == "movie"]
            
            if not movie_sessions:
                await ctx.send("❌ No active movie sessions found on Plex")
                return
            
            current_movie_session = movie_sessions[0]
            movie_title = current_movie_session.title
            
            # Set current movie
            self.movie_state.set_current_movie(movie_title)
            
            # Get voice channel members
            voice_channel = discord.utils.get(ctx.guild.voice_channels, name="General")
            if not voice_channel:
                # Try to find any voice channel with members
                for channel in ctx.guild.voice_channels:
                    if len(channel.members) > 0:
                        voice_channel = channel
                        break
            
            if not voice_channel or len(voice_channel.members) == 0:
                await ctx.send(f"❌ No users found in voice channels")
                return
            
            # Get session info for position tracking
            session_info = await self.plex_service.get_enhanced_session_info()
            
            # Get movie metadata
            movie_info = await self.plex_service.get_movie_metadata(movie_title)
            genres = movie_info.get('genres', ['Horror']) if movie_info else ['Horror']
            year = movie_info.get('year') if movie_info else None
            director = movie_info.get('director') if movie_info else None
            
            # Start tracking for all voice channel members
            started_count = 0
            for member in voice_channel.members:
                if member.bot:  # Skip bots
                    continue
                    
                try:
                    # Get position data for accurate tracking
                    movie_duration_ms = session_info.get('duration_ms') if session_info else None
                    join_position_ms = session_info.get('current_position_ms') if session_info else None
                    
                    self.movie_state.badge_system.start_watching(
                        user_id=member.id,
                        username=member.display_name,
                        movie_title=movie_title,
                        genres=genres,
                        year=year,
                        director=director,
                        movie_duration_ms=movie_duration_ms,
                        join_position_ms=join_position_ms
                    )
                    started_count += 1
                    
                except Exception as e:
                    print(f"Error starting tracking for {member.display_name}: {e}")
            
            if started_count > 0:
                progress = ((current_movie_session.viewOffset or 0) / (current_movie_session.duration or 1)) * 100
                
                embed = discord.Embed(
                    title="✅ Manual Tracking Started",
                    description=f"Started tracking **{started_count}** users",
                    color=discord.Color.green()
                )
                embed.add_field(name="🎬 Movie", value=movie_title, inline=True)
                embed.add_field(name="📊 Progress", value=f"{progress:.1f}%", inline=True)
                embed.add_field(name="🎤 Voice Channel", value=voice_channel.name, inline=True)
                
                # List tracked users
                user_list = []
                for member in voice_channel.members:
                    if not member.bot:
                        user_list.append(member.display_name)
                
                if user_list:
                    embed.add_field(
                        name="👥 Tracking Users",
                        value="\n".join(user_list),
                        inline=False
                    )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ No users started tracking (all bots or errors occurred)")
                
        except Exception as e:
            await ctx.send(f"❌ Error starting manual tracking: {e}")

    @commands.command(name="activewatches")
    async def show_active_watches(self, ctx: commands.Context):
        """Show current active watch sessions in memory."""
        
        active_watches = self.movie_state.badge_system.active_watches
        
        if not active_watches:
            embed = discord.Embed(
                title="📺 No Active Watches",
                description="No users are currently being tracked.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return
        
        # Get current movie position once (for efficiency)
        current_position_ms = None
        try:
            if self.plex_service.is_connected():
                current_session_info = await self.plex_service.get_enhanced_session_info()
                current_position_ms = current_session_info.get('current_position_ms') if current_session_info else None
        except Exception:
            pass  # Will use fallback calculation
        
        # Count excluding streaming account
        from config import STREAMING_ACCOUNT_NAME
        real_watchers = [w for w in active_watches.values() 
                        if w.username.lower() != STREAMING_ACCOUNT_NAME.lower()]
        
        embed = discord.Embed(
            title="👥 Active Watch Sessions",
            description=f"Currently tracking **{len(real_watchers)}** users",
            color=discord.Color.green()
        )
        
        # Show current movie if available
        if self.movie_state.current_movie:
            movie_info = self.movie_state.current_movie
            if current_position_ms:
                current_mins = current_position_ms // (1000 * 60)
                movie_info += f" (at {current_mins}m)"
            
            embed.add_field(
                name="🎬 Current Movie",
                value=movie_info,
                inline=False
            )
        
        # List all active watchers with their accurate watch times (excluding streaming account)
        watcher_info = []
        for user_id, watch in active_watches.items():
            try:
                user = self.bot.get_user(user_id)
                username = user.display_name if user else watch.username
                
                # Skip streaming account
                if watch.username.lower() == STREAMING_ACCOUNT_NAME.lower():
                    continue
                
                # Calculate actual watch duration based on movie content seen
                if current_position_ms and watch.join_position_ms is not None:
                    # Calculate actual movie content watched (accurate method)
                    content_watched_ms = max(0, current_position_ms - watch.join_position_ms)
                    duration_mins = int(content_watched_ms / (1000 * 60))
                    duration_type = "watched"
                else:
                    # Fallback to time-based calculation
                    from datetime import datetime, timezone
                    if watch.start_time.tzinfo is None:
                        start_time = watch.start_time.replace(tzinfo=timezone.utc)
                    else:
                        start_time = watch.start_time
                    duration = datetime.now(timezone.utc) - start_time
                    duration_mins = int(duration.total_seconds() / 60)
                    duration_type = "tracking"
                
                # Format position info
                position_info = ""
                if watch.join_position_ms is not None:
                    join_mins = watch.join_position_ms // (1000 * 60)
                    position_info = f" (joined at {join_mins}m)"
                
                watcher_info.append(f"**{username}** - {duration_mins}m {duration_type}{position_info}")
                
            except Exception as e:
                watcher_info.append(f"User {user_id} - tracking error")
        
        if watcher_info:
            # Split into chunks if too many users
            chunk_size = 10
            for i in range(0, len(watcher_info), chunk_size):
                chunk = watcher_info[i:i + chunk_size]
                field_name = "👤 Watchers" if i == 0 else f"👤 Watchers (cont. {i//chunk_size + 1})"
                embed.add_field(
                    name=field_name,
                    value="\n".join(chunk),
                    inline=False
                )
        
        # Add next auto-save info
        embed.add_field(
            name="💾 Auto-Save",
            value=f"Data auto-saves every {AUTO_SAVE_INTERVAL_MINUTES} minutes",
            inline=True
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="rate")
    async def rate_movie(self, ctx: commands.Context, rating: int, *, movie_title: str):
        """Rate a movie from 1-10 stars. Usage: !rate 8 The Shining"""
        
        if not hasattr(self.movie_state, 'badge_system') or not self.movie_state.badge_system:
            await ctx.send("❌ Badge system not available - ratings not supported.")
            return
        
        # Validate rating
        if not (1 <= rating <= 10):
            await ctx.send("❌ Rating must be between 1 and 10 stars!")
            return
        
        badge_system = self.movie_state.badge_system
        
        try:
            success = badge_system.rate_movie(ctx.author.id, ctx.author.display_name, movie_title, rating)
            
            if success:
                # Get rating object for display
                user_rating = badge_system.get_user_rating(ctx.author.id, movie_title)
                
                embed = discord.Embed(
                    title="⭐ Movie Rated!",
                    description=f"You rated **{movie_title}** {rating}/10 stars!",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name=f"{user_rating.rating_emoji} {user_rating.rating_text}",
                    value=f"{rating}/10 stars",
                    inline=False
                )
                
                # Show average rating if other people rated it
                avg_rating = badge_system.get_average_rating(movie_title)
                all_ratings = badge_system.get_movie_ratings(movie_title)
                
                if len(all_ratings) > 1:
                    embed.add_field(
                        name="📊 Community Rating", 
                        value=f"{avg_rating:.1f}/10 ({len(all_ratings)} ratings)",
                        inline=True
                    )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ You've already rated **{movie_title}**!")
                
        except ValueError as e:
            await ctx.send(f"❌ {e}")
        except Exception as e:
            await ctx.send(f"❌ Error rating movie: {e}")

    @commands.command(name="ratings")
    async def show_ratings(self, ctx: commands.Context, *, movie_title: str = None):
        """Show ratings for a movie or all movies. Usage: !ratings [movie name]"""
        
        if not hasattr(self.movie_state, 'badge_system') or not self.movie_state.badge_system:
            await ctx.send("❌ Badge system not available - ratings not supported.")
            return
        
        badge_system = self.movie_state.badge_system
        
        if movie_title:
            # Show ratings for specific movie
            ratings = badge_system.get_movie_ratings(movie_title)
            
            if not ratings:
                await ctx.send(f"📊 No ratings found for **{movie_title}**")
                return
            
            avg_rating = badge_system.get_average_rating(movie_title)
            
            embed = discord.Embed(
                title=f"⭐ Ratings for {movie_title}",
                description=f"Average: **{avg_rating:.1f}/10** ({len(ratings)} ratings)",
                color=discord.Color.blue()
            )
            
            # Show individual ratings
            rating_text = ""
            for rating in sorted(ratings, key=lambda x: x.rating, reverse=True):
                user = self.bot.get_user(rating.user_id)
                username = user.display_name if user else rating.username
                rating_text += f"{rating.rating_emoji} **{username}** - {rating.rating}/10 ({rating.rating_text})\n"
            
            embed.add_field(name="👥 User Ratings", value=rating_text, inline=False)
            
            await ctx.send(embed=embed)
            
        else:
            # Show all movie ratings
            all_rated_movies = badge_system.get_all_rated_movies()
            
            if not all_rated_movies:
                await ctx.send("📊 No movie ratings yet! Use `!rate <1-10> <movie>` to rate a movie.")
                return
            
            # Sort by average rating
            sorted_movies = sorted(all_rated_movies.items(), 
                                 key=lambda x: x[1]['average_rating'], reverse=True)
            
            embed = discord.Embed(
                title="⭐ All Movie Ratings",
                description=f"{len(sorted_movies)} movies rated by the community",
                color=discord.Color.gold()
            )
            
            # Show top rated movies (limit to prevent embed overflow)
            rating_text = ""
            for i, (movie_title, data) in enumerate(sorted_movies[:15]):
                avg_rating = data['average_rating']
                total_ratings = data['total_ratings']
                
                # Get emoji for average rating
                rating_emoji = "⭐"
                if avg_rating >= 9:
                    rating_emoji = "👑"
                elif avg_rating >= 7:
                    rating_emoji = "🔥"
                elif avg_rating >= 5:
                    rating_emoji = "😊"
                elif avg_rating >= 3:
                    rating_emoji = "😐"
                else:
                    rating_emoji = "💀"
                
                rating_text += f"{rating_emoji} **{movie_title}** - {avg_rating:.1f}/10 ({total_ratings})\n"
            
            embed.add_field(name="🏆 Top Rated Movies", value=rating_text, inline=False)
            
            if len(sorted_movies) > 15:
                embed.set_footer(text=f"Showing top 15 of {len(sorted_movies)} rated movies")
            
            await ctx.send(embed=embed)

    @commands.command(name="myratings")
    async def show_my_ratings(self, ctx: commands.Context):
        """Show your movie ratings."""
        
        if not hasattr(self.movie_state, 'badge_system') or not self.movie_state.badge_system:
            await ctx.send("❌ Badge system not available - ratings not supported.")
            return
        
        badge_system = self.movie_state.badge_system
        user_ratings = badge_system.get_user_ratings(ctx.author.id)
        
        if not user_ratings:
            await ctx.send("📊 You haven't rated any movies yet! Use `!rate <1-10> <movie>` to rate a movie.")
            return
        
        # Sort by rating (highest first)
        sorted_ratings = sorted(user_ratings, key=lambda x: x.rating, reverse=True)
        
        embed = discord.Embed(
            title=f"⭐ {ctx.author.display_name}'s Movie Ratings",
            description=f"You've rated {len(user_ratings)} movies",
            color=discord.Color.purple()
        )
        
        # Calculate user's average rating
        avg_user_rating = sum(r.rating for r in user_ratings) / len(user_ratings)
        embed.add_field(
            name="📊 Your Average",
            value=f"{avg_user_rating:.1f}/10 stars",
            inline=True
        )
        
        # Show ratings in chunks
        rating_text = ""
        for rating in sorted_ratings[:20]:  # Limit to prevent overflow
            rating_text += f"{rating.rating_emoji} **{rating.movie_title}** - {rating.rating}/10\n"
        
        embed.add_field(name="🎬 Your Ratings", value=rating_text, inline=False)
        
        if len(sorted_ratings) > 20:
            embed.set_footer(text=f"Showing top 20 of {len(sorted_ratings)} rated movies")
        
        await ctx.send(embed=embed)

    @commands.command(name="addmovie")
    async def add_movie_to_history(self, ctx: commands.Context, *, movie_info: str):
        """Manually add a movie to your watch history. Usage: !addmovie The Shining (1980) [Horror] [Stanley Kubrick]"""
        
        if not hasattr(self.movie_state, 'badge_system') or not self.movie_state.badge_system:
            await ctx.send("❌ Badge system not available - cannot add movies to history.")
            return
        
        # Parse movie info - basic format: "Title (Year) [Genre] [Director]"
        # Everything before first ( is title
        # Year in () 
        # Genres in []
        # Director in []
        
        import re
        
        # Extract movie title (everything before first parenthesis or bracket)
        title_match = re.match(r'^([^(\[]+)', movie_info.strip())
        movie_title = title_match.group(1).strip() if title_match else movie_info.strip()
        
        # Extract year
        year_match = re.search(r'\((\d{4})\)', movie_info)
        year = int(year_match.group(1)) if year_match else None
        
        # Extract genres (everything in first set of brackets)
        genre_match = re.search(r'\[([^\]]+)\]', movie_info)
        genres = [g.strip() for g in genre_match.group(1).split(',')] if genre_match else ["Horror"]
        
        # Extract director (everything in second set of brackets)
        director_matches = re.findall(r'\[([^\]]+)\]', movie_info)
        director = director_matches[1] if len(director_matches) > 1 else None
        
        badge_system = self.movie_state.badge_system
        
        try:
            success = badge_system.add_manual_watch(
                user_id=ctx.author.id,
                username=ctx.author.display_name,
                movie_title=movie_title,
                genres=genres,
                year=year,
                director=director
            )
            
            if success:
                embed = discord.Embed(
                    title="✅ Movie Added to History",
                    description=f"**{movie_title}** has been added to your watch history",
                    color=discord.Color.green()
                )
                
                if year:
                    embed.add_field(name="📅 Year", value=str(year), inline=True)
                if genres:
                    embed.add_field(name="🎭 Genres", value=", ".join(genres), inline=True)
                if director:
                    embed.add_field(name="🎬 Director", value=director, inline=True)
                
                embed.add_field(
                    name="💡 Next Step",
                    value=f"You can now rate this movie with `!rate <1-10> {movie_title}`",
                    inline=False
                )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ **{movie_title}** is already in your watch history!")
                
        except Exception as e:
            await ctx.send(f"❌ Error adding movie: {e}")
            
        # Show usage example
        if movie_info.strip() == "help":
            help_embed = discord.Embed(
                title="📚 Add Movie Help",
                description="Add a movie to your watch history manually",
                color=discord.Color.blue()
            )
            help_embed.add_field(
                name="📝 Format",
                value="`!addmovie Title (Year) [Genres] [Director]`",
                inline=False
            )
            help_embed.add_field(
                name="📋 Examples",
                value=(
                    "`!addmovie The Shining (1980) [Horror, Thriller] [Stanley Kubrick]`\n"
                    "`!addmovie Halloween (1978) [Horror] [John Carpenter]`\n"
                    "`!addmovie Hereditary (2018) [Horror]`\n"
                    "`!addmovie The Conjuring`"
                ),
                inline=False
            )
            help_embed.add_field(
                name="ℹ️ Notes",
                value="- Only title is required\n- Year, genres, and director are optional\n- Use commas to separate multiple genres",
                inline=False
            )
            
            await ctx.send(embed=help_embed)

    @commands.command(name="repair")
    async def repair_movie_watch(self, ctx: commands.Context, *, movie_title: str):
        """Add a movie you watched in the channel to your history with Plex metadata. Usage: !repair The Shining"""
        
        if not hasattr(self.movie_state, 'badge_system') or not self.movie_state.badge_system:
            await ctx.send("❌ Badge system not available - cannot repair movie history.")
            return
        
        if not self.plex_service or not self.plex_service.is_connected():
            await ctx.send("❌ Plex service not available - cannot fetch movie metadata.")
            return
        
        # Show loading message
        loading_msg = await ctx.send(f"🔍 Searching for **{movie_title}** in Plex library...")
        
        try:
            # Search for the movie in Plex library
            movie_info = await self.plex_service.get_movie_metadata(movie_title)
            
            if not movie_info:
                await loading_msg.edit(content=f"❌ **{movie_title}** not found in Plex library. Try using the exact title or use `!addmovie` for manual entry.")
                return
            
            # Extract metadata from Plex
            title = movie_info.get('title', movie_title)
            year = movie_info.get('year')
            genres = movie_info.get('genres', ['Horror'])
            director = movie_info.get('director')
            duration_minutes = movie_info.get('duration_minutes')
            
            badge_system = self.movie_state.badge_system
            
            # Check if user already has this movie in their history
            existing_watches = [w for w in badge_system.watch_history 
                             if w.user_id == ctx.author.id and w.movie_title.lower() == title.lower()]
            
            if existing_watches:
                await loading_msg.edit(content=f"⚠️ You already have **{title}** in your watch history! Use `!history {ctx.author.display_name}` to see your movies.")
                return
            
            # Add the movie as a completed watch
            success = badge_system.add_manual_watch(
                user_id=ctx.author.id,
                username=ctx.author.display_name,
                movie_title=title,
                genres=genres,
                year=year,
                director=director,
                duration_minutes=duration_minutes,  # Assume full watch
                completion_percentage=100.0  # Assume completed
            )
            
            if success:
                embed = discord.Embed(
                    title="🔧 Movie Repaired to History",
                    description=f"**{title}** has been added to your watch history with Plex metadata!",
                    color=discord.Color.green()
                )
                
                # Show movie details
                if year:
                    embed.add_field(name="📅 Year", value=str(year), inline=True)
                if genres:
                    embed.add_field(name="🎭 Genres", value=", ".join(genres), inline=True)
                if director:
                    embed.add_field(name="🎬 Director", value=director, inline=True)
                if duration_minutes:
                    embed.add_field(name="⏱️ Duration", value=f"{duration_minutes} minutes", inline=True)
                
                # Show updated stats
                user_stats = badge_system.user_stats.get(ctx.author.id)
                if user_stats:
                    total_movies = user_stats.total_movies
                    total_time_hours = user_stats.total_watch_time_hours
                    embed.add_field(
                        name="📊 Updated Stats",
                        value=f"Total movies: **{total_movies}**\nTotal time: **{total_time_hours:.1f}h**",
                        inline=True
                    )
                
                embed.add_field(
                    name="💡 Next Steps",
                    value=f"• Rate it: `!rate <1-10> {title}`\n• View history: `!history {ctx.author.display_name}`",
                    inline=False
                )
                
                await loading_msg.edit(content=None, embed=embed)
            else:
                await loading_msg.edit(content=f"❌ Failed to add **{title}** to your history.")
                
        except Exception as e:
            await loading_msg.edit(content=f"❌ Error repairing movie: {e}")

    @commands.group(name="hitlist", invoke_without_command=True)
    async def hitlist(self, ctx: commands.Context):
        """Show your personal hit list of movies you want to watch."""
        user_hit_list = self.hit_list.get_user_hit_list(ctx.author.id)
        
        if not user_hit_list:
            await ctx.send("🎯 Your hit list is empty! Use `/hitlist <movie>` to add movies you want to watch.")
            return
        
        embed = discord.Embed(
            title=f"🎯 {ctx.author.display_name}'s Hit List",
            description=f"**{len(user_hit_list)}** movies you want to watch",
            color=discord.Color.red()
        )
        
        # Show movies with interest counts
        movie_list = []
        for movie in user_hit_list:
            interest_count = self.hit_list.get_movie_interest_count(movie)
            if interest_count > 1:
                movie_list.append(f"• **{movie}** _(+{interest_count-1} others interested)_")
            else:
                movie_list.append(f"• **{movie}**")
        
        embed.add_field(
            name="Movies",
            value="\n".join(movie_list[:15]),  # Limit to avoid embed size issues
            inline=False
        )
        
        if len(user_hit_list) > 15:
            embed.add_field(
                name="",
                value=f"_...and {len(user_hit_list) - 15} more movies_",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @hitlist.command(name="add")
    async def hitlist_add(self, ctx: commands.Context, *, movie_title: str):
        """Add a movie to your hit list."""
        if not movie_title.strip():
            await ctx.send("❌ Please provide a movie title.")
            return
        
        movie_title = movie_title.strip()
        
        # Check if movie exists in Plex library (optional validation)
        horror_movies = await self.plex_service.get_horror_movies()
        if horror_movies and movie_title not in horror_movies:
            # Try to find similar movies
            similar = [m for m in horror_movies if movie_title.lower() in m.lower()]
            if similar:
                embed = discord.Embed(
                    title="🤔 Movie Not Found",
                    description=f"'{movie_title}' not found in library. Did you mean:",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="Similar Movies",
                    value="\n".join([f"• {movie}" for movie in similar[:5]]),
                    inline=False
                )
                embed.add_field(
                    name="Add Anyway?",
                    value="Use `/hitlist <movie>` if you're sure",
                    inline=False
                )
                await ctx.send(embed=embed)
                return
        
        # Add to hit list
        added = self.hit_list.add_to_hit_list(ctx.author.id, movie_title)
        
        if not added:
            await ctx.send(f"🎯 **{movie_title}** is already on your hit list!")
            return
        
        # Show success with interest count
        interest_count = self.hit_list.get_movie_interest_count(movie_title)
        
        embed = discord.Embed(
            title="🎯 Added to Hit List",
            description=f"Added **{movie_title}** to your hit list",
            color=discord.Color.green()
        )
        
        if interest_count > 1:
            embed.add_field(
                name="Interest Level",
                value=f"🔥 **{interest_count}** users want to watch this!",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @hitlist.command(name="remove")
    async def hitlist_remove(self, ctx: commands.Context, *, movie_title: str):
        """Remove a movie from your hit list."""
        if not movie_title.strip():
            await ctx.send("❌ Please provide a movie title.")
            return
        
        movie_title = movie_title.strip()
        removed = self.hit_list.remove_from_hit_list(ctx.author.id, movie_title)
        
        if not removed:
            await ctx.send(f"❌ **{movie_title}** is not on your hit list.")
            return
        
        embed = discord.Embed(
            title="🗑️ Removed from Hit List",
            description=f"Removed **{movie_title}** from your hit list",
            color=discord.Color.orange()
        )
        
        await ctx.send(embed=embed)

    @hitlist.command(name="show", aliases=["all"])
    async def hitlist_show(self, ctx: commands.Context, *, movie_title: str = None):
        """Show all movies people want to watch, or who wants to watch a specific movie."""
        
        if movie_title:
            # Show who wants to watch a specific movie
            movie_title = movie_title.strip()
            interested_users = self.hit_list.get_users_interested_in_movie(movie_title)
            
            if not interested_users:
                await ctx.send(f"❌ No one has **{movie_title}** on their hit list.")
                return
            
            embed = discord.Embed(
                title=f"🎯 Who Wants to Watch",
                description=f"**{movie_title}**",
                color=discord.Color.blue()
            )
            
            # Get usernames
            user_names = []
            for user_id in interested_users:
                try:
                    user = self.bot.get_user(user_id)
                    if user:
                        user_names.append(user.display_name)
                    else:
                        user_names.append(f"User {user_id}")
                except:
                    user_names.append(f"User {user_id}")
            
            embed.add_field(
                name=f"Interested Users ({len(interested_users)})",
                value="\n".join([f"• {name}" for name in user_names]),
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        else:
            # Show all movies with interest counts
            all_movies = self.hit_list.get_all_movies_with_interest()
            
            if not all_movies:
                await ctx.send("🎯 No movies on anyone's hit list yet!")
                return
            
            embed = discord.Embed(
                title="🎯 All Hit List Movies",
                description=f"**{len(all_movies)}** movies people want to watch",
                color=discord.Color.purple()
            )
            
            # Sort by interest count (most wanted first)
            sorted_movies = sorted(all_movies.items(), key=lambda x: x[1], reverse=True)
            
            movie_list = []
            for movie, count in sorted_movies[:20]:  # Limit to top 20
                if count > 1:
                    movie_list.append(f"• **{movie}** _({count} users)_")
                else:
                    movie_list.append(f"• **{movie}**")
            
            embed.add_field(
                name="Most Wanted Movies",
                value="\n".join(movie_list),
                inline=False
            )
            
            if len(all_movies) > 20:
                embed.add_field(
                    name="",
                    value=f"_...and {len(all_movies) - 20} more movies_",
                    inline=False
                )
            
            await ctx.send(embed=embed)


class BingoClearConfirmView(discord.ui.View):
    """Confirmation view for clearing bingo cards."""
    
    def __init__(self, user_id: int, horror_bingo_system):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.horror_bingo = horror_bingo_system
    
    @discord.ui.button(label="Yes, Clear Card", style=discord.ButtonStyle.danger)
    async def confirm_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirm clearing the bingo card."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Only the card owner can clear their card.", ephemeral=True)
            return
        
        await self.horror_bingo.clear_user_card(self.user_id)
        
        embed = discord.Embed(
            title="✅ Bingo Card Cleared",
            description="Your bingo card has been cleared. You can create a new one with `!bingo`.",
            color=discord.Color.green()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel clearing the bingo card."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Only the card owner can cancel.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="❌ Clear Cancelled",
            description="Your bingo card was not cleared.",
            color=discord.Color.red()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)


class HitListSlashCommand(commands.Cog):
    """Slash command for adding movies to hit list with autocomplete."""
    
    def __init__(self, bot: commands.Bot, plex_service: PlexService, hit_list_system):
        self.bot = bot
        self.plex_service = plex_service
        self.hit_list = hit_list_system

    async def movie_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        """Autocomplete for movie names from Plex library."""
        try:
            horror_movies = await self.plex_service.get_horror_movies()
            if not horror_movies:
                return []
            
            # Filter movies that match the current input
            return [
                app_commands.Choice(name=movie, value=movie)
                for movie in horror_movies
                if current.lower() in movie.lower()
            ][:25]  # Discord max 25 choices
        except Exception:
            return []

    @app_commands.command(
        name="hitlist",
        description="Add a movie to your hit list of movies you want to watch"
    )
    @app_commands.guilds(GUILD_ID)
    @app_commands.describe(movie_name="Pick a movie to add to your hit list")
    @app_commands.autocomplete(movie_name=movie_autocomplete)
    async def hitlist_slash(self, interaction: discord.Interaction, movie_name: str):
        """Slash command for adding movies to hit list with autocomplete."""
        
        # Add to hit list
        added = self.hit_list.add_to_hit_list(interaction.user.id, movie_name)
        
        if not added:
            await interaction.response.send_message(
                f"🎯 **{movie_name}** is already on your hit list!",
                ephemeral=True
            )
            return
        
        # Show success with interest count
        interest_count = self.hit_list.get_movie_interest_count(movie_name)
        
        if interest_count > 1:
            message = f"🎯 Added **{movie_name}** to your hit list!\n🔥 **{interest_count}** users want to watch this!"
        else:
            message = f"🎯 Added **{movie_name}** to your hit list!"
        
        await interaction.response.send_message(message, ephemeral=False)


async def setup(bot: commands.Bot, plex_service: PlexService, ai_service: AIService, movie_state: MovieState, badge_system=None):
    """Setup function to add utility commands to the bot."""
    utility_cog = UtilityCommands(bot, plex_service, ai_service, movie_state, badge_system)
    await bot.add_cog(utility_cog)
    
    # Add the hit list slash command
    await bot.add_cog(HitListSlashCommand(bot, plex_service, utility_cog.hit_list))