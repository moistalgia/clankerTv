#!/usr/bin/env python3
"""
Data Cleanup Script
==================

Consolidates duplicate watch entries for each user/movie combination.
Each user should have only one watch record per movie with total time watched.
"""

import json
from datetime import datetime
from collections import defaultdict

def cleanup_watch_data():
    """Clean up watch history and user stats to remove duplicates."""
    
    print("🧹 Starting data cleanup...")
    
    # Load current data
    with open('data/watch_history.json', 'r') as f:
        watch_history = json.load(f)
    
    with open('data/user_stats.json', 'r') as f:
        user_stats = json.load(f)
    
    print(f"📊 Current data: {len(watch_history)} watch entries, {len(user_stats)} users")
    
    # Group watches by user_id and movie_title
    user_movie_watches = defaultdict(list)
    
    for watch in watch_history:
        key = (watch['user_id'], watch['movie_title'])
        user_movie_watches[key].append(watch)
    
    print(f"📋 Found {len(user_movie_watches)} unique user/movie combinations")
    
    # Consolidate duplicates
    consolidated_watches = []
    consolidation_stats = {
        'duplicates_found': 0,
        'total_time_recovered': 0,
        'movies_consolidated': []
    }
    
    for (user_id, movie_title), watches in user_movie_watches.items():
        if len(watches) == 1:
            # No duplicates, keep as is
            consolidated_watches.append(watches[0])
        else:
            # Multiple entries - consolidate them
            consolidation_stats['duplicates_found'] += len(watches) - 1
            consolidation_stats['movies_consolidated'].append(f"{get_username(user_id, user_stats)} - {movie_title} ({len(watches)} entries)")
            
            print(f"🔄 Consolidating {len(watches)} entries for {get_username(user_id, user_stats)} - {movie_title}")
            
            # Sort by start time to get chronological order
            watches.sort(key=lambda x: x['start_time'])
            
            # Use the first (earliest) entry as base
            consolidated_watch = watches[0].copy()
            
            # Sum up all watch durations
            total_duration = sum(w['watch_duration_minutes'] for w in watches)
            
            # Get movie length limits (approximate based on known movies)
            movie_lengths = {
                'Hell House LLC': 93,
                'Hell Fest': 89,
                'The Cloverfield Paradox': 102,
                'The Shining': 146,
                'Halloween': 91,
                'Hereditary': 127
            }
            
            max_duration = movie_lengths.get(movie_title, 120)  # Default 2 hours if unknown
            
            # Cap duration at movie length
            final_duration = min(total_duration, max_duration)
            
            # Calculate completion percentage
            completion_percentage = (final_duration / max_duration) * 100 if max_duration > 0 else 100.0
            
            # Update consolidated entry
            consolidated_watch['watch_duration_minutes'] = final_duration
            consolidated_watch['completion_percentage'] = completion_percentage
            
            # Use the latest end_time if any entries are completed
            completed_watches = [w for w in watches if w.get('end_time') is not None]
            if completed_watches:
                # Use the latest completion time
                latest_end = max(completed_watches, key=lambda x: x['end_time'])['end_time']
                consolidated_watch['end_time'] = latest_end
            else:
                # All are still active, keep as null
                consolidated_watch['end_time'] = None
            
            consolidation_stats['total_time_recovered'] += total_duration - final_duration
            
            consolidated_watches.append(consolidated_watch)
            
            print(f"  ✅ {total_duration}m → {final_duration}m ({completion_percentage:.1f}% complete)")
    
    print(f"\n📈 Consolidation Results:")
    print(f"  • Original entries: {len(watch_history)}")
    print(f"  • Consolidated entries: {len(consolidated_watches)}")
    print(f"  • Duplicates removed: {consolidation_stats['duplicates_found']}")
    print(f"  • Excess time capped: {consolidation_stats['total_time_recovered']} minutes")
    
    if consolidation_stats['movies_consolidated']:
        print(f"\n🎬 Movies consolidated:")
        for movie in consolidation_stats['movies_consolidated']:
            print(f"  • {movie}")
    
    # Recalculate user stats from consolidated data
    print(f"\n🔄 Recalculating user statistics...")
    
    for user_id_str, stats in user_stats.items():
        user_id = int(user_id_str)
        username = stats['username']
        
        # Get all watches for this user
        user_watches = [w for w in consolidated_watches if w['user_id'] == user_id]
        
        # Recalculate stats
        old_movies = stats['total_movies']
        old_time = stats['total_watch_time_minutes']
        
        stats['total_movies'] = len(user_watches)
        stats['total_watch_time_minutes'] = sum(w['watch_duration_minutes'] for w in user_watches)
        stats['completed_movies'] = len([w for w in user_watches if w.get('end_time') is not None and w['completion_percentage'] >= 80])
        
        # Update genre preferences
        genre_counts = {}
        for watch in user_watches:
            for genre in watch.get('genres', []):
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        stats['favorite_genres'] = genre_counts
        
        # Update decade preferences  
        decade_counts = {}
        for watch in user_watches:
            if watch.get('year'):
                decade = f"{(watch['year'] // 10) * 10}s"
                decade_counts[decade] = decade_counts.get(decade, 0) + 1
        stats['favorite_decades'] = decade_counts
        
        # Update directors
        directors = list(set(w.get('director') for w in user_watches if w.get('director')))
        stats['directors_watched'] = directors
        
        print(f"  📊 {username}: {old_movies}→{stats['total_movies']} movies, {old_time}→{stats['total_watch_time_minutes']}m")
    
    # Create backup of original data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with open(f'data/watch_history_backup_{timestamp}.json', 'w') as f:
        json.dump(watch_history, f, indent=2)
    
    with open(f'data/user_stats_backup_{timestamp}.json', 'w') as f:
        json.dump(user_stats, f, indent=2)
    
    print(f"\n💾 Created backups:")
    print(f"  • watch_history_backup_{timestamp}.json")
    print(f"  • user_stats_backup_{timestamp}.json")
    
    # Write cleaned data
    with open('data/watch_history.json', 'w') as f:
        json.dump(consolidated_watches, f, indent=2)
    
    with open('data/user_stats.json', 'w') as f:
        json.dump(user_stats, f, indent=2)
    
    print(f"\n✅ Data cleanup complete!")
    print(f"📋 Summary:")
    print(f"  • Watch entries: {len(watch_history)} → {len(consolidated_watches)}")
    print(f"  • Duplicates removed: {consolidation_stats['duplicates_found']}")
    print(f"  • Users updated: {len(user_stats)}")
    
    return consolidation_stats

def get_username(user_id, user_stats):
    """Get username for user ID."""
    user_data = user_stats.get(str(user_id))
    if user_data:
        return user_data.get('username', f'User_{user_id}')
    return f'User_{user_id}'

if __name__ == "__main__":
    cleanup_watch_data()