"""
Plex Media Server Service
========================

Handles all interactions with Plex Media Server including playback control,
library management, and session monitoring.
"""

import tempfile
import os
from typing import List, Dict, Optional, Any
from plexapi.server import PlexServer
from plexapi.client import PlexClient
from config import PLEX_URL, PLEX_TOKEN, PLEX_LIBRARY, PREFERRED_LANG


class PlexService:
    """Service class for Plex Media Server operations."""
    
    def __init__(self):
        self.plex = None
        self.library = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Plex server."""
        try:
            self.plex = PlexServer(PLEX_URL, PLEX_TOKEN)
            self.library = self.plex.library.section(PLEX_LIBRARY)
            print(f"✅ Connected to Plex Server at {PLEX_URL}")
        except Exception as e:
            print(f"❌ Error connecting to Plex: {e}")
            self.plex = None
            self.library = None
    
    def is_connected(self) -> bool:
        """Check if Plex connection is established."""
        return self.plex is not None and self.library is not None
    
    async def get_horror_movies(self) -> List[str]:
        """
        Fetch all horror movies from Plex library.
        
        Returns:
            List of movie titles in format "Title (Year)"
        """
        try:
            if not self.is_connected():
                return []
            
            movies = self.library.search(genre="Horror")
            return [f"{m.title} ({m.year})" for m in movies]
        except Exception as e:
            print(f"❌ Failed to fetch horror movies: {e}")
            return []
    
    def get_movie(self, title_with_year: str):
        """
        Fetch Plex movie by 'Title (Year)' format.
        
        Args:
            title_with_year: Movie title in "Title (Year)" format
            
        Returns:
            Plex movie object or None
        """
        try:
            if not self.is_connected():
                return None
                
            if title_with_year.endswith(")"):
                # Split out the year if present
                title, year = title_with_year.rsplit("(", 1)
                title = title.strip()
                year = year.strip(" )")
                results = self.library.search(title=title, year=year)
            else:
                results = self.library.search(title=title_with_year)

            if results:
                return results[0]  # return the first match
        except Exception as e:
            print(f"❌ get_movie failed for {title_with_year}: {e}")
        return None
    
    def get_first_controllable_client(self):
        """
        Get the first available Plex client for playback control.
        
        Returns:
            PlexClient or None
        """
        try:
            if not self.is_connected():
                return None
                
            clients = self.plex.clients()
            return clients[0] if clients else None
        except Exception as e:
            print(f"❌ Failed to get Plex client: {e}")
            return None
    
    async def get_available_clients(self) -> List[Dict[str, str]]:
        """
        Get list of all available Plex clients.
        
        Returns:
            List of client info dictionaries
        """
        try:
            if not self.is_connected():
                return []
                
            clients = self.plex.clients()
            return [
                {"title": client.title, "platform": client.platform}
                for client in clients
            ]
        except Exception as e:
            print(f"❌ Failed to get clients: {e}")
            return []
    
    def get_current_sessions(self):
        """Get current Plex sessions."""
        try:
            if not self.is_connected():
                return []
            return self.plex.sessions()
        except Exception as e:
            print(f"❌ Failed to get sessions: {e}")
            return []
    
    async def get_time_remaining(self) -> Optional[Dict[str, Any]]:
        """
        Get remaining time for currently playing movie.
        
        Returns:
            Dictionary with title and formatted time or None
        """
        try:
            sessions = self.get_current_sessions()
            if not sessions:
                return None

            session = sessions[0]
            
            if session.duration and session.viewOffset is not None:
                remaining_ms = session.duration - session.viewOffset
                remaining_sec = int(remaining_ms / 1000)

                # Format nicely
                hours = remaining_sec // 3600
                minutes = (remaining_sec % 3600) // 60
                seconds = remaining_sec % 60
                formatted = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"

                return {
                    "title": session.title,
                    "formatted_time": formatted,
                    "remaining_seconds": remaining_sec
                }
        except Exception as e:
            print(f"❌ Failed to get time remaining: {e}")
        return None
    
    async def restart_current_movie(self) -> Optional[str]:
        """
        Restart the currently playing movie from the beginning.
        
        Returns:
            Movie title if successful, None otherwise
        """
        try:
            sessions = self.get_current_sessions()
            if not sessions:
                return None

            session = sessions[0]
            
            # Find the actual Plex client associated with this session
            player_name = session.players[0].title
            client = self.plex.client(player_name)

            if not client:
                return None

            # Restart by seeking to 0 ms
            client.seekTo(0)
            return session.title
            
        except Exception as e:
            print(f"❌ Failed to restart movie: {e}")
            return None
    
    async def get_enhanced_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed session info including movie positions for robust tracking.
        
        Returns:
            Dictionary with session details for enhanced completion calculation
        """
        try:
            sessions = self.get_current_sessions()
            if not sessions:
                return None
            
            session = sessions[0]
            if session.type != "movie":
                return None
            
            return {
                "title": session.title,
                "duration_ms": session.duration or 0,
                "current_position_ms": session.viewOffset or 0,
                "progress_percent": ((session.viewOffset or 0) / (session.duration or 1)) * 100 if session.duration else 0,
                "session_key": session.sessionKey,
                "player": session.players[0].title if session.players else "Unknown"
            }
        except Exception as e:
            print(f"❌ Failed to get enhanced session info: {e}")
            return None
    
    async def get_current_movie_info(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about currently playing movie.
        
        Returns:
            Dictionary with movie information or None
        """
        try:
            sessions = self.get_current_sessions()
            if not sessions:
                return None

            session = sessions[0]
            movie_title = session.title

            # Fetch additional info
            movie = self.get_movie(movie_title)
            synopsis = getattr(movie, "summary", "No synopsis available") if movie else "No synopsis available"
            imdb_rating = getattr(movie, "rating", "N/A") if movie else "N/A"
            imdb_url = f"https://www.imdb.com/find?q={movie_title.replace(' ', '+')}"

            return {
                "title": movie_title,
                "synopsis": synopsis,
                "imdb_rating": imdb_rating,
                "imdb_url": imdb_url,
                "session": session
            }
        except Exception as e:
            print(f"❌ Failed to get current movie info: {e}")
            return None
    
    async def play_movie(self, movie_title: str) -> Dict[str, Any]:
        """
        Play a specific movie on the first available client.
        
        Args:
            movie_title: Title of movie to play
            
        Returns:
            Dictionary with success status and details
        """
        try:
            # Get movie from library
            movie = self.get_movie(movie_title)
            if not movie:
                return {"success": False, "message": f"Could not find {movie_title} in Plex library"}
            
            # Get client
            client = self.get_first_controllable_client()
            if not client:
                return {"success": False, "message": "No controllable Plex clients found"}
            
            # Play movie
            client.playMedia(movie)
            return {
                "success": True, 
                "message": f"Now playing {movie_title} on {client.title}",
                "client_name": client.title
            }
            
        except Exception as e:
            return {"success": False, "message": f"Failed to play movie: {e}"}
    
    async def get_movie_metadata(self, movie_title: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed metadata for a movie.
        
        Args:
            movie_title: Title of movie to get metadata for
            
        Returns:
            Dictionary with movie metadata or None
        """
        try:
            movie = self.get_movie(movie_title)
            if not movie:
                return None
            
            # Extract genres
            genres = []
            if hasattr(movie, 'genres') and movie.genres:
                genres = [genre.tag for genre in movie.genres]
            
            # Extract director
            director = None
            if hasattr(movie, 'directors') and movie.directors:
                director = movie.directors[0].tag
            
            return {
                "title": movie.title,
                "year": getattr(movie, "year", None),
                "genres": genres,
                "director": director,
                "summary": getattr(movie, "summary", ""),
                "rating": getattr(movie, "rating", None),
                "duration": getattr(movie, "duration", None)
            }
            
        except Exception as e:
            print(f"❌ Failed to get movie metadata for {movie_title}: {e}")
            return None

    async def apply_subtitles(self) -> Dict[str, Any]:
        """
        Download and apply subtitles to currently playing movie.
        
        Returns:
            Dictionary with success status and details
        """
        try:
            sessions = self.get_current_sessions()
            if not sessions:
                return {"success": False, "message": "No movie currently playing"}

            session = sessions[0]
            movie_title = session.title

            # Get client
            if not session.players:
                return {"success": False, "message": "No players attached to session"}

            try:
                machine_id = session.players[0].machineIdentifier
                client = self.plex.client(machine_id)
            except Exception:
                return {"success": False, "message": "Could not connect to Plex client"}

            # Fetch the movie from the library
            movie = self.get_movie(movie_title)
            if not movie:
                return {"success": False, "message": f"Could not find movie '{movie_title}'"}

            # Search for subtitles
            try:
                subs = movie.searchSubtitles(language=PREFERRED_LANG)
            except Exception as e:
                return {"success": False, "message": f"Error searching subtitles: {e}"}

            if not subs:
                return {"success": False, "message": f"No subtitles found for '{movie_title}'"}

            # Download the first subtitle
            try:
                downloaded_file = movie.downloadSubtitles(subs[0])
                if not downloaded_file:
                    return {"success": False, "message": "Failed to download subtitle"}
            except Exception as e:
                return {"success": False, "message": f"Failed to download subtitle: {e}"}

            # Resume playbook with subtitle
            try:
                offset = session.viewOffset or 0
                client.playMedia(movie, subtitles=downloaded_file, offset=offset)
                return {
                    "success": True, 
                    "message": "Applied subtitle and resumed playback",
                    "offset": offset // 1000
                }
            except Exception as e:
                return {"success": False, "message": f"Failed to apply subtitle: {e}"}

        except Exception as e:
            return {"success": False, "message": f"Unexpected error: {e}"}