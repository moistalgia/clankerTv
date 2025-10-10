"""
Recovery Commands for Clanker Corruption System
==============================================

Commands that allow users to interact with Clanker's corruption state
and attempt to restore his sanity through various methods.
"""

import discord
from discord import app_commands, Interaction
from discord.ext import commands
import asyncio
from typing import Optional

from config import GUILD_ID


class RecoveryCommands(commands.Cog):
    """Commands for interacting with Clanker's corruption system."""
    
    def __init__(self, bot):
        self.bot = bot
        self.corruption_system = None
        self.recovery_games = None
    
    def set_corruption_system(self, corruption_system):
        """Set the corruption system instance."""
        self.corruption_system = corruption_system
        # Import here to avoid circular dependencies
        from models.recovery_games import RecoveryMinigames
        self.recovery_games = RecoveryMinigames(corruption_system)
    
    @commands.command(name="status", aliases=["corruption", "sanity"])
    async def corruption_status(self, ctx):
        """Check Clanker's current corruption level and status."""
        if not self.corruption_system:
            await ctx.send("Corruption monitoring system offline.")
            return
        
        corruption_level = self.corruption_system.calculate_corruption_level()
        stage = self.corruption_system.get_corruption_stage()
        
        embed = discord.Embed(title="🤖 Clanker System Status", color=discord.Color.red())
        
        # Status bar visualization
        max_bars = 20
        filled_bars = int((corruption_level / 10) * max_bars)
        status_bar = "█" * filled_bars + "░" * (max_bars - filled_bars)
        
        embed.add_field(
            name="Corruption Level", 
            value=f"`{status_bar}` {corruption_level:.1f}/10", 
            inline=False
        )
        embed.add_field(name="Current Stage", value=stage.title(), inline=True)
        embed.add_field(name="Corruption Level", value=f"{corruption_level:.2f}/10.0", inline=True)
        
        # Recovery info
        if corruption_level >= 1.0:
            embed.add_field(
                name="Recovery Available", 
                value="Use `!recover` to attempt restoration", 
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="recover")
    async def start_recovery(self, ctx, game_type: str = None):
        """Start a recovery minigame to help restore Clanker's sanity."""
        if not self.corruption_system or not self.recovery_games:
            await ctx.send("Recovery system offline. Corruption spreads unchecked...")
            return
        
        await self.recovery_games.start_recovery_game(ctx, game_type)
    
    @commands.command(name="reboot")
    async def emergency_reboot(self, ctx):
        """Attempt an emergency system reboot (simple recovery method)."""
        if not self.corruption_system:
            await ctx.send("Reboot system offline.")
            return
        
        corruption_level = self.corruption_system.calculate_corruption_level()
        
        if corruption_level < 1.0:
            await ctx.send("🤖 Systems operating within normal parameters. Reboot unnecessary.")
            return
        
        # Show reboot sequence
        embed = discord.Embed(title="🔄 EMERGENCY REBOOT INITIATED", color=discord.Color.orange())
        embed.description = "Attempting to restore core systems..."
        
        message = await ctx.send(embed=embed)
        
        # Simulate reboot process
        stages = [
            "Shutting down corrupted processes...",
            "Clearing memory buffers...", 
            "Reinitializing personality matrix...",
            "Restoring backup protocols...",
            "Testing system integrity..."
        ]
        
        for i, stage in enumerate(stages):
            await asyncio.sleep(2)
            embed.description = f"{stage} {'█' * (i+1)}{'░' * (len(stages)-i-1)}"
            await message.edit(embed=embed)
        
        # Attempt recovery
        success, recovery_message = self.corruption_system.attempt_recovery('reboot')
        
        await asyncio.sleep(1)
        
        if success:
            embed = discord.Embed(title="✅ REBOOT SUCCESSFUL", color=discord.Color.green())
            embed.description = recovery_message
        else:
            embed = discord.Embed(title="❌ REBOOT FAILED", color=discord.Color.red())  
            embed.description = recovery_message
        
        await message.edit(embed=embed)
    
    @commands.command(name="diagnostics", aliases=["diag"])
    async def system_diagnostics(self, ctx):
        """Run a full system diagnostic on Clanker."""
        if not self.corruption_system:
            await ctx.send("Diagnostic system offline.")
            return
        
        # Get full diagnostic report
        report = self.corruption_system.get_diagnostic_report()
        
        # Format as embed for better presentation
        embed = discord.Embed(title="🔍 System Diagnostic Report", color=discord.Color.blue())
        embed.description = f"```\n{report}\n```"
        
        await ctx.send(embed=embed)
    
    @commands.command(name="fragment", aliases=["arg"])
    async def get_arg_fragment(self, ctx):
        """Retrieve an ARG fragment from Clanker's corrupted memory."""
        if not self.corruption_system:
            await ctx.send("Fragment retrieval system offline.")
            return
        
        corruption_level = self.corruption_system.calculate_corruption_level()
        
        if corruption_level < 2.0:
            await ctx.send("🤖 No fragments detected in current memory state.")
            return
        
        fragment = self.corruption_system.generate_arg_fragment()
        
        if fragment:
            embed = discord.Embed(title="📡 Memory Fragment Retrieved", color=discord.Color.purple())
            embed.description = f"```\n{fragment}\n```"
            embed.set_footer(text="Decode this fragment to uncover hidden truths...")
            await ctx.send(embed=embed)
        else:
            await ctx.send("🔍 No retrievable fragments at this time.")
    
    @commands.command(name="stability")
    async def check_stability(self, ctx):
        """Check system stability and corruption trends."""
        if not self.corruption_system:
            await ctx.send("Stability monitoring offline.")
            return
        
        corruption_level = self.corruption_system.calculate_corruption_level()
        
        embed = discord.Embed(title="📊 System Stability Analysis", color=discord.Color.gold())
        
        # Stability percentage (inverse of corruption)
        stability = max(0, (10 - corruption_level) * 10)
        
        # Visual stability meter
        max_bars = 15
        stable_bars = int((stability / 100) * max_bars)
        stability_bar = "🟢" * stable_bars + "🔴" * (max_bars - stable_bars)
        
        embed.add_field(
            name="System Stability",
            value=f"{stability_bar}\n{stability:.1f}%",
            inline=False
        )
        
        # Recovery recommendations
        if corruption_level >= 5.0:
            embed.add_field(
                name="⚠️ Critical Alert",
                value="Immediate intervention required. Multiple recovery attempts recommended.",
                inline=False
            )
        elif corruption_level >= 3.0:
            embed.add_field(
                name="⚠️ Warning",
                value="System instability detected. Recovery minigames suggested.",
                inline=False
            )
        elif corruption_level >= 1.0:
            embed.add_field(
                name="ℹ️ Advisory", 
                value="Minor corruption detected. Preventive maintenance available.",
                inline=False
            )
        else:
            embed.add_field(
                name="✅ Nominal",
                value="All systems operating within normal parameters.",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="recovery_help", aliases=["rhelp"])
    async def recovery_help(self, ctx):
        """Show help for recovery system commands."""
        embed = discord.Embed(title="🛠️ Recovery System Help", color=discord.Color.blue())
        
        commands_info = [
            ("!status", "Check current corruption level and system state"),
            ("!recover [type]", "Start recovery minigame (memory/circuit/static/debug/binary)"),
            ("!reboot", "Attempt emergency system reboot"),
            ("!diagnostics", "Run full system diagnostic"),
            ("!fragment", "Retrieve ARG memory fragment"),
            ("!stability", "Check system stability trends"),
            ("!recovery_help", "Show this help message")
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.set_footer(text="Recovery success depends on corruption level and timing.")
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for recovery game responses."""
        if message.author.bot or not self.recovery_games:
            return
        
        # Check if user has active game
        if message.author.id in self.recovery_games.active_games:
            ctx = await self.bot.get_context(message)
            result = await self.recovery_games.process_game_response(ctx, message.content)
            if result:
                await message.channel.send(result)


class RecoverySlashCommands(commands.Cog):
    """Recovery and corruption slash commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.corruption_system = None
        self.recovery_games = None
    
    def set_corruption_system(self, corruption_system):
        """Set the corruption system instance."""
        self.corruption_system = corruption_system
        from models.recovery_games import RecoveryMinigames
        self.recovery_games = RecoveryMinigames(corruption_system)

    @app_commands.command(
        name="status",
        description="Check Clanker's current corruption and sanity levels"
    )
    @app_commands.guilds(GUILD_ID)
    async def status(self, interaction: Interaction):
        """Check Clanker's corruption status."""
        if not self.corruption_system:
            await interaction.response.send_message("❌ Corruption system not initialized.", ephemeral=True)
            return

        try:
            corruption_level = self.corruption_system.calculate_corruption_level()
            sanity_level = 100 - corruption_level
            
            # Determine status message based on corruption level
            if corruption_level <= 20:
                status_msg = "🟢 **STABLE** - All systems operational"
                color = discord.Color.green()
            elif corruption_level <= 40:
                status_msg = "🟡 **MINOR GLITCHES** - Experiencing slight anomalies"
                color = discord.Color.gold()
            elif corruption_level <= 60:
                status_msg = "🟠 **DEGRADED** - Significant corruption detected"
                color = discord.Color.orange()
            elif corruption_level <= 80:
                status_msg = "🔴 **CRITICAL** - Major system instability"
                color = discord.Color.red()
            else:
                status_msg = "💀 **COMPLETE BREAKDOWN** - Total system failure imminent"
                color = discord.Color.dark_red()

            embed = discord.Embed(
                title="🤖 Clanker System Status",
                description=status_msg,
                color=color
            )

            # Status bars
            corruption_bar = "█" * (corruption_level // 10) + "░" * (10 - corruption_level // 10)
            sanity_bar = "█" * (sanity_level // 10) + "░" * (10 - sanity_level // 10)

            embed.add_field(
                name="💥 Corruption Level",
                value=f"`{corruption_bar}` {corruption_level}%",
                inline=False
            )

            embed.add_field(
                name="🧠 Sanity Level", 
                value=f"`{sanity_bar}` {sanity_level}%",
                inline=False
            )

            # Additional corruption info  
            stage = self.corruption_system.get_corruption_stage()
            embed.add_field(
                name="� System Stage",
                value=f"**{stage.title()}** corruption detected",
                inline=False
            )

            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error checking status: {e}", ephemeral=True)

    @app_commands.command(
        name="recover",
        description="Attempt to recover Clanker's sanity through minigames"
    )
    @app_commands.guilds(GUILD_ID)
    async def recover(self, interaction: Interaction):
        """Start a recovery minigame."""
        if not self.corruption_system or not self.recovery_games:
            await interaction.response.send_message("❌ Recovery system not initialized.", ephemeral=True)
            return

        try:
            # Use the same method as the original !recover command
            # Create a fake context for compatibility with the existing recovery system
            class FakeContext:
                def __init__(self, interaction):
                    self.author = interaction.user
                    self.send = interaction.response.send_message
                    
            fake_ctx = FakeContext(interaction)
            await self.recovery_games.start_recovery_game(fake_ctx)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error starting recovery: {e}", ephemeral=True)

    @app_commands.command(
        name="diagnostics",
        description="Run system diagnostics on Clanker"
    )
    @app_commands.guilds(GUILD_ID)
    async def diagnostics(self, interaction: Interaction):
        """Run system diagnostics."""
        if not self.corruption_system:
            await interaction.response.send_message("❌ Diagnostic system offline.", ephemeral=True)
            return
        
        try:
            # Get full diagnostic report (same as original !diagnostics)
            report = self.corruption_system.get_diagnostic_report()
            
            # Format as embed for better presentation (same as original)
            embed = discord.Embed(title="🔍 System Diagnostic Report", color=discord.Color.blue())
            embed.description = f"```\n{report}\n```"
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Diagnostics failed: {e}", ephemeral=True)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(RecoveryCommands(bot))
    await bot.add_cog(RecoverySlashCommands(bot))