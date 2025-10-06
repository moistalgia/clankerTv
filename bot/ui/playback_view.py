"""
Playback Control View Component
==============================

Provides interactive playback controls for the currently playing movie.
"""

import discord
from discord.ui import View, Button
from services.plex_service import PlexService


class PlaybackControlView(View):
    """Interactive view for movie playback controls."""
    
    def __init__(self, plex_service: PlexService):
        super().__init__(timeout=300)  # 5 minute timeout
        self.plex_service = plex_service
        
        # Add playback control buttons
        self.add_item(Button(
            label="⏮️ -30s", 
            style=discord.ButtonStyle.secondary, 
            custom_id="seek_back"
        ))
        self.add_item(Button(
            label="▶️ Play/Pause", 
            style=discord.ButtonStyle.success, 
            custom_id="play_pause"
        ))
        self.add_item(Button(
            label="⏭️ +30s", 
            style=discord.ButtonStyle.secondary, 
            custom_id="seek_forward"
        ))
        self.add_item(Button(
            label="🔁 Restart", 
            style=discord.ButtonStyle.primary, 
            custom_id="restart"
        ))
        self.add_item(Button(
            label="⏭️ Next", 
            style=discord.ButtonStyle.danger, 
            custom_id="next_movie"
        ))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is valid and handle playback controls."""
        if not interaction.data or "custom_id" not in interaction.data:
            return False

        custom_id = interaction.data["custom_id"]
        
        # Get current sessions
        sessions = self.plex_service.get_current_sessions()
        if not sessions:
            await interaction.response.send_message(
                "❌ No active Plex session found.", 
                ephemeral=True
            )
            return False

        session = sessions[0]

        # Get client for control
        if not session.players:
            await interaction.response.send_message(
                "⚠️ No players attached to this session.", 
                ephemeral=True
            )
            return False

        try:
            machine_id = session.players[0].machineIdentifier
            client = self.plex_service.plex.client(machine_id)
        except Exception as e:
            await interaction.response.send_message(
                f"⚠️ Could not connect to Plex client: {e}", 
                ephemeral=True
            )
            return False

        # Handle different button actions
        if custom_id == "seek_back":
            await self._seek_back(interaction, session, client)
        elif custom_id == "seek_forward":
            await self._seek_forward(interaction, session, client)
        elif custom_id == "play_pause":
            await self._play_pause(interaction, client)
        elif custom_id == "restart":
            await self._restart(interaction, client)
        elif custom_id == "next_movie":
            await self._next_movie(interaction)

        return True

    async def _seek_back(self, interaction: discord.Interaction, session, client):
        """Seek back 30 seconds."""
        if session.viewOffset is not None:
            new_offset = max(session.viewOffset - 30000, 0)
            client.seekTo(new_offset)
            await interaction.response.send_message("⏮️ Rewound 30s", ephemeral=True)

    async def _seek_forward(self, interaction: discord.Interaction, session, client):
        """Seek forward 30 seconds."""
        if session.viewOffset is not None and session.duration:
            new_offset = min(session.viewOffset + 30000, session.duration)
            client.seekTo(new_offset)
            await interaction.response.send_message("⏭️ Forwarded 30s", ephemeral=True)

    async def _play_pause(self, interaction: discord.Interaction, client):
        """Toggle play/pause."""
        try:
            if client.isPlayingMedia(includePaused=False):
                client.pause()
                await interaction.response.send_message("⏸️ Paused", ephemeral=True)
            else:
                client.play()
                await interaction.response.send_message("▶️ Resumed", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)

    async def _restart(self, interaction: discord.Interaction, client):
        """Restart movie from beginning."""
        client.seekTo(0)
        await interaction.response.send_message("🔁 Restarted movie", ephemeral=True)

    async def _next_movie(self, interaction: discord.Interaction):
        """Play next movie in queue."""
        # This would need to be implemented with the queue management system
        await interaction.response.send_message("⏭️ Playing next movie...", ephemeral=True)
        # TODO: Integrate with queue management