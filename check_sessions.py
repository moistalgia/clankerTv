#!/usr/bin/env python3
"""
Check Active Watch Sessions
===========================

Check if there are any active watch sessions and their current duration.
"""

import json
from datetime import datetime
from models.badge_system import WatchBadgeSystem

def check_active_sessions():
    """Check for active watch sessions."""
    
    print("🔍 Checking Active Watch Sessions...")
    
    # Initialize badge system
    badge_system = WatchBadgeSystem()
    
    print(f"📊 Total users: {len(badge_system.user_stats)}")
    print(f"🎬 Active sessions: {len(badge_system.active_watches)}")
    
    if badge_system.active_watches:
        print("\n⏱️  Active Watch Sessions:")
        for user_id, watch in badge_system.active_watches.items():
            # Calculate current duration
            now = datetime.now()
            current_duration = int((now - watch.start_time).total_seconds() / 60)
            
            print(f"   👤 User ID: {user_id}")
            print(f"   🎬 Movie: {watch.movie_title}")
            print(f"   ⏰ Started: {watch.start_time.strftime('%H:%M:%S')}")
            print(f"   ⏳ Current Duration: {current_duration} minutes")
            print()
    else:
        print("\n❌ No active watch sessions found.")
        print("   To start tracking:")
        print("   1. Join voice channel ID: 1422665247994548285")
        print("   2. Use !play <movie> command")
        print("   3. Stay in channel while watching")
    
    # Show recent completed sessions
    if badge_system.watch_history:
        print("\n📚 Recent Completed Sessions:")
        for watch in badge_system.watch_history[-3:]:  # Last 3 sessions
            print(f"   🎬 {watch.movie_title}")
            print(f"   👤 User ID: {watch.user_id}")
            print(f"   ⏱️  Duration: {watch.watch_duration_minutes} minutes")
            print(f"   ✅ Completion: {watch.completion_percentage}%")
            print()

if __name__ == "__main__":
    check_active_sessions()