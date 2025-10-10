"""
Watch Badge System Models
========================

Data models for tracking user watch statistics, badges, and achievements.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import json
import os
from pathlib import Path


class BadgeType(Enum):
    """Types of badges that can be earned."""
    MOVIE_COUNT = "movie_count"
    TIME_BASED = "time_based"
    GENRE_SPECIALIST = "genre_specialist"
    SOCIAL = "social"
    SPECIAL_ACHIEVEMENT = "special_achievement"
    STREAK = "streak"
    SEASONAL = "seasonal"


@dataclass
class Badge:
    """Individual badge definition."""
    id: str
    name: str
    description: str
    emoji: str
    badge_type: BadgeType
    requirement_value: int = 0
    requirement_data: Dict = field(default_factory=dict)
    rarity: str = "common"  # common, rare, epic, legendary
    
    def __str__(self):
        return f"{self.emoji} **{self.name}**"


@dataclass
class MovieRating:
    """User rating for a movie."""
    user_id: int
    movie_title: str
    rating: int  # 1-10 stars
    rated_date: datetime
    username: str = ""
    
    @property
    def rating_emoji(self) -> str:
        """Get emoji representation of rating."""
        emoji_map = {
            1: "💀",   # Dead (terrible)
            2: "🤮",   # Sick (awful) 
            3: "😴",   # Sleeping (boring)
            4: "😐",   # Neutral (meh)
            5: "🤷",   # Shrug (okay)
            6: "😊",   # Smile (good)
            7: "😍",   # Love eyes (great)
            8: "🤩",   # Star eyes (amazing)
            9: "🔥",   # Fire (incredible)
            10: "👑"   # Crown (masterpiece)
        }
        return emoji_map.get(self.rating, "❓")
    
    @property
    def rating_text(self) -> str:
        """Get text description of rating."""
        text_map = {
            1: "Terrible",
            2: "Awful", 
            3: "Boring",
            4: "Meh",
            5: "Okay",
            6: "Good",
            7: "Great",
            8: "Amazing",
            9: "Incredible",
            10: "Masterpiece"
        }
        return text_map.get(self.rating, "Unknown")


@dataclass
class MovieWatch:
    """Record of a user watching a movie with enhanced position tracking."""
    movie_title: str
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    watch_duration_minutes: int = 0
    completion_percentage: float = 0.0
    genres: List[str] = field(default_factory=list)
    year: Optional[int] = None
    director: Optional[str] = None
    # Enhanced position tracking for robust completion calculation
    movie_duration_ms: Optional[int] = None  # Total movie duration from Plex
    join_position_ms: Optional[int] = None   # Movie position when user joined
    leave_position_ms: Optional[int] = None  # Movie position when user left
    
    @property
    def is_completed(self) -> bool:
        """Check if movie was watched to completion (>80%)."""
        return self.completion_percentage >= 80.0
    
    @property
    def watch_date(self) -> datetime:
        """Get the date this movie was watched."""
        return self.start_time.date()
    
    def calculate_enhanced_completion(self) -> float:
        """Calculate completion based on actual movie content seen."""
        if not all([self.movie_duration_ms, self.join_position_ms is not None]):
            # Fall back to time-based calculation if Plex data unavailable
            return self._calculate_time_based_completion()
        
        # Use leave position if available, otherwise assume movie ended
        end_position = self.leave_position_ms if self.leave_position_ms is not None else self.movie_duration_ms
        
        # Calculate actual movie content watched
        content_watched_ms = max(0, end_position - self.join_position_ms)
        completion = (content_watched_ms / self.movie_duration_ms) * 100
        
        return max(0.0, min(100.0, completion))
    
    def _calculate_time_based_completion(self) -> float:
        """Fallback time-based completion calculation."""
        if not self.movie_duration_ms or self.watch_duration_minutes <= 0:
            return 0.0
        
        movie_duration_minutes = self.movie_duration_ms / (1000 * 60)
        return min(100.0, (self.watch_duration_minutes / movie_duration_minutes) * 100)


@dataclass
class UserBadge:
    """Badge earned by a user."""
    badge_id: str
    earned_date: datetime
    progress_value: int = 0
    
    def __str__(self):
        return f"🏆 Earned: {self.earned_date.strftime('%Y-%m-%d')}"


@dataclass
class UserStats:
    """User's watch statistics and progress."""
    user_id: int
    username: str
    total_movies: int = 0
    total_watch_time_minutes: int = 0
    completed_movies: int = 0
    current_streak_days: int = 0
    longest_streak_days: int = 0
    last_watch_date: Optional[datetime] = None
    favorite_genres: Dict[str, int] = field(default_factory=dict)
    favorite_decades: Dict[str, int] = field(default_factory=dict)
    directors_watched: Set[str] = field(default_factory=set)
    ai_interactions: int = 0
    votes_cast: int = 0
    movies_requested: int = 0
    
    @property
    def total_watch_time_hours(self) -> float:
        """Get total watch time in hours."""
        return self.total_watch_time_minutes / 60.0
    
    @property
    def average_completion_rate(self) -> float:
        """Calculate average completion rate."""
        if self.total_movies == 0:
            return 0.0
        return (self.completed_movies / self.total_movies) * 100.0


class WatchBadgeSystem:
    """Main system for managing watch badges and statistics."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize empty collections
        self.user_stats: Dict[int, UserStats] = {}
        self.user_badges: Dict[int, List[UserBadge]] = {}
        self.watch_history: List[MovieWatch] = []
        self.active_watches: Dict[int, MovieWatch] = {}  # user_id -> current watch
        self.movie_ratings: List[MovieRating] = []  # All user movie ratings
        self.badge_definitions = self._initialize_badges()
        
        # Load existing data
        self._load_data()
    
    def _initialize_badges(self) -> Dict[str, Badge]:
        """Initialize all available badges."""
        badges = {}
        
        # Movie Count Badges
        movie_count_badges = [
            Badge("first_blood", "First Blood", "Watch your first horror movie", "🎭", BadgeType.MOVIE_COUNT, 1, rarity="common"),
            Badge("rising_terror", "Rising Terror", "Watch 5 horror movies", "🔥", BadgeType.MOVIE_COUNT, 5, rarity="common"),
            Badge("ghost_hunter", "Ghost Hunter", "Watch 10 horror movies", "👻", BadgeType.MOVIE_COUNT, 10, rarity="rare"),
            Badge("vampire_lord", "Vampire Lord", "Watch 25 horror movies", "🧛", BadgeType.MOVIE_COUNT, 25, rarity="rare"),
            Badge("death_collector", "Death Collector", "Watch 50 horror movies", "💀", BadgeType.MOVIE_COUNT, 50, rarity="epic"),
            Badge("horror_legend", "Horror Legend", "Watch 100 horror movies", "🌟", BadgeType.MOVIE_COUNT, 100, rarity="legendary"),
        ]
        
        # Time-Based Badges
        time_badges = [
            Badge("night_owl", "Night Owl", "Watch a movie past midnight", "🌙", BadgeType.TIME_BASED, rarity="common"),
            Badge("dawn_survivor", "Dawn Survivor", "Watch movies until sunrise (6+ hours)", "🌅", BadgeType.TIME_BASED, 360, rarity="rare"),
            Badge("endurance", "Endurance Runner", "Watch 6+ hours in one session", "⏳", BadgeType.TIME_BASED, 360, rarity="rare"),
            Badge("weekend_warrior", "Weekend Warrior", "Watch 3+ movies in one weekend", "📅", BadgeType.TIME_BASED, 3, rarity="common"),
        ]
        
        # Genre Specialist Badges
        genre_badges = [
            Badge("slasher_expert", "Slasher Expert", "Watch 10 slasher films", "🔪", BadgeType.GENRE_SPECIALIST, 10, {"genre": "slasher"}, "rare"),
            Badge("paranormal_investigator", "Paranormal Investigator", "Watch 10 supernatural films", "👻", BadgeType.GENRE_SPECIALIST, 10, {"genre": "supernatural"}, "rare"),
            Badge("mind_bender", "Mind Bender", "Watch 10 psychological thrillers", "🧠", BadgeType.GENRE_SPECIALIST, 10, {"genre": "psychological"}, "rare"),
            Badge("zombie_apocalypse", "Zombie Apocalypse", "Watch 10 zombie films", "🧟", BadgeType.GENRE_SPECIALIST, 10, {"genre": "zombie"}, "rare"),
            Badge("haunted_house", "Haunted House", "Watch 10 haunted house films", "🏠", BadgeType.GENRE_SPECIALIST, 10, {"genre": "haunted"}, "rare"),
        ]
        
        # Social Badges
        social_badges = [
            Badge("democracy", "Democracy", "Vote in 10 next-up polls", "🗳️", BadgeType.SOCIAL, 10, rarity="common"),
            Badge("trendsetter", "Trendsetter", "Request 5 movies that get watched", "🎯", BadgeType.SOCIAL, 5, rarity="rare"),
            Badge("commentary_king", "Commentary King", "Trigger 50 AI responses", "💬", BadgeType.SOCIAL, 50, rarity="rare"),
        ]
        
        # Special Achievement Badges
        special_badges = [
            Badge("halloween_legend", "Halloween Legend", "Watch on Halloween night", "🎃", BadgeType.SPECIAL_ACHIEVEMENT, rarity="epic"),
            Badge("clankers_chosen", "Clanker's Chosen", "Trigger AI responses 100 times", "🕷️", BadgeType.SPECIAL_ACHIEVEMENT, 100, rarity="legendary"),
            Badge("directors_cut", "Director's Cut", "Watch complete filmography of a director (5+ films)", "🎬", BadgeType.SPECIAL_ACHIEVEMENT, 5, rarity="epic"),
            Badge("horror_bingo_master", "Horror Bingo Master", "Get your first bingo in Horror Bingo", "🎰", BadgeType.SPECIAL_ACHIEVEMENT, 1, rarity="rare"),
        ]
        
        # Streak Badges
        streak_badges = [
            Badge("dedicated", "Dedicated", "Watch movies 3 days in a row", "🔥", BadgeType.STREAK, 3, rarity="common"),
            Badge("marathon_runner", "Marathon Runner", "Watch movies 7 days in a row", "🏃", BadgeType.STREAK, 7, rarity="rare"),
            Badge("unstoppable", "Unstoppable", "Watch movies 14 days in a row", "⚡", BadgeType.STREAK, 14, rarity="epic"),
            Badge("legend", "Living Legend", "Watch movies 30 days in a row", "👑", BadgeType.STREAK, 30, rarity="legendary"),
        ]
        
        all_badges = movie_count_badges + time_badges + genre_badges + social_badges + special_badges + streak_badges
        
        for badge in all_badges:
            badges[badge.id] = badge
        
        return badges
    
    def start_watching(self, user_id: int, username: str, movie_title: str, 
                      genres: List[str] = None, year: int = None, director: str = None,
                      movie_duration_ms: int = None, join_position_ms: int = None):
        """Start tracking a user's movie watch session with smart resume logic."""
        
        current_time = datetime.now()
        
        # Check for existing watch session that can be resumed
        existing_watch_entry = self._find_resumable_watch_session(user_id, movie_title, current_time, movie_duration_ms)
        
        if existing_watch_entry:
            # Resume existing session - update active watches but don't create new history entry
            print(f"📺 Resuming watch session for user {user_id} - {movie_title}")
            
            resumed_watch = MovieWatch(
                movie_title=movie_title,
                user_id=user_id,
                start_time=existing_watch_entry.start_time,  # Keep original start time
                genres=genres or existing_watch_entry.genres,
                year=year or existing_watch_entry.year,
                director=director or existing_watch_entry.director,
                movie_duration_ms=movie_duration_ms or existing_watch_entry.movie_duration_ms,
                join_position_ms=join_position_ms  # Update with current join position
            )
            
            # Copy existing progress
            resumed_watch.watch_duration_minutes = existing_watch_entry.watch_duration_minutes
            resumed_watch.completion_percentage = existing_watch_entry.completion_percentage
            
            self.active_watches[user_id] = resumed_watch
            
        else:
            # Start new session
            print(f"🆕 Starting new watch session for user {user_id} - {movie_title}")
            
            watch = MovieWatch(
                movie_title=movie_title,
                user_id=user_id,
                start_time=current_time,
                genres=genres or [],
                year=year,
                director=director,
                movie_duration_ms=movie_duration_ms,
                join_position_ms=join_position_ms
            )
            
            self.active_watches[user_id] = watch
            
            # Create new watch history entry
            initial_watch_entry = MovieWatch(
                movie_title=movie_title,
                user_id=user_id,
                start_time=watch.start_time,
                end_time=None,  # Still active
                watch_duration_minutes=0,  # Will be updated by auto-save
                completion_percentage=0.0,  # Will be updated by auto-save
                genres=genres or [],
                year=year,
                director=director,
                movie_duration_ms=movie_duration_ms,
                join_position_ms=join_position_ms
            )
            
            self.watch_history.append(initial_watch_entry)
        
        # Ensure user stats exist
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats(user_id=user_id, username=username)
        if user_id not in self.user_badges:
            self.user_badges[user_id] = []
        
        # Save progress
        self._save_data()
    
    def _find_resumable_watch_session(self, user_id: int, movie_title: str, current_time: datetime, movie_duration_ms: int = None) -> MovieWatch:
        """Find an existing watch session that can be resumed within the same movie timeframe."""
        
        # Look for recent watch sessions for this user and movie (both active and recently ended)
        for watch in reversed(self.watch_history):
            if (watch.user_id == user_id and 
                watch.movie_title == movie_title):
                
                # Calculate if we're still within the movie's runtime window
                if movie_duration_ms:
                    movie_duration_minutes = movie_duration_ms / (1000 * 60)
                    # Add 15 minute buffer for pauses, discussions, etc.
                    max_session_duration = movie_duration_minutes + 15
                else:
                    # Default: assume 2.5 hour window for unknown movies
                    max_session_duration = 150
                
                # Check if current time is within the movie session window from original start
                session_elapsed = (current_time - watch.start_time).total_seconds() / 60
                
                if session_elapsed <= max_session_duration:
                    # Additional check: if the watch has an end_time, make sure we're still within the movie window
                    if watch.end_time is not None:
                        time_since_end = (current_time - watch.end_time).total_seconds() / 60
                        # For ended sessions, allow resumption if we're still within the overall movie window
                        # This handles cases where someone leaves and comes back later during the same movie
                        remaining_movie_time = max_session_duration - session_elapsed
                        if remaining_movie_time <= 0:
                            print(f"⏰ Movie session window expired: {session_elapsed:.1f}m elapsed (max: {max_session_duration:.1f}m)")
                            continue
                    
                    print(f"🔄 Found resumable session: {session_elapsed:.1f}m elapsed (max: {max_session_duration:.1f}m)")
                    # Clear the end_time so it becomes active again
                    watch.end_time = None
                    return watch
                else:
                    print(f"⏰ Session too old: {session_elapsed:.1f}m elapsed (max: {max_session_duration:.1f}m)")
        
        return None
    
    def finish_watching(self, user_id: int, completion_percentage: float = None, end_time: datetime = None, 
                       leave_position_ms: int = None) -> List[Badge]:
        """Finish a user's watch session and check for new badges with enhanced completion calculation."""
        if user_id not in self.active_watches:
            return []
        
        watch = self.active_watches[user_id]
        watch.end_time = end_time or datetime.now()
        watch.leave_position_ms = leave_position_ms
        watch.watch_duration_minutes = int((watch.end_time - watch.start_time).total_seconds() / 60)
        
        # Use enhanced completion calculation if possible, otherwise fall back to provided percentage
        if completion_percentage is not None:
            # Manual override provided
            watch.completion_percentage = completion_percentage
        else:
            # Calculate based on actual movie content seen
            watch.completion_percentage = watch.calculate_enhanced_completion()
        
        # Find and update existing watch history entry (created at startup)
        current_watch_entry = None
        for existing_watch in reversed(self.watch_history):
            if (existing_watch.user_id == user_id and 
                existing_watch.movie_title == watch.movie_title and 
                existing_watch.end_time is None):  # Still active/incomplete
                current_watch_entry = existing_watch
                break
        
        if current_watch_entry:
            # Update existing entry with final values
            current_watch_entry.end_time = watch.end_time
            current_watch_entry.watch_duration_minutes = watch.watch_duration_minutes
            current_watch_entry.completion_percentage = watch.completion_percentage
            current_watch_entry.leave_position_ms = watch.leave_position_ms
        else:
            # Fallback: add to history if no existing entry found (shouldn't happen with new design)
            self.watch_history.append(watch)
        
        del self.active_watches[user_id]
        
        # Update user stats
        self._update_user_stats(user_id, watch)
        
        # Check for new badges
        new_badges = self._check_new_badges(user_id)
        
        # Save progress after changes
        self._save_data()
        
        return new_badges
    
    def _update_user_stats(self, user_id: int, watch: MovieWatch):
        """Update user statistics based on completed watch."""
        stats = self.user_stats[user_id]
        
        stats.total_movies += 1
        stats.total_watch_time_minutes += watch.watch_duration_minutes
        
        if watch.is_completed:
            stats.completed_movies += 1
        
        # Update streaks
        today = datetime.now().date()
        if stats.last_watch_date:
            if stats.last_watch_date == today - timedelta(days=1):
                stats.current_streak_days += 1
            elif stats.last_watch_date != today:
                stats.current_streak_days = 1
        else:
            stats.current_streak_days = 1
        
        stats.longest_streak_days = max(stats.longest_streak_days, stats.current_streak_days)
        stats.last_watch_date = today
        
        # Update genre preferences
        for genre in watch.genres:
            stats.favorite_genres[genre] = stats.favorite_genres.get(genre, 0) + 1
        
        # Update decade preferences
        if watch.year:
            decade = f"{(watch.year // 10) * 10}s"
            stats.favorite_decades[decade] = stats.favorite_decades.get(decade, 0) + 1
        
        # Update directors
        if watch.director:
            stats.directors_watched.add(watch.director)
    
    def _check_new_badges(self, user_id: int) -> List[Badge]:
        """Check if user has earned any new badges."""
        stats = self.user_stats[user_id]
        current_badges = {badge.badge_id for badge in self.user_badges[user_id]}
        new_badges = []
        
        for badge_id, badge in self.badge_definitions.items():
            if badge_id in current_badges:
                continue  # Already has this badge
            
            earned = False
            
            if badge.badge_type == BadgeType.MOVIE_COUNT:
                earned = stats.total_movies >= badge.requirement_value
            
            elif badge.badge_type == BadgeType.STREAK:
                earned = stats.current_streak_days >= badge.requirement_value
            
            elif badge.badge_type == BadgeType.GENRE_SPECIALIST:
                genre = badge.requirement_data.get("genre", "")
                count = stats.favorite_genres.get(genre, 0)
                earned = count >= badge.requirement_value
            
            elif badge.badge_type == BadgeType.SOCIAL:
                if badge_id == "democracy":
                    earned = stats.votes_cast >= badge.requirement_value
                elif badge_id == "trendsetter":
                    earned = stats.movies_requested >= badge.requirement_value
                elif badge_id == "commentary_king":
                    earned = stats.ai_interactions >= badge.requirement_value
            
            elif badge.badge_type == BadgeType.SPECIAL_ACHIEVEMENT:
                if badge_id == "halloween_legend":
                    today = datetime.now()
                    earned = today.month == 10 and today.day == 31
                elif badge_id == "clankers_chosen":
                    earned = stats.ai_interactions >= badge.requirement_value
                elif badge_id == "directors_cut":
                    # Check if user has watched 5+ movies from same director
                    director_counts = {}
                    for watch in self.watch_history:
                        if watch.user_id == user_id and watch.director:
                            director_counts[watch.director] = director_counts.get(watch.director, 0) + 1
                    earned = any(count >= 5 for count in director_counts.values())
                elif badge_id == "horror_bingo_master":
                    # This badge is awarded manually through the bingo system
                    earned = False
            
            if earned:
                user_badge = UserBadge(badge_id=badge_id, earned_date=datetime.now())
                self.user_badges[user_id].append(user_badge)
                new_badges.append(badge)
        
        return new_badges
    
    def get_user_badges(self, user_id: int) -> List[Tuple[Badge, UserBadge]]:
        """Get all badges for a user."""
        if user_id not in self.user_badges:
            return []
        
        result = []
        for user_badge in self.user_badges[user_id]:
            badge = self.badge_definitions.get(user_badge.badge_id)
            if badge:
                result.append((badge, user_badge))
        
        return result
    
    def get_leaderboard(self, category: str = "total_movies", limit: int = 10) -> List[Tuple[UserStats, int]]:
        """Get leaderboard for specified category, excluding streaming account."""
        from config import STREAMING_ACCOUNT_NAME
        
        # Filter out streaming account from leaderboards
        eligible_users = [user for user in self.user_stats.values() 
                         if user.username.lower() != STREAMING_ACCOUNT_NAME.lower()]
        
        if category == "total_movies":
            sorted_users = sorted(eligible_users, key=lambda x: x.total_movies, reverse=True)
        elif category == "watch_time":
            sorted_users = sorted(eligible_users, key=lambda x: x.total_watch_time_minutes, reverse=True)
        elif category == "current_streak":
            sorted_users = sorted(eligible_users, key=lambda x: x.current_streak_days, reverse=True)
        elif category == "badges":
            sorted_users = sorted(eligible_users, key=lambda x: len(self.user_badges.get(x.user_id, [])), reverse=True)
        else:
            sorted_users = list(eligible_users)
        
        return [(user, rank + 1) for rank, user in enumerate(sorted_users[:limit])]
    
    async def check_and_award_badge(self, user_id: int, badge_id: str, value: int = 1) -> bool:
        """Manually check and award a specific badge to a user."""
        # Initialize user if needed
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats(user_id=user_id, username=f"User_{user_id}")
        
        if user_id not in self.user_badges:
            self.user_badges[user_id] = []
        
        # Check if user already has this badge
        if any(badge.badge_id == badge_id for badge in self.user_badges[user_id]):
            return False
        
        # Check if badge exists
        if badge_id not in self.badge_definitions:
            return False
        
        # Award the badge
        user_badge = UserBadge(badge_id=badge_id, earned_date=datetime.now())
        self.user_badges[user_id].append(user_badge)
        self._save_data()  # Auto-save
        return True

    def increment_ai_interaction(self, user_id: int, username: str = None):
        """Increment AI interaction count for user."""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats(user_id=user_id, username=username or "Unknown")
        if user_id not in self.user_badges:
            self.user_badges[user_id] = []
        
        self.user_stats[user_id].ai_interactions += 1
        new_badges = self._check_new_badges(user_id)
        
        # Save progress after changes
        self._save_data()
        
        return new_badges
    
    def increment_vote(self, user_id: int, username: str = None):
        """Increment vote count for user."""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats(user_id=user_id, username=username or "Unknown")
        if user_id not in self.user_badges:
            self.user_badges[user_id] = []
        
        self.user_stats[user_id].votes_cast += 1
        new_badges = self._check_new_badges(user_id)
        
        # Save progress after changes
        self._save_data()
        
        return new_badges
    
    def increment_movie_request(self, user_id: int, username: str = None):
        """Increment movie request count for user."""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats(user_id=user_id, username=username or "Unknown")
        if user_id not in self.user_badges:
            self.user_badges[user_id] = []
        
        self.user_stats[user_id].movies_requested += 1
        new_badges = self._check_new_badges(user_id)
        
        # Save progress after changes
        self._save_data()
        
        return new_badges
    
    def rate_movie(self, user_id: int, username: str, movie_title: str, rating: int) -> bool:
        """Rate a movie (1-10 stars). Returns True if successful, False if already rated."""
        # Validate rating
        if not (1 <= rating <= 10):
            raise ValueError("Rating must be between 1 and 10")
        
        # Check if user has already rated this movie
        existing_rating = self.get_user_rating(user_id, movie_title)
        if existing_rating:
            return False  # Already rated
        
        # Check if user has watched this movie
        has_watched = any(watch.user_id == user_id and watch.movie_title == movie_title 
                         for watch in self.watch_history)
        if not has_watched:
            raise ValueError("You must watch a movie before rating it")
        
        # Add rating
        movie_rating = MovieRating(
            user_id=user_id,
            movie_title=movie_title,
            rating=rating,
            rated_date=datetime.now(),
            username=username
        )
        
        self.movie_ratings.append(movie_rating)
        
        # Save progress
        self._save_data()
        
        return True
    
    def get_user_rating(self, user_id: int, movie_title: str) -> Optional[MovieRating]:
        """Get user's rating for a specific movie."""
        for rating in self.movie_ratings:
            if rating.user_id == user_id and rating.movie_title == movie_title:
                return rating
        return None
    
    def get_movie_ratings(self, movie_title: str) -> List[MovieRating]:
        """Get all ratings for a specific movie."""
        return [rating for rating in self.movie_ratings if rating.movie_title == movie_title]
    
    def get_user_ratings(self, user_id: int) -> List[MovieRating]:
        """Get all ratings by a specific user."""
        return [rating for rating in self.movie_ratings if rating.user_id == user_id]
    
    def get_average_rating(self, movie_title: str) -> Optional[float]:
        """Get average rating for a movie."""
        ratings = self.get_movie_ratings(movie_title)
        if not ratings:
            return None
        return sum(r.rating for r in ratings) / len(ratings)
    
    def get_all_rated_movies(self) -> Dict[str, Dict]:
        """Get all movies with ratings, sorted by average rating."""
        movie_data = {}
        
        for rating in self.movie_ratings:
            if rating.movie_title not in movie_data:
                movie_data[rating.movie_title] = {
                    'ratings': [],
                    'total_ratings': 0,
                    'average_rating': 0.0
                }
            
            movie_data[rating.movie_title]['ratings'].append(rating)
            
        # Calculate averages
        for movie_title, data in movie_data.items():
            data['total_ratings'] = len(data['ratings'])
            data['average_rating'] = sum(r.rating for r in data['ratings']) / data['total_ratings']
        
        return movie_data
    
    def add_manual_watch(self, user_id: int, username: str, movie_title: str, 
                        watch_date: datetime = None, genres: List[str] = None,
                        year: int = None, director: str = None, 
                        duration_minutes: int = None, completion_percentage: float = None) -> bool:
        """Manually add a movie to watch history (for movies watched before tracking)."""
        
        # Check if already exists
        existing_watch = any(watch.user_id == user_id and watch.movie_title == movie_title 
                           for watch in self.watch_history)
        if existing_watch:
            return False  # Already in history
        
        # Initialize user if needed
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats(user_id=user_id, username=username)
        if user_id not in self.user_badges:
            self.user_badges[user_id] = []
        
        # Use provided values or defaults
        final_duration = duration_minutes if duration_minutes is not None else 90  # Average movie length
        final_completion = completion_percentage if completion_percentage is not None else 100.0  # Assume completed
        
        # Create manual watch record
        watch = MovieWatch(
            movie_title=movie_title,
            user_id=user_id,
            start_time=watch_date or datetime.now(),
            end_time=watch_date or datetime.now(),
            watch_duration_minutes=final_duration,
            completion_percentage=final_completion,
            genres=genres or ["Horror"],
            year=year,
            director=director
        )
        
        self.watch_history.append(watch)
        
        # Update user stats
        self._update_user_stats(user_id, watch)
        
        # Save progress
        self._save_data()
        
        return True
    
    def _load_data(self):
        """Load all persistent data from files."""
        try:
            # Load user stats
            stats_file = self.data_dir / "user_stats.json"
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats_data = json.load(f)
                    for user_id_str, data in stats_data.items():
                        user_id = int(user_id_str)
                        # Convert back to UserStats object
                        stats = UserStats(
                            user_id=data['user_id'],
                            username=data['username'],
                            total_movies=data['total_movies'],
                            total_watch_time_minutes=data['total_watch_time_minutes'],
                            completed_movies=data['completed_movies'],
                            current_streak_days=data['current_streak_days'],
                            longest_streak_days=data['longest_streak_days'],
                            last_watch_date=datetime.fromisoformat(data['last_watch_date']) if data.get('last_watch_date') else None,
                            favorite_genres=data['favorite_genres'],
                            favorite_decades=data['favorite_decades'],
                            directors_watched=set(data['directors_watched']),
                            ai_interactions=data['ai_interactions'],
                            votes_cast=data['votes_cast'],
                            movies_requested=data['movies_requested']
                        )
                        self.user_stats[user_id] = stats
                        
            # Load user badges
            badges_file = self.data_dir / "user_badges.json"
            if badges_file.exists():
                with open(badges_file, 'r') as f:
                    badges_data = json.load(f)
                    for user_id_str, badge_list in badges_data.items():
                        user_id = int(user_id_str)
                        user_badges = []
                        for badge_data in badge_list:
                            badge = UserBadge(
                                badge_id=badge_data['badge_id'],
                                earned_date=datetime.fromisoformat(badge_data['earned_date']),
                                progress_value=badge_data['progress_value']
                            )
                            user_badges.append(badge)
                        self.user_badges[user_id] = user_badges
            
            # Load watch history
            history_file = self.data_dir / "watch_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                    for watch_data in history_data:
                        watch = MovieWatch(
                            movie_title=watch_data['movie_title'],
                            user_id=watch_data['user_id'],
                            start_time=datetime.fromisoformat(watch_data['start_time']),
                            end_time=datetime.fromisoformat(watch_data['end_time']) if watch_data.get('end_time') else None,
                            watch_duration_minutes=watch_data['watch_duration_minutes'],
                            completion_percentage=watch_data['completion_percentage'],
                            genres=watch_data['genres'],
                            year=watch_data.get('year'),
                            director=watch_data.get('director')
                        )
                        self.watch_history.append(watch)
            
            # Load movie ratings
            ratings_file = self.data_dir / "movie_ratings.json"
            if ratings_file.exists():
                with open(ratings_file, 'r') as f:
                    ratings_data = json.load(f)
                    for rating_data in ratings_data:
                        rating = MovieRating(
                            user_id=rating_data['user_id'],
                            movie_title=rating_data['movie_title'],
                            rating=rating_data['rating'],
                            rated_date=datetime.fromisoformat(rating_data['rated_date']),
                            username=rating_data.get('username', '')
                        )
                        self.movie_ratings.append(rating)
            
            print(f"✅ Loaded badge data: {len(self.user_stats)} users, {len(self.watch_history)} watch records, {len(self.movie_ratings)} ratings")
            
        except Exception as e:
            print(f"⚠️ Error loading badge data: {e}")
            print("Starting with fresh badge system...")
    
    def _save_data(self):
        """Save all persistent data to files."""
        try:
            # Save user stats
            stats_data = {}
            for user_id, stats in self.user_stats.items():
                stats_dict = {
                    'user_id': stats.user_id,
                    'username': stats.username,
                    'total_movies': stats.total_movies,
                    'total_watch_time_minutes': stats.total_watch_time_minutes,
                    'completed_movies': stats.completed_movies,
                    'current_streak_days': stats.current_streak_days,
                    'longest_streak_days': stats.longest_streak_days,
                    'last_watch_date': stats.last_watch_date.isoformat() if stats.last_watch_date else None,
                    'favorite_genres': stats.favorite_genres,
                    'favorite_decades': stats.favorite_decades,
                    'directors_watched': list(stats.directors_watched),
                    'ai_interactions': stats.ai_interactions,
                    'votes_cast': stats.votes_cast,
                    'movies_requested': stats.movies_requested
                }
                stats_data[str(user_id)] = stats_dict
            
            with open(self.data_dir / "user_stats.json", 'w') as f:
                json.dump(stats_data, f, indent=2)
            
            # Save user badges
            badges_data = {}
            for user_id, badge_list in self.user_badges.items():
                badge_dicts = []
                for badge in badge_list:
                    badge_dict = {
                        'badge_id': badge.badge_id,
                        'earned_date': badge.earned_date.isoformat(),
                        'progress_value': badge.progress_value
                    }
                    badge_dicts.append(badge_dict)
                badges_data[str(user_id)] = badge_dicts
            
            with open(self.data_dir / "user_badges.json", 'w') as f:
                json.dump(badges_data, f, indent=2)
            
            # Save watch history (keep only last 1000 records to prevent file bloat)
            recent_history = self.watch_history[-1000:] if len(self.watch_history) > 1000 else self.watch_history
            history_data = []
            for watch in recent_history:
                watch_dict = {
                    'movie_title': watch.movie_title,
                    'user_id': watch.user_id,
                    'start_time': watch.start_time.isoformat(),
                    'end_time': watch.end_time.isoformat() if watch.end_time else None,
                    'watch_duration_minutes': watch.watch_duration_minutes,
                    'completion_percentage': watch.completion_percentage,
                    'genres': watch.genres,
                    'year': watch.year,
                    'director': watch.director
                }
                history_data.append(watch_dict)
            
            with open(self.data_dir / "watch_history.json", 'w') as f:
                json.dump(history_data, f, indent=2)
            
            # Save movie ratings
            ratings_data = []
            for rating in self.movie_ratings:
                rating_dict = {
                    'user_id': rating.user_id,
                    'movie_title': rating.movie_title,
                    'rating': rating.rating,
                    'rated_date': rating.rated_date.isoformat(),
                    'username': rating.username
                }
                ratings_data.append(rating_dict)
            
            with open(self.data_dir / "movie_ratings.json", 'w') as f:
                json.dump(ratings_data, f, indent=2)
            
            print(f"✅ Saved badge data: {len(self.user_stats)} users, {len(recent_history)} watch records, {len(self.movie_ratings)} ratings")
            
        except Exception as e:
            print(f"❌ Error saving badge data: {e}")
    
    def update_watch_progress(self, user_id: int, duration_minutes: int, completion_percentage: float):
        """Update watch progress for active session and sync to watch history."""
        
        # Find the current active watch
        if user_id not in self.active_watches:
            return
        
        active_watch = self.active_watches[user_id]
        
        # Update the active watch with current progress
        active_watch.watch_duration_minutes = duration_minutes
        active_watch.completion_percentage = completion_percentage
        
        # Find or create corresponding watch history entry
        # Look for the most recent incomplete entry for this user and movie
        current_watch_entry = None
        for watch in reversed(self.watch_history):
            if (watch.user_id == user_id and 
                watch.movie_title == active_watch.movie_title and 
                watch.end_time is None):  # Still active/incomplete
                current_watch_entry = watch
                break
        
        if current_watch_entry:
            # Update existing entry
            current_watch_entry.watch_duration_minutes = duration_minutes
            current_watch_entry.completion_percentage = completion_percentage
        else:
            # Create new watch history entry for this session
            new_watch = MovieWatch(
                movie_title=active_watch.movie_title,
                user_id=user_id,
                start_time=active_watch.start_time,
                end_time=None,  # Still active
                watch_duration_minutes=duration_minutes,
                completion_percentage=completion_percentage,
                genres=active_watch.genres,
                year=active_watch.year,
                director=active_watch.director,
                movie_duration_ms=active_watch.movie_duration_ms,
                join_position_ms=active_watch.join_position_ms,
                current_position_ms=getattr(active_watch, 'current_position_ms', None)
            )
            self.watch_history.append(new_watch)
        
        # Update user stats incrementally (don't double-count)
        if user_id in self.user_stats:
            stats = self.user_stats[user_id]
            
            # Update total watch time to match current progress
            # We need to be careful not to double-count, so we calculate total from all watch history
            total_time = sum(w.watch_duration_minutes for w in self.watch_history if w.user_id == user_id)
            stats.total_watch_time_minutes = total_time
    
    def save_progress(self):
        """Public method to save current progress."""
        self._save_data()
    
    def backup_data(self):
        """Create a timestamped backup of all data."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.data_dir / "backups" / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy current data files to backup
            import shutil
            for filename in ["user_stats.json", "user_badges.json", "watch_history.json", "movie_ratings.json"]:
                source = self.data_dir / filename
                if source.exists():
                    shutil.copy2(source, backup_dir / filename)
            
            print(f"✅ Created backup at {backup_dir}")
            return backup_dir
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return None