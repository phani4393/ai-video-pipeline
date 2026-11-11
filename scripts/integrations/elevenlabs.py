"""
ElevenLabs Voice Synthesis Integration
======================================

Generates natural speech audio from text using ElevenLabs' neural voice models.

Usage:
    from integrations.elevenlabs import ElevenLabsVoice
    
    voice = ElevenLabsVoice(api_key="xxx", voice_id="xxx")
    voice.generate_speech("Hello world", Path("output.mp3"))
"""

import os
import requests
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class VoiceInfo:
    """Information about a voice"""
    voice_id: str
    name: str
    category: str
    labels: dict


class ElevenLabsVoice:
    """
    Client for ElevenLabs text-to-speech API.
    
    ElevenLabs provides high-quality neural voice synthesis with
    voice cloning capabilities.
    """
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    # Available models
    MODELS = {
        "multilingual_v2": "eleven_multilingual_v2",  # Best quality, 29 languages
        "turbo_v2": "eleven_turbo_v2",  # Fastest, English only
        "monolingual": "eleven_monolingual_v1"  # Legacy
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None
    ):
        """
        Initialize ElevenLabs client.
        
        Args:
            api_key: ElevenLabs API key. Falls back to ELEVENLABS_API_KEY env var.
            voice_id: Default voice ID. Falls back to ELEVENLABS_VOICE_ID env var.
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID")
        
        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key required. Set ELEVENLABS_API_KEY env var "
                "or pass api_key parameter."
            )
    
    def generate_speech(
        self,
        text: str,
        output_path: Path,
        voice_id: Optional[str] = None,
        model: str = "multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.5
    ) -> Path:
        """
        Generate speech audio from text.
        
        Args:
            text: The text to convert to speech
            output_path: Where to save the MP3 file
            voice_id: Voice to use (defaults to instance voice_id)
            model: Model to use - "multilingual_v2", "turbo_v2", or "monolingual"
            stability: Voice stability (0-1). Higher = more consistent
            similarity_boost: Voice clarity (0-1). Higher = clearer
            style: Style exaggeration (0-1). Higher = more expressive
            
        Returns:
            Path to the generated audio file
        """
        
        voice = voice_id or self.voice_id
        if not voice:
            raise ValueError("No voice_id provided. Set ELEVENLABS_VOICE_ID or pass voice_id.")
        
        url = f"{self.BASE_URL}/text-to-speech/{voice}"
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": self.MODELS.get(model, model),
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=300  # Long timeout for large texts
        )
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
        
        # Ensure directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save audio
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path
    
    def generate_speech_streaming(
        self,
        text: str,
        output_path: Path,
        voice_id: Optional[str] = None,
        model: str = "turbo_v2"
    ) -> Path:
        """
        Generate speech with streaming (faster for long texts).
        """
        
        voice = voice_id or self.voice_id
        if not voice:
            raise ValueError("No voice_id provided.")
        
        url = f"{self.BASE_URL}/text-to-speech/{voice}/stream"
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": self.MODELS.get(model, model),
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with requests.post(url, headers=headers, json=payload, stream=True) as response:
            if response.status_code != 200:
                raise Exception(f"ElevenLabs API error: {response.status_code}")
            
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        
        return output_path
    
    def list_voices(self) -> list[VoiceInfo]:
        """Get list of available voices."""
        
        url = f"{self.BASE_URL}/voices"
        headers = {"xi-api-key": self.api_key}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code}")
        
        voices = []
        for v in response.json()["voices"]:
            voices.append(VoiceInfo(
                voice_id=v["voice_id"],
                name=v["name"],
                category=v.get("category", "unknown"),
                labels=v.get("labels", {})
            ))
        
        return voices
    
    def clone_voice(
        self,
        name: str,
        audio_files: list[Path],
        description: str = ""
    ) -> str:
        """
        Create a cloned voice from audio samples.
        
        Args:
            name: Name for the cloned voice
            audio_files: List of audio file paths (MP3, WAV, etc.)
            description: Optional description
            
        Returns:
            The new voice_id
        """
        
        url = f"{self.BASE_URL}/voices/add"
        headers = {"xi-api-key": self.api_key}
        
        files = []
        for f in audio_files:
            files.append(("files", (f.name, open(f, "rb"), "audio/mpeg")))
        
        data = {
            "name": name,
            "description": description or f"Cloned voice: {name}"
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        
        # Close file handles
        for _, (_, handle, _) in files:
            handle.close()
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
        
        return response.json()["voice_id"]
    
    def get_usage(self) -> dict:
        """Get current API usage and limits."""
        
        url = f"{self.BASE_URL}/user/subscription"
        headers = {"xi-api-key": self.api_key}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code}")
        
        data = response.json()
        return {
            "character_count": data.get("character_count", 0),
            "character_limit": data.get("character_limit", 0),
            "remaining": data.get("character_limit", 0) - data.get("character_count", 0)
        }


# Convenience function
def text_to_speech(text: str, output_path: str) -> Path:
    """
    Simple function to generate speech.
    Requires ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID env vars.
    """
    voice = ElevenLabsVoice()
    return voice.generate_speech(text, Path(output_path))


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  List voices: python elevenlabs.py voices")
        print("  Generate: python elevenlabs.py speak 'Your text here' output.mp3")
        print("  Usage stats: python elevenlabs.py usage")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        voice = ElevenLabsVoice()
        
        if command == "voices":
            voices = voice.list_voices()
            print(f"Available voices ({len(voices)}):\n")
            for v in voices:
                print(f"  {v.name}")
                print(f"    ID: {v.voice_id}")
                print(f"    Category: {v.category}")
                print()
        
        elif command == "speak" and len(sys.argv) >= 4:
            text = sys.argv[2]
            output = sys.argv[3]
            print(f"Generating speech...")
            result = voice.generate_speech(text, Path(output))
            print(f"✅ Saved to: {result}")
        
        elif command == "usage":
            usage = voice.get_usage()
            print(f"Character usage: {usage['character_count']:,} / {usage['character_limit']:,}")
            print(f"Remaining: {usage['remaining']:,}")
        
        else:
            print("Invalid command. Use 'voices', 'speak', or 'usage'")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Set your API key: $env:ELEVENLABS_API_KEY = 'xxx'")
        print("Set voice ID: $env:ELEVENLABS_VOICE_ID = 'xxx'")
