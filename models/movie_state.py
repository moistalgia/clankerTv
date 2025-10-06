"""
Movie State Management
=====================

Manages all movie-related state including playlists, requests, votes, and current playback.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .badge_system import WatchBadgeSystem


@dataclass
class CurrentMovieInfo:
    """Information about the currently playing movie."""
    title: Optional[str] = None
    synopsis: Optional[str] = None
    imdb_rating: Optional[str] = None
    url: Optional[str] = None


@dataclass
class NextUpState:
    """State for the next-up voting poll."""
    movies: List[str] = field(default_factory=list)  # Movies in current poll
    view: Optional[Any] = None  # Discord View instance
    embeds: Optional[List[Any]] = None  # Current poll embeds
    message_id: Optional[int] = None  # Discord message ID


class MovieState:
    """Manages all movie-related state and operations."""
    
    def __init__(self):
        # Movie library and queue management
        self.playlist: List[str] = []  # Horror movies from Plex in "Title (Year)" format
        self.requests: Dict[str, List[int]] = {}  # Movie requests: {movie_title: [user_ids]}
        self.votes: defaultdict = defaultdict(int)  # Legacy vote tracking
        self.current_movie: Optional[str] = None  # Currently playing movie title
        
        # Current movie information
        self.current_movie_info = CurrentMovieInfo()
        
        # Next-up voting state
        self.nextup_state = NextUpState()
        
        # Badge system integration
        self.badge_system = WatchBadgeSystem()
        
        # Legacy compatibility variables
        self.next_up_options: List[str] = []  # List of movie titles
        self.next_up_votes: Dict[str, int] = {}  # {"movie_title": vote_count}
    
    def add_movie_request(self, movie_title: str, user_id: int) -> bool:
        """
        Add a movie request (doot) for a user.
        
        Args:
            movie_title: Title of the movie to request
            user_id: Discord user ID making the request
            
        Returns:
            True if request was added, False if user already has a request
        """
        # Check if user already has a request for any movie
        if any(user_id in voters for voters in self.requests.values()):
            return False
        
        if movie_title not in self.requests:
            self.requests[movie_title] = []
        
        self.requests[movie_title].append(user_id)
        return True
    
    def remove_user_requests(self, user_id: int) -> List[str]:
        """
        Remove all requests from a specific user.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            List of movie titles that had requests removed
        """
        removed_movies = []
        
        for movie_title, voters in list(self.requests.items()):
            if user_id in voters:
                voters.remove(user_id)
                removed_movies.append(movie_title)
                
                # Remove empty entries
                if len(voters) == 0:
                    del self.requests[movie_title]
        
        return removed_movies
    
    def remove_movie_request(self, movie_title: str) -> bool:
        """
        Remove all requests for a specific movie.
        
        Args:
            movie_title: Title of movie to remove requests for
            
        Returns:
            True if movie was found and removed, False otherwise
        """
        if movie_title in self.requests:
            del self.requests[movie_title]
            return True
        return False
    
    def get_most_requested_movie(self) -> Optional[str]:
        """
        Get the movie with the most requests.
        
        Returns:
            Movie title with most votes or None if no requests
        """
        if not self.requests:
            return None
        
        return max(self.requests.items(), key=lambda x: len(x[1]))[0]
    
    def get_request_count(self, movie_title: str) -> int:
        """
        Get number of requests for a specific movie.
        
        Args:
            movie_title: Title of movie to check
            
        Returns:
            Number of users who requested this movie
        """
        return len(self.requests.get(movie_title, []))
    
    def clear_all_requests(self):
        """Clear all movie requests."""
        self.requests.clear()
    
    def clear_all_votes(self):
        """Clear all legacy votes."""
        self.votes.clear()
    
    def update_playlist(self, new_playlist: List[str]):
        """
        Update the movie playlist.
        
        Args:
            new_playlist: New list of movie titles
        """
        self.playlist = new_playlist.copy()
    
    def set_current_movie(self, movie_title: Optional[str]):
        """
        Set the currently playing movie.
        
        Args:
            movie_title: Title of currently playing movie or None
        """
        self.current_movie = movie_title
    
    def update_current_movie_info(self, title: str = None, synopsis: str = None, 
                                 imdb_rating: str = None, url: str = None):
        """
        Update current movie information.
        
        Args:
            title: Movie title
            synopsis: Movie synopsis
            imdb_rating: IMDB rating
            url: IMDB URL
        """
        if title is not None:
            self.current_movie_info.title = title
        if synopsis is not None:
            self.current_movie_info.synopsis = synopsis
        if imdb_rating is not None:
            self.current_movie_info.imdb_rating = imdb_rating
        if url is not None:
            self.current_movie_info.url = url
    
    def start_nextup_poll(self, movies: List[str], view=None, embeds=None, message_id: int = None):
        """
        Start a new next-up voting poll.
        
        Args:
            movies: List of movies in the poll
            view: Discord View instance
            embeds: Poll embeds
            message_id: Discord message ID
        """
        self.nextup_state.movies = movies.copy()
        self.nextup_state.view = view
        self.nextup_state.embeds = embeds
        self.nextup_state.message_id = message_id
    
    def clear_nextup_poll(self):
        """Clear the current next-up poll."""
        self.nextup_state = NextUpState()
    
    def is_nextup_poll_active(self) -> bool:
        """Check if a next-up poll is currently active."""
        return bool(self.nextup_state.movies and self.nextup_state.view)
    
    def get_formatted_requests(self) -> str:
        """
        Get formatted string of all current requests.
        
        Returns:
            Formatted string showing all requests with vote counts
        """
        if not self.requests:
            return "No pending requests."
        
        lines = []
        for movie, voters in self.requests.items():
            lines.append(f"• {movie} ({len(voters)} votes)")
        
        return "**Pending Movie Requests:**\n" + "\n".join(lines)