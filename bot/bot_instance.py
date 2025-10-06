"""
Discord bot instance creation and configuration
==============================================

Creates and configures the Discord bot with all necessary intents and settings.
"""

import discord
from discord.ext import commands
from config import COMMAND_PREFIX, GUILD_ID

def create_bot() -> commands.Bot:
    """
    Create and configure the Discord bot instance.
    
    Returns:
        commands.Bot: Configured Discord bot instance
    """
    # Configure intents
    intents = discord.Intents.all()
    
    # Create bot instance
    bot = commands.Bot(
        command_prefix=COMMAND_PREFIX,
        intents=intents,
        help_command=None  # We'll use a custom help command
    )
    
    return bot

# Global bot instance
bot = create_bot()