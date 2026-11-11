"""
HeyGen Avatar Video Integration
===============================

Generates AI avatar videos from text using HeyGen's API.

Usage:
    from integrations.heygen import HeyGenAvatar
    
    avatar = HeyGenAvatar(api_key="xxx")
    video_url = avatar.create_video("Hello, welcome to my channel!")
"""

import os
import time
import requests
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class AvatarInfo:
    """Information about an avatar"""
    avatar_id: str
    name: str
    gender: str
    preview_url: str


@dataclass
class VideoStatus:
    """Status of video generation"""
    video_id: str
    status: str  # pending, processing, completed, failed
    video_url: Optional[str] = None
    error: Optional[str] = None


class HeyGenAvatar:
    """
    Client for HeyGen avatar video generation API.
    
    HeyGen creates realistic AI avatar videos from text scripts.
    """
    
    BASE_URL = "https://api.heygen.com"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None
    ):
        """
        Initialize HeyGen client.
        
        Args:
            api_key: HeyGen API key. Falls back to HEYGEN_API_KEY env var.
            avatar_id: Default avatar ID. Falls back to HEYGEN_AVATAR_ID env var.
            voice_id: Default voice ID. Falls back to HEYGEN_VOICE_ID env var.
        """
        self.api_key = api_key or os.getenv("HEYGEN_API_KEY")
        self.avatar_id = avatar_id or os.getenv("HEYGEN_AVATAR_ID")
        self.voice_id = voice_id or os.getenv("HEYGEN_VOICE_ID")
        
        if not self.api_key:
            raise ValueError(
                "HeyGen API key required. Set HEYGEN_API_KEY env var "
                "or pass api_key parameter."
            )
    
    def _headers(self) -> dict:
        return {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def create_video(
        self,
        text: str,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None,
        background: str = "transparent",
        width: int = 1920,
        height: int = 1080,
        wait_for_completion: bool = True,
        timeout: int = 600
    ) -> str:
        """
        Create an avatar video from text.
        
        Args:
            text: The script for the avatar to speak
            avatar_id: Avatar to use (defaults to instance avatar_id)
            voice_id: Voice to use (defaults to instance voice_id or avatar's default)
            background: Background type - "transparent", "white", "green", or URL
            width: Video width in pixels
            height: Video height in pixels
            wait_for_completion: If True, wait until video is ready
            timeout: Max seconds to wait for completion
            
        Returns:
            URL to download the video (if wait_for_completion)
            or video_id (if not waiting)
        """
        
        avatar = avatar_id or self.avatar_id
        if not avatar:
            raise ValueError("No avatar_id provided. Set HEYGEN_AVATAR_ID or pass avatar_id.")
        
        # Build video input
        video_input = {
            "character": {
                "type": "avatar",
                "avatar_id": avatar,
                "avatar_style": "normal"
            },
            "voice": {
                "type": "text",
                "input_text": text
            }
        }
        
        # Add voice_id if specified
        voice = voice_id or self.voice_id
        if voice:
            video_input["voice"]["voice_id"] = voice
        
        # Set background
        if background == "transparent":
            video_input["background"] = {"type": "transparent"}
        elif background in ["white", "green"]:
            video_input["background"] = {"type": "color", "value": background}
        elif background.startswith("http"):
            video_input["background"] = {"type": "image", "value": background}
        else:
            video_input["background"] = {"type": "color", "value": background}
        
        payload = {
            "video_inputs": [video_input],
            "dimension": {
                "width": width,
                "height": height
            }
        }
        
        # Start video generation
        response = requests.post(
            f"{self.BASE_URL}/v2/video/generate",
            headers=self._headers(),
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"HeyGen API error: {response.status_code} - {response.text}")
        
        data = response.json()
        video_id = data["data"]["video_id"]
        
        if not wait_for_completion:
            return video_id
        
        # Poll for completion
        return self._wait_for_video(video_id, timeout)
    
    def _wait_for_video(self, video_id: str, timeout: int = 600) -> str:
        """Wait for video to complete and return the URL."""
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_video_status(video_id)
            
            if status.status == "completed":
                return status.video_url
            elif status.status == "failed":
                raise Exception(f"Video generation failed: {status.error}")
            
            # Wait before next poll
            time.sleep(10)
        
        raise TimeoutError(f"Video generation timed out after {timeout} seconds")
    
    def get_video_status(self, video_id: str) -> VideoStatus:
        """Check the status of a video generation job."""
        
        response = requests.get(
            f"{self.BASE_URL}/v1/video_status.get",
            headers=self._headers(),
            params={"video_id": video_id},
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"HeyGen API error: {response.status_code}")
        
        data = response.json()["data"]
        
        return VideoStatus(
            video_id=video_id,
            status=data["status"],
            video_url=data.get("video_url"),
            error=data.get("error")
        )
    
    def list_avatars(self) -> list[AvatarInfo]:
        """Get list of available avatars."""
        
        response = requests.get(
            f"{self.BASE_URL}/v2/avatars",
            headers=self._headers(),
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"HeyGen API error: {response.status_code}")
        
        avatars = []
        for a in response.json()["data"]["avatars"]:
            avatars.append(AvatarInfo(
                avatar_id=a["avatar_id"],
                name=a.get("avatar_name", "Unknown"),
                gender=a.get("gender", "unknown"),
                preview_url=a.get("preview_image_url", "")
            ))
        
        return avatars
    
    def list_voices(self) -> list[dict]:
        """Get list of available voices."""
        
        response = requests.get(
            f"{self.BASE_URL}/v2/voices",
            headers=self._headers(),
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"HeyGen API error: {response.status_code}")
        
        return response.json()["data"]["voices"]
    
    def download_video(self, video_url: str, output_path: Path) -> Path:
        """Download a completed video to local file."""
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        response = requests.get(video_url, stream=True, timeout=300)
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path
    
    def get_remaining_credits(self) -> dict:
        """Get remaining API credits."""
        
        response = requests.get(
            f"{self.BASE_URL}/v1/user/remaining_quota",
            headers=self._headers(),
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"HeyGen API error: {response.status_code}")
        
        return response.json()["data"]


# Convenience function
def create_avatar_video(text: str, output_path: str = None) -> str:
    """
    Simple function to create an avatar video.
    Requires HEYGEN_API_KEY and HEYGEN_AVATAR_ID env vars.
    
    Returns the video URL. If output_path is provided, downloads to that path.
    """
    avatar = HeyGenAvatar()
    video_url = avatar.create_video(text)
    
    if output_path:
        avatar.download_video(video_url, Path(output_path))
        return output_path
    
    return video_url


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  List avatars: python heygen.py avatars")
        print("  List voices: python heygen.py voices")
        print("  Create video: python heygen.py create 'Your script text'")
        print("  Check status: python heygen.py status <video_id>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        client = HeyGenAvatar()
        
        if command == "avatars":
            avatars = client.list_avatars()
            print(f"Available avatars ({len(avatars)}):\n")
            for a in avatars[:10]:  # Show first 10
                print(f"  {a.name}")
                print(f"    ID: {a.avatar_id}")
                print(f"    Gender: {a.gender}")
                print()
        
        elif command == "voices":
            voices = client.list_voices()
            print(f"Available voices ({len(voices)}):\n")
            for v in voices[:10]:
                print(f"  {v.get('name', 'Unknown')}")
                print(f"    ID: {v.get('voice_id')}")
                print(f"    Language: {v.get('language', 'unknown')}")
                print()
        
        elif command == "create" and len(sys.argv) >= 3:
            text = sys.argv[2]
            print("Creating avatar video...")
            print("(This may take 2-5 minutes)\n")
            video_url = client.create_video(text)
            print(f"✅ Video ready!")
            print(f"Download URL: {video_url}")
        
        elif command == "status" and len(sys.argv) >= 3:
            video_id = sys.argv[2]
            status = client.get_video_status(video_id)
            print(f"Video ID: {status.video_id}")
            print(f"Status: {status.status}")
            if status.video_url:
                print(f"URL: {status.video_url}")
            if status.error:
                print(f"Error: {status.error}")
        
        else:
            print("Invalid command. Use 'avatars', 'voices', 'create', or 'status'")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Set your API key: $env:HEYGEN_API_KEY = 'xxx'")
        print("Set avatar ID: $env:HEYGEN_AVATAR_ID = 'xxx'")
