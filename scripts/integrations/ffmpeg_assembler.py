"""
FFmpeg Video Assembly
=====================

Programmatic video composition using FFmpeg.
No traditional video editing software required.

Usage:
    from integrations.ffmpeg_assembler import FFmpegAssembler
    
    assembler = FFmpegAssembler()
    assembler.compose_video(
        avatar_video=Path("avatar.mp4"),
        voice_audio=Path("voice.mp3"),
        output_path=Path("final.mp4")
    )
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class BrandConfig:
    """Branding configuration for video assembly"""
    font: str = "Arial"
    font_size: int = 24
    font_color: str = "white"
    outline_color: str = "black"
    avatar_scale: float = 0.35
    avatar_position: str = "bottom-right"  # bottom-right, bottom-left, center
    watermark_path: Optional[str] = None


class FFmpegAssembler:
    """
    Assembles video from components using FFmpeg.
    
    FFmpeg must be installed and available in PATH.
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        self.ffmpeg = ffmpeg_path
        self.ffprobe = ffprobe_path
        
        # Verify FFmpeg is available
        if not self._check_ffmpeg():
            raise RuntimeError(
                "FFmpeg not found. Install from https://ffmpeg.org/download.html\n"
                "Or set FFMPEG_PATH environment variable."
            )
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(
                [self.ffmpeg, "-version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _run_ffmpeg(self, args: list, description: str = ""):
        """Run FFmpeg command with error handling"""
        cmd = [self.ffmpeg, "-y"] + args  # -y to overwrite
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(
                f"FFmpeg error ({description}):\n{result.stderr}"
            )
        
        return result
    
    def get_duration(self, file_path: Path) -> float:
        """Get duration of audio/video file in seconds"""
        cmd = [
            self.ffprobe,
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    
    def replace_audio(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path
    ) -> Path:
        """Replace video's audio track with a new audio file"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._run_ffmpeg([
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            str(output_path)
        ], "replace audio")
        
        return output_path
    
    def add_subtitles(
        self,
        video_path: Path,
        subtitle_path: Path,
        output_path: Path,
        brand: BrandConfig = None
    ) -> Path:
        """Burn subtitles into video"""
        
        brand = brand or BrandConfig()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Escape the subtitle path for FFmpeg filter
        sub_path_escaped = str(subtitle_path).replace("\\", "/").replace(":", "\\:")
        
        # Build subtitle style
        style = (
            f"Fontname={brand.font},"
            f"Fontsize={brand.font_size},"
            f"PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,"
            f"Outline=2,"
            f"Shadow=1,"
            f"Alignment=2,"
            f"MarginV=50"
        )
        
        self._run_ffmpeg([
            "-i", str(video_path),
            "-vf", f"subtitles='{sub_path_escaped}':force_style='{style}'",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "copy",
            str(output_path)
        ], "burn subtitles")
        
        return output_path
    
    def overlay_avatar(
        self,
        background_path: Path,
        avatar_path: Path,
        output_path: Path,
        brand: BrandConfig = None
    ) -> Path:
        """Overlay avatar video on background"""
        
        brand = brand or BrandConfig()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate avatar position
        scale = brand.avatar_scale
        if brand.avatar_position == "bottom-right":
            x, y = "W-w-50", "H-h-50"
        elif brand.avatar_position == "bottom-left":
            x, y = "50", "H-h-50"
        else:  # center
            x, y = "(W-w)/2", "(H-h)/2"
        
        self._run_ffmpeg([
            "-i", str(background_path),
            "-i", str(avatar_path),
            "-filter_complex",
            f"[1:v]scale=iw*{scale}:-1[avatar];[0:v][avatar]overlay={x}:{y}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            str(output_path)
        ], "overlay avatar")
        
        return output_path
    
    def concatenate_clips(
        self,
        clips: list[Path],
        output_path: Path,
        crossfade: float = 0
    ) -> Path:
        """Concatenate multiple video clips"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if crossfade > 0:
            # Use xfade filter for crossfade transitions
            return self._concat_with_crossfade(clips, output_path, crossfade)
        
        # Simple concat with concat demuxer
        concat_file = output_path.parent / "concat_list.txt"
        
        with open(concat_file, "w") as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        self._run_ffmpeg([
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path)
        ], "concatenate clips")
        
        concat_file.unlink()
        return output_path
    
    def _concat_with_crossfade(
        self,
        clips: list[Path],
        output_path: Path,
        duration: float
    ) -> Path:
        """Concatenate clips with crossfade transitions"""
        
        if len(clips) < 2:
            return self.concatenate_clips(clips, output_path)
        
        # Build complex filter for xfade
        inputs = []
        filter_parts = []
        
        for i, clip in enumerate(clips):
            inputs.extend(["-i", str(clip)])
        
        # Chain xfade filters
        prev_label = "[0:v]"
        for i in range(1, len(clips)):
            next_label = f"[v{i}]" if i < len(clips) - 1 else "[outv]"
            offset = i * 5 - duration  # Approximate offset
            filter_parts.append(
                f"{prev_label}[{i}:v]xfade=transition=fade:duration={duration}:offset={offset}{next_label}"
            )
            prev_label = next_label
        
        self._run_ffmpeg(
            inputs + [
                "-filter_complex", ";".join(filter_parts),
                "-map", "[outv]",
                "-c:v", "libx264",
                "-preset", "fast",
                str(output_path)
            ],
            "concat with crossfade"
        )
        
        return output_path
    
    def create_color_background(
        self,
        output_path: Path,
        duration: float,
        color: str = "black",
        width: int = 1920,
        height: int = 1080
    ) -> Path:
        """Create a solid color video"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._run_ffmpeg([
            "-f", "lavfi",
            "-i", f"color=c={color}:s={width}x{height}:d={duration}",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            str(output_path)
        ], "create background")
        
        return output_path
    
    def export_format(
        self,
        input_path: Path,
        output_path: Path,
        width: int,
        height: int,
        fps: int = 30,
        bitrate: str = "8M"
    ) -> Path:
        """Export video in specific format/resolution"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._run_ffmpeg([
            "-i", str(input_path),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                   f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "-r", str(fps),
            "-b:v", bitrate,
            "-c:v", "libx264",
            "-preset", "slow",
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_path)
        ], f"export {width}x{height}")
        
        return output_path
    
    def compose_video(
        self,
        voice_audio: Path,
        output_path: Path,
        avatar_video: Optional[Path] = None,
        broll_clips: Optional[list[Path]] = None,
        subtitles: Optional[Path] = None,
        brand: BrandConfig = None
    ) -> Path:
        """
        Full video composition from components.
        
        Args:
            voice_audio: Main audio track
            output_path: Final output path
            avatar_video: Optional avatar talking head video
            broll_clips: Optional list of B-roll clips
            subtitles: Optional SRT subtitle file
            brand: Branding configuration
            
        Returns:
            Path to the composed video
        """
        
        brand = brand or BrandConfig()
        work_dir = output_path.parent / "temp_assembly"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        duration = self.get_duration(voice_audio)
        current_video = None
        
        try:
            # Step 1: Create base (either B-roll sequence or solid background)
            if broll_clips and len(broll_clips) > 0:
                current_video = self.concatenate_clips(
                    broll_clips,
                    work_dir / "broll_sequence.mp4"
                )
            else:
                # Create black background
                current_video = self.create_color_background(
                    work_dir / "background.mp4",
                    duration=duration
                )
            
            # Step 2: Overlay avatar if provided
            if avatar_video and avatar_video.exists():
                current_video = self.overlay_avatar(
                    current_video,
                    avatar_video,
                    work_dir / "with_avatar.mp4",
                    brand
                )
            
            # Step 3: Replace/add audio
            with_audio = work_dir / "with_audio.mp4"
            self._run_ffmpeg([
                "-i", str(current_video),
                "-i", str(voice_audio),
                "-c:v", "copy",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                str(with_audio)
            ], "add audio")
            current_video = with_audio
            
            # Step 4: Burn subtitles if provided
            if subtitles and subtitles.exists():
                current_video = self.add_subtitles(
                    current_video,
                    subtitles,
                    work_dir / "with_subs.mp4",
                    brand
                )
            
            # Step 5: Final encode
            self._run_ffmpeg([
                "-i", str(current_video),
                "-c:v", "libx264",
                "-preset", "slow",
                "-crf", "18",
                "-c:a", "aac",
                "-b:a", "192k",
                str(output_path)
            ], "final encode")
            
            return output_path
            
        finally:
            # Clean up temp files
            shutil.rmtree(work_dir, ignore_errors=True)


class VideoExporter:
    """Export video in multiple platform formats"""
    
    FORMATS = {
        "youtube_hd": {"width": 1920, "height": 1080, "fps": 30, "bitrate": "8M"},
        "youtube_4k": {"width": 3840, "height": 2160, "fps": 30, "bitrate": "35M"},
        "shorts": {"width": 1080, "height": 1920, "fps": 30, "bitrate": "8M"},
        "linkedin": {"width": 1080, "height": 1080, "fps": 30, "bitrate": "6M"},
    }
    
    def __init__(self):
        self.assembler = FFmpegAssembler()
    
    def export_all(
        self,
        source: Path,
        output_dir: Path,
        formats: list[str] = None
    ) -> dict[str, Path]:
        """
        Export video in multiple formats.
        
        Args:
            source: Source video file
            output_dir: Directory for exports
            formats: List of format names (defaults to all)
            
        Returns:
            Dict mapping format name to output path
        """
        
        formats = formats or list(self.FORMATS.keys())
        output_dir.mkdir(parents=True, exist_ok=True)
        
        outputs = {}
        for fmt_name in formats:
            if fmt_name not in self.FORMATS:
                continue
            
            fmt = self.FORMATS[fmt_name]
            output_path = output_dir / f"{fmt_name}.mp4"
            
            self.assembler.export_format(
                source,
                output_path,
                width=fmt["width"],
                height=fmt["height"],
                fps=fmt["fps"],
                bitrate=fmt["bitrate"]
            )
            
            outputs[fmt_name] = output_path
        
        return outputs


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Check FFmpeg: python ffmpeg_assembler.py check")
        print("  Get duration: python ffmpeg_assembler.py duration video.mp4")
        print("  Add subtitles: python ffmpeg_assembler.py subs video.mp4 subs.srt output.mp4")
        print("  Export formats: python ffmpeg_assembler.py export video.mp4 output_dir/")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        assembler = FFmpegAssembler()
        
        if command == "check":
            print("✅ FFmpeg is available and working!")
        
        elif command == "duration" and len(sys.argv) >= 3:
            video = sys.argv[2]
            duration = assembler.get_duration(Path(video))
            print(f"Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
        
        elif command == "subs" and len(sys.argv) >= 5:
            video = sys.argv[2]
            subs = sys.argv[3]
            output = sys.argv[4]
            print(f"Adding subtitles to {video}...")
            result = assembler.add_subtitles(Path(video), Path(subs), Path(output))
            print(f"✅ Saved to: {result}")
        
        elif command == "export" and len(sys.argv) >= 4:
            video = sys.argv[2]
            output_dir = sys.argv[3]
            print(f"Exporting {video} to multiple formats...")
            exporter = VideoExporter()
            results = exporter.export_all(Path(video), Path(output_dir))
            print("✅ Exported:")
            for name, path in results.items():
                print(f"  {name}: {path}")
        
        else:
            print("Invalid command")
            
    except RuntimeError as e:
        print(f"Error: {e}")
