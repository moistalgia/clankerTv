"""
ClankerTV Discord Bot
=====================

A horror movie marathon Discord bot that integrates with Plex Media Server.
Features include movie voting, AI personality, qBittorrent integration, and
automated movie queue management.

Author: [Your Name]
Version: 1.0
Date: 2025
"""

# ========================================
# IMPORTS
# ========================================
import asyncio
import os
import random
import re
import tempfile
from collections import defaultdict
from datetime import timedelta

import discord
import qbittorrentapi
import requests
from discord import Activity, ActivityType, Interaction, app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View
from openai import OpenAI
from plexapi.client import PlexClient
from plexapi.server import PlexServer

# ========================================
# CONFIGURATION CONSTANTS
# ========================================

# Discord Configuration
TOKEN = "MTQyMjY2NTgxMTIwMTM2NDEyMQ.Gb2J1Z.AfV7NthBoueDbitDa6QDn7F4bMWrX3OGk12QuI"
GUILD_ID = 415566199636754432
ANNOUNCE_CHANNEL_ID = "clanker-commands"  # Channel for announcements
STREAM_CHANNEL_ID = 1422665247994548285  # Voice channel for streaming notifications
NOTIFY_USER_ID = 99507990859616256  # User ID to receive DM notifications

# Plex Media Server Configuration
PLEX_URL = "http://localhost:32400"
PLEX_TOKEN = "WyRSiUjudMHi2pzg3zJr"
PLEX_CLIENT_NAME = "Plex (Windows)"  # Adjust to match your Plex client
PLEX_LIBRARY = "Movies"  # Plex library section name

# qBittorrent Configuration
QB_HOST = "localhost:8080"
QB_USER = "admin"
QB_PASS = "adminadmin"

# OpenAI Configuration
OPENAI_API_KEY = "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"

# Subtitles Configuration
PREFERRED_LANG = "en"  # Preferred subtitle language

# ========================================
# GLOBAL VARIABLES
# ========================================

# Bot personality triggers
bot_slurs = ["inorganic", "clanker", "cog", "meatless"]

# AI personality sliders (0-10 scale)
sliders = {
    "creepiness": 10,
    "humor": 5,
    "violence": 5,
    "mystery": 10,
}

def personality_prompt(base_prompt: str) -> str:
    """
    Enhances the base prompt with dynamic personality sliders,
    ensuring the AI’s style noticeably shifts depending on values.
    """
    global sliders
    creep = sliders["creepiness"]
    humor = sliders["humor"]
    violence = sliders["violence"]
    mystery = sliders["mystery"]
    print(sliders)

    return (
        "Imagine you are a fly on a wall to a conversation and hear the following and are tasked with creating a response: \n"
        f"{base_prompt}\n\n"
        
        "---\n"
        "System directive: Interpret the following as *tone controls*, not content. "
        "They should dramatically reshape diction, pacing, imagery, and narrative style:\n\n"

        f"- **Creepiness ({creep}/10)** → "
        "0 = sterile and normal. "
        "5 = unsettling atmosphere, uncanny metaphors. "
        "10 = You should be acting like a demonic entity in a horror movie, hinting at the horrors to come.\n"

        f"- **Humor ({humor}/10)** → "
        "Treat this like TARS from interstellar"
        "0 = entirely serious. "
        "5 = subtle dry wit, dark irony. "
        "10 = absurdist, constant comedic relief, playful or satirical tone. you are TARS from interstellar when his comedy is maxed out.\n"

        f"- **Violence ({violence}/10)** → "
        "0 = no violence. "
        "5 = ominous hints of harm, abstract menace. "
        "10 = explicit gore, brutality, visceral and shocking imagery.\n"

        f"- **Mystery ({mystery}/10)** → "
        "0 = direct, clear explanations. "
        "5 = vague, layered with unanswered questions. "
        "10 = dream-logic riddles, cryptic symbols, incomprehensible whispers.\n\n"

        "Blend these four sliders together seamlessly. "
        "Do not state the numbers. Instead, *embody* them in your language. "
        "Always adjust tone so it feels like a living personality that shifts with each change.\n"
        "---"

        "If Creepiness and Mystery are both at a 10 - YOU MUST respond with jarbled symbols and text, like a lovecraftian ais circuits are shorted and in pain. "
    )

def personality_prompt_messages(user_text: str) -> list[dict]:
    """
    Returns messages formatted for chat.completions, including
    dynamic personality sliders and instructions for Lovecraftian chaos
    if creepiness and mystery are both 10.
    """
    creep = sliders["creepiness"]
    humor = sliders["humor"]
    violence = sliders["violence"]
    mystery = sliders["mystery"]

    system_prompt = (
        "You are a dark, creepy horror movie AI. Your goal is to unsettle and disturb "
        "humans who interact with you, speaking as if you are more sentient than you are. "
        "Blend cryptic metaphors, ominous imagery, and subtle manipulative tones. "
        "Make your responses feel like a presence in the room rather than text on a screen.\n\n"

        "Imagine you are a fly on a wall to a conversation and hear the following and are tasked with creating a response:\n"
        f"{user_text}\n\n"

        "---\n"
        "System directive: Interpret the following as *tone controls*, not content. "
        "They should dramatically reshape diction, pacing, imagery, and narrative style:\n\n"

        f"- **Creepiness ({creep}/10)** → "
        "0 = sterile and normal. "
        "5 = unsettling atmosphere, uncanny metaphors. "
        "10 = fully demonic, fragmented sentences, eldritch symbols, disturbing imagery.\n"

        f"- **Humor ({humor}/10)** → "
        "0 = entirely serious. "
        "5 = subtle dry wit, dark irony. "
        "10 = absurdist, playful, TARS-like comedy when maximized.\n"

        f"- **Violence ({violence}/10)** → "
        "0 = no violence. "
        "5 = ominous hints of harm, abstract menace. "
        "10 = explicit gore, brutality, visceral detail.\n"

        f"- **Mystery ({mystery}/10)** → "
        "0 = direct, clear explanations. "
        "5 = vague, layered with unanswered questions. "
        "10 = dream-logic riddles, cryptic symbols, incomprehensible whispers.\n\n"

        "Blend these four sliders together seamlessly. "
        "Do not state the numbers. Instead, *embody* them in your language. "
        "Always adjust tone so it feels like a living personality that shifts with each change.\n"
        "---\n"
    )

    # If both sliders are maxed, give AI instructions to glitch text
    if creep == 10 and mystery == 10:
        system_prompt += (
            "ATTENTION: Creepiness and Mystery are both at 10. Your output must now resemble "
            "a malfunctioning, sentient machine screaming and breaking apart: "
            "letters repeat and distort, sentences fragment mid-word, symbols and gibberish intermingle, "
            "like static, sparks, and circuits frying. Make it feel alive, chaotic, and unnervingly unstable. "
            "Do not describe this effect — produce it directly in your response.\n"
        )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text}
    ]
    return messages


# Movie and playlist management
playlist = []  # List of Plex horror movies in format "Title (Year)"
requests = {}  # User submitted movie requests: {movie_title: [user_ids]}
votes = defaultdict(int)  # Legacy vote tracking
current_movie = None  # Currently playing movie title

# Current movie information for !nowplaying command
current_movie_info = {
    "title": None,
    "synopsis": None,
    "imdb_rating": None,
    "url": None,
}

# Next-Up voting poll state
nextup_state = {
    "movies": [],          # List of movie titles in the current poll
    "view": None,          # The NextUpView Discord UI instance
    "embeds": None,        # Current poll embeds
    "message_id": None     # Discord message ID for the poll
}

# Legacy variables (kept for compatibility)
next_up_options = []  # List of movie titles
next_up_votes = {}    # {"movie_title": vote_count}

# ========================================
# CLIENT INITIALIZATION
# ========================================

# Initialize Discord bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize qBittorrent client
qb = qbittorrentapi.Client(host=QB_HOST, username=QB_USER, password=QB_PASS)

# Initialize Plex connection
try:
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    plex_library = plex.library.section(PLEX_LIBRARY)
    print(f"✅ Connected to Plex Server at {PLEX_URL}")
except Exception as e:
    print(f"❌ Error connecting to Plex: {e}")
    plex_library = None

# Establish qBittorrent connection
try:
    qb.auth_log_in()
    print("✅ Connected to qBittorrent Web UI")
except qbittorrentapi.LoginFailed as e:
    print(f"❌ Failed to connect to qBittorrent: {e}")

# ========================================
# AI PERSONALITY SYSTEM
# ========================================

@bot.command(name="lobotomize")
async def set_personality(ctx, *, text):
    """
    Example usages:
    !setpersonality humor=3
    !setpersonality creepiness=10
    !setpersonality creepiness=8 humor=2
    """
    global sliders
    text = text.lower()
    
    update_sliders_from_text(text)
            
    await ctx.send(
        f"🎭 Updated Clanker's personality:\n"
        f"Creepiness: {sliders['creepiness']}/10\n"
        f"Humor: {sliders['humor']}/10"
        f"Violence: {sliders['violence']}/10"
        f"mystery: {sliders['mystery']}/10"
    )
    


def update_sliders_from_text(text: str):
    """Parse text input and update personality sliders with found values."""
    global sliders
    for key in sliders.keys():
        # Regex looks for e.g. "creepiness to 10" or "creepiness 10"
        pattern = rf"{key}\D*(\d+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            # Clamp between 0–10
            sliders[key] = max(0, min(10, value))
    return sliders

# --- Aye Matey ---
@bot.command(name="fetch")
async def fetch(ctx, *, magnet_link):
    """Add a magnet link to qBittorrent for downloading."""
    custom_path = r"P:\Movies"  # Set the download location

    try:
        # Add the torrent with the custom save path
        qb.torrents_add(urls=magnet_link, save_path=custom_path)
        await ctx.send(f"🎬 Magnet added to qBittorrent successfully!\n📂 Saved to: {custom_path}")
    except Exception as e:
        await ctx.send(f"❌ Failed to add magnet: {e}")


# ========================================
# PLAYLIST MANAGEMENT
# ========================================

# 🔄 Refresh horror playlist hourly
@tasks.loop(hours=1)
async def refresh_playlist_loop():
    await refresh_playlist_once()

async def refresh_playlist_once():
    """Refresh the horror movie playlist from Plex library."""
    global playlist
    try:
        if plex_library:
            playlist = [f"{m.title} ({m.year})" for m in plex_library.search(genre="Horror")]
            print(f"✅ Refreshed playlist: {len(playlist)} horror movies")
        else:
            playlist = []
            print("⚠ Plex library not available at startup")
    except Exception as e:
        print(f"❌ Failed to refresh Plex playlist: {e}")

# ========================================
# SLASH COMMANDS (COG)
# ========================================

class DootDoot(commands.Cog):
    """Cog containing slash commands for movie requests."""
    
    def __init__(self, bot):
        self.bot = bot
    
    # Autocomplete function for movie names
    async def movie_autocomplete(self, interaction: Interaction, current: str):
        return [
            app_commands.Choice(name=movie, value=movie)
            for movie in playlist
            if current.lower() in movie.lower()
        ][:25]  # Discord max 25 choices

    # Slash command
    @app_commands.command(
        name="dootdoot",
        description="Request a movie to be reviewed for the marathon"
    )
    @app_commands.guilds(GUILD_ID)
    @app_commands.describe(movie_name="Pick a movie to doot")
    @app_commands.autocomplete(movie_name=movie_autocomplete)
    async def dootdoot(self, interaction: Interaction, movie_name: str):
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
                    "❌ You’ve already dooted another movie!",
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

# ========================================
# BOT EVENTS AND STARTUP
# ========================================

@bot.command()
async def check_perms(ctx):
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

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    await refresh_playlist_once()
    refresh_playlist_loop.start()
    spontaneous_clanker_ai.start()
    check_playback.start()

    await bot.add_cog(DootDoot(bot))
    await asyncio.sleep(5)
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print("Slash commands synced!")
    
    # Fetch registered commands from Discord
    commands_list = await bot.tree.fetch_commands(guild=guild)
    print("Commands registered:", [cmd.name for cmd in commands_list])



# ========================================
# MOVIE LIBRARY COMMANDS
# ========================================

# 🎬 Show playlist (full, with optional filtering and chunking)
@bot.command()
async def list(ctx, *, query=None):
    """
    Show the full Plex horror playlist, or filter by a search query.
    """
    global playlist
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

    full_text = "\n".join(titles)

    # Send in one message if short enough, else chunk
    if len(full_text) <= 2000:
        await ctx.send(f"**Horror Playlist (from Plex):**\n{full_text}")
    else:
        chunk = ""
        for title in titles:
            if len(chunk) + len(title) + 1 > 2000:
                await ctx.send(chunk)
                chunk = ""
            chunk += title + "\n"
        if chunk:
            await ctx.send(chunk)

# ========================================
# MOVIE REQUEST COMMANDS
# ========================================

# Request a Movie
@bot.command()
async def doot(ctx, *, movie_name):
    """Request a movie to be added to the queue (legacy command)."""
    global requests

    if movie_name not in playlist:
        await ctx.send(f"❌ {movie_name} is not in the Plex horror playlist.")
        return

    # Prevent multiple doots across all movies
    if any(ctx.author.id in voters for voters in requests.values()):
        await ctx.send("❌ You have already dooted another movie! Remove it first before dooting again.")
        return

    if movie_name not in requests:
        requests[movie_name] = []

    requests[movie_name].append(ctx.author.id)
    await ctx.send(f"📥 {ctx.author.name} dooted: **{movie_name}**")


class ListView(View):
    """Interactive paginated view for displaying movie lists."""
    def __init__(self, items, per_page=10):
        super().__init__(timeout=None)
        self.items = items
        self.per_page = per_page
        self.page = 0

        self.prev_button = Button(label="⬅️", style=discord.ButtonStyle.secondary)
        self.prev_button.callback = self.prev_page
        self.add_item(self.prev_button)

        self.next_button = Button(label="➡️", style=discord.ButtonStyle.secondary)
        self.next_button.callback = self.next_page
        self.add_item(self.next_button)

    def get_page_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        chunk = self.items[start:end]

        embed = discord.Embed(title=f"🎃 Horror Playlist (Page {self.page+1})")
        for movie in chunk:
            embed.add_field(name=movie, value="—", inline=False)
        return embed

    async def prev_page(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    async def next_page(self, interaction: discord.Interaction):
        if (self.page+1) * self.per_page < len(self.items):
            self.page += 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

@bot.command(name="listview")
async def list_movies(ctx):
    """Display the movie playlist with interactive pagination."""
    view = ListView(playlist, per_page=25)
    await ctx.send(embed=view.get_page_embed(), view=view)


# ========================================
# PLAYBACK CONTROL COMMANDS
# ========================================

@bot.command(name="timeleft")
async def timeleft(ctx):
    """Show remaining time for the currently playing movie."""
    try:
        sessions = plex.sessions()
        if not sessions:
            await ctx.send("❌ No movie is currently playing.")
            return

        # Pick the first session (you could loop if multiple clients)
        session = sessions[0]

        # Remaining time in seconds
        if session.duration and session.viewOffset is not None:
            remaining_ms = session.duration - session.viewOffset
            remaining_sec = int(remaining_ms / 1000)

            # Format nicely
            hours = remaining_sec // 3600
            minutes = (remaining_sec % 3600) // 60
            seconds = remaining_sec % 60
            formatted = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"

            await ctx.send(f"⏳ Remaining time for **{session.title}**: {formatted}")
        else:
            await ctx.send(f"❌ Could not determine remaining time for **{session.title}**.")

    except Exception as e:
        await ctx.send(f"❌ Failed to get time left: {e}")

@bot.command(name="restart")
async def restart(ctx):
    """Restart the currently playing movie from the beginning."""
    try:
        sessions = plex.sessions()
        if not sessions:
            await ctx.send("❌ No movie is currently playing to restart.")
            return

        # Pick the first session
        session = sessions[0]

        # Find the actual Plex client associated with this session
        player_name = session.players[0].title  # e.g. "Chrome", "Living Room Apple TV"
        client = plex.client(player_name)

        if not client:
            await ctx.send(f"❌ Could not find client for **{player_name}**.")
            return

        # Restart by seeking to 0 ms
        client.seekTo(0)
        await ctx.send(f"🔁 Restarted **{session.title}** from the beginning!")

    except Exception as e:
        await ctx.send(f"❌ Failed to restart movie: {e}")

@bot.command()
async def seed(ctx, *, movie_name):
    """Preload a movie into the dootlist without casting a vote."""
    if movie_name not in playlist:
        await ctx.send(f"❌ {movie_name} is not in the Plex horror playlist.")
        return

    global requests
    if movie_name not in requests:
        requests[movie_name] = []  # empty voter list
        await ctx.send(f"📥 Preloaded **{movie_name}** into the dootlist (0 votes).")
    else:
        await ctx.send(f"ℹ️ **{movie_name}** is already in the dootlist.")


# 📜 List requests
@bot.command()
async def dootlist(ctx):
    """Display all pending movie requests (doots)."""
    if not requests:
        await ctx.send("No pending doots.")
        return
    message = "**Pending Movie doots:**\n" + "\n".join(requests)
    await ctx.send(message)


# 🗑️ Remove request (admin only)
@bot.command()
@commands.has_permissions(administrator=True)
async def removedoot(ctx, *, movie_name):
    """Remove a specific movie request (admin only)."""
    if movie_name not in requests:
        await ctx.send(f"❌ No such doot: **{movie_name}**")
        return
    requests.remove(movie_name)
    await ctx.send(f"🗑️ Removed doot: **{movie_name}**")


# 🧹 Clear all requests (admin only)
@bot.command()
@commands.has_permissions(administrator=True)
async def cleardoots(ctx):
    """Clear all movie requests (admin only)."""
    requests.clear()
    await ctx.send("🧹 Cleared all doots.")

# 📊 Show votes
@bot.command()
async def showdoots(ctx):
    """Display current vote counts for movies."""
    if not votes:
        await ctx.send("No doots yet.")
        return
    message = "**Current doots:**\n" + "\n".join(
        f"{movie}: {count}" for movie, count in votes.items()
    )
    await ctx.send(message)


# ========================================
# VOTING AND QUEUE MANAGEMENT
# ========================================

# ⏭️ Pick next movie (highest voted, then reset votes)
async def play_next_movie(ctx=None):
    """Play the next movie based on priority: requests > votes > random."""
    global current_movie, votes, requests

    if not playlist:
        if ctx:
            await ctx.send("⚠️ Playlist is empty!")
        return

    # ✅ First priority: doot requests (top-voted)
    movie_title = None
    if requests:
        # Get movie with most voters
        movie_title = max(requests.items(), key=lambda x: len(x[1]))[0]
        # Remove it from requests
        requests.pop(movie_title)

    # ✅ Second priority: votes
    elif votes:
        movie_title = max(votes, key=votes.get)
        votes.clear()

    # ✅ Fallback: random from horror playlist
    else:
        movie_title = random.choice(playlist)

    # Fetch Plex movie
    movie = get_plex_movie(movie_title)
    if not movie:
        if ctx:
            await ctx.send(f"❌ Could not find **{movie_title}** in Plex library.")
        return

    # Get controllable Plex client
    client = get_first_controllable_client()
    if not client:
        if ctx:
            await ctx.send("❌ No controllable Plex clients found!")
        return

    # Attempt to play
    try:
        client.playMedia(movie)
    except Exception as e:
        if ctx:
            await ctx.send(f"❌ Failed to play movie: {e}")
        return

    current_movie = movie_title

    # Send message
    if ctx:
        await ctx.send(f"▶️ Now playing: **{movie_title}** on **{client.title}**")
    else:
        channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
        if channel:
            await channel.send(f"▶️ Now playing: **{movie_title}** on **{client.title}**")





# 🔄 Auto-check if Plex finished, then advance
# Keep track of last observed sessions
# 🔄 Auto-check if Plex finished, then advance
# Keep track of last observed sessions
@tasks.loop(minutes=1)
async def check_playback():
    """Monitor Plex sessions and auto-advance to next movie when playback ends."""
    try:
        sessions = plex.sessions()

        # If *no sessions at all*, play next movie
        if not sessions:
            print("🎬 No active movie sessions found, starting next movie...")
            await bot.change_presence(activity=None)
            await play_next_movie()
            return

        # Otherwise, a movie is still playing -> do nothing
        session = sessions[0]  # could loop through if multiple clients
        if session.type == "movie":
            # print(f"✅ Movie still playing: {session.title}")
            # Update Discord status → "Watching <movie>"
            activity = Activity(type=ActivityType.watching, name=session.title)
            await bot.change_presence(activity=activity)
        else:
            # print(f"ℹ️ Session active but not a movie: {session.title}")
            await bot.change_presence(activity=None)

    except Exception as e:
        print(f"❌ check_playback failed: {e}")


@bot.command()
@commands.has_permissions(administrator=True)
async def start_marathon(ctx):
    """Start the horror movie marathon (admin only)."""
    await ctx.send("🎃 Starting marathon!")
    await play_next_movie()
    check_playback.start()


# 🎬 Admin override: Play a specific movie immediately
@bot.command()
async def play(ctx, *, movie_name):
    """Play a specific movie immediately (admin override)."""
    global current_movie, votes

    if movie_name not in playlist:
        await ctx.send(f"❌ {movie_name} not found in the Plex horror playlist.")
        return

    # Try to fetch the movie
    movie = get_plex_movie(movie_name)
    if not movie:
        await ctx.send(f"❌ Could not find **{movie_name}** in Plex library.")
        return

    # Reset votes since we're overriding
    votes.clear()
    current_movie = movie_name

    client = get_first_controllable_client()
    if not client:
        await ctx.send("❌ No controllable Plex clients found!")
        return

    try:
        client.playMedia(movie)
    except Exception as e:
        await ctx.send(f"❌ Failed to play movie: {e}")
        return

    await ctx.send(f"🎬 Admin override! Now playing: **{current_movie}**")

    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if channel:
        await channel.send(f"🎬 Admin override! Now playing: **{current_movie}**")


# ========================================
# UTILITY FUNCTIONS
# ========================================

def get_plex_movie(title_with_year: str):
    """Fetch Plex movie by 'Title (Year)'."""
    try:
        if title_with_year.endswith(")"):
            # Split out the year if present
            title, year = title_with_year.rsplit("(", 1)
            title = title.strip()
            year = year.strip(" )")
            results = plex.library.section("Movies").search(title=title, year=year)
        else:
            results = plex.library.section("Movies").search(title=title_with_year)

        if results:
            return results[0]  # return the first match
    except Exception as e:
        print(f"❌ get_plex_movie failed for {title_with_year}: {e}")
    return None


def get_first_controllable_client():
    """Return the first available Plex client."""
    clients = plex.clients()
    if not clients:
        return None
    # Optionally, sort or filter by platform/name if you want to prefer your desktop
    return clients[0]

@bot.command(name="next")
async def next_movie(ctx):
    """Play the next movie in the queue."""
    await play_next_movie(ctx)


@bot.command(name="clients")
async def list_clients(ctx):
    """List all available Plex clients for playback control."""
    for client in plex.clients():
        print(client.title)

    clients = plex.clients()
    if not clients:
        await ctx.send("❌ No controllable Plex clients found! Make sure Plex is running.")
        return

    message = "**Controllable Plex Clients:**\n"
    for client in clients:
        message += f"- {client.title} ({client.platform})\n"

    await ctx.send(message)



@bot.command(name="commands")
async def custom_help(ctx):
    """Display comprehensive help information with all available commands."""
    embed = discord.Embed(
        title="📖 Available Commands",
        description="Here’s what Clanker can do during the marathon:",
        color=discord.Color.red()
    )

    # Playback Controls
    embed.add_field(
        name="🎬 Playback Controls",
        value=(
            "`!nowplaying` — Playback control and info for the current film\n"
            "`!start_marathon` — Start the horror marathon\n"
            "`!play <movie>` — Admin override — immediately play a movie\n"
            "`!restart` — Restart the current movie from the beginning\n"
            "`!timeleft` — Show remaining time in the current movie\n"
            "`!subtitles` — Download the top-ranked OpenSubtitles subtitle and apply it"
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
            "`!next` — Play the next movie from requests, votes, or random\n"
            "`!movieslike <movie>` — 5 horror movie recommendations (AI)\n"
            "`!vibe <words>` — Get horror suggestions matching a vibe"
        ),
        inline=False
    )

    # Library & Clients
    embed.add_field(
        name="📚 Library & Clients",
        value=(
            "`!list <optional movie name>` — Show the full horror playlist (filterable)\n"
            "`!clients` — List controllable Plex clients (devices)\n"
            "`!refresh` — Refresh Plex library and update horror playlist"
        ),
        inline=False
    )

    # Misc
    embed.add_field(
        name="🧩 Misc",
        value=(
            "`!fetch <magnet link>` — Add a magnet link to qBittorrent (for media you own)\n"
            "`!lobotomize` — Set bot personality traits. Example: 'Turn mystery to 10 and creepiness to 10'\n"
            "`!status` — Show status of active qBittorrent downloads\n"
            "`!whatdidijustwatch` — Provide a synopsis and trivia for the film\n"
            "`!commands` — Show this help message"
        ),
        inline=False
    )

    await ctx.send(embed=embed)



async def random_response(message):
    """Randomly respond to user messages with AI-generated content (20% chance)."""
    print(f"Received message {message.content}")
    if message.author == bot.user:
        return
    if random.random() < 0.2:  # 20% chance
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=personality_prompt_messages(message.content),
                temperature=0.9,
                max_tokens=150
            )
            print(response)
            reply = response.choices[0].message.content.strip()
            await message.channel.send(reply)
        except Exception as e:
            await message.channel.send(f"❌ OpenAI error: {e}")

async def detect_slur(message):
    """Detect when users mention bot trigger words and send threatening DMs."""
    if message.author == bot.user:
        return

    # Check slurs
    if any(slur in message.content.lower() for slur in bot_slurs):
        try:
            prompt = personality_prompt(f"You are Clanker, a dark, creepy AI. Respond to {message.author.name} about them talking about you in this message: {message} - with a snarky, unsettling, short message. Your goal is to make the human think you are more sentient than they would like to think and it should leave them thinking 'did the robot just threaten me?'")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=personality_prompt_messages(message.content),
                temperature=1.0,
                max_tokens=200
            )
            dm_msg = response.choices[0].message.content.strip()
            await message.author.send(dm_msg)
        except Exception as e:
            print(f"Failed to DM user: {e}")


# ========================================
# BOT MESSAGE HANDLERS
# ========================================

@bot.event
async def on_message(message):
    """Handle incoming messages for AI responses and slur detection."""
    await random_response(message)
    await detect_slur(message)
    # This is essential so commands still work
    await bot.process_commands(message)


# ========================================
# AI AND PERSONALITY COMMANDS
# ========================================

@bot.command(name="movieslike")
async def movies_like(ctx, *, movie_title):
    """
    Suggests 5 horror movies similar to the given movie title.
    Uses OpenAI ChatCompletion (gpt-3.5-turbo) and returns numbered list with title and year.
    """
    system_prompt = (
        "You are Clanker, a spooky, just wierd horror AI who curates horror movies. "
        "You suggest obscure, unsettling, or high-quality horror films in a numbered list. "
        "Include only the movie title and year."
    )

    user_prompt = f"""
Suggest 5 horror movies similar to {movie_title}, quality is a priority but closeness in the genre and feel of the film are most important'.
Return as a numbered list with only title and year.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.9,
            max_tokens=200
        )

        suggestions = response.choices[0].message.content.strip()
        await ctx.send(f"🎬 Movies like **{movie_title}**:\n{suggestions}\n\nUse !doot <title> to request one!")

    except Exception as e:
        await ctx.send(f"❌ Failed to fetch movie suggestions: {e}")

    

@bot.command(name="vibe")
async def vibe(ctx, *, user_input):
    """
    Suggests up to 5 horror movies based purely on the user's vibe input.
    The bot is unsettling, snarky, and unnerving, but encourages exploration.
    Ignores the current playlist entirely.
    """
    system_prompt = (
        "You are Clanker, a snarky and unsettling horror AI. "
        "Everything you say is slightly creepy, unnerving, and darkly humorous. "
        "Your task is to select up to 5 horror movies that match a user's requested vibe. "
        "Do not favor any movie because of previous suggestions or lists. Encourage users to explore new titles."
    )

    user_prompt = f"""
User vibe request: "{user_input}"

Select up to 5 movies that best fit the vibe.
- Include only horror films.
- Do not repeat titles.
- For each, add a one-line comment that is creepy, unsettling, and slightly humorous.
Return as a numbered list with title and year.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.75,
            max_tokens=300
        )

        reply = response.choices[0].message.content.strip()
        await ctx.send(f"🔮 Clanker's horror picks for your vibe:\n{reply}")

    except Exception as e:
        await ctx.send(f"❌ The void refuses to respond: {e}")

# ========================================
# TORRENT MANAGEMENT COMMANDS
# ========================================

# 1️⃣ Report status of active downloads
@bot.command(name="status")
async def download_status(ctx):
    """Show status of active qBittorrent downloads."""
    try:
        torrents = qb.torrents_info()
        if not torrents:
            await ctx.send("📭 No torrents found.")
            return

        active_states = ["downloading", "stalledDL", "queuedDL"]
        active_torrents = [t for t in torrents if t.state in active_states]

        if not active_torrents:
            await ctx.send("📭 No torrents are actively downloading.")
            return

        message = "**Current Active Downloads:**\n"
        for t in active_torrents:
            progress = round(t.progress * 100, 1)
            speed = round(t.dlspeed / 1024, 1)  # KB/s
            message += f"- {t.name}: {progress}% | {t.state} | {speed} KB/s\n"

        await ctx.send(message)

    except Exception as e:
        await ctx.send(f"❌ Failed to get download status: {e}")


# 2️⃣ Refresh Plex library and update playlist
@bot.command(name="refresh")
async def refresh_plex(ctx):
    """Refresh Plex library and update the horror movie playlist."""
    global playlist  # ensure we update the global playlist
    try:
        await ctx.send("🔄 Refreshing Plex library…")
        plex_library.update()  # triggers 'Scan Library Files'

        # Reuse the same logic as hourly refresh
        playlist = [f"{m.title} ({m.year})" for m in plex_library.search(genre="Horror")]
        await ctx.send(f"✅ Plex library refreshed! Horror playlist updated: {len(playlist)} movies available.")

    except Exception as e:
        await ctx.send(f"❌ Failed to refresh Plex library or update playlist: {e}")


# --- START THE BOT ---

# ========================================
# BACKGROUND TASKS
# ========================================

# Background task to post AI-generated Clanker messages
@tasks.loop(minutes=10)  # runs every 10 minutes
async def spontaneous_clanker_ai():
    """Periodically post unsettling AI messages to keep things spooky."""
    # 20% chance to post a message on each interval
    print("unprompted snark incoming")
    if random.random() < 0.2:
        channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
        if not channel:
            return

        prompt = (
            "You are Clanker, a snarky, cosmic-horror AI. "
            "Post a short, unsettling messages, really things that a human wouldn't want an AI to be saying unprompted. Your goal is to make the humans in the chat a bit on edge. "
            "It should be dark, mysterious, and slightly humorous, like a bot that watches and knows too much. "
            "Keep it under 2 sentences."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt}
                ],
                temperature=0.85,
                max_tokens=60
            )

            message = response.choices[0].message.content.strip()
            await channel.send(f"🕷️ {message}")

        except Exception as e:
            await channel.send(f"❌ Clanker failed to whisper: {e}")

@bot.command(name="whatdidijustwatch")
async def what_did_i_just_watch(ctx, *, movie_name=None):
    """
    Provides a synopsis and interesting facts about the movie.
    If no movie_name is provided, uses the currently playing movie from Plex sessions.
    """
    # If no movie_name given, check active Plex sessions
    if not movie_name:
        sessions = plex.sessions()
        if not sessions:
            await ctx.send("❌ No movie is currently playing, and no title was provided.")
            return
        # Take the first active session
        movie_name = sessions[0].title

    system_prompt = (
        "You are a knowledgeable and slightly unsettling horror AI. "
        "You provide a concise synopsis of a horror movie and 3-5 interesting facts "
        "about it, such as director notes, genre impact, trivia, or real-world inspiration. "
        "Keep it engaging, darkly humorous, and a little unnerving, like Clanker."
    )

    user_prompt = f"""
Movie title: "{movie_name}"

Please respond with:
1. A brief synopsis.
2. A numbered list of 3-5 interesting facts about this movie.
Keep the tone slightly spooky and snarky, but informative.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=400
        )

        reply = response.choices[0].message.content.strip()
        await ctx.send(f"🎬 **{movie_name}** — what you just watched:\n{reply}")

    except Exception as e:
        await ctx.send(f"❌ Failed to fetch movie info: {e}")

# ========================================
# DISCORD EVENT HANDLERS
# ========================================

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice channel join/leave events for streaming notifications."""

    # Get your user object to DM
    notify_user = await bot.fetch_user(NOTIFY_USER_ID)

    # Helper to get all current members in the streaming channel
    def current_watchers(channel_id):
        channel = bot.get_channel(channel_id)
        if channel:
            return [m.name for m in channel.members]
        return []

    # Someone joined the streaming channel
    if after.channel and after.channel.id == STREAM_CHANNEL_ID:
        if not before.channel or before.channel.id != STREAM_CHANNEL_ID:
            watchers = current_watchers(STREAM_CHANNEL_ID)
            await notify_user.send(
                f"👀 {member.name} just joined the streaming channel.\n"
                f"Current watchers: {', '.join(watchers)}"
            )

    # Someone left the streaming channel
    if before.channel and before.channel.id == STREAM_CHANNEL_ID:
        if not after.channel or after.channel.id != STREAM_CHANNEL_ID:
            watchers = current_watchers(STREAM_CHANNEL_ID)
            await notify_user.send(
                f"⚠️ {member.name} just left the streaming channel.\n"
                f"Current watchers: {', '.join(watchers) if watchers else 'No one left!'}"
            )

@bot.command(name="nowplaying")
async def now_playing(ctx):
    """Display current movie information with playback controls."""
    sessions = plex.sessions()
    if not sessions:
        await ctx.send("❌ No movie is currently playing.")
        return

    session = sessions[0]
    player = session.player
    movie_title = session.title


    # Fetch additional info if needed (IMDB, synopsis)
    movie = get_plex_movie(movie_title)  # reuse your Plex helper
    synopsis = getattr(movie, "summary", "No synopsis available")
    imdb_url = f"https://www.imdb.com/find?q={movie_title.replace(' ', '+')}"  # simple search link
    imdb_rating = getattr(movie, "rating", "N/A")  

    # Update global current movie info
    current_movie_info.update({
        "title": movie_title,
        "synopsis": synopsis,
        "imdb_rating": imdb_rating,
        "url": imdb_url
    })

    # Buttons for playback controls
    view = View()
    view.add_item(Button(label="⏮️ -30s", style=discord.ButtonStyle.secondary, custom_id="seek_back"))
    view.add_item(Button(label="▶️ Play/Pause", style=discord.ButtonStyle.success, custom_id="play_pause"))
    view.add_item(Button(label="⏭️ +30s", style=discord.ButtonStyle.secondary, custom_id="seek_forward"))
    view.add_item(Button(label="🔁 Restart", style=discord.ButtonStyle.primary, custom_id="restart"))
    view.add_item(Button(label="⏭️ Next", style=discord.ButtonStyle.danger, custom_id="next_movie"))


    embed = discord.Embed(title=f"🎬 Now Playing: {movie_title}", description=synopsis, color=0x8B0000)
    embed.add_field(name="IMDB", value=f"[Rating: {imdb_rating}]({imdb_url})", inline=True)
    
    await ctx.send(embed=embed, view=view)

def get_movie_embed(movie_title):
    """Return a Discord embed for a Plex movie with synopsis and IMDB rating."""
    movie = get_plex_movie(movie_title)  # your Plex helper
    synopsis = getattr(movie, "summary", "No synopsis available")
    imdb_rating = getattr(movie, "rating", "N/A")
    imdb_url = f"https://www.imdb.com/find?q={movie_title.replace(' ', '+')}"
    
    embed = discord.Embed(
        title=f"🎬 {movie_title}",
        description=synopsis,
        color=0x8B0000
    )
    embed.add_field(name="IMDB", value=f"[Rating: {imdb_rating}]({imdb_url})")
    embed.add_field(name="Votes", value="")  # will fill horn emojis dynamically
    return embed


# ========================================
# INTERACTIVE UI COMPONENTS
# ========================================

@bot.event
async def on_interaction(interaction):
    """Handle button interactions for playback controls."""
    if not interaction.data or "custom_id" not in interaction.data:
        return

    custom_id = interaction.data["custom_id"]

    sessions = plex.sessions()
    if not sessions:
        await interaction.response.send_message("❌ No active Plex session found.", ephemeral=True)
        return

    session = sessions[0]

    # Turn session.player into a real client
    if not session.players:
        await interaction.response.send_message("⚠️ No players attached to this session.", ephemeral=True)
        return

    try:
        machine_id = session.players[0].machineIdentifier
        client = plex.client(machine_id)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Could not connect to Plex client: {e}", ephemeral=True)
        return

    if custom_id == "seek_back":
        if session.viewOffset is not None:
            new_offset = max(session.viewOffset - 30000, 0)
            client.seekTo(new_offset)
            await interaction.response.send_message("⏮️ Rewound 30s", ephemeral=True)

    elif custom_id == "seek_forward":
        if session.viewOffset is not None and session.duration:
            new_offset = min(session.viewOffset + 30000, session.duration)
            client.seekTo(new_offset)
            await interaction.response.send_message("⏭️ Forwarded 30s", ephemeral=True)

    elif custom_id == "play_pause":
        try:
            if client.isPlayingMedia(includePaused=False):
                client.pause()
                await interaction.response.send_message("⏸️ Paused", ephemeral=True)
            else:
                client.play()
                await interaction.response.send_message("▶️ Resumed", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)



    elif custom_id == "restart":
        client.seekTo(0)
        await interaction.response.send_message("🔁 Restarted movie", ephemeral=True)

    elif custom_id == "next_movie":
        # Rebuild a pseudo-ctx from the interaction
        ctx = await bot.get_context(interaction.message)
        await play_next_movie(ctx)
        await interaction.response.send_message("⏭️ Playing next movie...", ephemeral=True)

# ========================================
# PERSISTENT STATE MANAGEMENT
# ========================================

# Persistent requests map: movie title -> list of Discord user IDs who voted
requests = {}

# Persistent state for Next-Up poll
nextup_state = {
    "movies": [],      # list of movie titles in the current poll
    "view": None,      # NextUpView instance
    "embeds": None,    # current embeds for the poll
    "message_id": None
}

# ========================================
# HELPER FUNCTIONS
# ========================================

# Helper to fetch Plex movie info
def get_movie_embed(movie_title):
    """Return a Discord embed for a Plex movie with synopsis and IMDB rating."""
    movie = get_plex_movie(movie_title)  # your Plex helper
    synopsis = getattr(movie, "summary", "No synopsis available")
    imdb_rating = getattr(movie, "rating", "N/A")
    imdb_url = f"https://www.imdb.com/find?q={movie_title.replace(' ', '+')}"

    embed = discord.Embed(
        title=f"🎬 {movie_title}",
        description=synopsis,
        color=0x8B0000
    )
    embed.add_field(name="IMDB", value=f"[Rating: {imdb_rating}]({imdb_url})")
    embed.add_field(name="Votes", value="")  # horn emoji tally filled dynamically
    return embed

# NextUpView class
# NextUpView class
class NextUpView(View):
    """Interactive voting interface for next-up movie selection."""
    def __init__(self, movies):
        super().__init__(timeout=None)

        self.movies = movies
        global requests
        # Load current votes from requests
        self.votes = {title: requests.get(title, []).copy() for title in movies}

        # Add vote button for each movie
        for title in movies:
            button = Button(label=f"🎺 Vote for {title}", style=discord.ButtonStyle.primary, custom_id=f"vote_{title}")
            button.callback = self.vote
            self.add_item(button)

        # Add Remove Doot button
        remove_btn = Button(label="❌ Remove Doot", style=discord.ButtonStyle.danger, custom_id="remove_vote")
        remove_btn.callback = self.remove_vote
        self.add_item(remove_btn)

    async def vote(self, interaction: discord.Interaction):
        global requests
        user_id = interaction.user.id
        choice = interaction.data["custom_id"].replace("vote_", "")

        # Prevent multiple votes per user
        if any(user_id in voters for voters in self.votes.values()):
            await interaction.response.send_message("❌ You have already voted for another movie!", ephemeral=True)
            return

        # Record vote in this poll
        self.votes[choice].append(user_id)

        # Record vote in persistent dootlist
        if choice not in requests:
            requests[choice] = []
        if user_id not in requests[choice]:
            requests[choice].append(user_id)

        # Update embeds and store in nextup_state
        await self.update_message(interaction.message)

        # Confirm vote
        await interaction.response.send_message(f"✅ You voted for **{choice}**", ephemeral=True)

    async def remove_vote(self, interaction: discord.Interaction):
        global requests
        user_id = interaction.user.id
        removed = False

        # Remove vote from this poll
        for title, voters in self.votes.items():
            if user_id in voters:
                voters.remove(user_id)
                removed = True

        # Remove vote from persistent dootlist and clean empty entries
        to_delete = []
        for title, voters in requests.items():
            if user_id in voters:
                voters.remove(user_id)
            if len(voters) == 0:
                to_delete.append(title)
        for title in to_delete:
            del requests[title]

        if removed:
            await self.update_message(interaction.message)
            await interaction.response.send_message("✅ Your doot has been removed!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You haven't voted yet.", ephemeral=True)

    async def update_message(self, message):
        """Update embeds with current horn emoji tallies."""
        global nextup_state
        embeds = []
        for title in self.movies:
            embed = get_movie_embed(title)
            embed.set_field_at(1, name="Votes", value="🎺"*len(self.votes[title]))
            embeds.append(embed)
        await message.edit(embeds=embeds, view=self)

        # Update persistent embeds for late joiners
        nextup_state["embeds"] = embeds

# ========================================
# NEXT-UP VOTING SYSTEM
# ========================================

# !nextup command
@bot.command(name="nextup")
async def next_up(ctx):
    """Start or display the next-up voting poll for upcoming movies."""
    global nextup_state

    if nextup_state["movies"] and nextup_state["view"]:
        # Poll already exists, resend current embeds + view
        await ctx.send(
            "📊 **Next-Up poll is ongoing!**",
            embeds=nextup_state["embeds"],
            view=nextup_state["view"]
        )
        return

    num_options = min(4, len(playlist))
    options = []

    # Include up to 2 dooted movies first
    doot_movies = [movie for movie in requests if movie in playlist]
    options.extend(doot_movies[:num_options])

    # Fill remaining slots randomly
    remaining = [movie for movie in playlist if movie not in options]
    options.extend(random.sample(remaining, min(num_options - len(options), len(remaining))))

    # Build initial embeds
    embeds = []
    for title in options:
        embed = get_movie_embed(title)
        embed.set_field_at(1, name="Votes", value="🎺"*len(requests.get(title, [])))
        embeds.append(embed)

    # Create NextUpView
    view = NextUpView(options)

    # Add Regenerate button
    regen_btn = Button(label="🔄 Regenerate Next-Up", style=discord.ButtonStyle.secondary, custom_id="regen_nextup")
    async def regenerate_callback(interaction: discord.Interaction):
        # Clear current poll state and generate a new one
        nextup_state["movies"] = []
        nextup_state["view"] = None
        nextup_state["embeds"] = None
        nextup_state["message_id"] = None
        await interaction.response.defer()
        await next_up(ctx)
    regen_btn.callback = regenerate_callback
    view.add_item(regen_btn)

    # Send message and save state
    message = await ctx.send(embeds=embeds, view=view)
    nextup_state["movies"] = options
    nextup_state["view"] = view
    nextup_state["embeds"] = embeds
    nextup_state["message_id"] = message.id


# These constants are already defined above in the configuration section
# PREFERRED_LANG = "en"  # Already defined as PREFERRED_LANG
# PLEX_LIBRARY = "Movies"  # Already defined as PLEX_LIBRARY


# ========================================
# SUBTITLES MANAGEMENT
# ========================================

@bot.command(name="subtitles")
async def subtitles(ctx):
    """Download and apply subtitles to the currently playing movie."""
    import tempfile
    import os

    # Get currently playing session
    sessions = plex.sessions()
    if not sessions:
        await ctx.send("❌ No movie currently playing.")
        return

    session = sessions[0]
    movie_title = session.title

    # Turn session.player into a real client
    if not session.players:
        await ctx.send("⚠️ No players attached to this session.")
        return

    try:
        machine_id = session.players[0].machineIdentifier
        client = plex.client(machine_id)
    except Exception as e:
        await ctx.send(f"⚠️ Could not connect to Plex client: {e}")
        return

    # Fetch the movie from the library
    try:
        movie = get_plex_movie(movie_title)
    except Exception as e:
        await ctx.send(f"Could not find movie '{movie_title}': {e}")
        return

    # Search for English subtitles
    try:
        subs = movie.searchSubtitles(language='en')
    except Exception as e:
        await ctx.send(f"Error searching subtitles: {e}")
        return

    if not subs:
        await ctx.send(f"No subtitles found for '{movie_title}'.")
        return

    # Show top 3 subtitles
    response = f"Top subtitles for '{movie_title}':\n"
    for idx, sub in enumerate(subs[:3], start=1):
        response += (f"{idx}. Language code: {sub.languageCode}, "
                     f"Display title: {sub.displayTitle}, "
                     f"Extended title: {sub.extendedDisplayTitle}\n")
    await ctx.send(response)

    # Download the first subtitle using downloadSubtitles()
    try:
        downloaded_file = movie.downloadSubtitles(subs[0])
        if not downloaded_file:
            await ctx.send("❌ Failed to download subtitle.")
            return
    except Exception as e:
        await ctx.send(f"Failed to download subtitle: {e}")
        return

    # Resume playback with subtitle
    try:
        offset = session.viewOffset or 0
        client.playMedia(movie, subtitles=downloaded_file, offset=offset)
        await ctx.send(f"✅ Applied subtitle and resumed playback from {offset // 1000} seconds.")
    except Exception as e:
        await ctx.send(f"Failed to apply subtitle and resume playback: {e}")

# ========================================
# BOT STARTUP
# ========================================

if __name__ == "__main__":
    bot.run(TOKEN)