# Stage 6: Headless Video Assembly & Publishing

## Overview

This stage combines all generated assets (avatar video, voice, B-roll, subtitles) into a final, publish-ready video using programmatic tools instead of traditional editing software like Premiere Pro.

## Assembly Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VIDEO ASSEMBLY PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  INPUTS                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ Avatar   │ │  Voice   │ │  B-Roll  │ │Subtitles │ │  Brand   │     │
│  │  .mp4    │ │  .mp3    │ │  clips   │ │  .srt    │ │  assets  │     │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │
│       │            │            │            │            │            │
│       └────────────┼────────────┼────────────┼────────────┘            │
│                    ▼            ▼            ▼                          │
│              ┌─────────────────────────────────────┐                   │
│              │         ASSEMBLY ENGINE             │                   │
│              │    (FFmpeg / HyperFrames / Python)  │                   │
│              └──────────────────┬──────────────────┘                   │
│                                 │                                       │
│                                 ▼                                       │
│              ┌─────────────────────────────────────┐                   │
│              │       COMPOSITION LAYERS            │                   │
│              ├─────────────────────────────────────┤                   │
│              │ Layer 1: Background / B-roll        │                   │
│              │ Layer 2: Avatar overlay             │                   │
│              │ Layer 3: Lower thirds / graphics    │                   │
│              │ Layer 4: Animated captions          │                   │
│              │ Layer 5: Logo watermark             │                   │
│              └──────────────────┬──────────────────┘                   │
│                                 │                                       │
│                                 ▼                                       │
│              ┌─────────────────────────────────────┐                   │
│              │         OUTPUT VARIANTS             │                   │
│              ├─────────────────────────────────────┤                   │
│              │ • YouTube (16:9, 1080p/4K)          │                   │
│              │ • Shorts/Reels/TikTok (9:16, 1080p) │                   │
│              │ • LinkedIn (1:1 or 16:9)            │                   │
│              └─────────────────────────────────────┘                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## FFmpeg Assembly Commands

### Basic Composition

```python
import subprocess
from pathlib import Path

class FFmpegAssembler:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg = ffmpeg_path
        
    def compose_video(
        self,
        avatar_video: Path,
        voice_audio: Path,
        broll_clips: list[Path],
        subtitles: Path,
        output_path: Path,
        brand_config: dict
    ) -> Path:
        """
        Compose final video from all assets
        """
        
        # Step 1: Replace avatar audio with high-quality voice
        avatar_with_voice = self._replace_audio(avatar_video, voice_audio)
        
        # Step 2: Create B-roll sequence based on script timecodes
        broll_sequence = self._create_broll_sequence(broll_clips)
        
        # Step 3: Composite avatar over B-roll at specified sections
        composited = self._composite_layers(
            background=broll_sequence,
            avatar=avatar_with_voice,
            brand_config=brand_config
        )
        
        # Step 4: Burn in subtitles
        final = self._add_subtitles(composited, subtitles, brand_config)
        
        return final
    
    def _replace_audio(self, video: Path, audio: Path) -> Path:
        """Replace video audio track with voice file"""
        
        output = video.parent / f"{video.stem}_voiced.mp4"
        
        cmd = [
            self.ffmpeg, "-y",
            "-i", str(video),
            "-i", str(audio),
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            str(output)
        ]
        
        subprocess.run(cmd, check=True)
        return output
    
    def _create_broll_sequence(self, clips: list[Path]) -> Path:
        """Concatenate B-roll clips with crossfade transitions"""
        
        # Create concat file
        concat_file = Path("temp_concat.txt")
        with open(concat_file, "w") as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        output = Path("temp_broll_sequence.mp4")
        
        cmd = [
            self.ffmpeg, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264",
            "-preset", "fast",
            str(output)
        ]
        
        subprocess.run(cmd, check=True)
        concat_file.unlink()
        
        return output
    
    def _composite_layers(
        self,
        background: Path,
        avatar: Path,
        brand_config: dict
    ) -> Path:
        """Overlay avatar on background with positioning"""
        
        output = Path("temp_composited.mp4")
        
        # Avatar position (bottom-right corner)
        avatar_scale = brand_config.get("avatar_scale", 0.35)
        avatar_x = brand_config.get("avatar_x", "W-w-50")
        avatar_y = brand_config.get("avatar_y", "H-h-50")
        
        cmd = [
            self.ffmpeg, "-y",
            "-i", str(background),
            "-i", str(avatar),
            "-filter_complex",
            f"[1:v]scale=iw*{avatar_scale}:-1[avatar];"
            f"[0:v][avatar]overlay={avatar_x}:{avatar_y}:enable='between(t,0,999)'",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            str(output)
        ]
        
        subprocess.run(cmd, check=True)
        return output
    
    def _add_subtitles(
        self,
        video: Path,
        subtitles: Path,
        brand_config: dict
    ) -> Path:
        """Burn subtitles into video with custom styling"""
        
        output = Path("final_output.mp4")
        
        # Subtitle style
        font = brand_config.get("font", "Arial")
        font_size = brand_config.get("font_size", 24)
        font_color = brand_config.get("font_color", "&HFFFFFF")
        outline_color = brand_config.get("outline_color", "&H000000")
        
        style = (
            f"Fontname={font},"
            f"Fontsize={font_size},"
            f"PrimaryColour={font_color},"
            f"OutlineColour={outline_color},"
            f"Outline=2,"
            f"Shadow=1,"
            f"Alignment=2,"  # Bottom center
            f"MarginV=50"
        )
        
        cmd = [
            self.ffmpeg, "-y",
            "-i", str(video),
            "-vf", f"subtitles={subtitles}:force_style='{style}'",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-c:a", "copy",
            str(output)
        ]
        
        subprocess.run(cmd, check=True)
        return output
```

### Animated Captions (TikTok/Reels Style)

```python
def create_animated_captions(
    video: Path,
    word_timestamps: list[dict],
    output: Path,
    style: dict
) -> Path:
    """
    Create word-by-word animated captions like TikTok/Reels.
    Uses ASS subtitles for animation effects.
    """
    
    ass_content = generate_ass_subtitles(word_timestamps, style)
    ass_file = Path("temp_animated.ass")
    
    with open(ass_file, "w", encoding="utf-8") as f:
        f.write(ass_content)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video),
        "-vf", f"ass={ass_file}",
        "-c:v", "libx264",
        "-preset", "fast",
        str(output)
    ]
    
    subprocess.run(cmd, check=True)
    ass_file.unlink()
    
    return output


def generate_ass_subtitles(words: list[dict], style: dict) -> str:
    """Generate ASS format with word-by-word highlights"""
    
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style['font']},{style['size']},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,50,50,80,1
Style: Highlight,{style['font']},{style['size']},&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,50,50,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    events = []
    for word in words:
        start = format_ass_time(word['start'])
        end = format_ass_time(word['end'])
        text = word['word']
        
        # Highlight current word, show context
        events.append(
            f"Dialogue: 0,{start},{end},Highlight,,0,0,0,,{text}"
        )
    
    return header + "\n".join(events)
```

## Multi-Format Export

```python
class VideoExporter:
    """Export video in multiple formats for different platforms"""
    
    FORMATS = {
        "youtube_hd": {
            "resolution": "1920x1080",
            "aspect": "16:9",
            "fps": 30,
            "bitrate": "8M"
        },
        "youtube_4k": {
            "resolution": "3840x2160",
            "aspect": "16:9",
            "fps": 30,
            "bitrate": "35M"
        },
        "shorts": {
            "resolution": "1080x1920",
            "aspect": "9:16",
            "fps": 30,
            "bitrate": "8M"
        },
        "linkedin": {
            "resolution": "1080x1080",
            "aspect": "1:1",
            "fps": 30,
            "bitrate": "6M"
        }
    }
    
    def export_all(self, source: Path, output_dir: Path) -> dict[str, Path]:
        """Export video in all platform formats"""
        
        outputs = {}
        
        for format_name, settings in self.FORMATS.items():
            output_path = output_dir / f"{format_name}.mp4"
            self._export_format(source, output_path, settings)
            outputs[format_name] = output_path
        
        return outputs
    
    def _export_format(self, source: Path, output: Path, settings: dict):
        """Export single format"""
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(source),
            "-vf", f"scale={settings['resolution']}:force_original_aspect_ratio=decrease,"
                   f"pad={settings['resolution']}:(ow-iw)/2:(oh-ih)/2",
            "-r", str(settings['fps']),
            "-b:v", settings['bitrate'],
            "-c:v", "libx264",
            "-preset", "slow",
            "-c:a", "aac",
            "-b:a", "192k",
            str(output)
        ]
        
        subprocess.run(cmd, check=True)
```

## Automated Publishing

### YouTube Upload

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class YouTubePublisher:
    def __init__(self, credentials_path: str):
        self.creds = Credentials.from_authorized_user_file(credentials_path)
        self.youtube = build("youtube", "v3", credentials=self.creds)
        
    def upload_video(
        self,
        video_path: Path,
        metadata: dict,
        thumbnail_path: Path = None
    ) -> str:
        """Upload video to YouTube and return video ID"""
        
        body = {
            "snippet": {
                "title": metadata["title"],
                "description": metadata["description"],
                "tags": metadata["tags"],
                "categoryId": "28"  # Science & Technology
            },
            "status": {
                "privacyStatus": metadata.get("privacy", "private"),
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True
        )
        
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = request.execute()
        video_id = response["id"]
        
        # Upload thumbnail
        if thumbnail_path:
            self._set_thumbnail(video_id, thumbnail_path)
        
        return video_id
    
    def _set_thumbnail(self, video_id: str, thumbnail_path: Path):
        """Set custom thumbnail for video"""
        
        self.youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumbnail_path))
        ).execute()
    
    def schedule_video(self, video_id: str, publish_at: str):
        """Schedule video for future publication"""
        
        self.youtube.videos().update(
            part="status",
            body={
                "id": video_id,
                "status": {
                    "privacyStatus": "private",
                    "publishAt": publish_at  # ISO 8601 format
                }
            }
        ).execute()
```

### Multi-Platform Publishing

```python
class MultiPlatformPublisher:
    """Publish to YouTube, LinkedIn, and Instagram"""
    
    def __init__(self, config: dict):
        self.youtube = YouTubePublisher(config["youtube_creds"])
        self.linkedin = LinkedInPublisher(config["linkedin_token"])
        self.instagram = InstagramPublisher(config["instagram_token"])
        
    def publish_all(
        self,
        video_outputs: dict[str, Path],
        metadata: dict,
        schedule: dict = None
    ) -> dict:
        """Publish to all platforms"""
        
        results = {}
        
        # YouTube (long-form)
        results["youtube"] = self.youtube.upload_video(
            video_outputs["youtube_hd"],
            metadata["youtube"]
        )
        
        # YouTube Shorts
        if "shorts" in video_outputs:
            results["youtube_shorts"] = self.youtube.upload_video(
                video_outputs["shorts"],
                {**metadata["shorts"], "title": f"#Shorts {metadata['shorts']['title']}"}
            )
        
        # LinkedIn
        results["linkedin"] = self.linkedin.upload_video(
            video_outputs.get("linkedin", video_outputs["youtube_hd"]),
            metadata["linkedin"]
        )
        
        # Instagram Reels
        if "shorts" in video_outputs:
            results["instagram"] = self.instagram.upload_reel(
                video_outputs["shorts"],
                metadata["instagram"]
            )
        
        return results
```

## Complete Pipeline Orchestration

```python
from pathlib import Path
import asyncio
from loguru import logger

class VideoPipelineOrchestrator:
    """Master orchestrator for the entire video production pipeline"""
    
    def __init__(self, config: dict):
        self.config = config
        self.assembler = FFmpegAssembler()
        self.exporter = VideoExporter()
        self.publisher = MultiPlatformPublisher(config["publishing"])
        
    async def produce_video(self, topic_id: str) -> dict:
        """
        Execute complete video production pipeline
        """
        
        work_dir = Path(f"output/{topic_id}")
        work_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting production for topic: {topic_id}")
        
        # Load assets from previous stages
        assets = self._load_assets(work_dir)
        
        # Stage 6a: Compose video
        logger.info("Composing video layers...")
        composed = self.assembler.compose_video(
            avatar_video=assets["avatar"],
            voice_audio=assets["voice"],
            broll_clips=assets["broll"],
            subtitles=assets["subtitles"],
            output_path=work_dir / "composed.mp4",
            brand_config=self.config["brand"]
        )
        
        # Stage 6b: Export formats
        logger.info("Exporting platform formats...")
        exports = self.exporter.export_all(
            composed,
            work_dir / "exports"
        )
        
        # Stage 6c: Publish (if auto-publish enabled)
        if self.config.get("auto_publish", False):
            logger.info("Publishing to platforms...")
            metadata = self._generate_metadata(topic_id)
            publish_results = self.publisher.publish_all(exports, metadata)
        else:
            publish_results = {"status": "ready_for_manual_publish"}
        
        logger.success(f"Production complete for topic: {topic_id}")
        
        return {
            "topic_id": topic_id,
            "exports": {k: str(v) for k, v in exports.items()},
            "publish_results": publish_results
        }
    
    def _load_assets(self, work_dir: Path) -> dict:
        """Load generated assets from Stage 5"""
        
        return {
            "avatar": work_dir / "avatar.mp4",
            "voice": work_dir / "voice.mp3",
            "broll": list((work_dir / "broll").glob("*.mp4")),
            "subtitles": work_dir / "subtitles.srt"
        }
    
    def _generate_metadata(self, topic_id: str) -> dict:
        """Generate platform-specific metadata"""
        
        # Load from Airtable or local manifest
        # Return structured metadata for each platform
        pass
```

## Final Output Structure

```
output/{topic_id}/
├── voice.mp3                    # Stage 5
├── avatar.mp4                   # Stage 5
├── broll/                       # Stage 5
│   ├── clip_001.mp4
│   └── clip_002.mp4
├── subtitles.srt                # Stage 5
├── composed.mp4                 # Stage 6 - Master file
├── exports/                     # Stage 6 - Platform variants
│   ├── youtube_hd.mp4
│   ├── youtube_4k.mp4
│   ├── shorts.mp4
│   └── linkedin.mp4
├── thumbnail.png                # Generated or provided
├── manifest.json                # Production metadata
└── publish_log.json             # Publishing results
```
