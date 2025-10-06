"""
Interactive List View Component
==============================

Provides paginated list display with navigation controls.
"""

import discord
from discord.ui import View, Button
from typing import List


class ListView(View):
    """Interactive paginated view for displaying movie lists."""
    
    def __init__(self, items: List[str], per_page: int = 10):
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

    def get_page_embed(self) -> discord.Embed:
        """Generate embed for current page."""
        start = self.page * self.per_page
        end = start + self.per_page
        chunk = self.items[start:end]

        embed = discord.Embed(title=f"🎃 Horror Playlist (Page {self.page+1})")
        for movie in chunk:
            embed.add_field(name=movie, value="—", inline=False)
        return embed

    async def prev_page(self, interaction: discord.Interaction):
        """Navigate to previous page."""
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    async def next_page(self, interaction: discord.Interaction):
        """Navigate to next page."""
        if (self.page+1) * self.per_page < len(self.items):
            self.page += 1
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)