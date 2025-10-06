"""
Movie-related Discord commands
=============================

Contains all commands for movie browsing, requesting, and playlist management.
"""

import random
from typing import Optional

import discord
from discord import app_commands, Interaction
from discord.ui import Button
from discord.ext import commands

from config import GUILD_ID, MOVIES_PER_PAGE
from services.plex_service import PlexService
from bot.ui.list_view import ListView
from bot.ui.nextup_view import NextUpView
from models.movie_state import MovieState
from bot.tasks import background_tasks


class MovieCommands(commands.Cog):
    """Cog containing movie-related commands."""
    
    def __init__(self, bot: commands.Bot, plex_service: PlexService, movie_state: MovieState):
        self.bot = bot
        self.plex_service = plex_service
        self.movie_state = movie_state

    @commands.command(name="list")
    async def list_movies(self, ctx: commands.Context, *, query: Optional[str] = None):
        """
        Show the full Plex horror playlist, or filter by a search query.
        
        Args:
            query: Optional search term to filter movies
        """
        playlist = self.movie_state.playlist
        
        if not playlist:
            await ctx.send("📭 No horror movies found in Plex.")
            return

        # Ensure all titles are strings
        titles = [str(m) for m in playlist]

        # Filter if query is provided
        if query:
            filtered = [t for t in titles if query.lower() in t.lower()]
            if not filtered:
                await ctx.send(f"❌ No movies found matching '{query}'.")
                return
            titles = filtered

        # Create text list like the original
        full_text = "\n".join(titles)
        
        # Create title based on whether filtering was used
        if query:
            title = f"**Horror Movies (Filtered: '{query}'):**\n"
        else:
            title = "**Horror Playlist (from Plex):**\n"
        
        # Send in one message if short enough, else chunk
        if len(title + full_text) <= 2000:
            await ctx.send(title + full_text)
        else:
            chunk = ""
            for title_item in titles:
                if len(chunk) + len(title_item) + 1 > 1900:  # Leave room for title
                    await ctx.send(title + chunk if not chunk else chunk)
                    title = ""  # Only send title once
                    chunk = ""
                chunk += title_item + "\n"
            if chunk:
                await ctx.send(title + chunk if title else chunk)

    @commands.command(name="doot")
    async def doot_movie(self, ctx: commands.Context, *, movie_name: str):
        """Request a movie to be added to the queue (legacy command)."""
        
        requests = self.movie_state.requests
        
        # Check if movie exists in playlist
        if movie_name not in self.movie_state.playlist:
            await ctx.send(f"❌ **{movie_name}** is not in the Plex horror playlist.")
            return

        # Prevent multiple doots across all movies
        if any(ctx.author.id in voters for voters in requests.values()):
            await ctx.send("❌ You have already dooted another movie! Remove it first before dooting again.")
            return

        if movie_name not in requests:
            requests[movie_name] = []

        requests[movie_name].append(ctx.author.id)
        await ctx.send(f"📥 {ctx.author.name} dooted: **{movie_name}**")

    @commands.command(name="seed")
    async def seed_movie(self, ctx: commands.Context, *, movie_name: str):
        """Preload a movie into the dootlist without casting a vote."""
        if movie_name not in self.movie_state.playlist:
            await ctx.send(f"❌ **{movie_name}** is not in the Plex horror playlist.")
            return

        requests = self.movie_state.requests
        if movie_name not in requests:
            requests[movie_name] = []  # empty voter list
            await ctx.send(f"📥 Preloaded **{movie_name}** into the dootlist (0 votes).")
        else:
            await ctx.send(f"ℹ️ **{movie_name}** is already in the dootlist.")

    @commands.command(name="next")
    async def next_movie(self, ctx: commands.Context):
        """Play the next movie in the queue."""
        await background_tasks.play_next_movie()
        await ctx.send("⏭️ Playing next movie...")

    @commands.command(name="nextup")
    async def next_up(self, ctx: commands.Context):
        """Start or display the next-up voting poll for upcoming movies."""
        nextup_state = self.movie_state.nextup_state

        if nextup_state.movies and nextup_state.view:
            # Poll already exists, resend current embeds + view
            await ctx.send(
                "📊 **Next-Up poll is ongoing!**",
                embeds=nextup_state.embeds,
                view=nextup_state.view
            )
            return

        playlist = self.movie_state.playlist
        if not playlist:
            await ctx.send("⚠️ Playlist is empty!")
            return

        # Generate up to 4 options
        num_options = min(4, len(playlist))
        options = []

        # Include up to 2 dooted movies first
        doot_movies = [movie for movie in self.movie_state.requests if movie in playlist]
        options.extend(doot_movies[:min(2, num_options)])

        # Fill remaining slots randomly
        remaining = [movie for movie in playlist if movie not in options]
        if remaining:
            additional_count = min(num_options - len(options), len(remaining))
            if additional_count > 0:
                options.extend(random.sample(remaining, additional_count))

        if not options:
            await ctx.send("⚠️ No movies available for voting!")
            return

        # Create NextUpView
        view = NextUpView(options, self.movie_state, self.plex_service)

        # Build initial embeds
        embeds = []
        for title in options:
            embed = await view._get_movie_embed(title)
            embeds.append(embed)

        # Add Regenerate button
        regen_btn = Button(
            label="🔄 Regenerate Next-Up",
            style=discord.ButtonStyle.secondary,
            custom_id="regen_nextup"
        )
        
        async def regenerate_callback(interaction: discord.Interaction):
            # Clear current poll state and generate a new one
            self.movie_state.clear_nextup_poll()
            await interaction.response.defer()
            await self.next_up(ctx)
        
        regen_btn.callback = regenerate_callback
        view.add_item(regen_btn)

        # Send message and save state
        message = await ctx.send(embeds=embeds, view=view)
        self.movie_state.start_nextup_poll(options, view, embeds, message.id)

    @commands.command(name="undoot")
    async def undoot_movie(self, ctx: commands.Context, *, movie_name: str):
        """Preload a movie into the dootlist without casting a vote."""
        
        requests = self.movie_state.requests
        
        if movie_name not in requests:
            await ctx.send(f"❌ **{movie_name}** is not currently in the dootlist.")
            return

        if ctx.author.id not in requests[movie_name]:
            await ctx.send(f"❌ You haven't dooted **{movie_name}**.")
            return

        requests[movie_name].remove(ctx.author.id)
        if not requests[movie_name]:  # Remove empty entry
            del requests[movie_name]

        await ctx.send(f"🗑️ {ctx.author.name} undooted: **{movie_name}**")

    @commands.command(name="dootlist")
    async def show_doot_list(self, ctx: commands.Context):
        """Show all currently dooted movies and their vote counts."""
        requests = self.movie_state.requests
        
        if not requests:
            await ctx.send("📭 No movies are currently dooted.")
            return

        embed = discord.Embed(
            title="🎺 Current Doot List",
            color=0x8B0000
        )

        for movie, voters in sorted(requests.items(), key=lambda x: len(x[1]), reverse=True):
            embed.add_field(
                name=f"🎬 {movie}",
                value=f"{'🎺' * len(voters)} ({len(voters)} votes)",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="removedoot")
    @commands.has_permissions(administrator=True)
    async def remove_doot(self, ctx: commands.Context, *, movie_name: str):
        """Remove a specific movie request (admin only)."""
        requests = self.movie_state.requests
        
        if movie_name not in requests:
            await ctx.send(f"❌ No such doot: **{movie_name}**")
            return
        
        del requests[movie_name]
        await ctx.send(f"🗑️ Removed doot: **{movie_name}**")

    @commands.command(name="cleardoots")
    @commands.has_permissions(administrator=True)
    async def clear_doots(self, ctx: commands.Context):
        """Clear all movie requests (admin only)."""
        self.movie_state.requests.clear()
        await ctx.send("🧹 Cleared all doots.")

    @commands.command(name="showdoots")
    async def show_doots(self, ctx: commands.Context):
        """Display current vote counts for movies."""
        requests = self.movie_state.requests
        
        if not requests:
            await ctx.send("No doots yet.")
            return
        
        embed = discord.Embed(
            title="🎺 Current Doots",
            color=0x8B0000
        )
        
        doot_text = ""
        for movie, voters in sorted(requests.items(), key=lambda x: len(x[1]), reverse=True):
            vote_count = len(voters)
            doot_text += f"**{movie}**: {vote_count} vote{'s' if vote_count != 1 else ''}\n"
        
        embed.description = doot_text
        await ctx.send(embed=embed)

    @commands.command(name="play")
    @commands.has_permissions(administrator=True)
    async def play_movie(self, ctx: commands.Context, *, movie_name: str):
        """Play a specific movie immediately (admin override)."""
        playlist = self.movie_state.playlist
        
        if movie_name not in playlist:
            await ctx.send(f"❌ **{movie_name}** not found in the Plex horror playlist.")
            return
        
        try:
            # Play the movie using Plex service
            result = await self.plex_service.play_movie(movie_name)
            
            if result.get('success'):
                # Clear votes since we're overriding
                self.movie_state.clear_all_votes()
                self.movie_state.set_current_movie(movie_name)
                
                await ctx.send(f"▶️ Now playing: **{movie_name}** (admin override)")
            else:
                await ctx.send(f"❌ Failed to play **{movie_name}**: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            await ctx.send(f"❌ Error playing movie: {e}")

    @commands.command(name="listview")
    async def list_view(self, ctx: commands.Context):
        """Display the movie playlist with interactive pagination."""
        playlist = self.movie_state.playlist
        
        if not playlist:
            await ctx.send("📭 No horror movies found in Plex.")
            return
        
        # Create paginated view - reuse existing ListView
        view = ListView(playlist, MOVIES_PER_PAGE)
        embed = view.get_page_embed()
        embed.title = "🎬 Horror Movie Playlist (Interactive)"
        
        message = await ctx.send(embed=embed, view=view)
        view.message = message


class DootDootSlashCommand(commands.Cog):
    """Slash command version of doot for better UX with autocomplete."""
    
    def __init__(self, bot: commands.Bot, movie_state: MovieState):
        self.bot = bot
        self.movie_state = movie_state

    async def movie_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        """Autocomplete for movie names from the playlist."""
        playlist = self.movie_state.playlist
        if not playlist:
            return []

        return [
            app_commands.Choice(name=movie, value=movie)
            for movie in playlist
            if current.lower() in movie.lower()
        ][:25]  # Discord max 25 choices

    @app_commands.command(
        name="dootdoot",
        description="Request a movie to be reviewed for the marathon"
    )
    @app_commands.guilds(GUILD_ID)
    @app_commands.describe(movie_name="Pick a movie to doot")
    @app_commands.autocomplete(movie_name=movie_autocomplete)
    async def dootdoot(self, interaction: Interaction, movie_name: str):
        """Slash command for requesting movies with autocomplete."""
        playlist = self.movie_state.playlist
        requests = self.movie_state.requests
        
        if movie_name not in playlist:
            await interaction.response.send_message(
                f"❌ {movie_name} is not in the Plex horror playlist.",
                ephemeral=True
            )
            return

        # Only allow one vote per user for now
        for voters in requests.values():
            if interaction.user.id in voters:
                await interaction.response.send_message(
                    "❌ You've already dooted another movie!",
                    ephemeral=True
                )
                return

        if movie_name not in requests:
            requests[movie_name] = []

        requests[movie_name].append(interaction.user.id)
        await interaction.response.send_message(
            f"📥 {interaction.user.name} dooted: **{movie_name}**",
            ephemeral=False
        )


async def setup(bot: commands.Bot, plex_service: PlexService, movie_state: MovieState):
    """Setup function to add movie commands to the bot."""
    await bot.add_cog(MovieCommands(bot, plex_service, movie_state))
    await bot.add_cog(DootDootSlashCommand(bot, movie_state))