#!/usr/bin/env python3
"""
Ending Analysis Demo
===================

Demonstration script showing how the ending analysis command works.
Shows examples of how it adapts to different types of horror movies.
"""

import asyncio

# Mock AI Service for demonstration
class MockAIService:
    async def analyze_movie_ending(self, movie_name: str):
        """Mock AI responses for different types of horror movies."""
        
        # Simple slasher - straightforward analysis
        if movie_name.lower() in ["friday the 13th", "halloween", "scream"]:
            return """**What Happens**: The killer is defeated/unmasked, the final girl survives, but there's a last-second scare suggesting the threat isn't truly gone.

**Surface Interpretation**: Classic slasher formula - evil is temporarily defeated but never truly dies, setting up sequels and maintaining the genre's cyclical nature.

**Alternative Theories**: The "final scare" represents trauma's lasting impact - even when the immediate threat ends, psychological wounds remain.

**Thematic Analysis**: Reinforces slasher themes about survival, resilience, and the persistent nature of evil. The ending suggests that while individuals can overcome specific threats, the broader cultural anxieties these killers represent never fully disappear."""

        # Psychological/complex horror - deeper analysis  
        elif movie_name.lower() in ["hereditary", "the witch", "midsommar", "the lighthouse"]:
            return """**What Happens**: Reality breaks down completely as supernatural/psychological forces consume the protagonist(s), often ending in death, transformation, or complete mental collapse.

**Surface Interpretation**: The supernatural forces win - family curses, cults, or isolated madness prove inescapable.

**Alternative Theories**: 
• **Psychological Reading**: Everything supernatural is mental illness/trauma manifesting as horror
• **Generational Trauma Theory**: The ending represents inherited psychological damage finally consuming the family line
• **Grief Allegory**: The horror elements symbolize the stages and ultimate acceptance of loss

**Thematic Analysis**: These endings explore how we process uncontrollable forces - death, family dysfunction, isolation. The horror isn't just scary monsters, but the terrifying realization that some problems have no solutions, some pain has no healing. The protagonist's destruction represents our worst fears about helplessness and the fragility of sanity/society."""

        # Ambiguous/arthouse horror - very deep analysis
        elif movie_name.lower() in ["the babadook", "it follows", "under the skin", "annihilation"]:
            return """**What Happens**: The ending deliberately resists clear interpretation, mixing reality with metaphor, leaving key questions unanswered.

**Surface Interpretation**: The immediate threat is contained but not eliminated - suggesting ongoing struggle rather than resolution.

**Alternative Theories**:
• **Metaphor Theory**: The monster represents depression/grief/trauma that must be managed, not cured
• **Cycles Theory**: The ending suggests these forces are part of natural/psychological cycles that repeat
• **Transformation Theory**: The protagonist doesn't defeat the threat but learns to coexist with it, representing personal growth

**Thematic Analysis**: These endings reject traditional horror catharsis, instead exploring how we live with ongoing challenges. They suggest that true horror isn't monsters we can kill, but persistent aspects of human existence - mental illness, mortality, alienation - that we must learn to navigate rather than overcome. The ambiguity forces viewers to confront their own interpretations and anxieties."""

        # Generic/unknown movie - balanced analysis
        else:
            return f"""**What Happens**: [Based on {movie_name}] The climax resolves the central threat through [typical horror resolution].

**Surface Interpretation**: The horror follows genre conventions with [defeat of antagonist/survival of protagonist/twist revelation].

**Alternative Theories**: Different viewers might interpret the ending as [psychological vs supernatural/metaphorical vs literal/hopeful vs pessimistic].

**Thematic Analysis**: The ending likely explores common horror themes such as [good vs evil/survival/human nature/social fears]. The resolution suggests [thematic message based on genre expectations].

*Note: This analysis is generalized - specific details would depend on the actual film's content and directorial intent.*"""


def parse_analysis_sections(analysis: str) -> dict:
    """Parse analysis into structured sections for spoiler formatting."""
    sections = {}
    current_section = "📖 Analysis"
    current_content = ""
    
    lines = analysis.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header (starts with **)
        if line.startswith('**') and line.endswith('**') and len(line) > 4:
            # Save previous section if it has content
            if current_content.strip():
                sections[current_section] = current_content.strip()
            
            # Start new section
            section_title = line.strip('*').strip()
            
            # Add appropriate emojis for common sections
            if "what happens" in section_title.lower():
                current_section = "📝 What Happens"
            elif "surface" in section_title.lower() or "interpretation" in section_title.lower():
                current_section = "🎯 Surface Interpretation"  
            elif "alternative" in section_title.lower() or "theories" in section_title.lower():
                current_section = "🤔 Alternative Theories"
            elif "thematic" in section_title.lower() or "analysis" in section_title.lower():
                current_section = "📚 Thematic Analysis"
            else:
                current_section = f"📖 {section_title}"
            
            current_content = ""
        else:
            current_content += line + "\n"
    
    # Add the final section
    if current_content.strip():
        sections[current_section] = current_content.strip()
    
    # If no structured sections found, use the entire content
    if not sections:
        sections["📖 Analysis"] = analysis
    
    return sections


async def demo_ending_analysis():
    """Demonstrate the ending analysis system with different movie types."""
    print("🎭 Ending Analysis System Demo")
    print("=" * 50)
    
    ai_service = MockAIService()
    
    movies_to_demo = [
        ("Scream", "Simple Slasher"),
        ("Hereditary", "Psychological Horror"), 
        ("The Babadook", "Metaphorical Horror"),
        ("Unknown Movie", "Generic Analysis")
    ]
    
    for movie, category in movies_to_demo:
        print(f"\n🎬 **{movie}** ({category})")
        print("-" * 40)
        
        analysis = await ai_service.analyze_movie_ending(movie)
        
        # Format like Discord embed with spoiler tags would look
        print("⚠️ **SPOILER WARNING** - Click the spoiler tags below to reveal each section")
        print()
        
        # Parse into sections and show with spoiler formatting
        sections = parse_analysis_sections(analysis)
        
        for section_name, content in sections.items():
            print(f"{section_name}")
            # Show how spoiler tags would appear (simulated) - truncate for demo
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"||{preview}||")
            print()
        
        print("💡 Click spoiler tags to reveal • Discuss different interpretations with fellow watchers!")
        print("=" * 70)


def show_command_examples():
    """Show how the Discord command would be used."""
    print("\n🤖 Discord Command Usage")
    print("=" * 50)
    
    examples = [
        "!endinganalysis",
        "!endinganalysis Hereditary", 
        "!endinganalysis The Thing",
        "!endinganalysis Friday the 13th"
    ]
    
    for example in examples:
        print(f"💬 {example}")
        if example == "!endinganalysis":
            print("   → Analyzes currently playing movie")
        else:
            movie = example.split(" ", 1)[1]
            print(f"   → Analyzes ending of '{movie}'")
    
    print(f"\n✨ Features:")
    print(f"   🎯 Adapts depth to movie complexity")
    print(f"   📚 Multiple interpretation theories") 
    print(f"   ⚠️ Spoiler tag protection - click to reveal")
    print(f"   🎨 Structured sections with emojis")
    print(f"   🤖 AI-powered analysis")
    print(f"   📱 Works with current or specified movies")
    print(f"   🔒 Safe for mixed spoiler audiences")


def show_analysis_structure():
    """Show the analysis structure."""
    print(f"\n📋 Analysis Structure")
    print("=" * 50)
    
    structure = [
        ("📝 What Happens", "Brief summary of ending events"),
        ("🎯 Surface Interpretation", "Most straightforward reading"),
        ("🤔 Alternative Theories", "Different possible interpretations"),
        ("📚 Thematic Analysis", "What ending suggests about themes")
    ]
    
    for section, description in structure:
        print(f"{section}")
        print(f"   {description}")
        print(f"   Format: ||spoiler content|| - click to reveal")
    
    print(f"\n🔒 Spoiler Protection System:")
    print(f"   📱 Each section hidden behind spoiler tags")
    print(f"   🎯 Progressive disclosure - reveal what you want")
    print(f"   👥 Safe for mixed spoiler tolerance groups")
    print(f"   ⚠️ Clear warnings before any content")
    
    print(f"\n🎚️ Adaptive Depth:")
    print(f"   📺 Simple Slasher → Concise, straightforward")
    print(f"   🧠 Psychological → Multiple theories, deeper analysis") 
    print(f"   🎨 Arthouse → Complex interpretations, thematic exploration")
    print(f"   ❓ Unknown → Balanced, general approach")


async def main():
    """Run the ending analysis demo."""
    print("🎭 ClankerTV Ending Analysis Feature")
    print("=" * 50)
    
    await demo_ending_analysis()
    show_command_examples()
    show_analysis_structure()
    
    print(f"\n🎊 Key Benefits:")
    print(f"   💭 Enhances post-movie discussions") 
    print(f"   🔍 Reveals hidden meanings and themes")
    print(f"   📖 Educational for film analysis")
    print(f"   🎯 Respects movie complexity levels")
    print(f"   ⚡ Quick access during or after viewing")
    print(f"   🤝 Sparks group conversations")
    print(f"   🔒 Spoiler-safe for mixed audiences")
    print(f"   📱 Progressive disclosure - reveal what you want")
    
    print(f"\n🎃 Ending Analysis Demo Complete!")


if __name__ == "__main__":
    asyncio.run(main())