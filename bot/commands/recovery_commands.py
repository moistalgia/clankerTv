"""
Recovery Commands for Clanker Corruption System
==============================================

Commands that allow users to interact with Clanker's corruption state
and attempt to restore his sanity through various methods.
"""

import discord
from discord.ext import commands
import asyncio
from typing import Optional


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


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(RecoveryCommands(bot))