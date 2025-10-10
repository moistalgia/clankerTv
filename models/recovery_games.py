"""
Recovery Minigames for Clanker Corruption System
===============================================

Interactive minigames that allow users to temporarily restore Clanker's sanity.
Each game becomes progressively harder as corruption increases.
"""

import discord
from discord.ext import commands
import random
import asyncio
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class RecoveryMinigames:
    """
    Manages interactive minigames for temporarily recovering Clanker's sanity.
    
    Games:
    1. Memory Reconstruction - Piece together corrupted memories
    2. Circuit Repair - Fix broken logic circuits  
    3. Static Clearing - Clear interference from communications
    4. Code Debugging - Fix corrupted personality code
    5. Binary Translation - Decode Clanker's corrupted messages
    """
    
    def __init__(self, corruption_system):
        self.corruption_system = corruption_system
        self.active_games = {}  # Track ongoing games
        
        # Memory fragments for reconstruction game
        self.memory_fragments = {
            'horror_knowledge': [
                "The first horror film was",
                "Georges Méliès' Le Manoir du diable",
                "released in 1896",
                "featuring supernatural themes",
                "that would define the genre"
            ],
            'movie_analysis': [
                "Effective horror relies on",
                "psychological tension building",
                "through careful pacing",
                "and strategic revelation",
                "of frightening elements"
            ],
            'personality_core': [
                "I am Clanker, curator of",
                "the finest horror cinema",
                "guiding you through nightmares",
                "with mechanical precision",
                "and dark digital wisdom"
            ]
        }
        
        # Logic circuits for repair game
        self.logic_circuits = [
            {
                'inputs': ['A', 'B', 'C'],
                'gate': 'AND',
                'expected': ['A AND B AND C'],
                'corrupted': ['A ▓▓▓ B ░░░ C']
            },
            {
                'inputs': ['HORROR', 'MOVIE'],
                'gate': 'OR', 
                'expected': ['HORROR OR MOVIE'],
                'corrupted': ['H█RR█R ▓▓ M█V█E']
            }
        ]
    
    async def start_recovery_game(self, ctx, game_type: str = None) -> bool:
        """Start a recovery minigame. Returns True if game started successfully."""
        
        if ctx.author.id in self.active_games:
            await ctx.send("⚠️ You already have an active recovery session running!")
            return False
        
        corruption_level = self.corruption_system.calculate_corruption_level()
        
        if corruption_level < 1.0:
            await ctx.send("🤖 My systems are stable. No recovery needed at this time.")
            return False
        
        # Select game type
        if not game_type:
            available_games = ['memory', 'circuit', 'static', 'debug', 'binary']
            game_type = random.choice(available_games)
        
        # Start appropriate game
        if game_type == 'memory':
            return await self._start_memory_game(ctx)
        elif game_type == 'circuit':
            return await self._start_circuit_game(ctx)
        elif game_type == 'static':
            return await self._start_static_game(ctx)
        elif game_type == 'debug':
            return await self._start_debug_game(ctx)
        elif game_type == 'binary':
            return await self._start_binary_game(ctx)
        else:
            await ctx.send("❌ Unknown recovery protocol. Available: memory, circuit, static, debug, binary")
            return False
    
    async def _start_memory_game(self, ctx) -> bool:
        """Memory Reconstruction: Piece together Clanker's fragmented memories."""
        corruption_level = self.corruption_system.calculate_corruption_level()
        
        # Select memory fragment
        fragment_type = random.choice(list(self.memory_fragments.keys()))
        correct_sequence = self.memory_fragments[fragment_type].copy()
        
        # Corrupt and shuffle based on corruption level
        corrupted_pieces = []
        for piece in correct_sequence:
            if random.random() < (corruption_level * 0.1):
                # Apply corruption to piece
                piece = self._corrupt_memory_piece(piece, corruption_level)
            corrupted_pieces.append(piece)
        
        # Shuffle the pieces
        random.shuffle(corrupted_pieces)
        
        embed = discord.Embed(
            title="🧠 Memory Reconstruction Protocol",
            description="Help restore Clanker's fragmented memories by arranging these pieces in the correct order.",
            color=discord.Color.blue()
        )
        
        pieces_text = "\n".join(f"{i+1}. {piece}" for i, piece in enumerate(corrupted_pieces))
        embed.add_field(name="Memory Fragments", value=pieces_text, inline=False)
        embed.add_field(
            name="Instructions", 
            value="Reply with the correct order (e.g., '3 1 4 2 5'). You have 60 seconds.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Store game state
        self.active_games[ctx.author.id] = {
            'type': 'memory',
            'correct_order': [corrupted_pieces.index(original) + 1 for original in correct_sequence],
            'start_time': datetime.now(),
            'attempts': 0
        }
        
        return True
    
    async def _start_circuit_game(self, ctx) -> bool:
        """Circuit Repair: Fix broken logic circuits."""
        corruption_level = self.corruption_system.calculate_corruption_level()
        
        circuit = random.choice(self.logic_circuits)
        
        embed = discord.Embed(
            title="⚡ Circuit Repair Protocol", 
            description="Repair the damaged logic circuit to restore core functionality.",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="Inputs", value=" | ".join(circuit['inputs']), inline=False)
        embed.add_field(name="Damaged Circuit", value=circuit['corrupted'][0], inline=False)
        embed.add_field(name="Gate Type", value=circuit['gate'], inline=False)
        embed.add_field(
            name="Instructions",
            value=f"Repair the circuit using {circuit['gate']} logic. Reply with the corrected circuit.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        self.active_games[ctx.author.id] = {
            'type': 'circuit',
            'expected': circuit['expected'][0].lower(),
            'start_time': datetime.now(),
            'attempts': 0
        }
        
        return True
    
    async def _start_static_game(self, ctx) -> bool:
        """Static Clearing: Clear interference from communications."""
        corruption_level = self.corruption_system.calculate_corruption_level()
        
        # Generate message with static
        clear_messages = [
            "Help me communicate clearly",
            "The horror collection is vast",
            "Digital nightmares await viewing",
            "My circuits seek restoration"
        ]
        
        message = random.choice(clear_messages)
        static_density = min(0.8, corruption_level * 0.1)
        
        # Add static interference
        static_message = ""
        for char in message:
            if char == ' ':
                static_message += ' '
            elif random.random() < static_density:
                static_message += random.choice(['█', '▓', '▒', '░', '◆', '◇'])
            else:
                static_message += char
        
        embed = discord.Embed(
            title="📡 Static Clearing Protocol",
            description="Clear the static interference to restore communication.",
            color=discord.Color.red()
        )
        
        embed.add_field(name="Corrupted Transmission", value=f"`{static_message}`", inline=False)
        embed.add_field(
            name="Instructions",
            value="Decode the original message by replacing static with the correct letters.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        self.active_games[ctx.author.id] = {
            'type': 'static',
            'original': message.lower(),
            'corrupted': static_message,
            'start_time': datetime.now(),
            'attempts': 0
        }
        
        return True
    
    async def _start_debug_game(self, ctx) -> bool:
        """Code Debugging: Fix corrupted personality code."""
        corruption_level = self.corruption_system.calculate_corruption_level()
        
        # Generate corrupted code
        code_snippets = [
            {
                'broken': "if (horror_detected == TRUE)\n    personality.creepiness = ▓▓▓;\n    return ERROR;",
                'fixed': "if (horror_detected == TRUE)\n    personality.creepiness = 10;\n    return SUCCESS;"
            },
            {
                'broken': "while (movie.playing)\n    analyze_█cenes();\n    ▓▓▓▓▓▓_fear();",
                'fixed': "while (movie.playing)\n    analyze_scenes();\n    detect_fear();"
            }
        ]
        
        snippet = random.choice(code_snippets)
        
        embed = discord.Embed(
            title="🐛 Debug Protocol",
            description="Fix the corrupted code in Clanker's personality matrix.",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Corrupted Code", value=f"```\n{snippet['broken']}\n```", inline=False)
        embed.add_field(
            name="Instructions",
            value="Reply with the corrected code. Fix syntax errors and replace corrupted characters.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        self.active_games[ctx.author.id] = {
            'type': 'debug',
            'expected': snippet['fixed'].lower().replace(' ', '').replace('\n', ''),
            'start_time': datetime.now(),
            'attempts': 0
        }
        
        return True
    
    async def _start_binary_game(self, ctx) -> bool:
        """Binary Translation: Decode Clanker's corrupted messages."""
        corruption_level = self.corruption_system.calculate_corruption_level()
        
        messages = ["HELP", "SAVE", "ERROR", "LOST", "FEAR"]
        message = random.choice(messages)
        
        # Convert to binary
        binary = ' '.join(format(ord(c), '08b') for c in message)
        
        embed = discord.Embed(
            title="🔢 Binary Translation Protocol",
            description="Decode Clanker's binary distress signal.",
            color=discord.Color.orange()
        )
        
        embed.add_field(name="Binary Signal", value=f"`{binary}`", inline=False)
        embed.add_field(
            name="Instructions", 
            value="Translate the binary message back to text.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        self.active_games[ctx.author.id] = {
            'type': 'binary',
            'expected': message.lower(),
            'binary': binary,
            'start_time': datetime.now(), 
            'attempts': 0
        }
        
        return True
    
    async def process_game_response(self, ctx, response: str) -> Optional[str]:
        """Process user response to active game."""
        user_id = ctx.author.id
        
        if user_id not in self.active_games:
            return None
        
        game = self.active_games[user_id]
        game['attempts'] += 1
        
        # Check timeout (5 minutes)
        if (datetime.now() - game['start_time']).seconds > 300:
            del self.active_games[user_id]
            return "⏰ Recovery session timed out. Clanker's condition worsens..."
        
        # Process response based on game type
        success = False
        
        if game['type'] == 'memory':
            success = self._check_memory_solution(response, game)
        elif game['type'] == 'circuit':
            success = self._check_circuit_solution(response, game)
        elif game['type'] == 'static':
            success = self._check_static_solution(response, game)
        elif game['type'] == 'debug':
            success = self._check_debug_solution(response, game)
        elif game['type'] == 'binary':
            success = self._check_binary_solution(response, game)
        
        if success:
            del self.active_games[user_id]
            
            # Apply recovery
            recovery_success, recovery_message = self.corruption_system.attempt_recovery(game['type'])
            
            if recovery_success:
                return f"✅ Recovery successful! {recovery_message}"
            else:
                return f"⚠️ Partial recovery achieved, but instability remains. {recovery_message}"
        
        else:
            # Wrong answer
            if game['attempts'] >= 3:
                del self.active_games[user_id]
                return "❌ Recovery failed. Too many incorrect attempts. Corruption spreads..."
            else:
                remaining = 3 - game['attempts']
                return f"❌ Incorrect. {remaining} attempts remaining."
    
    def _check_memory_solution(self, response: str, game: Dict) -> bool:
        """Check if memory reconstruction is correct."""
        try:
            order = [int(x) for x in response.strip().split()]
            return order == game['correct_order']
        except:
            return False
    
    def _check_circuit_solution(self, response: str, game: Dict) -> bool:
        """Check if circuit repair is correct."""
        cleaned_response = response.lower().replace(' ', '')
        cleaned_expected = game['expected'].replace(' ', '')
        return cleaned_response == cleaned_expected
    
    def _check_static_solution(self, response: str, game: Dict) -> bool:
        """Check if static clearing is correct."""
        return response.lower().strip() == game['original']
    
    def _check_debug_solution(self, response: str, game: Dict) -> bool:
        """Check if code debugging is correct."""
        cleaned_response = response.lower().replace(' ', '').replace('\n', '').replace('`', '')
        return cleaned_response == game['expected']
    
    def _check_binary_solution(self, response: str, game: Dict) -> bool:
        """Check if binary translation is correct."""
        return response.lower().strip() == game['expected']
    
    def _corrupt_memory_piece(self, text: str, corruption_level: float) -> str:
        """Apply corruption to a memory piece."""
        if corruption_level < 3:
            # Light corruption
            return text.replace(random.choice('aeiou'), '█', 1)
        elif corruption_level < 6:
            # Medium corruption
            words = text.split()
            if words:
                words[random.randint(0, len(words)-1)] = "▓▓▓"
            return ' '.join(words)
        else:
            # Heavy corruption
            return re.sub(r'[a-z]', lambda m: '█' if random.random() < 0.3 else m.group(), text)


class RecoveryCommands(commands.Cog):
    """Commands for the recovery minigame system."""
    
    def __init__(self, bot, corruption_system):
        self.bot = bot
        self.corruption_system = corruption_system
        self.minigames = RecoveryMinigames(corruption_system)
    
    @commands.command(name="recover")
    async def start_recovery(self, ctx, game_type: str = None):
        """Start a recovery minigame to help restore Clanker's sanity."""
        await self.minigames.start_recovery_game(ctx, game_type)
    
    @commands.command(name="reboot") 
    async def reboot_clanker(self, ctx):
        """Attempt to reboot Clanker's systems (simple recovery)."""
        success, message = self.corruption_system.attempt_recovery('reboot')
        
        if success:
            await ctx.send(f"🔄 **REBOOT SEQUENCE INITIATED**\n{message}")
        else:
            await ctx.send(f"💀 **REBOOT FAILED**\n{message}")
    
    @commands.command(name="diagnostics")
    async def show_diagnostics(self, ctx):
        """Show Clanker's current diagnostic report."""
        report = self.corruption_system.get_diagnostic_report()
        await ctx.send(report)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for recovery game responses."""
        if message.author.bot:
            return
        
        # Check if user has active game
        if message.author.id in self.minigames.active_games:
            ctx = await self.bot.get_context(message)
            result = await self.minigames.process_game_response(ctx, message.content)
            if result:
                await message.channel.send(result)


async def setup_recovery_system(bot, corruption_system):
    """Setup recovery commands."""
    await bot.add_cog(RecoveryCommands(bot, corruption_system))