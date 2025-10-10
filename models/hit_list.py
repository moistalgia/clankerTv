"""
Hit List System
===============

Manages user "hit lists" - movies they want to watch with the group.
Automatically suggests movies when interested users are in voice chat together.
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class HitListEntry:
    """A movie on someone's hit list."""
    movie_title: str
    user_id: int
    username: str
    added_date: datetime = field(default_factory=datetime.now)


class HitListSystem:
    """Manages user hit lists and voice channel suggestions."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # user_id -> list of movie titles
        self.hit_lists: Dict[int, List[str]] = {}
        
        # Track when we last suggested movies to avoid spam
        self.last_suggestion_time: Optional[datetime] = None
        self.suggestion_cooldown_minutes = 5
        
        self._load_data()
    
    def _load_data(self):
        """Load hit list data from file."""
        try:
            hit_list_file = self.data_dir / "hit_lists.json"
            if hit_list_file.exists():
                with open(hit_list_file, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to int
                    self.hit_lists = {int(k): v for k, v in data.items()}
                print(f"✅ Loaded hit lists for {len(self.hit_lists)} users")
            else:
                print("📝 No existing hit list data found, starting fresh")
        except Exception as e:
            print(f"❌ Error loading hit list data: {e}")
            self.hit_lists = {}
    
    def _save_data(self):
        """Save hit list data to file."""
        try:
            hit_list_file = self.data_dir / "hit_lists.json"
            with open(hit_list_file, 'w') as f:
                # Convert int keys to string for JSON
                data = {str(k): v for k, v in self.hit_lists.items()}
                json.dump(data, f, indent=2)
            print(f"✅ Saved hit lists for {len(self.hit_lists)} users")
        except Exception as e:
            print(f"❌ Error saving hit list data: {e}")
    
    def add_to_hit_list(self, user_id: int, movie_title: str) -> bool:
        """
        Add a movie to user's hit list.
        
        Returns:
            True if added, False if already on list
        """
        if user_id not in self.hit_lists:
            self.hit_lists[user_id] = []
        
        if movie_title in self.hit_lists[user_id]:
            return False  # Already on list
        
        self.hit_lists[user_id].append(movie_title)
        self._save_data()
        return True
    
    def remove_from_hit_list(self, user_id: int, movie_title: str) -> bool:
        """
        Remove a movie from user's hit list.
        
        Returns:
            True if removed, False if not on list
        """
        if user_id not in self.hit_lists:
            return False
        
        if movie_title not in self.hit_lists[user_id]:
            return False
        
        self.hit_lists[user_id].remove(movie_title)
        
        # Clean up empty lists
        if not self.hit_lists[user_id]:
            del self.hit_lists[user_id]
        
        self._save_data()
        return True
    
    def get_user_hit_list(self, user_id: int) -> List[str]:
        """Get a user's hit list."""
        return self.hit_lists.get(user_id, [])
    
    def get_movie_interest_count(self, movie_title: str) -> int:
        """Get how many users have a movie on their hit list."""
        count = 0
        for hit_list in self.hit_lists.values():
            if movie_title in hit_list:
                count += 1
        return count
    
    def get_users_interested_in_movie(self, movie_title: str) -> List[int]:
        """Get list of user IDs who have this movie on their hit list."""
        interested_users = []
        for user_id, hit_list in self.hit_lists.items():
            if movie_title in hit_list:
                interested_users.append(user_id)
        return interested_users
    
    def get_all_movies_with_interest(self) -> Dict[str, int]:
        """Get all movies and their interest counts."""
        movie_counts = {}
        for hit_list in self.hit_lists.values():
            for movie in hit_list:
                movie_counts[movie] = movie_counts.get(movie, 0) + 1
        return movie_counts
    
    def find_shared_interests(self, user_ids: List[int]) -> Dict[str, List[int]]:
        """
        Find movies that multiple users in the list are interested in.
        
        Returns:
            Dict of movie_title -> list of interested user_ids from the input list
        """
        if len(user_ids) < 2:
            return {}
        
        shared_movies = {}
        
        for movie_title in self.get_all_movies_with_interest():
            interested_from_group = []
            
            for user_id in user_ids:
                if movie_title in self.get_user_hit_list(user_id):
                    interested_from_group.append(user_id)
            
            # Only include if 2+ users from the voice channel are interested
            if len(interested_from_group) >= 2:
                shared_movies[movie_title] = interested_from_group
        
        return shared_movies
    
    def should_suggest_now(self) -> bool:
        """Check if enough time has passed since last suggestion to avoid spam."""
        if self.last_suggestion_time is None:
            return True
        
        time_since_last = datetime.now() - self.last_suggestion_time
        return time_since_last.total_seconds() > (self.suggestion_cooldown_minutes * 60)
    
    def mark_suggestion_made(self):
        """Mark that we just made a suggestion."""
        self.last_suggestion_time = datetime.now()
    
    def remove_movie_from_all_lists(self, movie_title: str):
        """Remove a movie from all hit lists (e.g., after it's been watched)."""
        removed_count = 0
        users_to_clean = []
        
        for user_id, hit_list in self.hit_lists.items():
            if movie_title in hit_list:
                hit_list.remove(movie_title)
                removed_count += 1
                
                # Mark empty lists for cleanup
                if not hit_list:
                    users_to_clean.append(user_id)
        
        # Clean up empty lists
        for user_id in users_to_clean:
            del self.hit_lists[user_id]
        
        if removed_count > 0:
            self._save_data()
            print(f"🗑️ Removed '{movie_title}' from {removed_count} hit lists")
        
        return removed_count
    
    def cleanup_watched_movie(self, movie_title: str) -> int:
        """Remove a movie from all hit lists after it's been watched by the group."""
        return self.remove_movie_from_all_lists(movie_title)