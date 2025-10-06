#!/usr/bin/env python3
"""
Watch Stats Repair Script
========================

Repairs user watch statistics by recalculating from actual watch history
and adds missing watch entries based on actual viewing sessions.
"""

import json
from datetime import datetime, timedelta
from models.badge_system import WatchBadgeSystem, MovieWatch

def repair_watch_stats():
    """Repair watch statistics for users based on actual viewing."""
    
    print("🔧 Starting watch stats repair...")
    
    # Load badge system
    badge_system = WatchBadgeSystem()
    
    # User mappings (ID -> username for clarity)
    users = {
        99507990859616256: "moisty",
        153232848407494656: "choppascray", 
        845480209452630096: "PorkBorkins"  # Assuming this is PorkBorkins
    }
    
    print(f"📊 Current stats before repair:")
    for user_id, username in users.items():
        if user_id in badge_system.user_stats:
            stats = badge_system.user_stats[user_id]
            print(f"  {username}: {stats.total_movies} movies, {stats.total_watch_time_minutes}m")
        else:
            print(f"  {username}: No stats found")
    
    print(f"📚 Current watch history: {len(badge_system.watch_history)} entries")
    
    # Based on user description, add missing watch entries
    # "Myself and choppascray and PorkBorkins have watched all of Hell Fest, and up to the current position of cloverfield"
    # "ChoppyScray and i watched all of Hell House LLC"
    
    base_time = datetime.now() - timedelta(hours=3)  # 3 hours ago as a reasonable start time
    
    # Hell House LLC (91 minutes) - moisty and choppascray completed it
    hell_house_duration = 91
    hell_house_entries = [
        (99507990859616256, "moisty"),      # You
        (153232848407494656, "choppascray") # ChoppyScray
    ]
    
    # Hell Fest (89 minutes) - All three users completed it  
    hell_fest_duration = 89
    hell_fest_entries = [
        (99507990859616256, "moisty"),
        (153232848407494656, "choppascray"), 
        (845480209452630096, "PorkBorkins")
    ]
    
    # Cloverfield Paradox (102 minutes) - All three watched up to current position (~60% = 61 minutes)
    cloverfield_duration = 61  # Partial watch
    cloverfield_entries = [
        (99507990859616256, "moisty"),
        (153232848407494656, "choppascray"), 
        (845480209452630096, "PorkBorkins")
    ]
    
    new_entries = []
    
    print("\n🎬 Adding missing watch entries...")
    
    # Add Hell House LLC entries (if not already complete)
    for i, (user_id, username) in enumerate(hell_house_entries):
        # Check if user already has a complete Hell House entry
        existing = [w for w in badge_system.watch_history 
                   if w.user_id == user_id and w.movie_title == "Hell House LLC" 
                   and w.watch_duration_minutes >= hell_house_duration * 0.8]  # 80% threshold
        
        if not existing:
            start_time = base_time + timedelta(minutes=i * 2)  # Stagger start times
            end_time = start_time + timedelta(minutes=hell_house_duration)
            
            watch = MovieWatch(
                movie_title="Hell House LLC",
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                watch_duration_minutes=hell_house_duration,
                completion_percentage=100.0,
                genres=["Horror", "Mystery"],
                year=2015,
                director="Stephen Cognetti"
            )
            new_entries.append(watch)
            print(f"  ✅ Added Hell House LLC complete watch for {username}")
    
    # Add Hell Fest entries
    hell_fest_start = base_time + timedelta(hours=1, minutes=45)  # After Hell House
    for i, (user_id, username) in enumerate(hell_fest_entries):
        start_time = hell_fest_start + timedelta(minutes=i * 2)
        end_time = start_time + timedelta(minutes=hell_fest_duration)
        
        watch = MovieWatch(
            movie_title="Hell Fest",
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            watch_duration_minutes=hell_fest_duration,
            completion_percentage=100.0,
            genres=["Horror", "Thriller"],
            year=2018,
            director="Gregory Plotkin"
        )
        new_entries.append(watch)
        print(f"  ✅ Added Hell Fest complete watch for {username}")
    
    # Add Cloverfield Paradox partial entries
    cloverfield_start = hell_fest_start + timedelta(hours=1, minutes=35)  # After Hell Fest
    for i, (user_id, username) in enumerate(cloverfield_entries):
        start_time = cloverfield_start + timedelta(minutes=i * 2)
        end_time = start_time + timedelta(minutes=cloverfield_duration)
        
        watch = MovieWatch(
            movie_title="The Cloverfield Paradox",
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            watch_duration_minutes=cloverfield_duration,
            completion_percentage=59.8,  # ~60% of 102 minutes
            genres=["Science Fiction", "Thriller"],
            year=2018,
            director="Julius Onah"
        )
        new_entries.append(watch)
        print(f"  ✅ Added Cloverfield Paradox partial watch for {username}")
    
    # Add new entries to badge system
    for watch in new_entries:
        badge_system.watch_history.append(watch)
    
    print(f"\n📈 Added {len(new_entries)} new watch entries")
    
    # Now recalculate all user stats from scratch
    print("\n🔄 Recalculating user stats from watch history...")
    
    # Reset all user stats
    for user_id in users.keys():
        if user_id in badge_system.user_stats:
            stats = badge_system.user_stats[user_id]
            stats.total_movies = 0
            stats.total_watch_time_minutes = 0
            stats.completed_movies = 0
            stats.favorite_genres = {}
            stats.favorite_decades = {}
            stats.directors_watched = []
    
    # Recalculate from all watch history
    for watch in badge_system.watch_history:
        if watch.user_id in users:
            badge_system._update_user_stats(watch.user_id, watch)
    
    # Save updated data
    badge_system._save_data()
    
    print(f"\n✅ Repair complete! Updated stats:")
    for user_id, username in users.items():
        if user_id in badge_system.user_stats:
            stats = badge_system.user_stats[user_id]
            hours = stats.total_watch_time_minutes / 60
            print(f"  {username}: {stats.total_movies} movies, {stats.total_watch_time_minutes}m ({hours:.1f}h)")
            
            # Show their movies
            user_movies = [w for w in badge_system.watch_history if w.user_id == user_id]
            for movie in user_movies:
                status = "✅" if movie.completion_percentage >= 80 else "⏸️"
                print(f"    {status} {movie.movie_title} - {movie.watch_duration_minutes}m ({movie.completion_percentage:.0f}%)")
    
    print(f"\n🎯 Expected totals based on description:")
    print(f"  moisty: Hell House (91m) + Hell Fest (89m) + Cloverfield (61m) = ~241 minutes")
    print(f"  choppascray: Hell House (91m) + Hell Fest (89m) + Cloverfield (61m) = ~241 minutes") 
    print(f"  PorkBorkins: Hell Fest (89m) + Cloverfield (61m) = ~150 minutes")


if __name__ == "__main__":
    repair_watch_stats()