# Corruption Events Audio System

## Overview
The corruption events system includes dormant audio functionality that can enhance corruption manifestations with atmospheric sounds and effects.

## Current Status
🔇 **DORMANT** - Audio system is disabled by default (`audio_enabled = False`)

## Setup Requirements

### 1. Install FFmpeg
**Windows:**
```bash
# Download FFmpeg from https://ffmpeg.org/download.html
# Add FFmpeg to your system PATH
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS with Homebrew
brew install ffmpeg
```

### 2. Install Voice Dependencies
```bash
pip install PyNaCl
pip install discord.py[voice]
```

### 3. Create Audio Directory
```
clankerTV/
└── sounds/
    ├── static_brief.mp3
    ├── mechanical_click.mp3
    ├── electrical_hum.mp3
    ├── glitch_sequence.mp3
    ├── data_corruption.mp3
    ├── system_warning.mp3
    ├── cascade_failure.mp3
    ├── reality_distortion.mp3
    ├── dimensional_tear.mp3
    ├── void_whispers.mp3
    ├── demonic_chanting.mp3
    ├── entity_emergence.mp3
    ├── pentagram_ritual.mp3
    └── system_possession.mp3
```

## Audio File Categories

### Minor Events (1-3 corruption level)
- `static_brief.mp3` - Brief static burst
- `mechanical_click.mp3` - Mechanical clicking sounds
- `electrical_hum.mp3` - Low electrical humming

### Moderate Events (3-6 corruption level)
- `glitch_sequence.mp3` - Digital glitch sounds
- `data_corruption.mp3` - Data corruption noises
- `system_warning.mp3` - System alert tones

### Severe Events (6-8 corruption level)
- `cascade_failure.mp3` - System cascade failure sounds
- `reality_distortion.mp3` - Reality warping effects
- `dimensional_tear.mp3` - Dimensional breach audio

### Critical Events (8+ corruption level)
- `void_whispers.mp3` - Whispers from the void
- `demonic_chanting.mp3` - Demonic ritual chanting
- `entity_emergence.mp3` - Entity manifestation sounds
- `pentagram_ritual.mp3` - Pentagram summoning audio
- `system_possession.mp3` - System takeover effects

## Commands

### Enable/Disable Audio
```
!toggle_audio
```
- Toggles the audio system on/off
- Shows current status and warnings

### Test Audio System
```
!test_audio [filename]
```
- Tests audio playback
- Joins voice channel and plays test sound
- Use `!test_audio static_brief` to test specific file

## How It Works

1. **Voice Channel Detection**: Bot finds voice channels with users
2. **Permission Check**: Verifies bot can connect and speak
3. **Audio Selection**: Chooses appropriate audio for corruption event
4. **Playback**: Joins voice, plays audio, then disconnects
5. **Cleanup**: Automatically disconnects after 10 seconds

## Integration Points

Audio triggers are integrated into all corruption event types:
- `_minor_event()` → Minor audio effects
- `_moderate_event()` → Moderate audio effects  
- `_severe_event()` → Severe audio effects
- `_critical_event()` → Critical audio effects

## File Requirements

- **Format**: MP3 (recommended)
- **Duration**: 2-15 seconds for effects, up to 30 seconds for ambient
- **Quality**: 128kbps minimum, 320kbps recommended
- **Volume**: Normalized to prevent ear damage

## Activation Steps

1. Install FFmpeg and voice dependencies
2. Create `sounds/` directory
3. Add audio files with exact names listed above
4. Set `self.audio_enabled = True` in `corruption_events.py`
5. Use `!toggle_audio` to enable in Discord

## Notes

- Audio only plays if users are in voice channels
- Bot automatically disconnects after playing
- Audio files are optional - missing files won't cause errors
- System degrades gracefully if voice permissions are missing