"""
Playback control Discord commands
===============================

Contains all commands for controlling movie playback via Plex.
"""

import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional

from config import GUILD_ID

from services.plex_service import PlexService
from models.movie_state import MovieState


class PlaybackCommands(commands.Cog):
    """Cog containing playback control commands."""
    
    def __init__(self, bot: commands.Bot, plex_service: PlexService, movie_state: MovieState):
        self.bot = bot
        self.plex_service = plex_service
        self.movie_state = movie_state

    @commands.command(name="timeleft")
    async def time_left(self, ctx: commands.Context):
        """Show remaining time for the currently playing movie."""
        try:
            time_info = await self.plex_service.get_time_remaining()
            if time_info:
                await ctx.send(f"⏳ Remaining time for **{time_info['title']}**: {time_info['formatted_time']}")
            else:
                await ctx.send("❌ No movie is currently playing.")
        except Exception as e:
            await ctx.send(f"❌ Failed to get time left: {e}")

    @commands.command(name="restart")
    async def restart_movie(self, ctx: commands.Context):
        """Restart the currently playing movie from the beginning."""
        try:
            result = await self.plex_service.restart_current_movie()
            if result:
                await ctx.send(f"🔁 Restarted **{result}** from the beginning!")
            else:
                await ctx.send("❌ No movie is currently playing to restart.")
        except Exception as e:
            await ctx.send(f"❌ Failed to restart movie: {e}")

    @commands.command(name="nowplaying")
    async def now_playing(self, ctx: commands.Context):
        """Display current movie information with playback controls."""
        try:
            movie_info = await self.plex_service.get_current_movie_info()
            if not movie_info:
                await ctx.send("❌ No movie is currently playing.")
                return

            # Create playback control buttons
            from bot.ui.playback_view import PlaybackControlView
            view = PlaybackControlView(self.plex_service)

            # Create embed with movie information
            embed = discord.Embed(
                title=f"🎬 Now Playing: {movie_info['title']}", 
                description=movie_info.get('synopsis', 'No synopsis available'), 
                color=0x8B0000
            )
            
            if movie_info.get('imdb_rating'):
                embed.add_field(
                    name="IMDB", 
                    value=f"[Rating: {movie_info['imdb_rating']}]({movie_info.get('imdb_url', '#')})", 
                    inline=True
                )
            
            await ctx.send(embed=embed, view=view)
            
        except Exception as e:
            await ctx.send(f"❌ Failed to get current movie info: {e}")

    @commands.command(name="clients")
    async def list_clients(self, ctx: commands.Context):
        """List all available Plex clients for playback control."""
        try:
            clients = await self.plex_service.get_available_clients()
            if not clients:
                await ctx.send("❌ No controllable Plex clients found! Make sure Plex is running.")
                return

            message = "**Controllable Plex Clients:**\n"
            for client in clients:
                message += f"- {client['title']} ({client['platform']})\n"

            await ctx.send(message)
        except Exception as e:
            await ctx.send(f"❌ Failed to get Plex clients: {e}")

    @commands.command(name="subtitles")
    async def manage_subtitles(self, ctx: commands.Context):
        """Download and apply subtitles to the currently playing movie."""
        try:
            result = await self.plex_service.apply_subtitles()
            if result['success']:
                await ctx.send(f"✅ Applied subtitle and resumed playback from {result['offset']} seconds.")
            else:
                await ctx.send(f"❌ {result['message']}")
        except Exception as e:
            await ctx.send(f"❌ Failed to apply subtitles: {e}")


class PlaybackSlashCommands(commands.Cog):
    """Essential playback slash commands."""
    
    def __init__(self, bot: commands.Bot, plex_service: PlexService, movie_state: MovieState):
        self.bot = bot
        self.plex_service = plex_service
        self.movie_state = movie_state

    @app_commands.command(
        name="timeleft",
        description="Show remaining time for the currently playing movie"
    )
    @app_commands.guilds(GUILD_ID)
    async def timeleft(self, interaction: Interaction):
        """Show remaining time for the currently playing movie."""
        try:
            time_info = await self.plex_service.get_time_remaining()
            if time_info:
                await interaction.response.send_message(
                    f"⏳ Remaining time for **{time_info['title']}**: {time_info['formatted_time']}"
                )
            else:
                await interaction.response.send_message("❌ No movie is currently playing.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to check time: {e}", ephemeral=True)

    @app_commands.command(
        name="nowplaying",
        description="Show what movie is currently playing"
    )
    @app_commands.guilds(GUILD_ID)
    async def nowplaying(self, interaction: Interaction):
        """Show currently playing movie information."""
        try:
            current_info = await self.plex_service.get_current_movie_info()
            if current_info:
                embed = discord.Embed(
                    title="🎬 Now Playing",
                    description=f"**{current_info['title']}**",
                    color=discord.Color.green()
                )
                
                if 'progress' in current_info:
                    embed.add_field(
                        name="Progress",
                        value=f"{current_info['progress']}%",
                        inline=True
                    )
                
                if 'duration' in current_info:
                    embed.add_field(
                        name="Duration",
                        value=current_info['duration'],
                        inline=True
                    )
                
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("❌ No movie is currently playing.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to get current movie: {e}", ephemeral=True)

    @app_commands.command(
        name="clients",
        description="Show active Plex clients and their status"
    )
    @app_commands.guilds(GUILD_ID)
    async def clients(self, interaction: Interaction):
        """Show active Plex clients."""
        try:
            clients = await self.plex_service.get_available_clients()
            if not clients:
                await interaction.response.send_message("❌ No controllable Plex clients found! Make sure Plex is running.", ephemeral=True)
                return

            message = "**Controllable Plex Clients:**\n"
            for client in clients:
                message += f"- {client['title']} ({client['platform']})\n"

            await interaction.response.send_message(message)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to get clients: {e}", ephemeral=True)

    @app_commands.command(
        name="restart",
        description="Restart the currently playing movie from the beginning"
    )
    @app_commands.guilds(GUILD_ID)
    async def restart(self, interaction: Interaction):
        """Restart the currently playing movie."""
        try:
            result = await self.plex_service.restart_current_movie()
            if result:
                await interaction.response.send_message(f"🔁 Restarted **{result}** from the beginning!")
            else:
                await interaction.response.send_message("❌ No movie is currently playing to restart.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to restart movie: {e}", ephemeral=True)

    @app_commands.command(
        name="subtitles",
        description="Download and apply subtitles to the currently playing movie"
    )
    @app_commands.guilds(GUILD_ID)
    async def subtitles(self, interaction: Interaction):
        """Download and apply subtitles to the currently playing movie."""
        try:
            result = await self.plex_service.apply_subtitles()
            if result['success']:
                await interaction.response.send_message(f"✅ Applied subtitle and resumed playback from {result['offset']} seconds.")
            else:
                await interaction.response.send_message(f"❌ {result['message']}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to apply subtitles: {e}", ephemeral=True)


async def setup(bot: commands.Bot, plex_service: PlexService, movie_state: MovieState):
    """Setup function to add playback commands to the bot."""
    await bot.add_cog(PlaybackCommands(bot, plex_service, movie_state))
    await bot.add_cog(PlaybackSlashCommands(bot, plex_service, movie_state))