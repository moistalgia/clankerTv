"""
AI and personality-related Discord commands
==========================================

Contains commands for AI interactions, movie suggestions, and personality management.
"""

import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional

from config import GUILD_ID

from services.ai_service import AIService
from models.movie_state import MovieState
from services.plex_service import PlexService


class AICommands(commands.Cog):
    """Cog containing AI and personality commands."""
    
    def __init__(self, bot: commands.Bot, ai_service: AIService, movie_state: MovieState, plex_service: PlexService):
        self.bot = bot
        self.ai_service = ai_service
        self.movie_state = movie_state
        self.plex_service = plex_service

    @commands.command(name="lobotomize")
    async def set_personality(self, ctx: commands.Context, *, text: str):
        """
        Set bot personality traits.
        
        Example usages:
        !lobotomize humor=3
        !lobotomize creepiness=10
        !lobotomize creepiness=8 humor=2
        """
        old_sliders = self.ai_service.get_personality_sliders().copy()
        new_sliders = self.ai_service.update_personality_from_text(text)
        
        await ctx.send(
            f"🎭 Updated Clanker's personality:\n"
            f"Creepiness: {new_sliders['creepiness']}/10\n"
            f"Humor: {new_sliders['humor']}/10\n"
            f"Violence: {new_sliders['violence']}/10\n"
            f"Mystery: {new_sliders['mystery']}/10"
        )



    @commands.command(name="vibe")
    async def vibe_suggestions(self, ctx: commands.Context, *, user_input: str):
        """
        Suggests up to 5 horror movies based purely on the user's vibe input.
        The bot is unsettling, snarky, and unnerving, but encourages exploration.
        Ignores the current playlist entirely.
        """
        try:
            suggestions = await self.ai_service.get_vibe_movies(user_input)
            await ctx.send(f"🔮 Clanker's horror picks for your vibe:\n{suggestions}")
        except Exception as e:
            await ctx.send(f"❌ The void refuses to respond: {e}")

    @commands.command(name="whatdidijustwatch")
    async def what_did_i_just_watch(self, ctx: commands.Context, *, movie_name: Optional[str] = None):
        """
        Provides a synopsis and interesting facts about the movie.
        If no movie_name is provided, uses the currently playing movie from Plex sessions.
        """
        # If no movie_name given, check active Plex sessions
        if not movie_name:
            try:
                current_info = await self.plex_service.get_current_movie_info()
                if not current_info:
                    await ctx.send("❌ No movie is currently playing, and no title was provided.")
                    return
                movie_name = current_info['title']
            except Exception as e:
                await ctx.send(f"❌ Failed to get current movie: {e}")
                return

        try:
            analysis = await self.ai_service.analyze_movie(movie_name)
            await ctx.send(f"🎬 **{movie_name}** — what you just watched:\n{analysis}")
        except Exception as e:
            await ctx.send(f"❌ Failed to fetch movie info: {e}")

    @commands.command(name="endinganalysis")
    async def ending_analysis(self, ctx: commands.Context, *, movie_name: Optional[str] = None):
        """
        Provides ending analysis with interpretations and theories.
        If no movie_name is provided, uses the currently playing movie.
        Adjusts depth based on movie complexity.
        """
        # If no movie_name given, check active Plex sessions
        if not movie_name:
            try:
                current_info = await self.plex_service.get_current_movie_info()
                if not current_info:
                    await ctx.send("❌ No movie is currently playing, and no title was provided.")
                    return
                movie_name = current_info['title']
            except Exception as e:
                await ctx.send(f"❌ Failed to get current movie: {e}")
                return

        # Show loading message for longer analysis
        loading_msg = await ctx.send(f"🎬 Analyzing the ending of **{movie_name}**... This may contain spoilers!")
        
        try:
            analysis = await self.ai_service.analyze_movie_ending(movie_name)
            
            # Create embed for better formatting
            embed = discord.Embed(
                title=f"🎭 Ending Analysis: {movie_name}",
                description="⚠️ **SPOILER WARNING** - Click the spoiler tags below to reveal each section",
                color=discord.Color.dark_red()
            )
            
            # Parse analysis into structured sections with spoiler tags
            sections = self._parse_analysis_sections(analysis)
            
            # Add each section as a separate embed field with spoiler protection
            for section_name, section_content in sections.items():
                # Wrap content in spoiler tags
                spoiler_content = f"||{section_content.strip()}||"
                
                # Handle long content by splitting if necessary
                if len(spoiler_content) > 1024:
                    # Split long sections into multiple parts
                    lines = section_content.split('\n')
                    current_content = ""
                    part_num = 1
                    
                    for line in lines:
                        test_content = current_content + line + "\n"
                        if len(f"||{test_content}||") <= 1024:
                            current_content = test_content
                        else:
                            if current_content:
                                embed.add_field(
                                    name=f"{section_name} (Part {part_num})",
                                    value=f"||{current_content.strip()}||",
                                    inline=False
                                )
                                part_num += 1
                            current_content = line + "\n"
                    
                    if current_content:
                        embed.add_field(
                            name=f"{section_name} (Part {part_num})" if part_num > 1 else section_name,
                            value=f"||{current_content.strip()}||",
                            inline=False
                        )
                else:
                    embed.add_field(
                        name=section_name,
                        value=spoiler_content,
                        inline=False
                    )
            
            embed.set_footer(text="💡 Click spoiler tags to reveal • Discuss different interpretations with fellow watchers!")
            
            # Update the loading message with the analysis
            await loading_msg.edit(content=None, embed=embed)
            
        except Exception as e:
            await loading_msg.edit(content=f"❌ Failed to analyze ending: {e}")

    def _parse_analysis_sections(self, analysis: str) -> dict:
        """Parse analysis into structured sections for spoiler formatting."""
        sections = {}
        current_section = "📖 Analysis"
        current_content = ""
        
        lines = analysis.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header (starts with **)
            if line.startswith('**') and line.endswith('**') and len(line) > 4:
                # Save previous section if it has content
                if current_content.strip():
                    sections[current_section] = current_content.strip()
                
                # Start new section
                section_title = line.strip('*').strip()
                
                # Add appropriate emojis for common sections
                if "what happens" in section_title.lower():
                    current_section = "📝 What Happens"
                elif "surface" in section_title.lower() or "interpretation" in section_title.lower():
                    current_section = "🎯 Surface Interpretation"  
                elif "alternative" in section_title.lower() or "theories" in section_title.lower():
                    current_section = "🤔 Alternative Theories"
                elif "thematic" in section_title.lower() or "analysis" in section_title.lower():
                    current_section = "📚 Thematic Analysis"
                else:
                    current_section = f"📖 {section_title}"
                
                current_content = ""
            else:
                current_content += line + "\n"
        
        # Add the final section
        if current_content.strip():
            sections[current_section] = current_content.strip()
        
        # If no structured sections found, use the entire content
        if not sections:
            sections["📖 Analysis"] = analysis
        
        return sections

    @commands.command(name="catchmeup")
    async def catch_me_up(self, ctx: commands.Context):
        """
        Analyze current movie timestamp and DM the requester with plot synopsis up to that point.
        Provides spoiler-free context for viewers who joined mid-movie.
        """
        try:
            # Get current movie information and timestamp
            current_info = await self.plex_service.get_current_movie_info()
            if not current_info:
                await ctx.send("❌ No movie is currently playing.")
                return

            session = current_info.get('session')
            if not session:
                await ctx.send("❌ Could not get playback session information.")
                return

            # Calculate progress percentage and time elapsed
            if session.viewOffset is None or session.duration is None:
                await ctx.send("❌ Could not determine current playback position.")
                return

            elapsed_ms = session.viewOffset
            total_ms = session.duration
            progress_percent = (elapsed_ms / total_ms) * 100
            
            # Convert to human-readable time
            elapsed_minutes = elapsed_ms // (1000 * 60)
            elapsed_hours = elapsed_minutes // 60
            elapsed_mins_remainder = elapsed_minutes % 60
            
            if elapsed_hours > 0:
                elapsed_formatted = f"{elapsed_hours}h {elapsed_mins_remainder}m"
            else:
                elapsed_formatted = f"{elapsed_mins_remainder}m"

            movie_title = current_info['title']
            
            # Generate AI catch-up summary
            catchup_summary = await self.ai_service.generate_catchup_summary(
                movie_title, 
                progress_percent, 
                elapsed_formatted
            )
            
            # Prepare the full message
            header = f"🎬 **Catch-up for {movie_title}**\n⏱️ **Current Progress:** {elapsed_formatted} ({progress_percent:.1f}%)\n\n"
            footer = f"\n\n*This summary covers events up to the current timestamp. Enjoy the rest of the movie! 🍿*"
            full_message = header + catchup_summary + footer
            
            # Send DM to user (with chunking if needed)
            try:
                if len(full_message) <= 2000:
                    # Send as single message
                    await ctx.author.send(full_message)
                else:
                    # Send header first
                    await ctx.author.send(header.rstrip())
                    
                    # Chunk the summary content
                    remaining_summary = catchup_summary
                    
                    while remaining_summary:
                        # Calculate available space for this chunk
                        continuation_text = "\n\n*[continued...]*"
                        
                        if len(remaining_summary) + len(footer) <= 1980:  # Last chunk with footer
                            await ctx.author.send(remaining_summary + footer)
                            break
                        else:
                            # Calculate max chunk size (leave room for continuation indicator)
                            max_chunk_size = 2000 - len(continuation_text)
                            
                            if len(remaining_summary) <= max_chunk_size:
                                # This chunk fits, but we need to add continuation
                                await ctx.author.send(remaining_summary + continuation_text)
                                remaining_summary = ""
                            else:
                                # Need to break this chunk
                                chunk_text = remaining_summary[:max_chunk_size]
                                
                                # Find best break point
                                break_point = max_chunk_size
                                
                                # Try to break at paragraph (but not too small)
                                last_paragraph = chunk_text.rfind('\n\n')
                                if last_paragraph > max_chunk_size * 0.5:
                                    break_point = last_paragraph
                                else:
                                    # Try to break at sentence end
                                    for punct in ['. ', '! ', '? ']:
                                        last_sentence = chunk_text.rfind(punct)
                                        if last_sentence > max_chunk_size * 0.5:
                                            break_point = last_sentence + len(punct)
                                            break
                                    else:
                                        # Break at word boundary as last resort
                                        last_space = chunk_text.rfind(' ')
                                        if last_space > max_chunk_size * 0.7:  # Don't make too small
                                            break_point = last_space
                                
                                # Send this chunk
                                chunk_to_send = remaining_summary[:break_point].strip()
                                await ctx.author.send(chunk_to_send + continuation_text)
                                
                                # Update remaining text
                                remaining_summary = remaining_summary[break_point:].strip()
                
                # Confirm in channel (without spoilers)
                await ctx.send(f"📨 Sent catch-up summary for **{movie_title}** to your DMs, {ctx.author.mention}!")
                
            except discord.Forbidden:
                # If DM fails, send error message
                await ctx.send(
                    f"❌ Couldn't send DM to {ctx.author.mention}. "
                    f"Please enable DMs from server members to use this command."
                )
                
        except Exception as e:
            error_msg = str(e)
            if "API request error" in error_msg:
                await ctx.send(f"❌ AI service configuration issue: Please check with the bot admin.")
            elif "authentication error" in error_msg:
                await ctx.send(f"❌ AI service authentication failed: Please contact the bot admin.")
            elif "rate limit" in error_msg:
                await ctx.send(f"❌ AI service is temporarily busy. Please try again in a few moments.")
            else:
                await ctx.send(f"❌ Failed to generate catch-up summary: {error_msg}")


class MoviesLikeSlashCommand(commands.Cog):
    """Slash command version of movieslike for better UX with autocomplete."""
    
    def __init__(self, bot: commands.Bot, ai_service: AIService, movie_state: MovieState):
        self.bot = bot
        self.ai_service = ai_service
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
        name="movieslike",
        description="Get 5 horror movie recommendations similar to any movie (autocomplete shows playlist)"
    )
    @app_commands.guilds(GUILD_ID)
    @app_commands.describe(movie_title="Enter any movie title (autocomplete shows our playlist for convenience)")
    @app_commands.autocomplete(movie_title=movie_autocomplete)
    async def movieslike(self, interaction: Interaction, movie_title: str):
        """Slash command for getting similar movie recommendations. Accepts any movie title, autocomplete shows playlist for convenience."""
        try:
            # Defer response since AI calls can take time
            await interaction.response.defer()
            
            suggestions = await self.ai_service.get_similar_movies(movie_title)
            await interaction.followup.send(
                f"🎬 Movies like **{movie_title}**:\n{suggestions}\n\nUse `/dootdoot <title>` to request one!"
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to fetch movie suggestions: {e}",
                ephemeral=True
            )


class AIAnalysisSlashCommands(commands.Cog):
    """AI analysis slash commands with autocomplete."""
    
    def __init__(self, bot: commands.Bot, ai_service: AIService, movie_state: MovieState, plex_service: PlexService):
        self.bot = bot
        self.ai_service = ai_service
        self.movie_state = movie_state
        self.plex_service = plex_service

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
        name="whatdidijustwatch",
        description="Get AI analysis and interesting facts about a movie"
    )
    @app_commands.guilds(GUILD_ID)
    @app_commands.describe(movie_name="Pick a movie to analyze (leave empty for currently playing movie)")
    @app_commands.autocomplete(movie_name=movie_autocomplete)
    async def whatdidijustwatch(self, interaction: Interaction, movie_name: str = None):
        """Get AI movie analysis with autocomplete."""
        await interaction.response.defer()  # AI calls can take time
        
        # If no movie_name given, check active Plex sessions
        if not movie_name:
            try:
                current_info = await self.plex_service.get_current_movie_info()
                if not current_info:
                    await interaction.followup.send("❌ No movie is currently playing, and no title was provided.", ephemeral=True)
                    return
                movie_name = current_info['title']
            except Exception as e:
                await interaction.followup.send(f"❌ Failed to get current movie: {e}", ephemeral=True)
                return

        try:
            analysis = await self.ai_service.analyze_movie(movie_name)
            
            embed = discord.Embed(
                title=f"🎬 {movie_name}",
                description="What you just watched:",
                color=discord.Color.blue()
            )
            embed.add_field(name="AI Analysis", value=analysis[:1024], inline=False)
            if len(analysis) > 1024:
                embed.add_field(name="Continued...", value=analysis[1024:2048], inline=False)
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to fetch movie analysis: {e}", ephemeral=True)

    @app_commands.command(
        name="endinganalysis",
        description="Get AI analysis of a movie's ending with interpretations and theories"
    )
    @app_commands.guilds(GUILD_ID)
    @app_commands.describe(movie_name="Pick a movie to analyze the ending (leave empty for currently playing)")
    @app_commands.autocomplete(movie_name=movie_autocomplete)
    async def endinganalysis(self, interaction: Interaction, movie_name: str = None):
        """Get AI ending analysis with autocomplete."""
        await interaction.response.defer()  # AI calls can take time
        
        # If no movie_name given, check active Plex sessions
        if not movie_name:
            try:
                current_info = await self.plex_service.get_current_movie_info()
                if not current_info:
                    await interaction.followup.send("❌ No movie is currently playing, and no title was provided.", ephemeral=True)
                    return
                movie_name = current_info['title']
            except Exception as e:
                await interaction.followup.send(f"❌ Failed to get current movie: {e}", ephemeral=True)
                return

        try:
            analysis = await self.ai_service.analyze_movie_ending(movie_name)
            
            embed = discord.Embed(
                title=f"🎭 {movie_name} - Ending Analysis",
                description="Deep dive into the conclusion:",
                color=discord.Color.purple()
            )
            embed.add_field(name="Interpretation & Theories", value=analysis[:1024], inline=False)
            if len(analysis) > 1024:
                embed.add_field(name="Continued...", value=analysis[1024:2048], inline=False)
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to analyze movie ending: {e}", ephemeral=True)

    @app_commands.command(
        name="catchmeup",
        description="Get plot summary up to current timestamp (sent privately)"
    )
    @app_commands.guilds(GUILD_ID)
    async def catchmeup(self, interaction: Interaction):
        """Analyze current movie timestamp and DM plot synopsis up to that point."""
        await interaction.response.defer(ephemeral=True)  # This is always private
        
        try:
            # Get current movie information and timestamp
            current_info = await self.plex_service.get_current_movie_info()
            if not current_info:
                await interaction.followup.send("❌ No movie is currently playing.", ephemeral=True)
                return

            session = current_info.get('session')
            if not session:
                await interaction.followup.send("❌ Could not get playback session information.", ephemeral=True)
                return

            # Calculate progress percentage and time elapsed
            if session.viewOffset is None or session.duration is None:
                await interaction.followup.send("❌ Could not determine current playback position.", ephemeral=True)
                return

            elapsed_ms = session.viewOffset
            total_ms = session.duration
            progress_percent = (elapsed_ms / total_ms) * 100
            
            # Convert to human-readable time
            elapsed_minutes = elapsed_ms // (1000 * 60)
            elapsed_hours = elapsed_minutes // 60
            elapsed_mins_remainder = elapsed_minutes % 60
            
            if elapsed_hours > 0:
                time_str = f"{elapsed_hours}h {elapsed_mins_remainder}m"
            else:
                time_str = f"{elapsed_minutes}m"

            movie_title = current_info['title']

            # Get AI summary up to current point
            summary = await self.ai_service.generate_catchup_summary(
                movie_title, progress_percent, time_str
            )
            
            # Create embed for the summary
            embed = discord.Embed(
                title=f"📝 Catch-Up Summary: {movie_title}",
                description=f"Plot summary up to **{time_str}** ({progress_percent:.1f}% complete)",
                color=discord.Color.blue()
            )
            
            # Split summary into chunks if too long
            if len(summary) <= 1024:
                embed.add_field(name="What's Happened So Far", value=summary, inline=False)
            else:
                # Split into multiple fields
                chunks = [summary[i:i+1024] for i in range(0, len(summary), 1024)]
                for i, chunk in enumerate(chunks[:3]):  # Max 3 chunks
                    field_name = "What's Happened So Far" if i == 0 else "Continued..."
                    embed.add_field(name=field_name, value=chunk, inline=False)
            
            embed.add_field(
                name="⚠️ Spoiler-Free Zone", 
                value="This summary only covers events up to the current timestamp.",
                inline=False
            )
            
            # Send privately via followup
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to generate catch-up summary: {e}", ephemeral=True)


async def setup(bot: commands.Bot, ai_service: AIService, movie_state: MovieState, plex_service: PlexService):
    """Setup function to add AI commands to the bot."""
    await bot.add_cog(AICommands(bot, ai_service, movie_state, plex_service))
    await bot.add_cog(MoviesLikeSlashCommand(bot, ai_service, movie_state))
    await bot.add_cog(AIAnalysisSlashCommands(bot, ai_service, movie_state, plex_service))