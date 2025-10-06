#!/usr/bin/env python3
"""
Horror Bingo Demo
================

Demonstration script showing how the Horror Bingo system works.
This script simulates the bingo card generation and interaction.
"""

import asyncio
import json
from datetime import datetime

# Mock AI Service for demonstration
class MockAIService:
    async def get_completion(self, prompt, max_tokens=800):
        """Mock AI response for horror tropes."""
        # Simulate realistic horror tropes for different movie types
        if "Scream" in prompt or "slasher" in prompt.lower():
            return """1. Phone rings ominously
2. Killer calls victim
3. Door left open
4. False scare with cat
5. Garage door malfunctions
6. Someone says "Hello?"
7. Killer in backseat
8. Character trips while running
9. Weapon thrown away
10. Group decides to split up
11. Car won't start
12. Cell phone no signal
13. Power goes out
14. Investigates noise alone
15. Mask revealed dramatically
16. Final girl emerges
17. Killer presumed dead
18. Last minute jump scare
19. Mirror reflection scare
20. Closet door creaks
21. Blood on bathroom mirror
22. Stairs creak loudly
23. Breathing behind victim
24. Door slams shut
25. Killer not really dead"""

        elif "Halloween" in prompt or "Michael Myers" in prompt:
            return """1. Heavy breathing sounds
2. Shape in background
3. Babysitter alone
4. Knife disappears
5. Phone line cut
6. Closet door opens
7. Body discovered
8. Dog barks at nothing
9. TV static interference
10. Car keys missing
11. Front door left open
12. Porch light flickers
13. Someone watches from window
14. Laundry blows ominously
15. Shed door bangs
16. Footsteps on roof
17. Kitchen knife missing
18. Radio plays alone
19. Rocking chair moves
20. Sheet ghost fake-out
21. Mask in mirror
22. Doorbell rings repeatedly
23. Hand grabs from darkness
24. Killer vanishes
25. Final confrontation"""

        else:
            # Generic horror tropes
            return """1. Jump scare
2. Creaking floorboards
3. Power goes out
4. Cell phone no signal
5. Character investigates alone
6. Ominous mirror reflection
7. Door slams shut
8. Flickering lights
9. Scream in distance
10. Car won't start
11. Basement explored
12. Attic sounds
13. Someone says "Hello?"
14. Music stops suddenly
15. Footsteps overhead
16. Window breaks
17. Blood appears
18. Clock strikes midnight
19. Animal acts strange
20. Phone rings ominously
21. Shadow moves
22. Knocking sounds
23. Voice whispers
24. Something under bed
25. Final girl emerges"""


async def demo_horror_bingo():
    """Demonstrate the Horror Bingo system."""
    print("🎃 Horror Bingo System Demo")
    print("=" * 50)
    
    # Import the horror bingo system
    import sys
    sys.path.append('.')
    from models.horror_bingo import HorrorBingoSystem, BingoCard
    
    # Create mock services
    ai_service = MockAIService()
    horror_bingo = HorrorBingoSystem(ai_service)
    
    print("\n📋 Creating bingo card for 'Scream' (1996)...")
    
    # Create a bingo card
    card = await horror_bingo.create_bingo_card(
        user_id=12345,
        movie_title="Scream",
        movie_genre="slasher"
    )
    
    print(f"✅ Card created for user {card.user_id}")
    print(f"🎬 Movie: {card.movie_title}")
    print(f"📅 Created: {card.created_at}")
    
    # Display the tropes in a grid
    print("\n🎰 Bingo Card Layout:")
    print("+" + "-" * 23 + "+" + "-" * 23 + "+" + "-" * 23 + "+" + "-" * 23 + "+" + "-" * 23 + "+")
    
    for row in range(5):
        row_text = "|"
        for col in range(5):
            index = row * 5 + col
            trope = card.tropes[index][:21]  # Truncate for display
            if len(card.tropes[index]) > 21:
                trope += ".."
            row_text += f" {trope:<21} |"
        print(row_text)
        print("+" + "-" * 23 + "+" + "-" * 23 + "+" + "-" * 23 + "+" + "-" * 23 + "+" + "-" * 23 + "+")
    
    # Simulate marking some squares
    print("\n🎯 Simulating user interactions...")
    
    # Mark a few squares to demonstrate
    marked_squares = [0, 1, 2, 3, 4]  # Top row
    for square in marked_squares:
        card.mark_square(square)
        print(f"   ✅ Marked square {square + 1}: '{card.tropes[square]}'")
    
    # Check for bingo
    new_lines = card.get_new_lines()
    if new_lines:
        print(f"\n🎉 BINGO! Completed lines: {new_lines}")
    else:
        print(f"\n📊 Progress: {sum(card.marked)}/25 squares marked, no bingo yet")
    
    # Show visual representation
    print("\n📱 Discord Visual Representation:")
    grid_text = ""
    for row in range(5):
        row_text = ""
        for col in range(5):
            index = row * 5 + col
            mark = "✅" if card.marked[index] else "⬜"
            row_text += mark
        grid_text += row_text + "\n"
    
    print(grid_text)
    
    # Show completion stats
    total_marked = sum(card.marked)
    completion_percent = (total_marked / 25) * 100
    print(f"📊 Completion: {total_marked}/25 ({completion_percent:.0f}%)")
    
    if card.completed_lines:
        print(f"🏆 Completed lines: {', '.join(card.completed_lines)}")
    
    # Demonstrate badge system integration
    print(f"\n🏆 Badge System Integration:")
    print(f"   - First bingo would award 'Horror Bingo Master' badge")
    print(f"   - Badge is only awarded once per user")
    print(f"   - Progress is automatically saved to JSON files")
    
    # Show data persistence
    print(f"\n💾 Data Persistence:")
    print(f"   - Cards saved to: {horror_bingo.data_file}")
    print(f"   - Automatic save after each interaction")
    print(f"   - Cards persist across bot restarts")
    
    print(f"\n🎮 Discord Commands Available:")
    print(f"   !bingo                 - Create card for current movie")
    print(f"   !bingo <movie>         - Create card for specific movie")
    print(f"   !mybingo              - Show current card") 
    print(f"   !clearbingo           - Clear current card")
    print(f"   !bingostats           - Show system statistics")
    
    print(f"\n✨ Features:")
    print(f"   📱 Interactive Discord UI with 25 buttons")
    print(f"   🤖 AI-generated movie-specific tropes")
    print(f"   🎯 Real-time bingo detection") 
    print(f"   🏆 Badge system integration")
    print(f"   💾 Persistent progress storage")
    print(f"   👥 Multi-user support")
    
    print(f"\n🎃 Horror Bingo Demo Complete!")


if __name__ == "__main__":
    asyncio.run(demo_horror_bingo())