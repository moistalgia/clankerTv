"""
Badge System Commands
====================

Commands for viewing badges, stats, leaderboards, and achievements.
"""

import discord
from discord.ext import commands
from typing import Optional
from datetime import datetime

from models.badge_system import WatchBadgeSystem, BadgeType
from services.plex_service import PlexService


class BadgeCommands(commands.Cog):
    """Cog containing badge and achievement system commands."""
    
    def __init__(self, bot: commands.Bot, badge_system: WatchBadgeSystem, plex_service: PlexService):
        self.bot = bot
        self.badge_system = badge_system
        self.plex_service = plex_service

    @commands.command(name="badges")
    async def show_badges(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Display all badges earned by a user (defaults to command author)."""
        target_user = member or ctx.author
        user_badges = self.badge_system.get_user_badges(target_user.id)
        
        if not user_badges:
            if target_user == ctx.author:
                await ctx.send("🏆 You haven't earned any badges yet! Start watching movies to unlock achievements.")
            else:
                await ctx.send(f"🏆 {target_user.display_name} hasn't earned any badges yet.")
            return
        
        # Group badges by rarity
        rarity_groups = {"legendary": [], "epic": [], "rare": [], "common": []}
        
        for badge, user_badge in user_badges:
            rarity_groups[badge.rarity].append((badge, user_badge))
        
        embed = discord.Embed(
            title=f"🏆 {target_user.display_name}'s Badge Collection",
            description=f"**{len(user_badges)} badges earned**",
            color=discord.Color.gold()
        )
        
        # Add badge fields by rarity (highest first)
        for rarity in ["legendary", "epic", "rare", "common"]:
            badges_in_rarity = rarity_groups[rarity]
            if badges_in_rarity:
                rarity_emoji = {"legendary": "👑", "epic": "💎", "rare": "⭐", "common": "🔸"}
                field_value = ""
                
                for badge, user_badge in badges_in_rarity:
                    earned_date = user_badge.earned_date.strftime("%m/%d")
                    field_value += f"{badge.emoji} **{badge.name}** *(earned {earned_date})*\n"
                
                embed.add_field(
                    name=f"{rarity_emoji[rarity]} {rarity.title()} Badges",
                    value=field_value,
                    inline=False
                )
        
        await ctx.send(embed=embed)

    @commands.command(name="stats")
    async def show_stats(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Display detailed watch statistics for a user."""
        target_user = member or ctx.author
        
        if target_user.id not in self.badge_system.user_stats:
            if target_user == ctx.author:
                await ctx.send("📊 You haven't watched any movies yet! Join the next marathon to start earning stats.")
            else:
                await ctx.send(f"📊 {target_user.display_name} hasn't watched any movies yet.")
            return
        
        stats = self.badge_system.user_stats[target_user.id]
        user_badges = self.badge_system.get_user_badges(target_user.id)
        
        embed = discord.Embed(
            title=f"📊 {target_user.display_name}'s Watch Stats",
            color=discord.Color.blue()
        )
        
        # Main stats
        embed.add_field(
            name="🎬 Movies Watched",
            value=f"**{stats.total_movies}** total\n**{stats.completed_movies}** completed\n**{stats.average_completion_rate:.1f}%** avg completion",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Watch Time",
            value=f"**{stats.total_watch_time_hours:.1f}** hours\n**{stats.total_watch_time_minutes:,}** minutes",
            inline=True
        )
        
        embed.add_field(
            name="🔥 Streaks",
            value=f"**{stats.current_streak_days}** current\n**{stats.longest_streak_days}** longest",
            inline=True
        )
        
        # Top genres (top 3)
        if stats.favorite_genres:
            top_genres = sorted(stats.favorite_genres.items(), key=lambda x: x[1], reverse=True)[:3]
            genre_text = "\n".join([f"**{count}** {genre}" for genre, count in top_genres])
            embed.add_field(name="🎭 Top Genres", value=genre_text, inline=True)
        
        # Achievements
        embed.add_field(
            name="🏆 Achievements",
            value=f"**{len(user_badges)}** badges earned\n**{stats.ai_interactions}** AI interactions\n**{stats.votes_cast}** votes cast",
            inline=True
        )
        
        # Last activity
        if stats.last_watch_date:
            last_watch = stats.last_watch_date.strftime("%Y-%m-%d")
            embed.add_field(name="📅 Last Watch", value=last_watch, inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard")
    async def show_leaderboard(self, ctx: commands.Context, category: str = "movies"):
        """
        Display leaderboard for various categories.
        Categories: movies, time, streak, badges
        """
        category_map = {
            "movies": "total_movies",
            "time": "watch_time", 
            "streak": "current_streak",
            "badges": "badges"
        }
        
        if category.lower() not in category_map:
            await ctx.send("📊 Available leaderboard categories: `movies`, `time`, `streak`, `badges`")
            return
        
        leaderboard = self.badge_system.get_leaderboard(category_map[category.lower()], limit=10)
        
        if not leaderboard:
            await ctx.send("📊 No statistics available yet. Start watching movies to populate the leaderboard!")
            return
        
        category_emojis = {
            "movies": "🎬",
            "time": "⏱️",
            "streak": "🔥",
            "badges": "🏆"
        }
        
        category_names = {
            "movies": "Movies Watched",
            "time": "Watch Time",
            "streak": "Current Streak",
            "badges": "Badges Earned"
        }
        
        embed = discord.Embed(
            title=f"{category_emojis[category]} {category_names[category]} Leaderboard",
            color=discord.Color.gold()
        )
        
        leaderboard_text = ""
        for stats, rank in leaderboard:
            # Get user from bot
            try:
                user = await self.bot.fetch_user(stats.user_id)
                username = user.display_name if hasattr(user, 'display_name') else user.name
            except:
                username = stats.username
            
            # Format value based on category
            if category == "movies":
                value = f"{stats.total_movies} movies"
            elif category == "time":
                value = f"{stats.total_watch_time_hours:.1f} hours"
            elif category == "streak":
                value = f"{stats.current_streak_days} days"
            elif category == "badges":
                badge_count = len(self.badge_system.user_badges.get(stats.user_id, []))
                value = f"{badge_count} badges"
            
            # Rank emojis
            rank_emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
            
            leaderboard_text += f"{rank_emoji} **{username}** - {value}\n"
        
        embed.description = leaderboard_text
        await ctx.send(embed=embed)

    @commands.command(name="progress")
    async def show_progress(self, ctx: commands.Context):
        """Show progress towards next badges."""
        user_id = ctx.author.id
        
        if user_id not in self.badge_system.user_stats:
            await ctx.send("📈 You haven't started your horror journey yet! Watch your first movie to begin tracking progress.")
            return
        
        stats = self.badge_system.user_stats[user_id]
        earned_badges = {badge.badge_id for badge in self.badge_system.user_badges.get(user_id, [])}
        
        embed = discord.Embed(
            title=f"📈 {ctx.author.display_name}'s Badge Progress",
            color=discord.Color.orange()
        )
        
        progress_info = []
        
        # Check movie count badges
        movie_milestones = [1, 5, 10, 25, 50, 100]
        for milestone in movie_milestones:
            badge_id = {1: "first_blood", 5: "rising_terror", 10: "ghost_hunter", 
                       25: "vampire_lord", 50: "death_collector", 100: "horror_legend"}[milestone]
            
            if badge_id not in earned_badges:
                remaining = milestone - stats.total_movies
                if remaining <= 5:  # Show if close
                    badge = self.badge_system.badge_definitions[badge_id]
                    progress_info.append(f"{badge.emoji} **{badge.name}** - {remaining} more movies")
                break
        
        # Check streak badges
        streak_milestones = [3, 7, 14, 30]
        for milestone in streak_milestones:
            badge_id = {3: "dedicated", 7: "marathon_runner", 14: "unstoppable", 30: "legend"}[milestone]
            
            if badge_id not in earned_badges:
                remaining = milestone - stats.current_streak_days
                if remaining <= 3:  # Show if close
                    badge = self.badge_system.badge_definitions[badge_id]
                    progress_info.append(f"{badge.emoji} **{badge.name}** - {remaining} more days")
                break
        
        # Check AI interaction badges
        if "commentary_king" not in earned_badges and stats.ai_interactions >= 25:
            remaining = 50 - stats.ai_interactions
            progress_info.append(f"💬 **Commentary King** - {remaining} more AI interactions")
        
        if progress_info:
            embed.description = "\n".join(progress_info[:5])  # Show top 5
        else:
            embed.description = "🎯 Keep watching movies to unlock new badges!"
        
        await ctx.send(embed=embed)

    @commands.command(name="allbadges")
    async def show_all_badges(self, ctx: commands.Context):
        """Display information about all available badges."""
        embed = discord.Embed(
            title="🏆 All Available Badges",
            description="Complete list of badges you can earn in ClankerTV",
            color=discord.Color.purple()
        )
        
        # Group badges by type
        type_groups = {}
        for badge in self.badge_system.badge_definitions.values():
            badge_type = badge.badge_type.value
            if badge_type not in type_groups:
                type_groups[badge_type] = []
            type_groups[badge_type].append(badge)
        
        type_names = {
            "movie_count": "🎬 Movie Milestones",
            "time_based": "⏰ Time Challenges", 
            "genre_specialist": "🎭 Genre Master",
            "social": "👥 Social Achievements",
            "special_achievement": "⭐ Special Achievements",
            "streak": "🔥 Streak Rewards"
        }
        
        for badge_type, badges in type_groups.items():
            if badge_type in type_names:
                field_value = ""
                for badge in sorted(badges, key=lambda x: x.requirement_value):
                    field_value += f"{badge.emoji} **{badge.name}** - {badge.description}\n"
                
                embed.add_field(
                    name=type_names[badge_type],
                    value=field_value,
                    inline=False
                )
        
        await ctx.send(embed=embed)

    @commands.command(name="savedata")
    @commands.has_permissions(administrator=True)
    async def save_badge_data(self, ctx: commands.Context):
        """Manually save badge system data (admin only)."""
        try:
            self.badge_system.save_progress()
            
            # Get some stats for confirmation
            total_users = len(self.badge_system.user_stats)
            total_watches = len(self.badge_system.watch_history)
            total_badges = sum(len(badges) for badges in self.badge_system.user_badges.values())
            
            await ctx.send(
                f"💾 **Badge data saved successfully!**\n"
                f"📊 **Stats:** {total_users} users, {total_watches} watch records, {total_badges} badges earned"
            )
        except Exception as e:
            await ctx.send(f"❌ Failed to save badge data: {e}")

    @commands.command(name="backupdata")
    @commands.has_permissions(administrator=True)
    async def backup_badge_data(self, ctx: commands.Context):
        """Create a timestamped backup of badge data (admin only)."""
        try:
            backup_path = self.badge_system.backup_data()
            if backup_path:
                await ctx.send(f"📦 **Backup created successfully!**\nLocation: `{backup_path}`")
            else:
                await ctx.send("❌ Failed to create backup.")
        except Exception as e:
            await ctx.send(f"❌ Failed to create backup: {e}")
            
    @commands.command(name="badgestats")
    async def badge_system_stats(self, ctx: commands.Context):
        """Show overall badge system statistics."""
        try:
            total_users = len(self.badge_system.user_stats)
            total_watches = len(self.badge_system.watch_history)
            total_badges = sum(len(badges) for badges in self.badge_system.user_badges.values())
            active_watches = len(self.badge_system.active_watches)
            
            # Calculate some interesting stats
            if self.badge_system.user_stats:
                total_watch_time = sum(stats.total_watch_time_minutes for stats in self.badge_system.user_stats.values())
                total_movies = sum(stats.total_movies for stats in self.badge_system.user_stats.values())
                avg_completion = sum(stats.average_completion_rate for stats in self.badge_system.user_stats.values()) / len(self.badge_system.user_stats)
            else:
                total_watch_time = total_movies = avg_completion = 0
            
            embed = discord.Embed(
                title="📊 Badge System Statistics",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="👥 Users & Activity",
                value=f"**{total_users}** registered users\n**{active_watches}** currently watching\n**{total_badges}** total badges earned",
                inline=True
            )
            
            embed.add_field(
                name="🎬 Movie Stats",
                value=f"**{total_movies}** movies watched\n**{total_watches}** watch sessions\n**{avg_completion:.1f}%** avg completion",
                inline=True
            )
            
            embed.add_field(
                name="⏱️ Watch Time",
                value=f"**{total_watch_time:,}** total minutes\n**{total_watch_time/60:.1f}** total hours\n**{total_watch_time/60/24:.1f}** total days",
                inline=True
            )
            
            # Most earned badge
            badge_counts = {}
            for badge_list in self.badge_system.user_badges.values():
                for badge in badge_list:
                    badge_counts[badge.badge_id] = badge_counts.get(badge.badge_id, 0) + 1
            
            if badge_counts:
                most_common_badge_id = max(badge_counts, key=badge_counts.get)
                most_common_badge = self.badge_system.badge_definitions.get(most_common_badge_id)
                if most_common_badge:
                    embed.add_field(
                        name="🏆 Most Earned Badge",
                        value=f"{most_common_badge.emoji} **{most_common_badge.name}**\nEarned by **{badge_counts[most_common_badge_id]}** users",
                        inline=False
                    )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Failed to get badge system stats: {e}")


async def setup(bot: commands.Bot, badge_system: WatchBadgeSystem, plex_service: PlexService):
    """Setup function to add badge commands to the bot."""
    await bot.add_cog(BadgeCommands(bot, badge_system, plex_service))