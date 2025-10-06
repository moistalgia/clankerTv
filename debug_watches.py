#!/usr/bin/env python3
"""
Debug Active Watches
===================

Debug script to check current active watch data and position calculations.
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from models.badge_system import WatchBadgeSystem
from services.plex_service import PlexService

async def debug_active_watches():
    """Debug current active watch sessions."""
    
    print("🔍 Debug Active Watches")
    print("=" * 40)
    
    # Initialize services
    badge_system = WatchBadgeSystem("data")
    plex_service = PlexService()
    
    print(f"📊 Badge System Status:")
    print(f"   Active watches: {len(badge_system.active_watches)}")
    print(f"   Total users: {len(badge_system.user_stats)}")
    print(f"   Watch history: {len(badge_system.watch_history)}")
    
    if not badge_system.active_watches:
        print("\n❌ No active watches found")
        return
    
    # Get current Plex position
    current_position_ms = None
    if plex_service.is_connected():
        try:
            current_session_info = await plex_service.get_enhanced_session_info()
            current_position_ms = current_session_info.get('current_position_ms') if current_session_info else None
            duration_ms = current_session_info.get('duration_ms') if current_session_info else None
            
            print(f"\n🎬 Plex Status:")
            if current_position_ms:
                current_mins = current_position_ms // (1000 * 60)
                print(f"   Current position: {current_mins} minutes ({current_position_ms} ms)")
                
                if duration_ms:
                    total_mins = duration_ms // (1000 * 60)
                    progress = (current_position_ms / duration_ms) * 100
                    print(f"   Movie duration: {total_mins} minutes ({duration_ms} ms)")
                    print(f"   Progress: {progress:.1f}%")
            else:
                print(f"   ❌ No current position data")
        except Exception as e:
            print(f"   ❌ Plex error: {e}")
    else:
        print(f"\n❌ Plex not connected")
    
    print(f"\n👥 Active Watch Details:")
    
    for user_id, watch in badge_system.active_watches.items():
        print(f"\n📋 User ID: {user_id}")
        print(f"   Username: {watch.username}")
        print(f"   Movie: {watch.movie_title}")
        print(f"   Start time: {watch.start_time}")
        print(f"   Join position: {watch.join_position_ms} ms ({(watch.join_position_ms or 0) // (1000 * 60)} min)")
        
        # Calculate time since tracking started
        if watch.start_time.tzinfo is None:
            start_time = watch.start_time.replace(tzinfo=timezone.utc)
        else:
            start_time = watch.start_time
        time_since_start = datetime.now(timezone.utc) - start_time
        tracking_mins = int(time_since_start.total_seconds() / 60)
        
        print(f"   Tracking duration: {tracking_mins} minutes (time-based)")
        
        # Calculate actual watch time
        if current_position_ms and watch.join_position_ms is not None:
            content_watched_ms = max(0, current_position_ms - watch.join_position_ms)
            content_mins = content_watched_ms // (1000 * 60)
            print(f"   Content watched: {content_mins} minutes (position-based) ✅")
            print(f"   Calculation: {current_position_ms} - {watch.join_position_ms} = {content_watched_ms} ms")
        else:
            print(f"   Content watched: Unable to calculate (missing position data) ❌")
        
        # Show the issue
        if current_position_ms and watch.join_position_ms is not None:
            content_mins = (current_position_ms - watch.join_position_ms) // (1000 * 60)
            if content_mins != tracking_mins:
                print(f"   🚨 ISSUE: Time-based ({tracking_mins}m) != Position-based ({content_mins}m)")
                print(f"   🔧 FIX: Use position-based calculation for accuracy")

if __name__ == "__main__":
    asyncio.run(debug_active_watches())