#!/usr/bin/env python3
"""
Manual Recovery - Start Tracking Current Watchers
===============================================

Manually trigger the startup detection logic to catch current watchers.
"""

import asyncio
from datetime import datetime
from services.plex_service import PlexService
from models.movie_state import MovieState

async def manual_startup_recovery():
    """Manually run startup detection logic for current session."""
    
    print("🚑 Manual Startup Recovery")
    print("=" * 30)
    
    # Initialize services
    plex_service = PlexService()
    movie_state = MovieState()
    
    if not plex_service.is_connected():
        print("❌ Plex not connected - cannot recover")
        return
    
    try:
        # Check for active Plex sessions
        sessions = plex_service.get_current_sessions()
        if not sessions:
            print("📺 No active Plex sessions found")
            return
        
        # Find movie sessions
        movie_sessions = [s for s in sessions if s.type == "movie"]
        if not movie_sessions:
            print("🎬 No movie sessions found")
            return
        
        # Get the first movie session
        current_movie_session = movie_sessions[0]
        movie_title = current_movie_session.title
        
        print(f"🎬 Found active movie: {movie_title}")
        print(f"📊 Progress: {((current_movie_session.viewOffset or 0) / (current_movie_session.duration or 1)) * 100:.1f}%")
        
        # Set current movie in state
        movie_state.set_current_movie(movie_title)
        
        # Get enhanced session info for position tracking
        session_info = await plex_service.get_enhanced_session_info()
        
        # Since this is a manual recovery, we'll simulate adding users
        # In real usage, you'd need to specify the actual Discord user IDs
        print("\n👥 Starting Manual Tracking...")
        print("⚠️  Note: This is a simulation - actual user IDs needed for real recovery")
        
        # Example user IDs (replace with actual Discord user IDs of people in voice channel)
        current_watchers = [
            {"id": 99507990859616256, "name": "moisty"},  # Replace with actual user if in channel
            {"id": 153232848407494656, "name": "choppascray"}  # Replace with actual user if in channel
        ]
        
        print("📝 To manually add real watchers, you need their Discord user IDs")
        print("   You can get these by:")
        print("   1. Right-click user in Discord → Copy User ID (developer mode required)")
        print("   2. Or use the bot's voice event logs to find IDs")
        
        for watcher in current_watchers:
            try:
                # Get movie metadata
                movie_info = await plex_service.get_movie_metadata(movie_title)
                genres = movie_info.get('genres', ['Horror']) if movie_info else ['Horror']
                year = movie_info.get('year') if movie_info else None
                director = movie_info.get('director') if movie_info else None
                
                # Get position data for accurate tracking
                movie_duration_ms = session_info.get('duration_ms') if session_info else None
                join_position_ms = session_info.get('current_position_ms') if session_info else None
                
                # Start tracking with enhanced position data
                movie_state.badge_system.start_watching(
                    user_id=watcher["id"],
                    username=watcher["name"],
                    movie_title=movie_title,
                    genres=genres,
                    year=year,
                    director=director,
                    movie_duration_ms=movie_duration_ms,
                    join_position_ms=join_position_ms
                )
                
                print(f"✅ Started tracking: {watcher['name']} (ID: {watcher['id']})")
                print(f"   🎬 Movie: {movie_title}")
                print(f"   📍 Join Position: {(join_position_ms or 0) // (1000 * 60)} minutes")
                
            except Exception as e:
                print(f"❌ Failed to start tracking for {watcher['name']}: {e}")
        
        print(f"\n📊 Recovery Status:")
        print(f"   Active sessions: {len(movie_state.badge_system.active_watches)}")
        print(f"   Current movie: {movie_state.current_movie}")
        
        if movie_state.badge_system.active_watches:
            print("\n✅ Manual recovery successful!")
            print("   Users are now being tracked")
            print("   When movie ends or users leave, completion will be calculated")
            print("   Try !moviestats command again - should now show data")
        else:
            print("\n❌ No users added to tracking")
            print("   Need to specify actual Discord user IDs of people in voice channel")
            
    except Exception as e:
        print(f"❌ Recovery failed: {e}")
        
    print(f"\n💡 For Future Prevention:")
    print("   1. Check bot startup logs for startup detection errors")
    print("   2. Ensure users are in voice channel before bot starts")
    print("   3. Add startup detection debugging/logging")
    print("   4. Consider adding manual !starttracking command")

if __name__ == "__main__":
    asyncio.run(manual_startup_recovery())