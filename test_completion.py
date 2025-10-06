#!/usr/bin/env python3
"""
Enhanced Completion Percentage for Late Joiners
==============================================

Demonstrates how to calculate accurate completion percentages for users who join movies in progress.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class CompletionCalculator:
    """Calculate accurate completion percentages for late joiners."""
    
    @staticmethod
    def calculate_late_joiner_completion(
        movie_duration_ms: int,
        movie_start_offset_ms: int,  # How far into movie when user joined
        user_watch_time_seconds: int,
        movie_end_offset_ms: Optional[int] = None  # Where movie was when user finished watching
    ) -> float:
        """
        Calculate completion percentage for a late joiner.
        
        Args:
            movie_duration_ms: Total movie duration in milliseconds
            movie_start_offset_ms: Movie position when user started watching
            user_watch_time_seconds: How long user actually watched
            movie_end_offset_ms: Movie position when user stopped watching (if left early)
            
        Returns:
            Completion percentage (0-100)
        """
        
        if movie_duration_ms <= 0:
            return 0.0
            
        # If movie ended naturally, user watched to the end
        if movie_end_offset_ms is None:
            movie_end_offset_ms = movie_duration_ms
        
        # Calculate how much of the movie the user actually saw
        movie_content_watched_ms = movie_end_offset_ms - movie_start_offset_ms
        
        # Convert to percentage of total movie
        completion_percentage = (movie_content_watched_ms / movie_duration_ms) * 100
        
        # Cap at 100% and ensure non-negative
        return max(0.0, min(100.0, completion_percentage))
    
    @staticmethod
    def calculate_traditional_completion(
        user_watch_time_seconds: int,
        movie_duration_seconds: int
    ) -> float:
        """
        Traditional calculation: user watch time vs movie duration.
        This can exceed 100% for late joiners who watch past movie end.
        """
        if movie_duration_seconds <= 0:
            return 0.0
            
        return min(100.0, (user_watch_time_seconds / movie_duration_seconds) * 100)

def test_completion_scenarios():
    """Test various late joiner completion scenarios."""
    
    print("🎬 Late Joiner Completion Percentage Testing")
    print("=" * 50)
    
    # Example: 120-minute horror movie (7200 seconds = 7,200,000 ms)
    movie_duration_ms = 120 * 60 * 1000  # 2 hours
    movie_duration_seconds = 120 * 60
    
    scenarios = [
        {
            "name": "Perfect Attendance",
            "description": "User watches entire movie from start",
            "join_offset_ms": 0,
            "watch_time_seconds": 120 * 60,
            "end_offset_ms": movie_duration_ms
        },
        {
            "name": "Late Joiner - Full Completion", 
            "description": "User joins 30 minutes in, watches to end",
            "join_offset_ms": 30 * 60 * 1000,  # 30 minutes in
            "watch_time_seconds": 90 * 60,      # Watches 90 minutes
            "end_offset_ms": movie_duration_ms   # Movie ends naturally
        },
        {
            "name": "Late Joiner - Early Leaver",
            "description": "User joins 30 min in, leaves 30 min before end", 
            "join_offset_ms": 30 * 60 * 1000,   # 30 minutes in
            "watch_time_seconds": 60 * 60,      # Watches 60 minutes
            "end_offset_ms": 90 * 60 * 1000     # Leaves at 90-minute mark
        },
        {
            "name": "Very Late Joiner",
            "description": "User joins with only 15 minutes left",
            "join_offset_ms": 105 * 60 * 1000,  # 105 minutes in (15 min left)
            "watch_time_seconds": 15 * 60,      # Watches final 15 minutes
            "end_offset_ms": movie_duration_ms   # Watches to end
        },
        {
            "name": "Brief Visit",
            "description": "User joins mid-movie, watches 10 minutes, leaves",
            "join_offset_ms": 45 * 60 * 1000,   # 45 minutes in
            "watch_time_seconds": 10 * 60,      # Watches 10 minutes
            "end_offset_ms": 55 * 60 * 1000     # Leaves after 10 minutes
        }
    ]
    
    calculator = CompletionCalculator()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Scenario {i}: {scenario['name']}")
        print(f"   📝 {scenario['description']}")
        
        # Calculate enhanced completion (based on movie content seen)
        enhanced_completion = calculator.calculate_late_joiner_completion(
            movie_duration_ms=movie_duration_ms,
            movie_start_offset_ms=scenario['join_offset_ms'],
            user_watch_time_seconds=scenario['watch_time_seconds'],
            movie_end_offset_ms=scenario['end_offset_ms']
        )
        
        # Calculate traditional completion (watch time vs total duration)
        traditional_completion = calculator.calculate_traditional_completion(
            user_watch_time_seconds=scenario['watch_time_seconds'],
            movie_duration_seconds=movie_duration_seconds
        )
        
        # Show timeline
        join_time_min = scenario['join_offset_ms'] // (60 * 1000)
        end_time_min = scenario['end_offset_ms'] // (60 * 1000)
        watch_time_min = scenario['watch_time_seconds'] // 60
        
        print(f"   📊 Timeline:")
        print(f"      🕐 Joined at: {join_time_min} minutes")
        print(f"      🕐 Left at: {end_time_min} minutes") 
        print(f"      ⏱️  Watch time: {watch_time_min} minutes")
        
        print(f"   📈 Completion Calculations:")
        print(f"      🎯 Enhanced: {enhanced_completion:.1f}% (movie content seen)")
        print(f"      📊 Traditional: {traditional_completion:.1f}% (time watched)")
        
        # Show which method is better
        if enhanced_completion != traditional_completion:
            better_method = "Enhanced" if enhanced_completion < traditional_completion else "Traditional"
            print(f"      💡 {better_method} method gives more accurate representation")
    
    print(f"\n🎓 Key Insights:")
    print("   🎯 Enhanced Method:")
    print("      ✅ Accurately reflects what % of movie content user saw")
    print("      ✅ Late joiners can't exceed 100% completion")  
    print("      ✅ Better for badge requirements")
    print()
    print("   📊 Traditional Method:")
    print("      ✅ Simple time-based calculation")
    print("      ❌ Can give misleading results for late joiners")
    print("      ❌ May exceed 100% if user watches past original runtime")
    
    print(f"\n💡 Recommendation:")
    print("   Use Enhanced Method when Plex session data is available")
    print("   Fall back to Traditional Method for manual tracking")

if __name__ == "__main__":
    test_completion_scenarios()