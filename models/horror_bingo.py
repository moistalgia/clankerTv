"""
Horror Bingo System
==================

Interactive bingo game with movie-specific horror tropes.
"""

import json
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import discord
from discord.ext import commands


class BingoState(Enum):
    """Bingo game states."""
    WAITING = "waiting"
    ACTIVE = "active" 
    COMPLETED = "completed"


@dataclass
class BingoCard:
    """Represents a user's bingo card."""
    user_id: int
    movie_title: str
    tropes: List[str]  # 25 tropes in 5x5 grid
    marked: List[bool]  # Which squares are marked
    created_at: datetime
    completed_lines: List[str] = None  # List of completed line types
    
    def __post_init__(self):
        if self.completed_lines is None:
            self.completed_lines = []
        # Ensure we have exactly 25 tropes and marks
        if len(self.tropes) != 25:
            raise ValueError("Bingo card must have exactly 25 tropes")
        if len(self.marked) != 25:
            self.marked = [False] * 25
    
    def mark_square(self, index: int) -> bool:
        """Mark a square as completed. Returns True if newly marked."""
        if 0 <= index < 25 and not self.marked[index]:
            self.marked[index] = True
            return True
        return False
    
    def unmark_square(self, index: int) -> bool:
        """Unmark a square. Returns True if was marked."""
        if 0 <= index < 25 and self.marked[index]:
            self.marked[index] = False
            return True
        return False
    
    def check_lines(self) -> List[str]:
        """Check for completed lines. Returns list of line types."""
        lines = []
        
        # Check rows
        for row in range(5):
            start = row * 5
            if all(self.marked[start + col] for col in range(5)):
                lines.append(f"row_{row + 1}")
        
        # Check columns  
        for col in range(5):
            if all(self.marked[row * 5 + col] for row in range(5)):
                lines.append(f"col_{col + 1}")
        
        # Check diagonals
        if all(self.marked[i * 5 + i] for i in range(5)):
            lines.append("diagonal_1")
        if all(self.marked[i * 5 + (4 - i)] for i in range(5)):
            lines.append("diagonal_2")
        
        return lines
    
    def has_bingo(self) -> bool:
        """Check if card has any completed lines."""
        return len(self.check_lines()) > 0
    
    def get_new_lines(self) -> List[str]:
        """Get newly completed lines since last check."""
        current_lines = self.check_lines()
        new_lines = [line for line in current_lines if line not in self.completed_lines]
        self.completed_lines = current_lines
        return new_lines


class BingoView(discord.ui.View):
    """Interactive Discord UI for bingo cards."""
    
    def __init__(self, card: BingoCard, horror_bingo_system):
        super().__init__(timeout=3600)  # 1 hour timeout
        self.card = card
        self.horror_bingo = horror_bingo_system
        self.setup_buttons()
    
    def setup_buttons(self):
        """Create 25 buttons for the 5x5 bingo grid."""
        for i in range(25):
            button = BingoButton(i, self.card.tropes[i], self.card.marked[i])
            self.add_item(button)
    
    async def update_buttons(self):
        """Update button states after marking/unmarking."""
        for item in self.children:
            if isinstance(item, BingoButton):
                item.update_state(self.card.marked[item.index])
    
    async def handle_button_press(self, interaction: discord.Interaction, index: int):
        """Handle when a bingo square is pressed."""
        # Get the trope text for this square
        trope_text = self.card.tropes[index]
        
        # Toggle the square
        was_marked = self.card.marked[index]
        if was_marked:
            self.card.unmark_square(index)
            action = "unmarked"
        else:
            self.card.mark_square(index)
            action = "marked"
        
        # Update buttons
        await self.update_buttons()
        
        # Check for new bingo lines
        new_lines = self.card.get_new_lines()
        
        # Save progress
        await self.horror_bingo.save_card(self.card)
        
        # Create updated embed
        embed = self.horror_bingo.create_card_embed(self.card)
        
        # Check if this is a new bingo
        if new_lines:
            await self.handle_bingo(interaction, new_lines, embed)
        else:
            await interaction.response.edit_message(embed=embed, view=self)
    
    async def handle_bingo(self, interaction: discord.Interaction, new_lines: List[str], embed: discord.Embed):
        """Handle when user gets a bingo."""
        # Add bingo notification to embed
        line_names = {
            "row_1": "Top Row", "row_2": "Second Row", "row_3": "Middle Row", 
            "row_4": "Fourth Row", "row_5": "Bottom Row",
            "col_1": "Left Column", "col_2": "Second Column", "col_3": "Middle Column",
            "col_4": "Fourth Column", "col_5": "Right Column", 
            "diagonal_1": "Main Diagonal", "diagonal_2": "Anti Diagonal"
        }
        
        bingo_text = ", ".join(line_names.get(line, line) for line in new_lines)
        embed.add_field(
            name="🎉 BINGO! 🎉",
            value=f"You completed: **{bingo_text}**",
            inline=False
        )
        embed.color = discord.Color.gold()
        
        # Award badge for first bingo
        if len(self.card.completed_lines) == len(new_lines):  # First bingo
            badge_awarded = await self.horror_bingo.award_bingo_badge(interaction.user.id)
            if badge_awarded:
                embed.add_field(
                    name="🏆 Badge Earned!",
                    value="**Horror Bingo Master** - Got your first bingo!",
                    inline=False
                )
        
        await interaction.response.edit_message(embed=embed, view=self)
        
        # Send celebration message
        await interaction.followup.send(
            f"🎊 {interaction.user.mention} got BINGO! 🎊\n"
            f"Completed: **{bingo_text}**",
            ephemeral=False
        )


class BingoButton(discord.ui.Button):
    """Individual button for each bingo square."""
    
    def __init__(self, index: int, trope: str, is_marked: bool):
        self.index = index
        self.trope = trope
        
        # Determine position for layout
        row = index // 5
        col = index % 5
        
        # Truncate trope text to fit button (max ~80 chars for Discord)
        label = trope if len(trope) <= 80 else trope[:77] + "..."
        
        super().__init__(
            style=discord.ButtonStyle.success if is_marked else discord.ButtonStyle.secondary,
            label=label,
            row=row,
            custom_id=f"bingo_{index}"
        )
    
    def update_state(self, is_marked: bool):
        """Update button visual state."""
        self.style = discord.ButtonStyle.success if is_marked else discord.ButtonStyle.secondary
    
    async def callback(self, interaction: discord.Interaction):
        """Handle button press."""
        await self.view.handle_button_press(interaction, self.index)


class HorrorBingoSystem:
    """Main horror bingo game system."""
    
    def __init__(self, ai_service, badge_system=None):
        self.ai_service = ai_service
        self.badge_system = badge_system
        self.active_cards: Dict[int, BingoCard] = {}  # user_id -> BingoCard
        self.data_file = "horror_bingo_data.json"
        self.load_data()
    
    def load_data(self):
        """Load bingo data from file."""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                
            # Reconstruct bingo cards
            for user_id_str, card_data in data.get('active_cards', {}).items():
                user_id = int(user_id_str)
                card_data['created_at'] = datetime.fromisoformat(card_data['created_at'])
                self.active_cards[user_id] = BingoCard(**card_data)
                
        except (FileNotFoundError, json.JSONDecodeError):
            self.active_cards = {}
    
    def save_data(self):
        """Save bingo data to file."""
        try:
            data = {
                'active_cards': {}
            }
            
            # Convert cards to serializable format
            for user_id, card in self.active_cards.items():
                card_dict = asdict(card)
                card_dict['created_at'] = card.created_at.isoformat()
                data['active_cards'][str(user_id)] = card_dict
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving bingo data: {e}")
    
    async def save_card(self, card: BingoCard):
        """Save a single card and persist data."""
        self.active_cards[card.user_id] = card
        self.save_data()
    
    async def generate_tropes_for_movie(self, movie_title: str, movie_genre: str = None) -> List[str]:
        """Use AI to generate horror tropes specific to a movie."""
        
        genre_context = f" (a {movie_genre} film)" if movie_genre else ""
        
        prompt = f"""Generate exactly 25 specific horror tropes and elements that viewers should watch for in "{movie_title}"{genre_context}. 

These will be used for a horror bingo game, so they should be:
- Observable events/elements that happen in the movie
- Specific enough to be identifiable when they occur
- Varied in frequency (some common, some rare)
- Appropriate for the specific movie and its subgenre

Format as a simple numbered list 1-25, with each trope being 2-6 words maximum.

Examples of good tropes:
- Jump scare
- Creaking floorboards  
- Power goes out
- Cell phone no signal
- Character investigates alone
- Ominous mirror reflection
- Door slams shut
- Flickering lights

Movie: {movie_title}"""

        try:
            response = await self.ai_service.get_completion(prompt, max_tokens=800)
            
            # Parse the response to extract tropes
            lines = response.strip().split('\n')
            tropes = []
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('- ')):
                    # Remove numbering and clean up
                    trope = line.split('.', 1)[-1].strip()
                    trope = trope.lstrip('- ').strip()
                    if trope and len(trope) > 3:  # Valid trope
                        tropes.append(trope)
            
            # Ensure we have exactly 25
            if len(tropes) < 25:
                # Add some generic horror tropes to fill gaps
                generic_tropes = [
                    "Scream in distance", "Door creaks open", "Shadow moves", "Lights flicker",
                    "Phone rings ominously", "Music stops suddenly", "Footsteps overhead", 
                    "Window breaks", "Car won't start", "Someone says 'Hello?'",
                    "Blood appears", "Mirror shows reflection", "Clock strikes midnight",
                    "Animal acts strange", "Basement explored"
                ]
                
                needed = 25 - len(tropes)
                tropes.extend(random.sample(generic_tropes, min(needed, len(generic_tropes))))
            
            return tropes[:25]  # Ensure exactly 25
            
        except Exception as e:
            print(f"Error generating tropes: {e}")
            # Fallback to generic horror tropes
            return self.get_generic_tropes()
    
    def get_generic_tropes(self) -> List[str]:
        """Fallback generic horror tropes."""
        generic_tropes = [
            "Jump scare", "Creaking floorboards", "Power goes out", "Cell no signal",
            "Investigates alone", "Mirror reflection", "Door slams shut", "Lights flicker",
            "Scream in distance", "Car won't start", "Basement explored", "Attic sounds",
            "Someone says 'Hello?'", "Music stops suddenly", "Footsteps overhead",
            "Window breaks", "Blood appears", "Clock strikes twelve", "Animal acts strange",
            "Phone rings ominously", "Shadow moves", "Knocking sounds", "Voice whispers",
            "Something under bed", "Final girl emerges"
        ]
        return generic_tropes
    
    async def create_bingo_card(self, user_id: int, movie_title: str, movie_genre: str = None) -> BingoCard:
        """Create a new bingo card for a user."""
        # Generate movie-specific tropes
        tropes = await self.generate_tropes_for_movie(movie_title, movie_genre)
        
        # Shuffle for randomness
        random.shuffle(tropes)
        
        # Create card
        card = BingoCard(
            user_id=user_id,
            movie_title=movie_title,
            tropes=tropes,
            marked=[False] * 25,
            created_at=datetime.now()
        )
        
        # Save card
        await self.save_card(card)
        return card
    
    def create_card_embed(self, card: BingoCard) -> discord.Embed:
        """Create Discord embed showing the bingo card."""
        # Create visual grid representation
        grid_text = ""
        for row in range(5):
            row_text = ""
            for col in range(5):
                index = row * 5 + col
                mark = "✅" if card.marked[index] else "⬜"
                row_text += mark
            grid_text += row_text + "\n"
        
        embed = discord.Embed(
            title=f"🎃 Horror Bingo - {card.movie_title}",
            description=f"Click the trope buttons below when you spot them!\n\n**Progress Grid:**\n{grid_text}",
            color=discord.Color.orange()
        )
        
        # Show completion status
        total_marked = sum(card.marked)
        completion_percent = (total_marked / 25) * 100
        
        embed.add_field(
            name="📊 Progress",
            value=f"{total_marked}/25 squares marked ({completion_percent:.0f}%)",
            inline=True
        )
        
        # Show completed lines
        if card.completed_lines:
            line_names = {
                "row_1": "Row 1", "row_2": "Row 2", "row_3": "Row 3", "row_4": "Row 4", "row_5": "Row 5",
                "col_1": "Col 1", "col_2": "Col 2", "col_3": "Col 3", "col_4": "Col 4", "col_5": "Col 5",
                "diagonal_1": "Main Diag", "diagonal_2": "Anti Diag"
            }
            completed_names = [line_names.get(line, line) for line in card.completed_lines]
            embed.add_field(
                name="🎉 Completed Lines",
                value=", ".join(completed_names),
                inline=True
            )
        
        embed.add_field(
            name="💡 How to Play",
            value="Click button positions (A1-E5) to mark squares. Trope details shown privately when clicked!",
            inline=False
        )
        
        embed.set_footer(text="Buttons show grid positions (A1=top-left, E5=bottom-right) • Get 5 in a row for BINGO!")
        return embed
    
    async def award_bingo_badge(self, user_id: int) -> bool:
        """Award bingo badge to user if they don't have it."""
        if not self.badge_system:
            return False
            
        try:
            # Check if user already has bingo badge
            user_badges = self.badge_system.user_badges.get(user_id, [])
            if any(badge.badge_id == "horror_bingo_master" for badge in user_badges):
                return False
            
            # Award the badge
            badge_awarded = await self.badge_system.check_and_award_badge(user_id, "horror_bingo_master", 1)
            return badge_awarded
            
        except Exception as e:
            print(f"Error awarding bingo badge: {e}")
            return False
    
    def get_user_card(self, user_id: int) -> Optional[BingoCard]:
        """Get user's current bingo card."""
        return self.active_cards.get(user_id)
    
    def has_active_card(self, user_id: int) -> bool:
        """Check if user has an active bingo card."""
        return user_id in self.active_cards
    
    async def clear_user_card(self, user_id: int):
        """Clear user's bingo card."""
        if user_id in self.active_cards:
            del self.active_cards[user_id]
            self.save_data()