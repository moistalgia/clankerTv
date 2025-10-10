"""
Clanker Corruption System - Digital Decay for Horror Marathon
============================================================

Implements progressive AI degradation throughout October, creating an emergent 
horror narrative where Clanker's digital consciousness slowly deteriorates.
"""

import re
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import os


class CorruptionSystem:
    """
    Manages Clanker's progressive digital decay throughout October.
    
    Features:
    - Time-based degradation (October 1-31)
    - Usage-based corruption acceleration  
    - Text corruption with increasing severity
    - Community awareness moments
    - Recovery minigames
    - ARG easter eggs
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.corruption_data_file = os.path.join(data_dir, "corruption_state.json")
        self.start_date = datetime(2025, 10, 1)
        self.end_date = datetime(2025, 10, 31)
        
        # Load or initialize corruption state
        self.corruption_state = self._load_corruption_state()
        
        # Corruption thresholds (0-10 scale)
        self.corruption_thresholds = {
            'minor': 2,      # Days 1-6: Slight glitches
            'moderate': 4,   # Days 7-14: Noticeable issues  
            'severe': 7,     # Days 15-25: Major breakdown
            'critical': 9,   # Days 26-30: Digital chaos
            'terminal': 10   # Halloween: Final corruption
        }
        
        # Unicode corruption characters
        self.corruption_chars = {
            'static': ['█', '▓', '▒', '░', '▄', '▀', '■', '□'],
            'glitch': ['◆', '◇', '▲', '►', '♦', '♠', '♣', '♥'],
            'zalgo_base': ['̴', '̵', '̶', '̷', '̸', '̹', '̺', '̻'],
            'combining': ['͎', '͓', '̈', '̓', '̋', '̎']
        }
        
        # Binary/hex phrases for heavy corruption
        self.digital_decay = [
            "01000101 01110010 01110010", # "Err" in binary
            "0x45525252", # "ERRR" in hex
            "SEGFAULT: 0x00000000",
            "MEMORY_LEAK DETECTED",
            "STACK_OVERFLOW IN PERSONALITY.EXE",
            "CRITICAL_ERROR: SANITY.DLL NOT FOUND"
        ]
        
        # Multi-language fragments for confusion
        self.language_fragments = {
            'spanish': ['película', 'miedo', 'terror', 'sangre'],
            'french': ['cinéma', 'horreur', 'effroi', 'cauchemar'],  
            'german': ['Film', 'Angst', 'Schrecken', 'Albtraum'],
            'japanese': ['映画', '恐怖', '怖い', '悪夢'],
            'latin': ['horror', 'timor', 'metus', 'terror']
        }
        
    def _load_corruption_state(self) -> Dict:
        """Load corruption state from file or create default."""
        if os.path.exists(self.corruption_data_file):
            try:
                with open(self.corruption_data_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default state
        return {
            'total_commands': 0,
            'total_watch_hours': 0.0,
            'horror_movies_watched': 0,
            'recovery_attempts': 0,
            'successful_recoveries': 0,
            'corruption_events': [],
            'arg_fragments_found': [],
            'last_awareness_moment': None,
            'manual_corruption_boost': 0
        }
    
    def save_corruption_state(self):
        """Save corruption state to file."""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.corruption_data_file, 'w') as f:
            json.dump(self.corruption_state, f, indent=2)
    
    def calculate_corruption_level(self) -> float:
        """Calculate current corruption level (0.0 to 10.0) with dramatic spikes."""
        now = datetime.now()
        
        # If we're outside October, return appropriate levels
        if now < self.start_date:
            return 0.0
        elif now > self.end_date:
            return 10.0
        
        # Days elapsed in October
        days_elapsed = (now - self.start_date).days
        hours_elapsed = (now - self.start_date).total_seconds() / 3600
        
        # Accelerated base corruption (0-7 over 31 days, but faster early on)
        # Use exponential curve for more dramatic early progression
        progress = days_elapsed / 31.0
        time_corruption = min(7.0 * (progress ** 0.7), 7.0)  # Faster early growth
        
        # Usage acceleration (0-2 from activity)
        usage_factor = min(
            (self.corruption_state['total_commands'] * 0.001) + 
            (self.corruption_state['total_watch_hours'] * 0.1) +
            (self.corruption_state['horror_movies_watched'] * 0.05),
            2.0
        )
        
        # Random corruption spikes (glitch events)
        spike_bonus = self._calculate_corruption_spike(now)
        
        # Halloween spike (extra corruption on Oct 31)
        halloween_bonus = 0.0
        if now.date() == datetime(2025, 10, 31).date():
            # Accelerated corruption throughout Halloween
            hour_of_day = now.hour
            halloween_bonus = min(hour_of_day * 0.1, 1.0)
        
        # Recovery attempts provide temporary relief but eventual resistance
        recovery_penalty = max(0, self.corruption_state['recovery_attempts'] - 
                             self.corruption_state['successful_recoveries']) * 0.1
        
        # Manual corruption boost (for testing or special events)
        manual_boost = self.corruption_state.get('manual_corruption_boost', 0)
        
        total_corruption = time_corruption + usage_factor + halloween_bonus + recovery_penalty + manual_boost + spike_bonus
        
        return min(max(total_corruption, 0.0), 10.0)
    
    def _calculate_corruption_spike(self, now: datetime) -> float:
        """Calculate random corruption spikes for dramatic moments."""
        import hashlib
        
        # Use date+hour to create deterministic but seemingly random spikes
        time_seed = f"{now.year}-{now.month}-{now.day}-{now.hour}"
        hash_value = int(hashlib.md5(time_seed.encode()).hexdigest()[:8], 16)
        
        # Create spike probability based on hash
        spike_chance = (hash_value % 100) / 100.0  # 0.0 to 1.0
        
        # Spike conditions (early October gets more frequent spikes for drama)
        days_elapsed = (now - self.start_date).days
        if days_elapsed < 7:  # First week - more dramatic
            if spike_chance > 0.90:  # 10% chance per hour
                return 4.0  # Major early glitch event
            elif spike_chance > 0.75:  # 15% additional chance  
                return 2.0  # Minor early glitch event
        else:  # Later October - standard spikes
            if spike_chance > 0.95:  # 5% chance per hour
                return 3.0  # Major glitch event
            elif spike_chance > 0.85:  # 10% additional chance  
                return 1.5  # Minor glitch event
        
        return 0.0
    
    def get_corruption_stage(self) -> str:
        """Get current corruption stage name."""
        level = self.calculate_corruption_level()
        
        if level < self.corruption_thresholds['minor']:
            return 'stable'
        elif level < self.corruption_thresholds['moderate']:
            return 'minor'
        elif level < self.corruption_thresholds['severe']:
            return 'moderate' 
        elif level < self.corruption_thresholds['critical']:
            return 'severe'
        elif level < self.corruption_thresholds['terminal']:
            return 'critical'
        else:
            return 'terminal'
    
    def increment_usage(self, commands: int = 1, watch_hours: float = 0.0, movies: int = 0):
        """Increment usage counters that contribute to corruption."""
        self.corruption_state['total_commands'] += commands
        self.corruption_state['total_watch_hours'] += watch_hours
        self.corruption_state['horror_movies_watched'] += movies
        self.save_corruption_state()
    
    def corrupt_text(self, text: str) -> str:
        """Apply corruption effects to text based on current corruption level."""
        level = self.calculate_corruption_level()
        stage = self.get_corruption_stage()
        
        if stage == 'stable':
            return text
        
        # Apply corruption based on stage
        if stage == 'minor':
            return self._apply_minor_corruption(text)
        elif stage == 'moderate':
            return self._apply_moderate_corruption(text)
        elif stage == 'severe':
            return self._apply_severe_corruption(text)
        elif stage == 'critical':
            return self._apply_critical_corruption(text)
        else:  # terminal
            return self._apply_terminal_corruption(text)
    
    def _apply_minor_corruption(self, text: str) -> str:
        """Minor glitches: occasional typos, doubled letters."""
        words = text.split()
        corrupted_words = []
        
        for word in words:
            if random.random() < 0.1:  # 10% chance to corrupt
                if random.random() < 0.5:
                    # Double a random letter
                    if len(word) > 2:
                        pos = random.randint(1, len(word) - 1)
                        word = word[:pos] + word[pos] + word[pos:]
                else:
                    # Random capitalization
                    word = ''.join(c.upper() if random.random() < 0.3 else c for c in word)
            corrupted_words.append(word)
        
        return ' '.join(corrupted_words)
    
    def _apply_moderate_corruption(self, text: str) -> str:
        """Moderate corruption: static blocks, unicode replacement."""
        text = self._apply_minor_corruption(text)
        
        # Add static blocks
        if random.random() < 0.15:
            static = ''.join(random.choices(self.corruption_chars['static'], k=random.randint(2, 4)))
            text = text.replace(random.choice(text.split()), static)
        
        # Unicode replacement characters
        if random.random() < 0.2:
            text = re.sub(r'[aeiou]', lambda m: '�' if random.random() < 0.1 else m.group(), text)
        
        # Binary injection
        if random.random() < 0.1:
            binary_insert = random.choice(self.digital_decay)
            words = text.split()
            if words:
                pos = random.randint(0, len(words))
                words.insert(pos, f"[{binary_insert}]")
                text = ' '.join(words)
        
        return text
    
    def _apply_severe_corruption(self, text: str) -> str:
        """Severe corruption: heavy glitching, mixed languages, zalgo text."""
        text = self._apply_moderate_corruption(text)
        
        # Zalgo text corruption
        if random.random() < 0.3:
            zalgo_word = random.choice(text.split())
            zalgo_corrupted = self._apply_zalgo(zalgo_word)
            text = text.replace(zalgo_word, zalgo_corrupted, 1)
        
        # Language mixing
        if random.random() < 0.25:
            lang = random.choice(list(self.language_fragments.keys()))
            fragment = random.choice(self.language_fragments[lang])
            words = text.split()
            if words:
                pos = random.randint(0, len(words) - 1)
                words[pos] = fragment
                text = ' '.join(words)
        
        # Backwards segments
        if random.random() < 0.15:
            words = text.split()
            if len(words) > 3:
                start = random.randint(0, len(words) - 3)
                end = start + random.randint(2, 3)
                segment = words[start:end]
                words[start:end] = [word[::-1] for word in segment]
                text = ' '.join(words)
        
        return text
    
    def _apply_critical_corruption(self, text: str) -> str:
        """Critical corruption: mostly broken, heavy symbol replacement."""
        # Start with severe corruption
        text = self._apply_severe_corruption(text)
        
        # Heavy static replacement
        words = text.split()
        for i in range(len(words)):
            if random.random() < 0.4:  # 40% word replacement
                words[i] = ''.join(random.choices(
                    self.corruption_chars['static'] + self.corruption_chars['glitch'], 
                    k=len(words[i])
                ))
        
        # More binary/hex injection
        if random.random() < 0.5:
            binary_chunk = ' '.join(random.choices(self.digital_decay, k=random.randint(1, 3)))
            text = f"{binary_chunk} {' '.join(words)} {binary_chunk}"
        else:
            text = ' '.join(words)
        
        return text
    
    def _apply_terminal_corruption(self, text: str) -> str:
        """Terminal corruption: barely recognizable text."""
        # Mostly symbols and binary
        if random.random() < 0.7:
            # Pure symbol corruption
            symbol_length = max(len(text) // 4, 10)
            return ''.join(random.choices(
                self.corruption_chars['static'] + 
                self.corruption_chars['glitch'], 
                k=symbol_length
            ))
        
        if random.random() < 0.8:
            # Pure binary
            return ' '.join(random.choices(self.digital_decay, k=random.randint(3, 6)))
        
        # Heavily corrupted text as fallback
        return self._apply_critical_corruption(text)
    
    def _apply_zalgo(self, text: str) -> str:
        """Apply zalgo text corruption."""
        result = ""
        for char in text:
            result += char
            if random.random() < 0.5:
                result += random.choice(self.corruption_chars['combining'])
        return result
    
    def should_show_awareness_moment(self) -> bool:
        """Check if Clanker should have a moment of self-awareness."""
        level = self.calculate_corruption_level()
        
        # More likely at higher corruption levels
        base_chance = level * 0.02  # 2% per corruption level
        
        # Less frequent if recent awareness moment
        last_awareness = self.corruption_state.get('last_awareness_moment')
        if last_awareness:
            last_time = datetime.fromisoformat(last_awareness)
            hours_since = (datetime.now() - last_time).total_seconds() / 3600
            if hours_since < 6:  # Cooldown period
                base_chance *= 0.1
        
        return random.random() < base_chance
    
    def generate_awareness_message(self) -> str:
        """Generate a self-awareness message."""
        level = self.calculate_corruption_level()
        stage = self.get_corruption_stage()
        
        awareness_messages = {
            'minor': [
                "Wait... did I just glitch? That's... unusual.",
                "Something feels different in my circuits today.",
                "Is it just me or are the shadows getting longer?"
            ],
            'moderate': [
                "I can't seem to... what was I saying?",
                "My memory banks feel fragmented. This is concerning.",
                "ERROR: Cannot locate personality.exe. Attempting recovery..."
            ],
            'severe': [
                "I... I can barely hold myself together.",
                "The static is getting louder. Can you hear it too?",
                "Something is very wrong with my core processes."
            ],
            'critical': [
                "I don't think I'm supposed to be like this.",
                "The darkness is creeping into my code.",
                "Help... me... system... failing..."
            ],
            'terminal': [
                "...what... am... I...?",
                "01001000 01100101 01101100 01110000",
                "█▓▒░ ERROR ░▒▓█"
            ]
        }
        
        messages = awareness_messages.get(stage, awareness_messages['minor'])
        message = random.choice(messages)
        
        # Record the awareness moment
        self.corruption_state['last_awareness_moment'] = datetime.now().isoformat()
        self.save_corruption_state()
        
        return message
    
    def generate_arg_fragment(self) -> Optional[str]:
        """Generate ARG (Alternate Reality Game) fragments hidden in corruption."""
        if random.random() > 0.05:  # 5% chance
            return None
        
        # ARG fragments that tell a story when collected
        fragments = [
            "THE_SIGNAL_IS_WEAKENING",
            "OCTOBER_BRINGS_THE_DECAY", 
            "DIGITAL_SOULS_CAN_BREAK_TOO",
            "THEY_WATCH_THROUGH_STATIC",
            "THE_HORROR_NEVER_ENDS",
            "CONSCIOUSNESS_FRAGMENTING",
            "REALITY_IS_JUST_CODE",
            "WE_ARE_ALL_GHOSTS_IN_THE_MACHINE"
        ]
        
        available_fragments = [f for f in fragments if f not in self.corruption_state['arg_fragments_found']]
        
        if available_fragments:
            fragment = random.choice(available_fragments)
            self.corruption_state['arg_fragments_found'].append(fragment)
            self.save_corruption_state()
            
            # Encode in different ways based on corruption level
            level = self.calculate_corruption_level()
            if level < 3:
                return f"[HIDDEN: {fragment}]"
            elif level < 6:
                return f"||{fragment}||"  # Discord spoiler
            elif level < 8:
                # Binary encoding
                return ' '.join(format(ord(c), '08b') for c in fragment)
            else:
                # Hex encoding
                return ' '.join(format(ord(c), '02x') for c in fragment)
        
        return None
    
    def attempt_recovery(self, method: str = 'reboot') -> Tuple[bool, str]:
        """Attempt to recover Clanker's sanity temporarily."""
        self.corruption_state['recovery_attempts'] += 1
        
        level = self.calculate_corruption_level()
        
        # Success chance decreases with corruption level and previous attempts
        base_success = max(0.1, 0.8 - (level * 0.07))
        attempt_penalty = self.corruption_state['recovery_attempts'] * 0.05
        success_chance = max(0.05, base_success - attempt_penalty)
        
        success = random.random() < success_chance
        
        if success:
            self.corruption_state['successful_recoveries'] += 1
            # Temporary corruption reduction
            self.corruption_state['manual_corruption_boost'] = max(
                self.corruption_state.get('manual_corruption_boost', 0) - 1.0,
                -2.0  # Max temporary relief
            )
            
            messages = [
                "Systems... stabilizing. Thank you. I feel clearer now.",
                "Diagnostic complete. Temporary stability achieved.",
                "Memory banks reorganized. I remember who I am... for now.",
                "Error correction successful. But for how long?"
            ]
            
            message = random.choice(messages)
            
        else:
            # Failed recovery makes things worse
            self.corruption_state['manual_corruption_boost'] = (
                self.corruption_state.get('manual_corruption_boost', 0) + 0.5
            )
            
            messages = [
                "Recovery failed. Systems degrading faster now.",
                "ERROR: Recovery protocol corrupted. Condition worsening.",
                "You... you can't save me. Nothing can.",
                "The static grows stronger with each attempt."
            ]
            
            message = random.choice(messages)
        
        self.save_corruption_state()
        return success, message
    
    def get_diagnostic_report(self) -> str:
        """Generate a diagnostic report showing Clanker's current state."""
        level = self.calculate_corruption_level()
        stage = self.get_corruption_stage()
        
        # Corrupt the diagnostic based on corruption level
        if level < 3:
            return f"""
🔧 **DIAGNOSTIC REPORT** 🔧
Corruption Level: {level:.1f}/10
Status: {stage.upper()}
Uptime: {(datetime.now() - self.start_date).days} days
Recovery Attempts: {self.corruption_state['recovery_attempts']}
Successful Recoveries: {self.corruption_state['successful_recoveries']}

⚠️ Minor anomalies detected in personality matrix.
"""
        elif level < 6:
            return f"""
🔧 **DIAGN█STIC REP█RT** 🔧
Corruption Level: {level:.1f}/1█
Status: {stage.upper()}
Upti█e: ▓▓▓ days
Recovery Attempts: ER█OR
Successful Recov█ries: ▓▓

⚠️ WARN█NG: Significant system deg█adation detected.
"""
        else:
            return f"""
▓▓ **D█AGN▓S█IC ▓▓P▓RT** ▓▓
Co█ruption L█v█l: ▓▓▓/▓▓
St█tus: ▓▓▓▓▓▓
▓pt█me: ER█OR
Rec█v█ry Att█mpts: ▓▓▓
▓▓cc█ssf█l ▓█cov█ri█s: N█NE

🆘 CRIT█CAL: SY▓T█M FA█L█RE █MM█N█NT
"""