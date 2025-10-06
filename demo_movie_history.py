#!/usr/bin/env python3
"""
Movie History Demo
=================

Demonstration script showing how the movie history system works.
This creates sample watch history data and shows the different views.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Sample movie watch data for demonstration
SAMPLE_WATCH_DATA = [
    {
        "movie_title": "Scream",
        "user_id": 12345,
        "start_time": (datetime.now() - timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() - timedelta(days=1, hours=-2)).isoformat(),
        "watch_duration_minutes": 111,
        "completion_percentage": 95.0,
        "genres": ["Horror", "Slasher", "Thriller"],
        "year": 1996,
        "director": "Wes Craven"
    },
    {
        "movie_title": "Halloween",
        "user_id": 67890,
        "start_time": (datetime.now() - timedelta(days=2)).isoformat(),
        "end_time": (datetime.now() - timedelta(days=2, hours=-1, minutes=-31)).isoformat(),
        "watch_duration_minutes": 91,
        "completion_percentage": 100.0,
        "genres": ["Horror", "Slasher"],
        "year": 1978,
        "director": "John Carpenter"
    },
    {
        "movie_title": "The Exorcist",
        "user_id": 12345,
        "start_time": (datetime.now() - timedelta(days=3)).isoformat(),
        "end_time": (datetime.now() - timedelta(days=3, hours=-2, minutes=-2)).isoformat(),
        "watch_duration_minutes": 122,
        "completion_percentage": 88.0,
        "genres": ["Horror", "Supernatural", "Drama"],
        "year": 1973,
        "director": "William Friedkin"
    },
    {
        "movie_title": "A Nightmare on Elm Street",
        "user_id": 11111,
        "start_time": (datetime.now() - timedelta(days=4)).isoformat(),
        "end_time": (datetime.now() - timedelta(days=4, hours=-1, minutes=-41)).isoformat(),
        "watch_duration_minutes": 101,
        "completion_percentage": 92.0,
        "genres": ["Horror", "Slasher", "Supernatural"],
        "year": 1984,
        "director": "Wes Craven"
    },
    {
        "movie_title": "Psycho",
        "user_id": 67890,
        "start_time": (datetime.now() - timedelta(days=5)).isoformat(),
        "end_time": (datetime.now() - timedelta(days=5, hours=-1, minutes=-49)).isoformat(),
        "watch_duration_minutes": 109,
        "completion_percentage": 100.0,
        "genres": ["Horror", "Psychological", "Thriller"],
        "year": 1960,
        "director": "Alfred Hitchcock"
    },
    {
        "movie_title": "The Thing",
        "user_id": 22222,
        "start_time": (datetime.now() - timedelta(days=6)).isoformat(),
        "end_time": (datetime.now() - timedelta(days=6, hours=-1, minutes=-48)).isoformat(),
        "watch_duration_minutes": 108,
        "completion_percentage": 85.0,
        "genres": ["Horror", "Sci-Fi", "Thriller"],
        "year": 1982,
        "director": "John Carpenter"
    },
    {
        "movie_title": "Scream",
        "user_id": 33333,
        "start_time": (datetime.now() - timedelta(days=7)).isoformat(),
        "end_time": (datetime.now() - timedelta(days=7, hours=-1, minutes=-51)).isoformat(),
        "watch_duration_minutes": 111,
        "completion_percentage": 78.0,
        "genres": ["Horror", "Slasher", "Thriller"],
        "year": 1996,
        "director": "Wes Craven"
    }
]

SAMPLE_USER_STATS = {
    "12345": {
        "user_id": 12345,
        "username": "HorrorFan123",
        "total_movies": 2,
        "total_watch_time_minutes": 233,
        "completed_movies": 2,
        "current_streak_days": 2,
        "longest_streak_days": 3,
        "last_watch_date": (datetime.now() - timedelta(days=1)).isoformat(),
        "favorite_genres": {"Horror": 2, "Slasher": 1, "Supernatural": 1},
        "favorite_decades": {"1990s": 1, "1970s": 1},
        "directors_watched": ["Wes Craven", "William Friedkin"],
        "ai_interactions": 15,
        "votes_cast": 8,
        "movies_requested": 3
    },
    "67890": {
        "user_id": 67890,
        "username": "CinemaGhost",
        "total_movies": 2,
        "total_watch_time_minutes": 200,
        "completed_movies": 2,
        "current_streak_days": 1,
        "longest_streak_days": 4,
        "last_watch_date": (datetime.now() - timedelta(days=2)).isoformat(),
        "favorite_genres": {"Horror": 2, "Slasher": 1, "Psychological": 1},
        "favorite_decades": {"1970s": 1, "1960s": 1},
        "directors_watched": ["John Carpenter", "Alfred Hitchcock"],
        "ai_interactions": 23,
        "votes_cast": 12,
        "movies_requested": 5
    }
}


def create_sample_data():
    """Create sample badge system data for demonstration."""
    print("📁 Creating sample movie history data...")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create watch history file
    with open(data_dir / "watch_history.json", 'w') as f:
        json.dump(SAMPLE_WATCH_DATA, f, indent=2)
    
    # Create user stats file
    with open(data_dir / "user_stats.json", 'w') as f:
        json.dump(SAMPLE_USER_STATS, f, indent=2)
    
    print(f"✅ Created {len(SAMPLE_WATCH_DATA)} watch records")
    print(f"✅ Created {len(SAMPLE_USER_STATS)} user profiles")


def analyze_sample_data():
    """Analyze and display the sample movie history data."""
    print("\n📊 Movie History Analysis")
    print("=" * 50)
    
    # Unique movies
    unique_movies = list(set(watch["movie_title"] for watch in SAMPLE_WATCH_DATA))
    print(f"🎬 Unique Movies ({len(unique_movies)}):")
    for movie in unique_movies:
        # Count watchers
        watchers = len([w for w in SAMPLE_WATCH_DATA if w["movie_title"] == movie])
        year = next(w["year"] for w in SAMPLE_WATCH_DATA if w["movie_title"] == movie)
        print(f"   • {movie} ({year}) - {watchers} watcher{'s' if watchers > 1 else ''}")
    
    # User activity
    print(f"\n👥 User Activity:")
    user_watches = {}
    for watch in SAMPLE_WATCH_DATA:
        user_id = str(watch["user_id"])
        if user_id not in user_watches:
            user_watches[user_id] = []
        user_watches[user_id].append(watch)
    
    for user_id, watches in user_watches.items():
        username = SAMPLE_USER_STATS.get(user_id, {}).get("username", f"User_{user_id}")
        total_time = sum(w["watch_duration_minutes"] for w in watches)
        completed = len([w for w in watches if w["completion_percentage"] >= 80])
        
        print(f"   • {username}: {len(watches)} movies, {total_time//60}h {total_time%60}m, {completed} completed")
    
    # Genre breakdown
    print(f"\n🎭 Genre Breakdown:")
    genre_counts = {}
    for watch in SAMPLE_WATCH_DATA:
        for genre in watch["genres"]:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {genre}: {count} movies")
    
    # Decade analysis
    print(f"\n📅 Decade Analysis:")
    decade_counts = {}
    for watch in SAMPLE_WATCH_DATA:
        decade = (watch["year"] // 10) * 10
        decade_key = f"{decade}s"
        decade_counts[decade_key] = decade_counts.get(decade_key, 0) + 1
    
    for decade, count in sorted(decade_counts.items()):
        print(f"   • {decade}: {count} movies")
    
    # Most watched movie
    movie_counts = {}
    for watch in SAMPLE_WATCH_DATA:
        movie_counts[watch["movie_title"]] = movie_counts.get(watch["movie_title"], 0) + 1
    
    most_watched = max(movie_counts.items(), key=lambda x: x[1])
    print(f"\n🏆 Most Watched: {most_watched[0]} ({most_watched[1]} times)")


def demo_discord_commands():
    """Show what the Discord commands would display."""
    print(f"\n🤖 Discord Command Examples")
    print("=" * 50)
    
    print("📚 !history")
    print("   Recent Movies Played by Bot:")
    recent_movies = {}
    for watch in SAMPLE_WATCH_DATA:
        movie = watch["movie_title"]
        if movie not in recent_movies or watch["start_time"] > recent_movies[movie]["start_time"]:
            recent_movies[movie] = watch
    
    for watch in sorted(recent_movies.values(), key=lambda x: x["start_time"], reverse=True):
        date_str = datetime.fromisoformat(watch["start_time"]).strftime("%m/%d/%y")
        watchers = len([w for w in SAMPLE_WATCH_DATA if w["movie_title"] == watch["movie_title"]])
        print(f"   • {watch['movie_title']} ({watch['year']}) - {date_str} - {watchers} watchers")
    
    print(f"\n👥 !history HorrorFan123")
    print("   Movie History - HorrorFan123:")
    user_watches = [w for w in SAMPLE_WATCH_DATA if w["user_id"] == 12345]
    for watch in sorted(user_watches, key=lambda x: x["start_time"], reverse=True):
        completion_emoji = "✅" if watch["completion_percentage"] >= 80 else "⏸️"
        date_str = datetime.fromisoformat(watch["start_time"]).strftime("%m/%d")
        duration = f"{watch['watch_duration_minutes']}m"
        print(f"   {completion_emoji} {watch['movie_title']} - {date_str} ({duration})")
    
    print(f"\n📊 !moviestats")
    total_watches = len(SAMPLE_WATCH_DATA)
    unique_movies = len(set(w["movie_title"] for w in SAMPLE_WATCH_DATA))
    completed = len([w for w in SAMPLE_WATCH_DATA if w["completion_percentage"] >= 80])
    completion_rate = (completed / total_watches * 100)
    
    # Calculate most watched movie
    movie_counts = {}
    for watch in SAMPLE_WATCH_DATA:
        movie_counts[watch["movie_title"]] = movie_counts.get(watch["movie_title"], 0) + 1
    most_watched = max(movie_counts.items(), key=lambda x: x[1])
    
    print(f"   🎬 Movies: {unique_movies} unique, {total_watches} total, {completion_rate:.1f}% completion")
    print(f"   👥 Users: {len(set(w['user_id'] for w in SAMPLE_WATCH_DATA))} unique watchers")
    print(f"   🏆 Most Watched: {most_watched[0]} ({most_watched[1]} times)")


def main():
    """Run the movie history demo."""
    print("🎬 ClankerTV Movie History Demo")
    print("=" * 50)
    
    create_sample_data()
    analyze_sample_data()
    demo_discord_commands()
    
    print(f"\n🎮 Available Discord Commands:")
    print(f"   !history              - Show recent movies played")
    print(f"   !history <user>       - Show user's watch history") 
    print(f"   !moviestats           - Comprehensive statistics")
    print(f"   !topwatchers          - Leaderboard of top watchers")
    
    print(f"\n✨ Features:")
    print(f"   📊 Comprehensive statistics and analytics")
    print(f"   👥 Per-user watch history tracking")
    print(f"   🎬 Movie popularity and rewatch tracking") 
    print(f"   📅 Genre and decade analysis")
    print(f"   🏆 Leaderboards and achievements")
    print(f"   💾 Persistent storage with badge system")
    
    print(f"\n📁 Data Files Created:")
    print(f"   data/watch_history.json  - All movie watch records")
    print(f"   data/user_stats.json     - User statistics and preferences")
    
    print(f"\n🎃 Movie History Demo Complete!")
    
    # Cleanup option
    cleanup = input(f"\n🗑️ Clean up demo data files? (y/n): ").lower().strip()
    if cleanup == 'y':
        import shutil
        if os.path.exists("data"):
            shutil.rmtree("data")
        print("✅ Demo data cleaned up!")


if __name__ == "__main__":
    main()