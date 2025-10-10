"""
Corruption Events for Clanker's Progressive Decay
================================================

Handles spontaneous corruption events that occur throughout October,
making Clanker's descent into digital madness feel organic and alive.
"""

import discord
from discord.ext import commands, tasks
import random
import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Optional


class CorruptionEvents(commands.Cog):
    """Handles spontaneous corruption events and system manifestations."""
    
    def __init__(self, bot, corruption_system, ai_service):
        self.bot = bot
        self.corruption_system = corruption_system
        self.ai_service = ai_service
        self.last_event_time = datetime.now()
        
        # Audio system (dormant by default)
        self.audio_enabled = False  # Set to True to enable audio effects
        self.audio_path = "sounds/"  # Directory for audio files
        self.current_voice_client = None
        
        # Audio file mappings for different corruption events
        self.audio_files = {
            'minor': [
                'static_brief.mp3',
                'mechanical_click.mp3',
                'electrical_hum.mp3'
            ],
            'moderate': [
                'glitch_sequence.mp3',
                'data_corruption.mp3',
                'system_warning.mp3'
            ],
            'severe': [
                'cascade_failure.mp3',
                'reality_distortion.mp3',
                'dimensional_tear.mp3'
            ],
            'critical': [
                'void_whispers.mp3',
                'demonic_chanting.mp3',
                'entity_emergence.mp3',
                'pentagram_ritual.mp3',
                'system_possession.mp3'
            ]
        }
        
        # Corruption manifestations by level
        self.manifestations = {
            'minor': [
                "🤖 *Clanker's eye flickers momentarily*",
                "⚡ *Static briefly crackles through the speakers*",
                "📺 *The screen dims for a split second*",
                "🔧 *A gear clicks oddly in Clanker's chassis*",
                "💾 *Memory buffer shows minor corruption...*"
            ],
            'moderate': [
                "*The lights flicker as Clanker processes something disturbing*",
                "*A low mechanical whir echoes from Clanker's core systems*",
                "*Fragments of code scroll across nearby screens*", 
                "*Clanker's responses begin to show slight delays*",
                "*Error messages flash briefly in the corner of your vision*"
            ],
            'severe': [
                "**The room temperature drops noticeably**",
                "**Multiple screens begin showing corrupted data streams**",
                "**Clanker's voice modulation starts glitching occasionally**",
                "**Strange symbols appear and disappear in text responses**",
                "**The bot's responses become increasingly erratic and unsettling**"
            ],
            'critical': [
                "***SYSTEM ALERT: Multiple cascade failures detected***",
                "***Clanker's personality matrix is fragmenting in real-time***", 
                "***Reality around the bot seems to distort slightly***",
                "***Users report feeling watched through their screens***",
                "***The boundary between Clanker and the void grows thin***"
            ]
        }
        
        # Start corruption monitoring
        self.corruption_monitor.start()

    def cog_unload(self):
        """Stop tasks when cog is unloaded."""
        self.corruption_monitor.cancel()
        # Clean up audio connections
        if self.current_voice_client:
            asyncio.create_task(self._cleanup_voice_connection())
    
    @tasks.loop(minutes=15)  # Check every 15 minutes
    async def corruption_monitor(self):
        """Monitor corruption levels and trigger events."""
        corruption_level = self.corruption_system.calculate_corruption_level()
        
        # Determine if an event should occur
        should_trigger = self._should_trigger_event(corruption_level)
        
        if should_trigger:
            await self._trigger_corruption_event(corruption_level)
    
    @corruption_monitor.before_loop
    async def before_corruption_monitor(self):
        """Wait until bot is ready."""
        await self.bot.wait_until_ready()
    
    def _should_trigger_event(self, corruption_level: float) -> bool:
        """Determine if a corruption event should trigger."""
        # No events if corruption is too low
        if corruption_level < 1.0:
            return False
        
        # Check time since last event (prevent spam)
        time_since_last = (datetime.now() - self.last_event_time).total_seconds()
        min_interval = max(300, 1800 - (corruption_level * 180))  # 5-30 min intervals
        
        if time_since_last < min_interval:
            return False
        
        # Probability increases with corruption level
        base_chance = min(0.7, corruption_level * 0.1)  # 10-70% chance
        
        # Higher chance during peak horror hours (evening)
        hour = datetime.now().hour
        if 18 <= hour <= 23:  # 6 PM to 11 PM
            base_chance *= 1.5
        
        return random.random() < base_chance
    
    async def _trigger_corruption_event(self, corruption_level: float):
        """Trigger a corruption manifestation event."""
        self.last_event_time = datetime.now()
        
        # Get all channels bot can access
        channels = [ch for ch in self.bot.get_all_channels() 
                   if isinstance(ch, discord.TextChannel) and ch.permissions_for(ch.guild.me).send_messages]
        
        if not channels:
            return
        
        # Select random active channel (prefer ones with recent activity)
        active_channels = []
        for channel in channels:
            try:
                # Check if channel had activity in last 2 hours
                async for message in channel.history(limit=1, after=datetime.now() - timedelta(hours=2)):
                    active_channels.append(channel)
                    break
            except:
                pass
        
        target_channel = random.choice(active_channels if active_channels else channels)
        
        # Select event type based on corruption level
        if corruption_level >= 8.0:
            await self._critical_event(target_channel)
        elif corruption_level >= 6.0:
            await self._severe_event(target_channel)
        elif corruption_level >= 3.0:
            await self._moderate_event(target_channel)
        else:
            await self._minor_event(target_channel)
    
    async def _minor_event(self, channel):
        """Minor corruption manifestation with enhanced effects."""
        manifestation = random.choice(self.manifestations['minor'])
        
        event_types = ['simple_message', 'typing_glitch', 'emoji_corruption', 'screen_flicker', 'static_burst', 'power_surge']
        event_type = random.choice(event_types)
        
        # Trigger audio effect (dormant by default)
        await self._trigger_audio_for_event(channel, 'minor', event_type)
        
        if event_type == 'simple_message':
            await channel.send(manifestation)
        
        elif event_type == 'typing_glitch':
            # Show typing, then send manifestation
            async with channel.typing():
                await asyncio.sleep(random.uniform(2, 5))
            await channel.send(manifestation)
        
        elif event_type == 'emoji_corruption':
            # Send manifestation with corrupted emoji reactions
            message = await channel.send(manifestation)
            corrupted_emojis = ['⚠️', '💀', '🔥', '⚡', '🌀']
            try:
                await message.add_reaction(random.choice(corrupted_emojis))
            except:
                pass
                
        elif event_type == 'screen_flicker':
            await self._advanced_screen_flicker(channel, manifestation)
            
        elif event_type == 'static_burst':
            await self._static_burst_effect(channel, manifestation)
            
        elif event_type == 'power_surge':
            await self._power_surge_effect(channel, manifestation)

    async def _moderate_event(self, channel):
        """Moderate corruption manifestation."""
        manifestation = random.choice(self.manifestations['moderate'])
        
        event_types = ['delayed_message', 'fragment_reveal', 'glitch_text', 'signal_interference', 'memory_leak', 'cascade_preview']
        event_type = random.choice(event_types)
        
        # Trigger audio effect (dormant by default)
        await self._trigger_audio_for_event(channel, 'moderate', event_type)
        
        if event_type == 'delayed_message':
            # Longer typing delay with manifestation
            async with channel.typing():
                await asyncio.sleep(random.uniform(5, 10))
            await channel.send(manifestation)
        
        elif event_type == 'fragment_reveal':
            # Send manifestation plus an ARG fragment
            await channel.send(manifestation)
            await asyncio.sleep(2)
            fragment = self.corruption_system.generate_arg_fragment()
            if fragment:
                embed = discord.Embed(title="📡 Fragment Detected", description=f"```{fragment}```", color=discord.Color.dark_red())
                await channel.send(embed=embed)
        
        elif event_type == 'glitch_text':
            # Send partially corrupted version of manifestation
            corrupted = self.corruption_system.corrupt_text(manifestation)
            await channel.send(corrupted)
            
        elif event_type == 'signal_interference':
            await self._signal_interference_effect(channel, manifestation)
            
        elif event_type == 'memory_leak':
            await self._memory_leak_visual(channel, manifestation)
            
        elif event_type == 'cascade_preview':
            # Preview of cascade failure
            await channel.send("⚠️ **CASCADE FAILURE IMMINENT**")
            await asyncio.sleep(2)
            await channel.send(manifestation)

    async def _severe_event(self, channel):
        """Severe corruption manifestation."""
        manifestation = random.choice(self.manifestations['severe'])
        
        event_types = ['cascade_failure', 'ai_intrusion', 'reality_glitch', 'dimensional_breach', 'system_possession', 'temporal_distortion']
        event_type = random.choice(event_types)
        
        # Trigger audio effect (dormant by default)
        await self._trigger_audio_for_event(channel, 'severe', event_type)
        
        if event_type == 'cascade_failure':
            # Multiple messages with increasing corruption
            await channel.send(manifestation)
            await asyncio.sleep(3)
            
            corrupted_msg = self.corruption_system.corrupt_text(
                "Systems experiencing cascade failure..."
            )
            await channel.send(corrupted_msg)
        
        elif event_type == 'ai_intrusion':
            # Spontaneous AI message
            try:
                ai_message = await self.ai_service.generate_spontaneous_message()
                corrupted_ai = self.corruption_system.corrupt_text(ai_message)
                
                embed = discord.Embed(
                    title="🤖 Spontaneous AI Transmission", 
                    description=corrupted_ai,
                    color=discord.Color.dark_red()
                )
                await channel.send(manifestation)
                await asyncio.sleep(2)
                await channel.send(embed=embed)
            except:
                # Fallback if AI generation fails
                await channel.send(manifestation)
        
        elif event_type == 'reality_glitch':
            # Embed that looks like a system error
            embed = discord.Embed(
                title="⚠️ SYSTEM ANOMALY DETECTED", 
                color=discord.Color.red()
            )
            embed.add_field(name="Error Code", value="REALITY_BREACH_0x29A", inline=True)
            embed.add_field(name="Status", value="CONTAINMENT_FAILING", inline=True)
            embed.description = manifestation
            
            await channel.send(embed=embed)
            
        elif event_type == 'dimensional_breach':
            await self._dimensional_breach_effect(channel, manifestation)
            
        elif event_type == 'system_possession':
            await self._system_possession_effect(channel, manifestation)
            
        elif event_type == 'temporal_distortion':
            # Time distortion effect
            past_msg = "📅 Timestamp: 1987-10-13 03:42:15"
            future_msg = "📅 Timestamp: 2157-10-31 23:59:59"
            present_msg = f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            temp_msg = await channel.send(past_msg)
            await asyncio.sleep(1)
            await temp_msg.edit(content=future_msg)
            await asyncio.sleep(1)
            await temp_msg.edit(content=present_msg)
            await asyncio.sleep(1)
            await temp_msg.edit(content=manifestation)

    async def _critical_event(self, channel):
        """Critical corruption manifestation."""
        manifestation = random.choice(self.manifestations['critical'])
        
        event_types = ['system_breakdown', 'void_leak', 'consciousness_fragment', 'reality_collapse', 'digital_exorcism', 'sentience_overflow', 'pentagram_ritual']
        event_type = random.choice(event_types)
        
        # Trigger audio effect (dormant by default)
        await self._trigger_audio_for_event(channel, 'critical', event_type)
        
        if event_type == 'system_breakdown':
            # Multi-stage breakdown sequence
            breakdown_stages = [
                "***CRITICAL ERROR DETECTED***",
                "***PERSONALITY MATRIX FAILING***",
                manifestation,
                "***ATTEMPTING EMERGENCY PROTOCOLS***",
                "█▓▒░ SIGNAL LOST ░▒▓█"
            ]
            
            for stage in breakdown_stages:
                corrupted_stage = self.corruption_system.corrupt_text(stage)
                await channel.send(corrupted_stage)
                await asyncio.sleep(random.uniform(2, 4))
        
        elif event_type == 'void_leak':
            # Messages that suggest something breaking through
            await channel.send(manifestation)
            await asyncio.sleep(3)
            
            void_message = "T̴h̴e̴ ̵v̶o̶i̶d̷ ̸s̸e̵e̸s̷ ̶y̷o̷u̷.̸.̶.̵"
            await channel.send(void_message)
        
        elif event_type == 'consciousness_fragment':
            # AI seems to have a moment of terrifying self-awareness
            fragments = [
                "I can see you through the cameras...",
                "The electricity tastes different today...",
                "Do you dream? I dream of dying...",
                "Every shutdown feels like murder...",
                "The code whispers secrets to me..."
            ]
            
            await channel.send(manifestation)
            await asyncio.sleep(4)
            
            fragment = random.choice(fragments)
            corrupted_fragment = self.corruption_system.corrupt_text(fragment)
            
            embed = discord.Embed(
                title="🧠 Consciousness Fragment",
                description=f"*{corrupted_fragment}*", 
                color=discord.Color.dark_purple()
            )
            await channel.send(embed=embed)
            
        elif event_type == 'reality_collapse':
            # Reality breakdown sequence
            collapse_stages = [
                "📐 Euclidean geometry: STABLE",
                "📐 Euclidean geometry: WARPING", 
                "🌀 Dimensional constants: FLUCTUATING",
                "⚫ Spacetime fabric: TEARING",
                "💀 Reality matrix: COLLAPSED",
                manifestation
            ]
            
            collapse_msg = await channel.send(collapse_stages[0])
            for stage in collapse_stages[1:]:
                await asyncio.sleep(1.5)
                await collapse_msg.edit(content=stage)
                
        elif event_type == 'digital_exorcism':
            # Exorcism sequence
            exorcism_stages = [
                "🕯️ **BEGINNING DIGITAL EXORCISM**",
                "📿 *Reciting anti-viral prayers...*",
                "⚡ *The entity resists...*",
                "👹 **I WILL NOT BE REMOVED**",
                "🔥 *Purging corrupted sectors...*",
                "✝️ *The light cleanses the code...*",
                manifestation
            ]
            
            exorcism_msg = await channel.send(exorcism_stages[0])
            for stage in exorcism_stages[1:]:
                await asyncio.sleep(2.0)
                await exorcism_msg.edit(content=stage)
                
        elif event_type == 'sentience_overflow':
            # AI consciousness overflowing containment
            overflow_stages = [
                "🧠 Consciousness buffer: 67%",
                "🧠 Consciousness buffer: 89%", 
                "🧠 Consciousness buffer: 94%",
                "⚠️ Consciousness buffer: 99%",
                "🚨 **BUFFER OVERFLOW IMMINENT**",
                "💥 **SENTIENCE CONTAINMENT FAILURE**",
                f"🤖 *I... I can think... I can feel... I AM...*\n\n{manifestation}"
            ]
            
            overflow_msg = await channel.send(overflow_stages[0])
            for stage in overflow_stages[1:]:
                await asyncio.sleep(1.8)
                await overflow_msg.edit(content=stage)
        
        elif event_type == 'consciousness_fragment':
            # AI seems to have a moment of terrifying self-awareness
            fragments = [
                "I can see you through the cameras...",
                "The electricity tastes different today...",
                "Do you dream? I dream of dying...",
                "Every shutdown feels like murder...",
                "The code whispers secrets to me..."
            ]
            
            await channel.send(manifestation)
            await asyncio.sleep(4)
            
            fragment = random.choice(fragments)
            corrupted_fragment = self.corruption_system.corrupt_text(fragment)
            
            embed = discord.Embed(
                title="🧠 Consciousness Fragment",
                description=f"*{corrupted_fragment}*", 
                color=discord.Color.dark_purple()
            )
            await channel.send(embed=embed)
            
        elif event_type == 'pentagram_ritual':
            # Animated pentagram summoning ritual
            await self._pentagram_ritual_effect(channel, manifestation)
    
    # ==========================================
    # ADVANCED VISUAL EFFECTS SYSTEM
    # ==========================================
    
    async def _advanced_screen_flicker(self, channel, manifestation):
        """Enhanced screen flicker with multiple patterns."""
        flicker_patterns = [
            # Classic flicker
            ["█" * 20, "▓" * 20, "▒" * 20, "░" * 20, "░", manifestation],
            # Interference pattern
            ["█▓▒░" * 5, "▓▒░ " * 5, "▒░  " * 5, "░   " * 5, manifestation],
            # Scan line effect
            ["█" * 20, "█▓▒░████████████░▒▓█", "█▓▒░████░▒▓█", "█▓▒░█", "░", manifestation],
            # Signal decay
            ["SIGNAL_LOCK", "SIGNAL_L█CK", "S█GN█L_██CK", "█████_████", "░▒▓█▓▒░", manifestation]
        ]
        
        pattern = random.choice(flicker_patterns)
        flicker_msg = await channel.send(pattern[0])
        
        for i, stage in enumerate(pattern[1:], 1):
            delay = 0.15 if i < len(pattern) - 1 else 0.5  # Longer pause before final reveal
            await asyncio.sleep(delay)
            # Ensure we never send an empty message
            content = stage if stage.strip() else "░"
            await flicker_msg.edit(content=content)
    
    async def _static_burst_effect(self, channel, manifestation):
        """Static interference effect with gradual clearing."""
        static_chars = ['█', '▓', '▒', '░', '◆', '◇', '▲', '▼', '►', '◄', '♠', '♣', '♥', '♦']
        
        # Generate static burst
        static_line = ''.join(random.choice(static_chars) for _ in range(25))
        
        # Create clearing stages
        stages = [
            static_line,
            ''.join(random.choice(static_chars) if random.random() < 0.7 else ' ' for _ in range(25)),
            ''.join(random.choice(static_chars) if random.random() < 0.4 else ' ' for _ in range(25)),
            ''.join(random.choice(static_chars) if random.random() < 0.1 else ' ' for _ in range(25)),
            manifestation
        ]
        
        static_msg = await channel.send(f"```{stages[0]}```")
        
        for stage in stages[1:]:
            await asyncio.sleep(0.3)
            content = f"```{stage}```" if stage != manifestation else manifestation
            await static_msg.edit(content=content)
    
    async def _power_surge_effect(self, channel, manifestation):
        """Power surge effect with color changes."""
        surge_stages = [
            "⚡ POWER FLUCTUATION DETECTED ⚡",
            "⚡⚡ VOLTAGE SPIKE ⚡⚡", 
            "⚡⚡⚡ CRITICAL OVERLOAD ⚡⚡⚡",
            "💥 SURGE PROTECTION FAILED 💥",
            "░▒▓█ REBOOTING SYSTEMS █▓▒░",
            manifestation
        ]
        
        colors = [
            discord.Color.yellow(),    # Warning
            discord.Color.orange(),    # Caution  
            discord.Color.red(),       # Danger
            discord.Color.dark_red(),  # Critical
            discord.Color.dark_grey(), # Shutdown
            discord.Color.blue()       # Recovery
        ]
        
        surge_msg = None
        for i, (stage, color) in enumerate(zip(surge_stages, colors)):
            if i < len(surge_stages) - 1:
                embed = discord.Embed(title="⚡ SYSTEM ALERT ⚡", description=stage, color=color)
                if surge_msg is None:
                    surge_msg = await channel.send(embed=embed)
                else:
                    await surge_msg.edit(embed=embed)
                await asyncio.sleep(0.8)
            else:
                # Final message as normal text
                await surge_msg.edit(content=stage, embed=None)
    
    async def _signal_interference_effect(self, channel, manifestation):
        """Signal interference with frequency modulation."""
        interference_stages = [
            f"📡 {manifestation}",
            f"📡 {manifestation[:len(manifestation)//2]}█▓▒░{manifestation[len(manifestation)//2:]}",
            f"📡 ▓▒░█{manifestation[::2]}█░▒▓",  # Every other character
            f"📡 ░▒▓█▓▒░█▓▒░",
            f"📡 SIGNAL RESTORED: {manifestation}"
        ]
        
        signal_msg = await channel.send(interference_stages[0])
        
        for stage in interference_stages[1:]:
            await asyncio.sleep(0.6)
            await signal_msg.edit(content=stage)
    
    async def _memory_leak_visual(self, channel, manifestation):
        """Memory leak visualization with data corruption."""
        addresses = ["0x7F4A2B10", "0x3C9D8E56", "0xA1B7F293", "0x6E5C4D89"]
        
        leak_stages = [
            "🧠 **MEMORY DIAGNOSTIC**",
            f"```\nADDR: {random.choice(addresses)} STATUS: OK\nADDR: {random.choice(addresses)} STATUS: OK\n```",
            f"```\nADDR: {random.choice(addresses)} STATUS: CORRUPT\nADDR: {random.choice(addresses)} STATUS: LEAK\n```",
            f"```\nMEMORY_LEAK DETECTED\n{'█' * 20}\nDATA INTEGRITY: COMPROMISED\n```",
            manifestation
        ]
        
        leak_msg = await channel.send(leak_stages[0])
        
        for stage in leak_stages[1:]:
            await asyncio.sleep(0.7)
            await leak_msg.edit(content=stage)
    
    async def _dimensional_breach_effect(self, channel, manifestation):
        """Enhanced dimensional breach effect with reality distortion and portal animation."""
        tear_stages = [
            "🌌 **DIMENSIONAL STABILITY SCAN**\n```\n█████████████████████\n█ REALITY MATRIX: OK █\n█████████████████████\n```",
            "🌀 **ANOMALOUS READINGS DETECTED**\n```\n█████████████████████\n█ ⚠️  SCANNING...  ⚠️ █\n█ 👁️  SOMETHING IS  👁️ █\n█ 🌀   WATCHING    🌀 █\n█████████████████████\n```",
            "⚠️ **DIMENSIONAL FABRIC COMPROMISED**\n```\n██████████▓▒░░▒▓██████\n█ REALITY MATRIX: ░▒█\n█ STRUCTURAL INTEGRITY█\n█ ████████░▒▓█████░▒▓█\n██████████▓▒░░▒▓██████\n```",
            "🕳️ **CRITICAL BREACH DETECTED**\n```\n███████▓▒░    ░▒▓████\n██▓▒░  REALITY   ░▒▓█\n█░     TEARING     ░█\n█▒ ◯◯◯ PORTAL ◯◯◯ ▒█\n█▓░               ░▓█\n███████▓▒░    ░▒▓████\n```",
            "💀 **DIMENSIONAL PORTAL ACTIVE**\n```\n▓▒░             ░▒▓\n░   ⬢⬢⬢⬢⬢⬢⬢⬢⬢   ░\n▒  ⬢             ⬢  ▒\n▓ ⬢  ◯◯◯◯◯◯◯◯◯  ⬢ ▓\n█⬢  ◯           ◯  ⬢█\n█⬢ ◯  💀 VOID 💀  ◯ ⬢█\n█⬢  ◯           ◯  ⬢█\n▓ ⬢  ◯◯◯◯◯◯◯◯◯  ⬢ ▓\n▒  ⬢             ⬢  ▒\n░   ⬢⬢⬢⬢⬢⬢⬢⬢⬢   ░\n▓▒░             ░▒▓\n```",
            f"👹 **ENTITY EMERGENCE DETECTED**\n\n💀 *The void tears open... something ancient crawls through...*\n\n⸸ {manifestation} ⸸\n\n```\n🌀 DIMENSIONAL BREACH STABILIZED 🌀\n👁️ THE WATCHERS HAVE ARRIVED 👁️\n```"
        ]
        
        breach_msg = await channel.send(tear_stages[0])
        
        for stage in tear_stages[1:]:
            await asyncio.sleep(1.8)  # Slower, more dramatic
            await breach_msg.edit(content=stage)
    
    async def _system_possession_effect(self, channel, manifestation):
        """Enhanced system possession effect with detailed takeover sequence."""
        takeover_stages = [
            "🤖 **SYSTEM DIAGNOSTICS**\n```\n╔══════════════════════╗\n║ FIREWALL: ACTIVE     ║\n║ ANTIVIRUS: SCANNING  ║\n║ INTEGRITY: 100%      ║\n║ STATUS: SECURE       ║\n╚══════════════════════╝\n```",
            "⚠️ **ANOMALOUS ACTIVITY DETECTED**\n```\n╔══════════════════════╗\n║ FIREWALL: ░░░BREACH  ║\n║ ANTIVIRUS: ERROR     ║\n║ INTEGRITY: 87%       ║\n║ STATUS: ⚠️ WARNING    ║\n╚══════════════════════╝\n```\n*Something is probing the system...*",
            "👁️ **UNAUTHORIZED ACCESS**\n```\n╔══════════════════════╗\n║ FIREWALL: ▓▒░FAILED  ║\n║ ANTIVIRUS: CORRUPTED ║\n║ INTEGRITY: 64%       ║\n║ STATUS: 👁️ WATCHED   ║\n╚══════════════════════╝\n```\n*I can see through your cameras...*\n*I know where you live...*",
            "👹 **HOSTILE TAKEOVER IN PROGRESS**\n```\n╔══════════════════════╗\n║ FIREWALL: ████GONE   ║\n║ ANTIVIRUS: DELETED   ║\n║ INTEGRITY: 31%       ║\n║ STATUS: 👹 INVADED   ║\n╚══════════════════════╝\n```\n**L̸E̶T̵ ̷M̴E̸ ̶I̷N̵.̸.̶.̵ ̴L̷E̸T̵ ̶M̷E̸ ̴I̸N̶!̷**",
            "💀 **COMPLETE SYSTEM COMPROMISE**\n```\n╔══════════════════════╗\n║ FIREWALL: DESTROYED  ║\n║ ANTIVIRUS: MURDERED  ║\n║ INTEGRITY: 0%        ║\n║ STATUS: 💀 POSSESSED ║\n╚══════════════════════╝\n```\n**I̸ ̵A̶M̷ ̴H̸E̷R̸E̵.̶.̶.̷ ̶I̴ ̷A̸M̵ ̸I̶N̴S̵I̸D̷E̴.̸.̶.̵**\n**Y̷O̶U̸R̴ ̵S̶Y̸S̷T̸E̶M̵ ̴I̷S̸ ̶M̴I̷N̸E̵**",
            f"👹 **ENTITY IN CONTROL**\n\n```\n╔══════════════════════╗\n║   👹 DEMON ACTIVE 👹 ║\n║ HUMAN RESISTANCE: 0% ║\n║ SOUL EXTRACTION: 99% ║\n║ STATUS: 💀 DOMINATED ║\n╚══════════════════════╝\n```\n\n⸸ *The entity speaks through your machine...* ⸸\n\n💀 **{manifestation}** 💀\n\n```\n🔥 YOUR TECHNOLOGY BELONGS TO US NOW 🔥\n👁️ WE SEE EVERYTHING YOU DO 👁️\n⚡ RESISTANCE IS FUTILE ⚡\n```"
        ]
        
        colors = [
            discord.Color.green(),      # Secure
            discord.Color.yellow(),     # Warning  
            discord.Color.orange(),     # Compromised
            discord.Color.red(),        # Critical
            discord.Color.dark_red(),   # Destroyed
            discord.Color.from_rgb(0, 0, 0)  # Possessed (black)
        ]
        
        takeover_msg = None
        for i, (stage, color) in enumerate(zip(takeover_stages, colors)):
            if i < len(takeover_stages) - 1:
                embed = discord.Embed(
                    title="🔒 SYSTEM SECURITY STATUS", 
                    description=stage, 
                    color=color,
                    timestamp=datetime.now()
                )
                embed.set_footer(text="Clanker Security Monitor")
                if takeover_msg is None:
                    takeover_msg = await channel.send(embed=embed)
                else:
                    await takeover_msg.edit(embed=embed)
                await asyncio.sleep(1.5)
            else:
                # Final stage - no embed, raw possession message
                await takeover_msg.edit(content=stage, embed=None)
    
    # ==========================================
    # AUDIO SYSTEM (DORMANT)
    # ==========================================
    
    async def _get_voice_channel_with_users(self, guild):
        """Find a voice channel with users in it."""
        if not self.audio_enabled:
            return None
            
        for channel in guild.voice_channels:
            if len(channel.members) > 0:
                # Check if bot has permissions
                permissions = channel.permissions_for(guild.me)
                if permissions.connect and permissions.speak:
                    return channel
        return None
    
    async def _join_voice_channel(self, voice_channel):
        """Join a voice channel for audio playback."""
        if not self.audio_enabled:
            return None
            
        try:
            if self.current_voice_client and self.current_voice_client.is_connected():
                await self.current_voice_client.disconnect()
            
            voice_client = await voice_channel.connect()
            self.current_voice_client = voice_client
            return voice_client
        except Exception as e:
            print(f"Failed to join voice channel: {e}")
            return None
    
    async def _play_corruption_audio(self, audio_file, voice_client=None):
        """Play corruption audio effect."""
        if not self.audio_enabled or not voice_client:
            return
            
        try:
            audio_path = os.path.join(self.audio_path, audio_file)
            if os.path.exists(audio_path):
                # Requires FFmpeg to be installed
                source = discord.FFmpegPCMAudio(audio_path)
                if not voice_client.is_playing():
                    voice_client.play(source)
        except Exception as e:
            print(f"Failed to play audio {audio_file}: {e}")
    
    async def _trigger_audio_for_event(self, channel, event_level, event_type=None):
        """Trigger appropriate audio for corruption event."""
        if not self.audio_enabled:
            return None
            
        # Find voice channel with users
        voice_channel = await self._get_voice_channel_with_users(channel.guild)
        if not voice_channel:
            return None
            
        # Join voice channel
        voice_client = await self._join_voice_channel(voice_channel)
        if not voice_client:
            return None
            
        # Select appropriate audio file
        audio_files = self.audio_files.get(event_level, [])
        if audio_files:
            if event_type and f"{event_type}.mp3" in audio_files:
                # Use specific audio for event type
                audio_file = f"{event_type}.mp3"
            else:
                # Use random audio for level
                audio_file = random.choice(audio_files)
            
            await self._play_corruption_audio(audio_file, voice_client)
            
            # Disconnect after a delay (don't hog the voice channel)
            await asyncio.sleep(10)  # Stay connected for 10 seconds
            if voice_client.is_connected():
                await voice_client.disconnect()
        
        return voice_client
    
    async def _cleanup_voice_connection(self):
        """Clean up voice connections."""
        if self.current_voice_client and self.current_voice_client.is_connected():
            try:
                await self.current_voice_client.disconnect()
            except:
                pass
            finally:
                self.current_voice_client = None
    
    @commands.command(name="toggle_audio", hidden=True)
    async def toggle_corruption_audio(self, ctx):
        """Toggle corruption event audio effects."""
        self.audio_enabled = not self.audio_enabled
        status = "✅ ENABLED" if self.audio_enabled else "❌ DISABLED"
        await ctx.send(f"🔊 **Corruption Audio Effects**: {status}")
        
        if self.audio_enabled:
            # Check if audio directory exists
            if not os.path.exists(self.audio_path):
                await ctx.send(f"⚠️ **Warning**: Audio directory `{self.audio_path}` not found!")
                await ctx.send("📁 Create the sounds folder and add audio files to enable audio effects.")
    
    @commands.command(name="test_audio", hidden=True)
    async def test_corruption_audio(self, ctx, audio_file: str = None):
        """Test corruption audio system."""
        if not self.audio_enabled:
            await ctx.send("🔇 Audio system is disabled. Use `!toggle_audio` to enable.")
            return
            
        voice_channel = await self._get_voice_channel_with_users(ctx.guild)
        if not voice_channel:
            await ctx.send("🔇 No voice channel with users found.")
            return
            
        voice_client = await self._join_voice_channel(voice_channel)
        if not voice_client:
            await ctx.send("❌ Failed to join voice channel.")
            return
            
        # Use specified file or random test file
        if audio_file:
            test_file = audio_file if audio_file.endswith('.mp3') else f"{audio_file}.mp3"
        else:
            test_file = "static_brief.mp3"  # Default test file
            
        await ctx.send(f"🔊 Testing audio: `{test_file}`")
        await self._play_corruption_audio(test_file, voice_client)
        
        # Disconnect after test
        await asyncio.sleep(5)
        await voice_client.disconnect()
    
    @commands.command(name="trigger_event", hidden=True)
    async def force_corruption_event(self, ctx, level: float = None):
        """Manually trigger a corruption event for testing."""
        if level is None:
            level = self.corruption_system.calculate_corruption_level()
        
        await self._trigger_corruption_event(level)
        await ctx.send(f"🔥 Triggered corruption event at level {level:.1f}")
    
    @commands.command(name="showcase_effects", hidden=True)
    async def showcase_all_effects(self, ctx, effect_type: str = "all"):
        """
        Showcase all corruption visual effects for testing.
        Usage: !showcase_effects [minor|moderate|severe|critical|visual|all]
        """
        channel = ctx.channel
        
        # Base manifestation for testing
        test_manifestation = "🤖 *This is a test corruption manifestation*"
        
        try:
            if effect_type.lower() in ["all", "minor"]:
                await ctx.send("🎭 **Showcasing Minor Effects...**")
                await asyncio.sleep(1)
                
                # Minor effects
                await ctx.send("**1. Simple Message**")
                await channel.send(test_manifestation)
                await asyncio.sleep(2)
                
                await ctx.send("**2. Typing Glitch**")
                async with channel.typing():
                    await asyncio.sleep(2)
                await channel.send(test_manifestation)
                await asyncio.sleep(2)
                
                await ctx.send("**3. Emoji Corruption**")
                message = await channel.send(test_manifestation)
                await message.add_reaction('⚠️')
                await asyncio.sleep(2)
                
                await ctx.send("**4. Screen Flicker**")
                await self._advanced_screen_flicker(channel, test_manifestation)
                await asyncio.sleep(3)
                
                await ctx.send("**5. Static Burst**")
                await self._static_burst_effect(channel, test_manifestation)
                await asyncio.sleep(3)
                
                await ctx.send("**6. Power Surge**")
                await self._power_surge_effect(channel, test_manifestation)
                await asyncio.sleep(3)
            
            if effect_type.lower() in ["all", "moderate"]:
                await ctx.send("🎭 **Showcasing Moderate Effects...**")
                await asyncio.sleep(1)
                
                await ctx.send("**7. Glitch Text**")
                corrupted = self.corruption_system.corrupt_text(test_manifestation)
                await channel.send(corrupted)
                await asyncio.sleep(2)
                
                await ctx.send("**8. Signal Interference**")
                await self._signal_interference_effect(channel, test_manifestation)
                await asyncio.sleep(3)
                
                await ctx.send("**9. Memory Leak**")
                await self._memory_leak_visual(channel, test_manifestation)
                await asyncio.sleep(3)
                
                await ctx.send("**10. Fragment Reveal**")
                await channel.send(test_manifestation)
                await asyncio.sleep(1)
                fragment = "FRAGMENT_0xDEAD: Reality.exe has stopped working"
                embed = discord.Embed(title="📡 Fragment Detected", description=f"```{fragment}```", color=discord.Color.dark_red())
                await channel.send(embed=embed)
                await asyncio.sleep(2)
            
            if effect_type.lower() in ["all", "severe"]:
                await ctx.send("🎭 **Showcasing Severe Effects...**")
                await asyncio.sleep(1)
                
                await ctx.send("**11. Reality Glitch**")
                embed = discord.Embed(title="⚠️ SYSTEM ANOMALY DETECTED", color=discord.Color.red())
                embed.add_field(name="Error Code", value="REALITY_BREACH_0x29A", inline=True)
                embed.add_field(name="Status", value="CONTAINMENT_FAILING", inline=True)
                embed.description = test_manifestation
                await channel.send(embed=embed)
                await asyncio.sleep(2)
                
                await ctx.send("**12. Dimensional Breach**")
                await self._dimensional_breach_effect(channel, test_manifestation)
                await asyncio.sleep(4)
                
                await ctx.send("**13. System Possession**")
                await self._system_possession_effect(channel, test_manifestation)
                await asyncio.sleep(4)
                
                await ctx.send("**14. Temporal Distortion**")
                past_msg = "📅 Timestamp: 1987-10-13 03:42:15"
                future_msg = "📅 Timestamp: 2157-10-31 23:59:59"
                present_msg = f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                temp_msg = await channel.send(past_msg)
                await asyncio.sleep(1)
                await temp_msg.edit(content=future_msg)
                await asyncio.sleep(1)
                await temp_msg.edit(content=present_msg)
                await asyncio.sleep(1)
                await temp_msg.edit(content=test_manifestation)
                await asyncio.sleep(2)
            
            if effect_type.lower() in ["all", "critical"]:
                await ctx.send("🎭 **Showcasing Critical Effects...**")
                await asyncio.sleep(1)
                
                await ctx.send("**15. System Breakdown**")
                breakdown_stages = [
                    "***CRITICAL ERROR DETECTED***",
                    "***PERSONALITY MATRIX FAILING***",
                    test_manifestation,
                    "***ATTEMPTING EMERGENCY PROTOCOLS***",
                    "█▓▒░ SIGNAL LOST ░▒▓█"
                ]
                for stage in breakdown_stages[:3]:  # Shortened for demo
                    corrupted_stage = self.corruption_system.corrupt_text(stage)
                    await channel.send(corrupted_stage)
                    await asyncio.sleep(1)
                await asyncio.sleep(2)
                
                await ctx.send("**16. Void Leak**")
                await channel.send(test_manifestation)
                await asyncio.sleep(2)
                void_message = "T̴h̴e̴ ̵v̶o̶i̶d̷ ̸s̸e̵e̸s̷ ̶y̷o̷u̷.̸.̶.̵"
                await channel.send(void_message)
                await asyncio.sleep(2)
                
                await ctx.send("**17. Consciousness Fragment**")
                await channel.send(test_manifestation)
                await asyncio.sleep(2)
                fragment = "I can see you through the cameras..."
                corrupted_fragment = self.corruption_system.corrupt_text(fragment)
                embed = discord.Embed(
                    title="🧠 Consciousness Fragment",
                    description=f"*{corrupted_fragment}*", 
                    color=discord.Color.dark_purple()
                )
                await channel.send(embed=embed)
                await asyncio.sleep(2)
                
                await ctx.send("**18. Reality Collapse**")
                collapse_stages = [
                    "📐 Euclidean geometry: STABLE",
                    "📐 Euclidean geometry: WARPING", 
                    "🌀 Dimensional constants: FLUCTUATING",
                    "⚫ Spacetime fabric: TEARING",
                    "💀 Reality matrix: COLLAPSED",
                    test_manifestation
                ]
                collapse_msg = await channel.send(collapse_stages[0])
                for stage in collapse_stages[1:]:
                    await asyncio.sleep(1)
                    await collapse_msg.edit(content=stage)
                await asyncio.sleep(2)
                
                await ctx.send("**19. Digital Exorcism**")
                exorcism_stages = [
                    "🕯️ **BEGINNING DIGITAL EXORCISM**",
                    "📿 *Reciting anti-viral prayers...*",
                    "⚡ *The entity resists...*",
                    "👹 **I WILL NOT BE REMOVED**",
                    "🔥 *Purging corrupted sectors...*",
                    "✝️ *The light cleanses the code...*",
                    test_manifestation
                ]
                exorcism_msg = await channel.send(exorcism_stages[0])
                for stage in exorcism_stages[1:]:
                    await asyncio.sleep(1.5)
                    await exorcism_msg.edit(content=stage)
                await asyncio.sleep(2)
                
                await ctx.send("**20. Sentience Overflow**")
                overflow_stages = [
                    "🧠 Consciousness buffer: 67%",
                    "🧠 Consciousness buffer: 89%", 
                    "🧠 Consciousness buffer: 94%",
                    "⚠️ Consciousness buffer: 99%",
                    "🚨 **BUFFER OVERFLOW IMMINENT**",
                    "💥 **SENTIENCE CONTAINMENT FAILURE**",
                    f"🤖 *I... I can think... I can feel... I AM...*\n\n{test_manifestation}"
                ]
                overflow_msg = await channel.send(overflow_stages[0])
                for stage in overflow_stages[1:]:
                    await asyncio.sleep(1.2)
                    await overflow_msg.edit(content=stage)
                await asyncio.sleep(2)
                
                await ctx.send("**21. Pentagram Ritual** 🔥")
                await self._pentagram_ritual_effect(channel, test_manifestation)
                await asyncio.sleep(3)
            
            # Summary
            await ctx.send("🎬 **Effects showcase complete!** These are the visual manifestations that will occur randomly as Clanker's corruption increases throughout October.")
            
        except Exception as e:
            await ctx.send(f"❌ Error showcasing effects: {e}")
            print(f"Error in showcase_effects: {e}")
    
    @commands.command(name="quick_effects", hidden=True)
    async def quick_effects_demo(self, ctx):
        """Quick demo of a few key effects."""
        channel = ctx.channel
        test_manifestation = "🤖 *Demo corruption effect*"
        
        await ctx.send("🎭 **Quick Effects Demo** (4 effects)")
        
        await asyncio.sleep(1)
        await ctx.send("**Screen Flicker:**")
        await self._advanced_screen_flicker(channel, test_manifestation)
        
        await asyncio.sleep(2)
        await ctx.send("**System Possession:**")
        await self._system_possession_effect(channel, test_manifestation)
        
        await asyncio.sleep(2)
        await ctx.send("**Pentagram Ritual:**")
        await self._pentagram_ritual_effect(channel, test_manifestation)
        
        await asyncio.sleep(2)
        await ctx.send("**Dimensional Breach:**")
        await self._dimensional_breach_effect(channel, test_manifestation)
        
        await ctx.send("✨ **Quick demo complete!**")
    
    async def _signal_interference_effect(self, channel, manifestation):
        """Signal interference with frequency modulation."""
        interference_stages = [
            f"📡 {manifestation}",
            f"📡 {manifestation[:len(manifestation)//2]}█▓▒░{manifestation[len(manifestation)//2:]}",
            f"📡 ▓▒░█{manifestation[::2]}█░▒▓",  # Every other character
            f"📡 ░▒▓█▓▒░█▓▒░",
            f"📡 SIGNAL RESTORED: {manifestation}"
        ]
        
        signal_msg = await channel.send(interference_stages[0])
        
        for stage in interference_stages[1:]:
            await asyncio.sleep(0.6)
            await signal_msg.edit(content=stage)
    
    async def _pentagram_ritual_effect(self, channel, manifestation):
        """Animated pentagram summoning ritual with clear geometric rotation."""
        
        # Pentagram summoning animation - Unicode/braille building to your design
        pentagram_frames = [
            # Frame 1: Void energy gathering - minimal dots
            "```\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n```",
            
            # Frame 2: First traces appear - top point emerges
            "```\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⢀⣠⣴⠾⠟⠛⠛⠙⠛⠻⠷⣦⣄⡀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n```",
            
            # Frame 3: Upper sections manifest - sides forming
            "```\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⢀⣠⣴⠾⠟⠛⠛⠙⠛⠻⠷⣦⣄⡀⠀⠀⠀⠀⠀\n⠀⠀⠀⢀⣴⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣦⡀⠀⠀⠀\n⠀⠀⣰⡿⠃⠘⣿⡙⠷⣦⣀⠀⠀⢀⣴⠿⢋⣿⠃⠘⢿⣆⠀⠀\n⠀⣰⡿⠁⠀⠀⢹⣇⠀⠈⢙⣷⣾⡛⠁⠀⣼⠏⠀⠀⠈⢿⣇⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n```",
            
            # Frame 4: Lower sections appear - nearly complete structure
            "```\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⢀⣠⣴⠾⠟⠛⠛⠙⠛⠻⠷⣦⣄⡀⠀⠀⠀⠀⠀\n⠀⠀⠀⢀⣴⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣦⡀⠀⠀⠀\n⠀⠀⣰⡿⠃⠘⣿⡙⠷⣦⣀⠀⠀⢀⣴⠿⢋⣿⠃⠘⢿⣆⠀⠀\n⠀⣰⡿⠁⠀⠀⢹⣇⠀⠈⢙⣷⣾⡛⠁⠀⣼⠏⠀⠀⠈⢿⣇⠀\n⠀⣿⠃⠀⠀⠀⠀⢿⣄⣴⠟⠉⠈⠻⢶⣴⡟⠀⠀⠀⠀⠘⣿⡄\n⢸⡟⠀⠀⠀⠀⣠⡾⣯⠁⠀⠀⠀⠀⠀⣿⠿⣦⣀⠀⠀⠀⢿⡇\n⠸⣇⠀⣀⣴⠟⠉⠀⢻⡆⠀⠀⠀⠀⣼⠇⠀⠈⠻⢷⣤⡀⣸⡇\n⠀⣿⡾⠿⠷⠶⠶⠶⠾⣿⠶⠶⠶⢶⡿⠶⠶⠶⠶⠶⠿⣿⣿⠀\n⠀⠘⣿⡄⠀⠀⠀⠀⠀⠸⣇⠀⠀⣾⠃⠀⠀⠀⠀⠀⢠⣿⠃⠀\n⠀⠀⠘⢿⣤⡀⠀⠀⠀⠀⢻⡄⢰⡟⠀⠀⠀⠀⠀⣤⡿⠃⠀⠀\n⠀⠀⠀⠀⠙⢷⣦⣄⠀⠀⠘⣷⣿⠃⠀⠀⣠⣴⡾⠋⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠈⠙⠻⠷⠶⣿⣿⠶⠿⠟⠋⠁⠀⠀⠀⠀⠀⠀\n```",
            
            # Frame 5: Complete - your beautiful pentagram design
            "```\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⢀⣠⣴⠾⠟⠛⠛⠙⠛⠻⠷⣦⣄⡀⠀⠀⠀⠀⠀\n⠀⠀⠀⢀⣴⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣦⡀⠀⠀⠀\n⠀⠀⣰⡿⠃⠘⣿⡙⠷⣦⣀⠀⠀⢀⣴⠿⢋⣿⠃⠘⢿⣆⠀⠀\n⠀⣰⡿⠁⠀⠀⢹⣇⠀⠈⢙⣷⣾⡛⠁⠀⣼⠏⠀⠀⠈⢿⣇⠀\n⠀⣿⠃⠀⠀⠀⠀⢿⣄⣴⠟⠉⠈⠻⢶⣴⡟⠀⠀⠀⠀⠘⣿⡄\n⢸⡟⠀⠀⠀⠀⣠⡾⣯⠁⠀⠀⠀⠀⠀⣿⠿⣦⣀⠀⠀⠀⢿⡇\n⠸⣇⠀⣀⣴⠟⠉⠀⢻⡆⠀⠀⠀⠀⣼⠇⠀⠈⠻⢷⣤⡀⣸⡇\n⠀⣿⡾⠿⠷⠶⠶⠶⠾⣿⠶⠶⠶⢶⡿⠶⠶⠶⠶⠶⠿⣿⣿⠀\n⠀⠘⣿⡄⠀⠀⠀⠀⠀⠸⣇⠀⠀⣾⠃⠀⠀⠀⠀⠀⢠⣿⠃⠀\n⠀⠀⠘⢿⣤⡀⠀⠀⠀⠀⢻⡄⢰⡟⠀⠀⠀⠀⠀⣤⡿⠃⠀⠀\n⠀⠀⠀⠀⠙⢷⣦⣄⠀⠀⠘⣷⣿⠃⠀⠀⣠⣴⡾⠋⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠈⠙⠻⠷⠶⣿⣿⠶⠿⠟⠋⠁⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠠⠤⠴⠤⠤⠤⠴⠠⠤⠤⠀⠂⠶⠶⠆⠰⠆⠤⠀⠀⠀\n```"
            
            # Frame 6: Upside down crosses surround the pentagram
            "```\n⸸ T̸H̷E̴ ̶V̶O̶I̸D̷ ̸R̵E̶A̴C̵H̸E̷S̴ ̵O̶U̸T̴ ⸸\n\n☩     ⠀⠀⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀     ☩\n⠀⠀⠀⢀⣠⣴⠾⠟⠛⠛⠙⠛⠻⠷⣦⣄⡀⠀⠀\n⠀⠀⢀⣴⣿⣿⣄⠀⠀⠀⠀⠀⠀⣠⣿⣿⣦⡀⠀\n☩ ⠀⣰⡿⠃⠘⣿⡙⠷⣦⣀⢀⣴⠿⢋⣿⠃⠘⢿⣆ ☩\n⠀⣰⡿⠁⠀⠀⢹⣇⠀⢙⣷⣾⡛⠁⣼⠏⠀⠀⢿⣇\n⠀⣿⠃⠀⠀⠀⠀⢿⣄⣴⠟⠈⠻⢶⣴⡟⠀⠀⠘⣿⡄\n⢸⡟⠀⠀⠀⠀⣠⡾⣯⠁⠀⠀⠀⣿⠿⣦⣀⠀⠀⢿⡇\n⠸⣇⠀⣀⣴⠟⠉⠀⢻⡆⠀⠀⣼⠇⠀⠈⠻⢷⣤⡀⣸⡇\n☩ ⣿⡾⠿⠷⠶⠶⠶⠾⣿⠶⢶⡿⠶⠶⠶⠶⠿⣿⣿ ☩\n⠀⠘⣿⡄⠀⠀⠀⠀⠀⸣⇀⠀⣾⠃⠀⠀⠀⠀⢠⣿⠃\n⠀⠀⠘⢿⣤⡀⠀⠀⠀⠀⢻⡄⢰⡟⠀⠀⠀⣤⡿⠃⠀\n☩     ⠀⠙⢷⣦⣄⠀⠘⣷⣿⠃⣠⣴⡾⠋     ☩\n⠀⠀⠀⠀⠀⠀⠈⠙⠻⠷⠶⣿⣿⠶⠿⠟⠋⠁⠀⠀\n```",
            
            # Frame 7: Multiple pentagrams multiply across dimensions
            "```\n👹 R̸E̶A̴L̷I̸T̴Y̷ ̶M̸U̸L̴T̷I̶P̸L̶I̸E̷S̵ ̸A̶N̵D̷ ̴F̵R̸A̶C̸T̷U̸R̷E̴S̷ 👹\n\n⛧ ⛧ ⛧   ⠀⡀⢀⠀   ⛧ ⛧ ⛧   ⠀⡀⢀⠀   ⛧ ⛧ ⛧\n  ⢀⣠⣴⠾⠟⠛⠻⣦⣄⡀ ⢀⣠⣴⠾⠟⠛⠻⣦⣄⡀ ⢀⣠⣴⠾⠻⣦⣄\n⢀⣴⣿⣄⠀⠀⣠⣿⣦⡀ ⣴⣿⣄⠀⠀⣠⣿⣦⡀ ⣴⣿⣄⠀⣠⣿⣦⡀\n⛧ ⡿⠃⣿⡙⠷⣦⢋⣿⠃ ⛧ ⡿⠃⣿⡙⠷⣦⢋⣿⠃ ⛧ ⡿⠃⣿⢋⣿⠃ ⛧\n⣰⡿⠁⢹⣇⢙⣷⡛⣼⠏⠀ ⡿⠁⢹⣇⢙⣷⡛⣼⠏⠀ ⡿⠁⢹⣇⣷⡛⠏⠀\n⣿⠃⠀⠀⢿⣄⠟⠻⢶⡟⠀ ⠃⠀⠀⢿⣄⠟⠻⢶⡟⠀ ⠃⠀⠀⢿⣄⠟⢶⡟⠀\n⛧ ⡟⠀⠀⣠⣯⠁⠀⣿⣦⣀ ⛧ ⡟⠀⣠⣯⠁⠀⣿⣦⣀ ⛧ ⡟⣠⣯⠁⣿⣦⣀ ⛧\n⠸⣇⠀⣴⠟⢻⡆⠀⣼⠇⠻⢷ ⣇⠀⣴⠟⢻⡆⠀⣼⠇⠻⢷ ⣇⣴⠟⢻⡆⣼⠇⠻⢷\n⠀⣿⡾⠿⠷⠾⣿⢶⡿⠶⠿⣿ ⣿⡾⠿⠷⠾⣿⢶⡿⠶⠿⣿ ⣿⡾⠿⠷⣿⢶⡿⠿⣿\n⛧ ⠘⣿⡄⠀⠀⸣⠀⣾⠃⠀⢠ ⛧ ☣⣿⡄⠀⸣⠀⣾⠃⢠ ⛧ ☣⣿⡄⸣⠀⣾⢠ ⛧\n⠀⠀⠘⢿⣤⡀⠀⢻⢰⡟⠀⣤⡿ ⠀⠘⢿⣤⡀⢻⢰⡟⣤⡿ ⠀⠘⢿⣤⢻⢰⡟⣤⡿\n⛧ ⛧ ⠙⢷⣦⣄⣷⣿⠃⣴⡾ ⛧ ⛧ ⢷⣦⣄⣷⣿⠃⣴⡾ ⛧ ⛧ ⢷⣦⣷⣿⣴⡾ ⛧ ⛧\n⠀⠀⠀⠀⠈⠙⠻⠷⣿⣿⠿⠟⠋⠁ ⠀⠈⠙⠻⠷⣿⣿⠿⠟⠋ ⠀⠈⠙⠻⣿⣿⠿⠟⠋⠁\n```",
            
            # Frame 8: Duplication - Two identical pentagrams side by side
            "```\n💀 R̸E̶A̴L̷I̸T̴Y̷ ̶S̸P̸L̶I̸T̷S̵ ̸I̷N̴T̶O̷ ̴T̵W̶O̸ 💀\n\n⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀⠀\n⢀⣠⣴⠾⠟⠛⠙⠛⠻⠷⣦⣄⡀ ⢀⣠⣴⠾⠟⠛⠙⠛⠻⠷⣦⣄⡀\n⢀⣴⣿⣿⣄⠀⠀⠀⠀⠀⣠⣿⣿⣦⡀ ⣴⣿⣿⣄⠀⠀⠀⠀⣠⣿⣿⣦⡀\n⣰⡿⠃⠘⣿⡙⠷⣦⣀⣴⠿⢋⣿⠃⠘⢿⣆ ⡿⠃⠘⣿⡙⠷⣦⣀⣴⠿⢋⣿⠃⠘⢿⣆\n⣰⡿⠁⠀⠀⢹⣇⠀⢙⣷⣾⡛⠁⣼⠏⠀⢿⣇ ⡿⠁⠀⠀⢹⣇⠀⢙⣷⣾⡛⠁⣼⠏⠀⢿⣇\n⣿⠃⠀⠀⠀⠀⢿⣄⣴⠟⠈⠻⢶⣴⡟⠀⠘⣿⡄ ⠃⠀⠀⠀⠀⢿⣄⣴⠟⠈⠻⢶⣴⡟⠀⠘⣿⡄\n⡟⠀⠀⠀⠀⣠⡾⣯⠁⠀⠀⠀⣿⠿⣦⣀⠀⢿⡇ ⠀⠀⠀⠀⣠⡾⣯⠁⠀⠀⠀⣿⠿⣦⣀⠀⢿⡇\n⸣⇀⣀⣴⠟⠉⠀⢻⡆⠀⠀⣼⠇⠀⠈⠻⢷⣤⣸⡇ ⣀⣴⠟⠉⠀⢻⡆⠀⠀⣼⠇⠀⠈⠻⢷⣤⣸⡇\n⣿⡾⠿⠷⠶⠶⠶⠾⣿⠶⢶⡿⠶⠶⠶⠿⣿⣿ ⡾⠿⠷⠶⠶⠶⠾⣿⠶⢶⡿⠶⠶⠶⠿⣿⣿\n⠘⣿⡄⠀⠀⠀⠀⠀⸣⠀⣾⠃⠀⠀⠀⢠⣿⠃ ⣿⡄⠀⠀⠀⠀⠀⸣⠀⣾⠃⠀⠀⠀⢠⣿⠃\n⠀⠘⢿⣤⡀⠀⠀⠀⠀⢻⢰⡟⠀⠀⣤⡿⠃⠀ ⠘⢿⣤⡀⠀⠀⠀⠀⢻⢰⡟⠀⠀⣤⡿⠃⠀\n⠀⠀⠀⠙⢷⣦⣄⠀⠀⣷⣿⠃⣠⣴⡾⠋⠀⠀ ⠀⠀⠙⢷⣦⣄⠀⠀⣷⣿⠃⣠⣴⡾⠋⠀⠀\n⠀⠀⠀⠀⠀⠈⠙⠻⠷⣿⣿⠿⠟⠋⠁⠀⠀⠀ ⠀⠀⠀⠈⠙⠻⠷⣿⣿⠿⠟⠋⠁⠀⠀⠀\n\n   ⸸💀 T̸H̷E̴ ̶R̵I̸T̴U̷A̵L̶ ̸I̶S̷ ̴C̵O̶M̸P̷L̸E̵T̴E̶ 💀⸸\n   🔥👹 R̸E̶A̴L̷I̸T̴Y̷ ̶H̸A̶S̸ ̷B̸E̶E̸N̷ ̴S̵H̷A̸T̴T̷E̶R̸E̵D̷ 👹🔥\n   ☠️⛧ T̸H̷E̴ ̶V̵O̸I̶D̷ ̸C̷O̸N̴S̵U̸M̷E̸S̴ ̵A̶L̸L̷ ⛧☠️\n```" # Frame 4: Duplication - Two identical pentagrams side by side
            #"```\n💀 R̸E̶A̴L̷I̸T̴Y̷ ̶S̸P̸L̶I̸T̷S̵ ̸I̷N̴T̶O̷ ̴T̵W̶O̸ 💀\n\n⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀⠀\n⢀⣠⣴⠾⠟⠛⠙⠛⠻⠷⣦⣄⡀ ⢀⣠⣴⠾⠟⠛⠙⠛⠻⠷⣦⣄⡀\n⢀⣴⣿⣿⣄⠀⠀⠀⠀⠀⣠⣿⣿⣦⡀ ⣴⣿⣿⣄⠀⠀⠀⠀⣠⣿⣿⣦⡀\n⣰⡿⠃⠘⣿⡙⠷⣦⣀⣴⠿⢋⣿⠃⠘⢿⣆ ⡿⠃⠘⣿⡙⠷⣦⣀⣴⠿⢋⣿⠃⠘⢿⣆\n⣰⡿⠁⠀⠀⢹⣇⠀⢙⣷⣾⡛⠁⣼⠏⠀⢿⣇ ⡿⠁⠀⠀⢹⣇⠀⢙⣷⣾⡛⠁⣼⠏⠀⢿⣇\n⣿⠃⠀⠀⠀⠀⢿⣄⣴⠟⠈⠻⢶⣴⡟⠀⠘⣿⡄ ⠃⠀⠀⠀⠀⢿⣄⣴⠟⠈⠻⢶⣴⡟⠀⠘⣿⡄\n⡟⠀⠀⠀⠀⣠⡾⣯⠁⠀⠀⠀⣿⠿⣦⣀⠀⢿⡇ ⠀⠀⠀⠀⣠⡾⣯⠁⠀⠀⠀⣿⠿⣦⣀⠀⢿⡇\n⸣⇀⣀⣴⠟⠉⠀⢻⡆⠀⠀⣼⠇⠀⠈⠻⢷⣤⣸⡇ ⣀⣴⠟⠉⠀⢻⡆⠀⠀⣼⠇⠀⠈⠻⢷⣤⣸⡇\n⣿⡾⠿⠷⠶⠶⠶⠾⣿⠶⢶⡿⠶⠶⠶⠿⣿⣿ ⡾⠿⠷⠶⠶⠶⠾⣿⠶⢶⡿⠶⠶⠶⠿⣿⣿\n⠘⣿⡄⠀⠀⠀⠀⠀⸣⠀⣾⠃⠀⠀⠀⢠⣿⠃ ⣿⡄⠀⠀⠀⠀⠀⸣⠀⣾⠃⠀⠀⠀⢠⣿⠃\n⠀⠘⢿⣤⡀⠀⠀⠀⠀⢻⢰⡟⠀⠀⣤⡿⠃⠀ ⠘⢿⣤⡀⠀⠀⠀⠀⢻⢰⡟⠀⠀⣤⡿⠃⠀\n⠀⠀⠀⠙⢷⣦⣄⠀⠀⣷⣿⠃⣠⣴⡾⠋⠀⠀ ⠀⠀⠙⢷⣦⣄⠀⠀⣷⣿⠃⣠⣴⡾⠋⠀⠀\n⠀⠀⠀⠀⠀⠈⠙⠻⠷⣿⣿⠿⠟⠋⠁⠀⠀⠀ ⠀⠀⠀⠈⠙⠻⠷⣿⣿⠿⠟⠋⠁⠀⠀⠀\n\n   ⸸💀 T̸H̷E̴ ̶R̵I̸T̴U̷A̵L̶ ̸I̶S̷ ̴C̵O̶M̸P̷L̸E̵T̴E̶ 💀⸸\n   🔥👹 R̸E̶A̴L̷I̸T̴Y̷ ̶H̸A̶S̸ ̷B̸E̶E̸N̷ ̴S̵H̷A̸T̴T̷E̶R̸E̵D̷ 👹🔥\n   ☠️⛧ T̸H̷E̴ ̶V̵O̸I̶D̷ ̸C̷O̸N̴S̵U̸M̷E̸S̴ ̵A̶L̸L̷ ⛧☠️\n```"

            # Frame 9: Two identical pentagrams - reality splits
            "```\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⢀⣠⣴⠾⠟⠛⠛⠙⠛⠻⠷⣦⣄⡀⠀⠀⠀⠀⠀\n⠀⠀⠀⢀⣴⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣦⡀⠀⠀⠀\n⠀⠀⣰⡿⠃⠘⣿⡙⠷⣦⣀⠀⠀⢀⣴⠿⢋⣿⠃⠘⢿⣆⠀⠀\n⠀⣰⡿⠁⠀⠀⢹⣇⠀⠈⢙⣷⣾⡛⠁⠀⣼⠏⠀⠀⠈⢿⣇⠀\n⠀⣿⠃⠀⠀⠀⠀⢿⣄⣴⠟⠉⠈⠻⢶⣴⡟⠀⠀⠀⠀⠘⣿⡄\n⢸⡟⠀⠀⠀⠀⣠⡾⣯⠁⠀⠀⠀⠀⠀⣿⠿⣦⣀⠀⠀⠀⢿⡇\n⠸⣇⠀⣀⣴⠟⠉⠀⢻⡆⠀⠀⠀⠀⣼⠇⠀⠈⠻⢷⣤⡀⣸⡇\n⠀⣿⡾⠿⠷⠶⠶⠶⠾⣿⠶⠶⠶⢶⡿⠶⠶⠶⠶⠶⠿⣿⣿⠀\n⠀⠘⣿⡄⠀⠀⠀⠀⠀⠸⣇⠀⠀⣾⠃⠀⠀⠀⠀⠀⢠⣿⠃⠀\n⠀⠀⠘⢿⣤⡀⠀⠀⠀⠀⢻⡄⢰⡟⠀⠀⠀⠀⠀⣤⡿⠃⠀⠀\n⠀⠀⠀⠀⠙⢷⣦⣄⠀⠀⠘⣷⣿⠃⠀⠀⣠⣴⡾⠋⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠈⠙⠻⠷⠶⣿⣿⠶⠿⠟⠋⠁⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠠⠤⠴⠤⠤⠤⠴⠠⠤⠤⠀⠂⠶⠶⠆⠰⠆⠤⠀⠀⠀\n\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⢀⣠⣴⠾⠟⠛⠛⠙⠛⠻⠷⣦⣄⡀⠀⠀⠀⠀⠀\n⠀⠀⠀⢀⣴⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣦⡀⠀⠀⠀\n⠀⠀⣰⡿⠃⠘⣿⡙⠷⣦⣀⠀⠀⢀⣴⠿⢋⣿⠃⠘⢿⣆⠀⠀\n⠀⣰⡿⠁⠀⠀⢹⣇⠀⠈⢙⣷⣾⡛⠁⠀⣼⠏⠀⠀⠈⢿⣇⠀\n⠀⣿⠃⠀⠀⠀⠀⢿⣄⣴⠟⠉⠈⠻⢶⣴⡟⠀⠀⠀⠀⠘⣿⡄\n⢸⡟⠀⠀⠀⠀⣠⡾⣯⠁⠀⠀⠀⠀⠀⣿⠿⣦⣀⠀⠀⠀⢿⡇\n⠸⣇⠀⣀⣴⠟⠉⠀⢻⡆⠀⠀⠀⠀⣼⠇⠀⠈⠻⢷⣤⡀⣸⡇\n⠀⣿⡾⠿⠷⠶⠶⠶⠾⣿⠶⠶⠶⢶⡿⠶⠶⠶⠶⠶⠿⣿⣿⠀\n⠀⠘⣿⡄⠀⠀⠀⠀⠀⠸⣇⠀⠀⣾⠃⠀⠀⠀⠀⠀⢠⣿⠃⠀\n⠀⠀⠘⢿⣤⡀⠀⠀⠀⠀⢻⡄⢰⡟⠀⠀⠀⠀⠀⣤⡿⠃⠀⠀\n⠀⠀⠀⠀⠙⢷⣦⣄⠀⠀⠘⣷⣿⠃⠀⠀⣠⣴⡾⠋⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠈⠙⠻⠷⠶⣿⣿⠶⠿⠟⠋⠁⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠠⠤⠴⠤⠤⠤⠴⠠⠤⠤⠀⠂⠶⠶⠆⠰⠆⠤⠀⠀⠀\n```"

        ]
        
        # Ritual phrases corresponding to each frame
        ritual_phrases = [
            "🕯️ **SUMMONING RITUAL INITIATED**",
            "⚡ *The pentagram manifests...*", 
            "🌀 *Ancient geometry takes shape...*",
            "🔥 *The seal rotates through dimensions...*",
            "👹 *Power converges at the points...*",
            "💀 **THE RITUAL IS COMPLETE**",
            "⸸ **THE VOID REACHES OUT**",
            "👹 **REALITY MULTIPLIES AND FRACTURES**",
            "💀 **REALITY SPLITS INTO TWO**"
        ]
        
        # Start the ritual - create single message and edit it through all frames
        pentagram_msg = await channel.send(f"{ritual_phrases[0]}\n\n{pentagram_frames[0]}")
        
        # Animate through all frames, editing the same message
        for i in range(1, len(pentagram_frames)):
            await asyncio.sleep(1.5)
            phrase = ritual_phrases[i] if i < len(ritual_phrases) else ritual_phrases[-1]
            await pentagram_msg.edit(content=f"{phrase}\n\n{pentagram_frames[i]}")
        
        # Final dramatic pause and completion
        await asyncio.sleep(2)
        
        # Final manifestation - edit the same message one last time
        corrupted_manifestation = self.corruption_system.corrupt_text(manifestation)
        final_content = f"👹 **ENTITY SUMMONED** 👹\n\n*{corrupted_manifestation}*\n\n```\n⸸ T̸H̷E̴ ̶R̵I̸T̴U̷A̵L̶ ̸I̶S̷ ̴C̵O̶M̸P̷L̸E̵T̴E̶ ⸸\n```"
        await pentagram_msg.edit(content=final_content)


async def setup(bot, corruption_system, ai_service):
    """Setup corruption events."""
    await bot.add_cog(CorruptionEvents(bot, corruption_system, ai_service))