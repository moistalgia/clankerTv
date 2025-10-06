"""
Next-Up Movie Poll UI View
========================

Discord UI components for the next-up movie voting system.
"""

import discord
from discord.ui import Button, View
from typing import List


class NextUpView(View):
    """Interactive voting interface for next-up movie selection."""
    
    def __init__(self, movies: List[str], movie_state, plex_service):
        super().__init__(timeout=None)
        self.movies = movies
        self.movie_state = movie_state
        self.plex_service = plex_service
        
        # Load current votes from requests
        self.votes = {title: movie_state.requests.get(title, []).copy() for title in movies}

        # Add vote button for each movie
        for title in movies:
            button = Button(
                label=f"🎺 Vote for {title[:25]}{'...' if len(title) > 25 else ''}",
                style=discord.ButtonStyle.primary,
                custom_id=f"vote_{title}"
            )
            button.callback = self.vote
            self.add_item(button)

        # Add Remove Doot button
        remove_btn = Button(
            label="❌ Remove Doot",
            style=discord.ButtonStyle.danger,
            custom_id="remove_vote"
        )
        remove_btn.callback = self.remove_vote
        self.add_item(remove_btn)

    async def vote(self, interaction: discord.Interaction):
        """Handle user voting for a movie."""
        user_id = interaction.user.id
        choice = interaction.data["custom_id"].replace("vote_", "")

        # Prevent multiple votes per user (check against persistent doot list)
        if any(user_id in voters for voters in self.movie_state.requests.values()):
            await interaction.response.send_message(
                "❌ You have already voted for another movie!",
                ephemeral=True
            )
            return

        # Record vote in this poll
        if choice not in self.votes:
            self.votes[choice] = []
        self.votes[choice].append(user_id)

        # Record vote in persistent dootlist
        if choice not in self.movie_state.requests:
            self.movie_state.requests[choice] = []
        if user_id not in self.movie_state.requests[choice]:
            self.movie_state.requests[choice].append(user_id)

        # Update embeds
        await self.update_message(interaction.message)

        # Confirm vote
        await interaction.response.send_message(
            f"✅ You voted for **{choice}**",
            ephemeral=True
        )

    async def remove_vote(self, interaction: discord.Interaction):
        """Handle removing user's vote."""
        user_id = interaction.user.id
        removed = False

        # Remove vote from this poll
        for title, voters in self.votes.items():
            if user_id in voters:
                voters.remove(user_id)
                removed = True

        # Remove vote from persistent dootlist and clean empty entries
        to_delete = []
        for title, voters in self.movie_state.requests.items():
            if user_id in voters:
                voters.remove(user_id)
            if len(voters) == 0:
                to_delete.append(title)
        for title in to_delete:
            del self.movie_state.requests[title]

        if removed:
            await self.update_message(interaction.message)
            await interaction.response.send_message(
                "✅ Your doot has been removed!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ You haven't voted yet.",
                ephemeral=True
            )

    async def update_message(self, message):
        """Update embeds with current horn emoji tallies."""
        embeds = []
        for title in self.movies:
            embed = await self._get_movie_embed(title)
            embeds.append(embed)
        
        await message.edit(embeds=embeds, view=self)
        
        # Update persistent embeds in movie state
        self.movie_state.nextup_state.embeds = embeds

    async def _get_movie_embed(self, title: str) -> discord.Embed:
        """Create movie embed with vote count."""
        # Get basic movie info from Plex
        movie_info = await self.plex_service.get_movie_metadata(title)
        
        if movie_info:
            embed = discord.Embed(
                title=movie_info['title'],
                description=movie_info.get('summary', 'No summary available')[:200] + '...' if len(movie_info.get('summary', '')) > 200 else movie_info.get('summary', 'No summary available'),
                color=0x8B0000
            )
            
            embed.add_field(
                name="Year",
                value=movie_info.get('year', 'Unknown'),
                inline=True
            )
            
            # Show total votes (persistent doot votes + current poll votes)
            persistent_votes = len(self.movie_state.requests.get(title, []))
            embed.add_field(
                name="Votes",
                value="🎺" * persistent_votes,
                inline=True
            )
            
            if movie_info.get('duration'):
                # Convert milliseconds to minutes if needed
                duration = movie_info['duration']
                if duration > 1000:  # Probably in milliseconds
                    duration = duration // (1000 * 60)  # Convert to minutes
                embed.add_field(
                    name="Duration",
                    value=f"{duration} min",
                    inline=True
                )
            
            if movie_info.get('genres'):
                embed.add_field(
                    name="Genres",
                    value=', '.join(movie_info['genres'][:3]),  # Show first 3 genres
                    inline=False
                )
        else:
            # Fallback embed if movie not found
            embed = discord.Embed(
                title=title,
                description="Movie information not available",
                color=0x8B0000
            )
            # Show total votes (persistent doot votes)
            persistent_votes = len(self.movie_state.requests.get(title, []))
            embed.add_field(
                name="Votes",
                value="🎺" * persistent_votes,
                inline=True
            )
        
        return embed