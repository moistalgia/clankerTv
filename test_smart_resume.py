#!/usr/bin/env python3
"""
Test Smart Watch Resume Functionality
====================================

Tests the smart resume logic for watch sessions to ensure users can
leave/rejoin voice channels without creating duplicate entries.
"""

import os
import sys
import json
import tempfile
import unittest.mock
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.badge_system import WatchBadgeSystem, MovieWatch

class TestSmartResume:
    """Test suite for smart watch session resume functionality."""
    
    def __init__(self):
        self.temp_dir = None
        self.badge_system = None
    
    def setup_test_environment(self):
        """Set up a temporary test environment."""
        print("🔧 Setting up test environment...")
        
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Override data directory for testing
        original_data_dir = None
        
        # Create badge system with temporary directory
        self.badge_system = WatchBadgeSystem()
        self.badge_system.data_dir = Path(self.temp_dir)
        
        # Initialize empty data
        self.badge_system.user_stats = {}
        self.badge_system.user_badges = {}
        self.badge_system.watch_history = []
        self.badge_system.active_watches = {}
        self.badge_system.movie_ratings = {}
        
        print(f"✅ Test environment created at: {self.temp_dir}")
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        import shutil
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)
            print("🧹 Test environment cleaned up")
    
    def test_scenario_1_quick_rejoin(self):
        """Test Scenario 1: User leaves and rejoins quickly (should resume)."""
        print("\n📋 Test Scenario 1: Quick Leave/Rejoin (Should Resume)")
        
        user_id = 12345
        username = "testuser"
        movie_title = "The Shining"
        movie_duration_ms = 146 * 60 * 1000  # 146 minutes
        
        # Initial join
        print("1️⃣ User starts watching...")
        self.badge_system.start_watching(
            user_id=user_id,
            username=username,
            movie_title=movie_title,
            genres=["Horror", "Drama"],
            year=1980,
            director="Stanley Kubrick",
            movie_duration_ms=movie_duration_ms,
            join_position_ms=0
        )
        
        # Simulate some watching time (update progress)
        print("2️⃣ Simulating 30 minutes of watching...")
        self.badge_system.update_watch_progress(
            user_id=user_id,
            duration_minutes=30,
            completion_percentage=20.5
        )
        
        # User leaves (simulate finish_watching but without completion)
        print("3️⃣ User leaves voice channel...")
        self.badge_system.finish_watching(user_id=user_id, completion_percentage=20.5)
        
        # Check watch history count
        initial_count = len(self.badge_system.watch_history)
        print(f"   Watch history entries: {initial_count}")
        
        # User rejoins quickly (5 minutes later)
        print("4️⃣ User rejoins 5 minutes later...")
        
        # Simulate current time being 5 minutes later
        import unittest.mock
        fake_time = datetime.now() + timedelta(minutes=5)
        
        with unittest.mock.patch('models.badge_system.datetime') as mock_datetime:
            mock_datetime.now.return_value = fake_time
            
            self.badge_system.start_watching(
                user_id=user_id,
                username=username,
                movie_title=movie_title,
                genres=["Horror", "Drama"],
                year=1980,
                director="Stanley Kubrick",
                movie_duration_ms=movie_duration_ms,
                join_position_ms=30 * 60 * 1000  # 30 minutes in
            )
        
        # Check results
        final_count = len(self.badge_system.watch_history)
        
        print(f"   📊 Results:")
        print(f"   • Initial entries: {initial_count}")
        print(f"   • Final entries: {final_count}")
        print(f"   • Should resume: {final_count == initial_count}")
        
        # Verify the session was resumed
        if final_count == initial_count:
            print("   ✅ SUCCESS: Session was resumed (no duplicate entry)")
            return True
        else:
            print("   ❌ FAILED: New entry created instead of resuming")
            return False
    
    def test_scenario_2_long_break(self):
        """Test Scenario 2: User rejoins after movie window expires (should create new)."""
        print("\n📋 Test Scenario 2: Long Break (Should Create New)")
        
        user_id = 12346
        username = "testuser2"
        movie_title = "Halloween"
        movie_duration_ms = 91 * 60 * 1000  # 91 minutes
        
        # Initial join
        print("1️⃣ User starts watching...")
        self.badge_system.start_watching(
            user_id=user_id,
            username=username,
            movie_title=movie_title,
            genres=["Horror"],
            year=1978,
            director="John Carpenter",
            movie_duration_ms=movie_duration_ms,
            join_position_ms=0
        )
        
        # Simulate some watching
        print("2️⃣ Simulating 20 minutes of watching...")
        self.badge_system.update_watch_progress(
            user_id=user_id,
            duration_minutes=20,
            completion_percentage=22.0
        )
        
        # User leaves
        print("3️⃣ User leaves voice channel...")
        self.badge_system.finish_watching(user_id=user_id, completion_percentage=22.0)
        
        initial_count = len(self.badge_system.watch_history)
        print(f"   Watch history entries: {initial_count}")
        
        # User rejoins after 3 hours (outside movie + buffer window)
        print("4️⃣ User rejoins 3 hours later...")
        
        fake_time = datetime.now() + timedelta(hours=3)
        
        with unittest.mock.patch('models.badge_system.datetime') as mock_datetime:
            mock_datetime.now.return_value = fake_time
            
            self.badge_system.start_watching(
                user_id=user_id,
                username=username,
                movie_title=movie_title,
                genres=["Horror"],
                year=1978,
                director="John Carpenter",
                movie_duration_ms=movie_duration_ms,
                join_position_ms=0  # Starting from beginning
            )
        
        final_count = len(self.badge_system.watch_history)
        
        print(f"   📊 Results:")
        print(f"   • Initial entries: {initial_count}")
        print(f"   • Final entries: {final_count}")
        print(f"   • Should create new: {final_count == initial_count + 1}")
        
        if final_count == initial_count + 1:
            print("   ✅ SUCCESS: New session created (outside time window)")
            return True
        else:
            print("   ❌ FAILED: Should have created new entry but didn't")
            return False
    
    def test_scenario_3_unknown_movie_duration(self):
        """Test Scenario 3: Unknown movie duration uses default 150m window."""
        print("\n📋 Test Scenario 3: Unknown Movie Duration (150m Default)")
        
        user_id = 12347
        username = "testuser3"
        movie_title = "Unknown Horror Movie"
        
        # Initial join (no movie_duration_ms provided)
        print("1️⃣ User starts watching unknown movie...")
        self.badge_system.start_watching(
            user_id=user_id,
            username=username,
            movie_title=movie_title,
            genres=["Horror"],
            year=2023,
            director="Unknown Director",
            movie_duration_ms=None,  # Unknown duration
            join_position_ms=0
        )
        
        # Simulate watching
        print("2️⃣ Simulating 45 minutes of watching...")
        self.badge_system.update_watch_progress(
            user_id=user_id,
            duration_minutes=45,
            completion_percentage=30.0
        )
        
        # User leaves
        print("3️⃣ User leaves voice channel...")
        self.badge_system.finish_watching(user_id=user_id, completion_percentage=30.0)
        
        initial_count = len(self.badge_system.watch_history)
        
        # User rejoins within 150m window (2 hours later)
        print("4️⃣ User rejoins 2 hours later (within 150m default window)...")
        
        fake_time = datetime.now() + timedelta(hours=2)
        
        with unittest.mock.patch('models.badge_system.datetime') as mock_datetime:
            mock_datetime.now.return_value = fake_time
            
            self.badge_system.start_watching(
                user_id=user_id,
                username=username,
                movie_title=movie_title,
                genres=["Horror"],
                year=2023,
                director="Unknown Director",
                movie_duration_ms=None,
                join_position_ms=45 * 60 * 1000
            )
        
        final_count = len(self.badge_system.watch_history)
        
        print(f"   📊 Results:")
        print(f"   • Initial entries: {initial_count}")
        print(f"   • Final entries: {final_count}")
        print(f"   • Should resume (2h < 150m): {final_count == initial_count}")
        
        if final_count == initial_count:
            print("   ✅ SUCCESS: Session resumed within default 150m window")
            return True
        else:
            print("   ❌ FAILED: Should have resumed but created new entry")
            return False
    
    def test_scenario_4_multiple_users_same_movie(self):
        """Test Scenario 4: Multiple users watching same movie (independent tracking)."""
        print("\n📋 Test Scenario 4: Multiple Users Same Movie (Independent)")
        
        movie_title = "The Conjuring"
        movie_duration_ms = 112 * 60 * 1000  # 112 minutes
        
        users = [
            (12348, "user_alice"),
            (12349, "user_bob"), 
            (12350, "user_charlie")
        ]
        
        # All users start watching
        print("1️⃣ All users start watching...")
        for user_id, username in users:
            self.badge_system.start_watching(
                user_id=user_id,
                username=username,
                movie_title=movie_title,
                genres=["Horror", "Thriller"],
                year=2013,
                director="James Wan",
                movie_duration_ms=movie_duration_ms,
                join_position_ms=0
            )
        
        initial_count = len(self.badge_system.watch_history)
        print(f"   Watch history entries: {initial_count}")
        
        # Alice leaves and rejoins (should resume)
        print("2️⃣ Alice leaves and rejoins quickly...")
        self.badge_system.finish_watching(user_id=12348)
        
        fake_time = datetime.now() + timedelta(minutes=5)
        with unittest.mock.patch('models.badge_system.datetime') as mock_datetime:
            mock_datetime.now.return_value = fake_time
            
            self.badge_system.start_watching(
                user_id=12348,
                username="user_alice",
                movie_title=movie_title,
                genres=["Horror", "Thriller"],
                year=2013,
                director="James Wan",
                movie_duration_ms=movie_duration_ms,
                join_position_ms=20 * 60 * 1000
            )
        
        final_count = len(self.badge_system.watch_history)
        
        print(f"   📊 Results:")
        print(f"   • Initial entries: {initial_count} (3 users)")
        print(f"   • Final entries: {final_count}")
        print(f"   • Alice's resume successful: {final_count == initial_count}")
        
        # Verify other users unaffected
        bob_entries = [w for w in self.badge_system.watch_history if w.user_id == 12349]
        charlie_entries = [w for w in self.badge_system.watch_history if w.user_id == 12350]
        
        print(f"   • Bob still has 1 entry: {len(bob_entries) == 1}")
        print(f"   • Charlie still has 1 entry: {len(charlie_entries) == 1}")
        
        success = (final_count == initial_count and 
                  len(bob_entries) == 1 and 
                  len(charlie_entries) == 1)
        
        if success:
            print("   ✅ SUCCESS: Independent user tracking works correctly")
            return True
        else:
            print("   ❌ FAILED: User tracking interference detected")
            return False
    
    def run_all_tests(self):
        """Run all test scenarios."""
        print("🧪 Starting Smart Resume Functionality Tests")
        print("=" * 60)
        
        self.setup_test_environment()
        
        results = []
        
        try:
            results.append(("Quick Rejoin", self.test_scenario_1_quick_rejoin()))
            results.append(("Long Break", self.test_scenario_2_long_break()))
            results.append(("Unknown Duration", self.test_scenario_3_unknown_movie_duration()))
            results.append(("Multiple Users", self.test_scenario_4_multiple_users_same_movie()))
            
        except Exception as e:
            print(f"\n❌ Test execution failed: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            self.cleanup_test_environment()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Smart resume functionality is working correctly.")
        else:
            print("⚠️  Some tests failed. Review the logic and fix issues.")
        
        return passed == total

if __name__ == "__main__":
    test_suite = TestSmartResume()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ Ready for production use!")
        sys.exit(0)
    else:
        print("\n❌ Fix issues before deploying.")
        sys.exit(1)