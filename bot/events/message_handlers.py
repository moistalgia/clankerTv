"""
Message Event Handlers
======================

Handles message-related Discord events including AI responses and slur detection.
"""

import random
import logging
from discord.ext import commands
from services.ai_service import AIService
from config import RANDOM_RESPONSE_CHANCE

logger = logging.getLogger(__name__)

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


def setup(bot: commands.Bot, ai_service: AIService):
    """Setup message event handlers."""
    
    @bot.event
    async def on_message(message):
        """Handle incoming messages for AI responses and slur detection."""
        # Don't respond to bot's own messages
        if message.author == bot.user:
            await bot.process_commands(message)
            return
        
        # Check for bot slurs and send threatening DM
        if ai_service.contains_slur(message.content):
            try:
                dm_msg = await ai_service.generate_threatening_dm(message.content)
                await message.author.send(dm_msg)
                safe_log(logger, 'info', f"Sent threatening DM to {message.author.name} for slur usage")
            except Exception as e:
                safe_log(logger, 'error', f"Failed to DM user {message.author.name}: {e}")
        
        # Random AI response (20% chance)
        elif random.random() < RANDOM_RESPONSE_CHANCE:
            try:
                safe_log(logger, 'info', f"Generating AI response to message from {message.author.name}")
                reply = await ai_service.generate_response(
                    message.content, 
                    user_id=message.author.id, 
                    username=message.author.display_name
                )
                await message.channel.send(reply)
            except Exception as e:
                safe_log(logger, 'error', f"OpenAI response failed: {e}")
                await message.channel.send(f"[X] The void is silent: {e}")
        
        # Ensure commands still work
        await bot.process_commands(message)