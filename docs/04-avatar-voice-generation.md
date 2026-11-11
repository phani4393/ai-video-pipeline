# Stage 5: Synthetic Media Production (Avatar & Voice)

## Overview

This stage transforms scripts into synthetic video assets:
1. **Voice synthesis** - Convert script text to audio using neural voice cloning
2. **Avatar video** - Generate talking-head footage using AI avatars
3. **B-roll generation** - Create supporting visuals via text-to-video models
4. **Subtitles** - Generate time-aligned captions using Whisper

## Architecture

```
                     ┌─────────────────────────┐
                     │    SCRIPT (Stage 4)     │
                     └───────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   VOICE TRACK   │ │   AVATAR VIDEO  │ │    B-ROLL       │
    │   (ElevenLabs)  │ │   (HeyGen)      │ │   (Kling AI)    │
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   audio.mp3     │ │   avatar.mp4    │ │   broll_01.mp4  │
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 ▼
                     ┌─────────────────────────┐
                     │    WHISPER (Local)      │
                     │    Transcription        │
                     └───────────┬─────────────┘
                                 │
                                 ▼
                     ┌─────────────────────────┐
                     │    subtitles.srt        │
                     └─────────────────────────┘
```

## Component 1: Voice Synthesis

### Option A: ElevenLabs (Cloud - Production Quality)

```python
import requests
from pathlib import Path

class ElevenLabsVoice:
    def __init__(self, api_key: str, voice_id: str):
        self.api_key = api_key
        self.voice_id = voice_id
        self.base_url = "https://api.elevenlabs.io/v1"
        
    def generate_speech(
        self, 
        text: str, 
        output_path: Path,
        model: str = "eleven_multilingual_v2"
    ) -> Path:
        """Generate speech audio from text"""
        
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        with open(output_path, "wb") as f:
            f.write(response.content)
            
        return output_path
    
    def clone_voice(self, name: str, audio_files: list[Path]) -> str:
        """Create a cloned voice from sample audio files"""
        
        url = f"{self.base_url}/voices/add"
        
        headers = {"xi-api-key": self.api_key}
        
        files = [
            ("files", (f.name, open(f, "rb"), "audio/mpeg"))
            for f in audio_files
        ]
        
        data = {
            "name": name,
            "description": "Cloned voice for video content"
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        
        return response.json()["voice_id"]
```

### Option B: Kokoro TTS (Local - Free)

```python
# For draft iterations to save API costs
import torch
from kokoro import KokoroTTS

class LocalVoice:
    def __init__(self):
        self.model = KokoroTTS()
        
    def generate_speech(self, text: str, output_path: Path) -> Path:
        """Generate speech locally (free, no API costs)"""
        
        audio = self.model.synthesize(text)
        audio.save(output_path)
        
        return output_path
```

### Voice Generation Strategy

```python
def generate_voice_track(script: dict, is_final: bool = False) -> Path:
    """
    Hybrid strategy:
    - Draft iterations: Use local Kokoro TTS (free)
    - Final production: Use ElevenLabs (paid, higher quality)
    """
    
    text = extract_spoken_text(script)
    output_path = Path(f"output/{script['topic_id']}/voice.mp3")
    
    if is_final:
        # Production quality
        voice = ElevenLabsVoice(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id=os.getenv("ELEVENLABS_VOICE_ID")
        )
    else:
        # Draft quality (free)
        voice = LocalVoice()
    
    return voice.generate_speech(text, output_path)
```

## Component 2: Avatar Video Generation

### HeyGen Integration

```python
import requests
import time

class HeyGenAvatar:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.heygen.com/v2"
        
    def create_video(
        self,
        script_text: str,
        avatar_id: str,
        voice_id: str,
        background: str = "transparent"
    ) -> str:
        """Generate avatar video from script"""
        
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": script_text,
                    "voice_id": voice_id
                },
                "background": {
                    "type": background
                }
            }],
            "dimension": {
                "width": 1920,
                "height": 1080
            }
        }
        
        # Start generation
        response = requests.post(
            f"{self.base_url}/video/generate",
            headers=headers,
            json=payload
        )
        
        video_id = response.json()["data"]["video_id"]
        
        # Poll for completion
        return self._wait_for_video(video_id)
    
    def _wait_for_video(self, video_id: str, timeout: int = 600) -> str:
        """Poll until video is ready"""
        
        headers = {"X-Api-Key": self.api_key}
        
        for _ in range(timeout // 10):
            response = requests.get(
                f"{self.base_url}/video/{video_id}",
                headers=headers
            )
            
            status = response.json()["data"]["status"]
            
            if status == "completed":
                return response.json()["data"]["video_url"]
            elif status == "failed":
                raise Exception("Video generation failed")
            
            time.sleep(10)
        
        raise TimeoutError("Video generation timed out")
```

### Alternative: Hedra (Free Tier)

```python
class HedraAvatar:
    """Free alternative for avatar generation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hedra.com/v1"
        
    def create_video(
        self,
        image_path: Path,  # Single photo input
        audio_path: Path,  # Pre-generated voice
        emotion: str = "neutral"
    ) -> str:
        """Generate talking avatar from photo + audio"""
        
        # Upload image and audio
        # Generate video
        # Return URL
        pass
```

## Component 3: B-Roll Generation

### Text-to-Video Prompts

```python
BROLL_PROMPT_TEMPLATE = """
Generate a {duration}-second cinematic B-roll clip:

SCENE: {description}
CAMERA: {camera_movement}
STYLE: Clean, modern tech aesthetic
LIGHTING: Soft, professional studio lighting
COLOR: Slightly desaturated with teal/orange grade

Technical specs:
- 4K resolution (3840x2160)
- 24fps
- No text overlays
- Seamless loop preferred
"""

# Camera movement options
CAMERA_MOVEMENTS = [
    "Static wide shot",
    "Slow dolly forward",
    "Gentle crane down",
    "Smooth orbit right",
    "Push in on subject",
    "Pull back reveal"
]
```

### Kling AI / Seedance Integration

```python
class BRollGenerator:
    def __init__(self, api_key: str, provider: str = "kling"):
        self.api_key = api_key
        self.provider = provider
        
    def generate_clip(
        self,
        description: str,
        duration: int = 5,
        camera: str = "static"
    ) -> str:
        """Generate B-roll clip from text description"""
        
        prompt = BROLL_PROMPT_TEMPLATE.format(
            duration=duration,
            description=description,
            camera_movement=camera
        )
        
        if self.provider == "kling":
            return self._generate_kling(prompt)
        elif self.provider == "seedance":
            return self._generate_seedance(prompt)
    
    def generate_from_script(self, script: dict) -> list[Path]:
        """Extract all B-roll sections and generate clips"""
        
        broll_sections = [
            s for s in script["sections"] 
            if s["type"] == "B-ROLL"
        ]
        
        clips = []
        for section in broll_sections:
            clip_url = self.generate_clip(
                description=section["description"],
                duration=section.get("duration_seconds", 5)
            )
            clips.append(self._download_clip(clip_url))
        
        return clips
```

## Component 4: Subtitle Generation (Whisper)

### Local Whisper Setup

```python
import whisper
from pathlib import Path

class SubtitleGenerator:
    def __init__(self, model_size: str = "base"):
        """
        Model sizes: tiny, base, small, medium, large
        Larger = more accurate but slower
        """
        self.model = whisper.load_model(model_size)
        
    def generate_srt(self, audio_path: Path, output_path: Path) -> Path:
        """Generate SRT subtitle file from audio"""
        
        result = self.model.transcribe(
            str(audio_path),
            task="transcribe",
            language="en",
            word_timestamps=True
        )
        
        srt_content = self._format_srt(result["segments"])
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        return output_path
    
    def _format_srt(self, segments: list) -> str:
        """Convert Whisper segments to SRT format"""
        
        srt_lines = []
        
        for i, segment in enumerate(segments, 1):
            start = self._format_timestamp(segment["start"])
            end = self._format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(text)
            srt_lines.append("")
        
        return "\n".join(srt_lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format"""
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
```

### Word-Level Captions for TikTok/Reels Style

```python
def generate_word_level_captions(audio_path: Path) -> list[dict]:
    """Generate word-by-word timestamps for animated captions"""
    
    model = whisper.load_model("base")
    
    result = model.transcribe(
        str(audio_path),
        word_timestamps=True
    )
    
    words = []
    for segment in result["segments"]:
        for word_info in segment.get("words", []):
            words.append({
                "word": word_info["word"],
                "start": word_info["start"],
                "end": word_info["end"],
                "confidence": word_info.get("probability", 1.0)
            })
    
    return words
```

## Cost Summary

| Component | Free Option | Paid Option | Cost/Video |
|-----------|-------------|-------------|------------|
| Voice | Kokoro TTS (local) | ElevenLabs | $0.30-1.00 |
| Avatar | Hedra free tier | HeyGen | $1-3 |
| B-Roll | Stock footage | Kling AI | $0.50-2.00 |
| Subtitles | Whisper (local) | - | $0 |
| **Total** | **~$0** | **~$3-6** | - |

## Output Assets

After Stage 5, the following files are ready for assembly:

```
output/{topic_id}/
├── voice.mp3           # Full voice track
├── avatar.mp4          # Talking head video (transparent BG)
├── broll/
│   ├── clip_001.mp4    # B-roll clips
│   ├── clip_002.mp4
│   └── clip_003.mp4
├── subtitles.srt       # Time-aligned captions
├── subtitles_words.json # Word-level timestamps
└── manifest.json       # Assembly instructions
```
