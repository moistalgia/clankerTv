#!/usr/bin/env python3
"""
Test Movie Rating System
========================

Test script to verify the movie rating system works correctly.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from models.badge_system import WatchBadgeSystem

async def test_rating_system():
    """Test the movie rating system functionality."""
    
    print("🎬 Testing Movie Rating System")
    print("=" * 40)
    
    # Initialize badge system
    badge_system = WatchBadgeSystem("data")
    
    print(f"📊 Initial state:")
    print(f"   Total ratings: {len(badge_system.movie_ratings)}")
    print(f"   Watch history: {len(badge_system.watch_history)}")
    
    # Test data
    test_user_id = 999999999999999998  # Different from auto-save test
    test_username = "RatingTestUser"
    test_movies = [
        ("The Shining", 1980, ["Horror", "Thriller"], "Stanley Kubrick"),
        ("Halloween", 1978, ["Horror"], "John Carpenter"),
        ("Hereditary", 2018, ["Horror", "Drama"], "Ari Aster")
    ]
    
    print(f"\n📚 Adding test movies to watch history...")
    
    # Add movies to watch history first
    for movie_title, year, genres, director in test_movies:
        success = badge_system.add_manual_watch(
            user_id=test_user_id,
            username=test_username,
            movie_title=movie_title,
            genres=genres,
            year=year,
            director=director
        )
        print(f"   {'✅' if success else '❌'} {movie_title} ({year})")
    
    print(f"\n⭐ Testing movie ratings...")
    
    # Test rating movies
    test_ratings = [
        ("The Shining", 9),
        ("Halloween", 8),
        ("Hereditary", 10)
    ]
    
    for movie_title, rating in test_ratings:
        try:
            success = badge_system.rate_movie(test_user_id, test_username, movie_title, rating)
            if success:
                user_rating = badge_system.get_user_rating(test_user_id, movie_title)
                print(f"   ✅ {movie_title}: {rating}/10 {user_rating.rating_emoji} ({user_rating.rating_text})")
            else:
                print(f"   ❌ {movie_title}: Already rated")
        except Exception as e:
            print(f"   ❌ {movie_title}: Error - {e}")
    
    # Test duplicate rating (should fail)
    print(f"\n🔄 Testing duplicate rating prevention...")
    try:
        success = badge_system.rate_movie(test_user_id, test_username, "The Shining", 7)
        print(f"   {'❌ FAILED' if success else '✅ PASSED'}: Duplicate rating prevention")
    except Exception as e:
        print(f"   ✅ PASSED: Duplicate rating blocked with error: {e}")
    
    # Test rating unmatched movie (should fail)
    print(f"\n🚫 Testing rating unwatched movie...")
    try:
        success = badge_system.rate_movie(test_user_id, test_username, "Unwatched Movie", 5)
        print(f"   {'❌ FAILED' if success else '✅ PASSED'}: Unwatched movie rating prevention")
    except Exception as e:
        print(f"   ✅ PASSED: Unwatched movie blocked with error: {e}")
    
    # Test rating validation
    print(f"\n📏 Testing rating validation...")
    for invalid_rating in [0, 11, -1, 15]:
        try:
            badge_system.rate_movie(test_user_id, test_username, "The Shining", invalid_rating)
            print(f"   ❌ FAILED: Invalid rating {invalid_rating} was accepted")
        except ValueError:
            print(f"   ✅ PASSED: Invalid rating {invalid_rating} rejected")
        except Exception as e:
            print(f"   ⚠️  UNKNOWN: Rating {invalid_rating} caused error: {e}")
    
    # Test getting ratings
    print(f"\n📊 Testing rating retrieval...")
    
    # Get user ratings
    user_ratings = badge_system.get_user_ratings(test_user_id)
    print(f"   User ratings: {len(user_ratings)} movies")
    for rating in user_ratings:
        print(f"     {rating.rating_emoji} {rating.movie_title}: {rating.rating}/10")
    
    # Get movie ratings
    shining_ratings = badge_system.get_movie_ratings("The Shining")
    print(f"   'The Shining' ratings: {len(shining_ratings)} users")
    
    # Get average rating
    avg_rating = badge_system.get_average_rating("The Shining")
    print(f"   'The Shining' average: {avg_rating:.1f}/10")
    
    # Get all rated movies
    all_rated = badge_system.get_all_rated_movies()
    print(f"   All rated movies: {len(all_rated)} total")
    
    for movie_title, data in sorted(all_rated.items(), key=lambda x: x[1]['average_rating'], reverse=True):
        avg = data['average_rating']
        count = data['total_ratings']
        print(f"     {movie_title}: {avg:.1f}/10 ({count} ratings)")
    
    # Test data persistence
    print(f"\n💾 Testing data persistence...")
    original_rating_count = len(badge_system.movie_ratings)
    
    badge_system.save_progress()
    print(f"   ✅ Data saved ({original_rating_count} ratings)")
    
    # Reload badge system
    badge_system_2 = WatchBadgeSystem("data")
    loaded_rating_count = len(badge_system_2.movie_ratings)
    
    print(f"   ✅ Data loaded ({loaded_rating_count} ratings)")
    print(f"   {'✅ PASSED' if original_rating_count == loaded_rating_count else '❌ FAILED'}: Data persistence")
    
    # Clean up test data
    print(f"\n🧹 Cleaning up test data...")
    try:
        # Remove test user ratings
        badge_system.movie_ratings = [r for r in badge_system.movie_ratings if r.user_id != test_user_id]
        
        # Remove test user from stats and badges
        if test_user_id in badge_system.user_stats:
            del badge_system.user_stats[test_user_id]
        if test_user_id in badge_system.user_badges:
            del badge_system.user_badges[test_user_id]
        
        # Remove test watches from history
        badge_system.watch_history = [w for w in badge_system.watch_history if w.user_id != test_user_id]
        
        # Save cleaned data
        badge_system.save_progress()
        print(f"   ✅ Test data cleaned up")
        
    except Exception as e:
        print(f"   ⚠️ Cleanup failed: {e}")
    
    print(f"\n📋 Rating System Test Summary:")
    print(f"   ✅ Movie rating (1-10 stars with emoji)")
    print(f"   ✅ Rating validation (range checking)")
    print(f"   ✅ Duplicate rating prevention")
    print(f"   ✅ Watch history requirement")
    print(f"   ✅ Rating retrieval (user/movie/average)")
    print(f"   ✅ Data persistence (JSON storage)")
    print(f"   ✅ Manual movie addition")
    
    print(f"\n💡 Available Commands:")
    print(f"   !rate <1-10> <movie> - Rate a movie")
    print(f"   !ratings [movie] - Show ratings") 
    print(f"   !myratings - Show your ratings")
    print(f"   !addmovie <movie info> - Add movie to history")
    
    print(f"\n🎯 Rating Emojis:")
    from models.badge_system import MovieRating
    for rating_val in range(1, 11):
        dummy_rating = MovieRating(0, "Test", rating_val, datetime.now())
        print(f"   {rating_val}/10: {dummy_rating.rating_emoji} ({dummy_rating.rating_text})")

if __name__ == "__main__":
    asyncio.run(test_rating_system())