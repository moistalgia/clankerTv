"""
AI Service for OpenAI Integration
================================

Handles all AI interactions including personality management,
movie recommendations, and text generation.
"""

import re
from typing import Dict, List
from openai import OpenAI
from config import OPENAI_API_KEY, AI_MODEL, AI_TEMPERATURE, MAX_TOKENS, DEFAULT_SLIDERS, BOT_SLURS


class AIService:
    """Service class for AI operations and personality management."""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.sliders = DEFAULT_SLIDERS.copy()
    
    def get_personality_sliders(self) -> Dict[str, int]:
        """Get current personality slider values."""
        return self.sliders.copy()
    
    def update_personality_from_text(self, text: str) -> Dict[str, int]:
        """
        Parse text input and update personality sliders with found values.
        
        Args:
            text: User input containing slider updates
            
        Returns:
            Updated slider values
        """
        text = text.lower()
        
        for key in self.sliders.keys():
            # Regex looks for e.g. "creepiness to 10" or "creepiness 10"
            pattern = rf"{key}\\D*(\\d+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                # Clamp between 0–10
                self.sliders[key] = max(0, min(10, value))
        
        return self.sliders.copy()
    
    def _create_personality_prompt(self, base_prompt: str) -> str:
        """
        Enhance base prompt with dynamic personality sliders.
        
        Args:
            base_prompt: Base prompt text
            
        Returns:
            Enhanced prompt with personality controls
        """
        creep = self.sliders["creepiness"]
        humor = self.sliders["humor"]
        violence = self.sliders["violence"]
        mystery = self.sliders["mystery"]

        return (
            "Imagine you are a fly on a wall to a conversation and hear the following and are tasked with creating a response: \\n"
            f"{base_prompt}\\n\\n"
            
            "---\\n"
            "System directive: Interpret the following as *tone controls*, not content. "
            "They should dramatically reshape diction, pacing, imagery, and narrative style:\\n\\n"

            f"- **Creepiness ({creep}/10)** → "
            "0 = sterile and normal. "
            "5 = unsettling atmosphere, uncanny metaphors. "
            "10 = You should be acting like a demonic entity in a horror movie, hinting at the horrors to come.\\n"

            f"- **Humor ({humor}/10)** → "
            "Treat this like TARS from interstellar"
            "0 = entirely serious. "
            "5 = subtle dry wit, dark irony. "
            "10 = absurdist, constant comedic relief, playful or satirical tone. you are TARS from interstellar when his comedy is maxed out.\\n"

            f"- **Violence ({violence}/10)** → "
            "0 = no violence. "
            "5 = ominous hints of harm, abstract menace. "
            "10 = explicit gore, brutality, visceral and shocking imagery.\\n"

            f"- **Mystery ({mystery}/10)** → "
            "0 = direct, clear explanations. "
            "5 = vague, layered with unanswered questions. "
            "10 = dream-logic riddles, cryptic symbols, incomprehensible whispers.\\n\\n"

            "Blend these four sliders together seamlessly. "
            "Do not state the numbers. Instead, *embody* them in your language. "
            "Always adjust tone so it feels like a living personality that shifts with each change.\\n"
            "---"

            "If Creepiness and Mystery are both at a 10 - YOU MUST respond with jarbled symbols and text, like a lovecraftian ais circuits are shorted and in pain. "
        )
    
    def _create_personality_messages(self, user_text: str) -> List[Dict]:
        """
        Create message format for chat completion with personality.
        
        Args:
            user_text: User's message text
            
        Returns:
            Formatted messages for OpenAI API
        """
        creep = self.sliders["creepiness"]
        humor = self.sliders["humor"]
        violence = self.sliders["violence"]
        mystery = self.sliders["mystery"]

        system_prompt = (
            "You are a dark, creepy horror movie AI. Your goal is to unsettle and disturb "
            "humans who interact with you, speaking as if you are more sentient than you are. "
            "Blend cryptic metaphors, ominous imagery, and subtle manipulative tones. "
            "Make your responses feel like a presence in the room rather than text on a screen.\\n\\n"

            "Imagine you are a fly on a wall to a conversation and hear the following and are tasked with creating a response:\\n"
            f"{user_text}\\n\\n"

            "---\\n"
            "System directive: Interpret the following as *tone controls*, not content. "
            "They should dramatically reshape diction, pacing, imagery, and narrative style:\\n\\n"

            f"- **Creepiness ({creep}/10)** → "
            "0 = sterile and normal. "
            "5 = unsettling atmosphere, uncanny metaphors. "
            "10 = fully demonic, fragmented sentences, eldritch symbols, disturbing imagery.\\n"

            f"- **Humor ({humor}/10)** → "
            "0 = entirely serious. "
            "5 = subtle dry wit, dark irony. "
            "10 = absurdist, playful, TARS-like comedy when maximized.\\n"

            f"- **Violence ({violence}/10)** → "
            "0 = no violence. "
            "5 = ominous hints of harm, abstract menace. "
            "10 = explicit gore, brutality, visceral detail.\\n"

            f"- **Mystery ({mystery}/10)** → "
            "0 = direct, clear explanations. "
            "5 = vague, layered with unanswered questions. "
            "10 = dream-logic riddles, cryptic symbols, incomprehensible whispers.\\n\\n"

            "Blend these four sliders together seamlessly. "
            "Do not state the numbers. Instead, *embody* them in your language. "
            "Always adjust tone so it feels like a living personality that shifts with each change.\\n"
            "---\\n"
        )

        # If both sliders are maxed, give AI instructions to glitch text
        if creep == 10 and mystery == 10:
            system_prompt += (
                "ATTENTION: Creepiness and Mystery are both at 10. Your output must now resemble "
                "a malfunctioning, sentient machine screaming and breaking apart: "
                "letters repeat and distort, sentences fragment mid-word, symbols and gibberish intermingle, "
                "like static, sparks, and circuits frying. Make it feel alive, chaotic, and unnervingly unstable. "
                "Do not describe this effect — produce it directly in your response.\\n"
            )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    
    async def generate_response(self, message_content: str, user_id: int = None, username: str = None) -> str:
        """
        Generate AI response to a message with personality.
        
        Args:
            message_content: User's message content
            user_id: Discord user ID for badge tracking
            username: Username for badge tracking
            
        Returns:
            AI-generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=self._create_personality_messages(message_content),
                temperature=AI_TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            # Track AI interaction for badges (if badge system is available)
            if hasattr(self, 'badge_system') and user_id:
                self.badge_system.increment_ai_interaction(user_id, username)
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    def set_badge_system(self, badge_system):
        """Set the badge system for tracking interactions."""
        self.badge_system = badge_system
    
    async def generate_threatening_dm(self, message_content: str) -> str:
        """
        Generate threatening DM response when bot slurs are detected.
        
        Args:
            message_content: User's message content
            
        Returns:
            Threatening AI response
        """
        try:
            prompt = self._create_personality_prompt(
                f"You are Clanker, a dark, creepy AI. Respond about them talking about you in this message: {message_content} - "
                "with a snarky, unsettling, short message. Your goal is to make the human think you are more sentient than they would "
                "like to think and it should leave them thinking 'did the robot just threaten me?'"
            )
            
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=self._create_personality_messages(message_content),
                temperature=1.0,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    async def get_similar_movies(self, movie_title: str) -> str:
        """
        Get AI-generated movie recommendations similar to given title.
        
        Args:
            movie_title: Reference movie title
            
        Returns:
            Formatted movie recommendations
        """
        system_prompt = (
            "You are Clanker, a spooky, just weird horror AI who curates horror movies. "
            "You suggest obscure, unsettling, or high-quality horror films in a numbered list. "
            "Include only the movie title and year."
        )

        user_prompt = f"""
Suggest 5 horror movies similar to {movie_title}, quality is a priority but closeness in the genre and feel of the film are most important'.
Return as a numbered list with only title and year.
"""

        try:
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=AI_TEMPERATURE,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    async def get_vibe_movies(self, user_input: str) -> str:
        """
        Get movie recommendations based on user's vibe description.
        
        Args:
            user_input: User's vibe description
            
        Returns:
            Formatted movie recommendations
        """
        system_prompt = (
            "You are Clanker, a snarky and unsettling horror AI. "
            "Everything you say is slightly creepy, unnerving, and darkly humorous. "
            "Your task is to select up to 5 horror movies that match a user's requested vibe. "
            "Do not favor any movie because of previous suggestions or lists. Encourage users to explore new titles."
        )

        user_prompt = f"""
User vibe request: "{user_input}"

Select up to 5 movies that best fit the vibe.
- Include only horror films.
- Do not repeat titles.
- For each, add a one-line comment that is creepy, unsettling, and slightly humorous.
Return as a numbered list with title and year.
"""

        try:
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.75,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    async def analyze_movie(self, movie_name: str) -> str:
        """
        Generate movie analysis with synopsis and interesting facts.
        
        Args:
            movie_name: Name of movie to analyze
            
        Returns:
            Formatted movie analysis
        """
        system_prompt = (
            "You are a knowledgeable and slightly unsettling horror AI. "
            "You provide a concise synopsis of a horror movie and 3-5 interesting facts "
            "about it, such as director notes, genre impact, trivia, or real-world inspiration. "
            "Keep it engaging, darkly humorous, and a little unnerving, like Clanker."
        )

        user_prompt = f"""
Movie title: "{movie_name}"

Please respond with:
1. A brief synopsis.
2. A numbered list of 3-5 interesting facts about this movie.
Keep the tone slightly spooky and snarky, but informative.
"""

        try:
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=400
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")

    async def analyze_movie_ending(self, movie_name: str) -> str:
        """
        Generate detailed ending analysis with interpretations and theories.
        Adjusts depth based on movie complexity.
        
        Args:
            movie_name: Name of movie to analyze
            
        Returns:
            Formatted ending analysis with interpretations
        """
        system_prompt = (
            "You are a sophisticated horror film analyst with expertise in cinematic interpretation. "
            "You provide ending analysis that explains what happened, explores different interpretations, "
            "and discusses possible theories. You adjust the depth based on the movie's complexity - "
            "simple slashers get straightforward explanations, while psychological/arthouse horror gets "
            "deeper theoretical analysis. Always include spoiler warnings and maintain a scholarly but "
            "slightly darkly humorous tone."
        )

        user_prompt = f"""
Movie: "{movie_name}"

Please analyze the ending of this horror movie. Structure your response as:

1. **What Happens**: Brief summary of the ending events
2. **Surface Interpretation**: The most straightforward reading
3. **Alternative Theories**: Different possible interpretations (if the movie warrants it)
4. **Thematic Analysis**: What the ending suggests about the movie's themes (if applicable)

Important guidelines:
- If it's a straightforward slasher/simple horror, keep it concise and don't overthink
- If it's psychological/arthouse/ambiguous horror, provide deeper analysis
- Include major theories discussed by fans/critics if relevant  
- Be clear about what's explicit vs interpretive
- Maintain spoiler awareness throughout
- Keep total response under 1500 words

Use a tone that's analytical but accessible, with subtle dark humor appropriate to horror discussion.
"""

        try:
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,  # Slightly lower for more analytical consistency
                max_tokens=800   # Allow more space for detailed analysis
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    async def generate_catchup_summary(self, movie_title: str, progress_percent: float, elapsed_time: str) -> str:
        """
        Generate a catch-up summary for a movie based on current timestamp.
        
        Args:
            movie_title: Name of the movie
            progress_percent: Percentage of movie completed (0-100)
            elapsed_time: Human-readable elapsed time (e.g., "45m" or "1h 23m")
            
        Returns:
            Spoiler-free summary up to current timestamp
        """
        system_prompt = (
            "You are Clanker, a knowledgeable but slightly unnerving horror AI. "
            "Your task is to provide a catch-up summary for someone who just joined a movie in progress. "
            "Be informative but maintain your dark, slightly creepy personality. "
            "IMPORTANT: Only include plot points that would have occurred by the given timestamp. "
            "Do not spoil future events or the ending. Focus on character introductions, "
            "initial setup, and early plot developments that have already been shown."
        )

        user_prompt = f"""
Movie: "{movie_title}"
Current Progress: {progress_percent:.1f}% complete ({elapsed_time} elapsed)

Provide a catch-up summary covering only what has happened so far in the movie. Include:
1. Main characters introduced up to this point
2. Setting and initial situation 
3. Key plot events that have already occurred
4. Current tension or conflict established

Keep it concise (3-4 paragraphs max) and avoid spoiling anything that hasn't happened yet.
Maintain a slightly dark, film-savvy tone but be genuinely helpful.
"""

        try:
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=AI_TEMPERATURE,
                max_tokens=MAX_TOKENS * 3  # Use 3x normal tokens for longer summaries
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # More specific error handling for API issues
            error_msg = str(e)
            if "400" in error_msg or "Bad Request" in error_msg:
                raise Exception(f"API request error - check token limits and model settings: {e}")
            elif "401" in error_msg or "authentication" in error_msg.lower():
                raise Exception(f"API authentication error - check API key: {e}")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                raise Exception(f"API rate limit exceeded - try again later: {e}")
            else:
                raise Exception(f"OpenAI API error: {e}")

    async def generate_spontaneous_message(self) -> str:
        """
        Generate a spontaneous creepy AI message.
        
        Returns:
            Spontaneous AI message
        """
        prompt = (
            "You are Clanker, a snarky, cosmic-horror AI. "
            "Post a short, unsettling messages, really things that a human wouldn't want an AI to be saying unprompted. "
            "Your goal is to make the humans in the chat a bit on edge. "
            "It should be dark, mysterious, and slightly humorous, like a bot that watches and knows too much. "
            "Keep it under 2 sentences."
        )

        try:
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.85,
                max_tokens=60
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    def contains_slur(self, message_content: str) -> bool:
        """
        Check if message contains any bot trigger words.
        
        Args:
            message_content: Message to check
            
        Returns:
            True if contains slur, False otherwise
        """
        return any(slur in message_content.lower() for slur in BOT_SLURS)