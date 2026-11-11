"""
Local Whisper Transcription
===========================

Generates subtitles from audio using OpenAI's Whisper model running locally.
This is FREE - no API calls required.

Usage:
    from integrations.whisper_local import SubtitleGenerator
    
    generator = SubtitleGenerator()
    generator.generate_srt(Path("audio.mp3"), Path("subtitles.srt"))
"""

import os
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# Check if whisper is installed
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


@dataclass
class TranscriptWord:
    """A single transcribed word with timing"""
    word: str
    start: float
    end: float
    confidence: float = 1.0


@dataclass
class TranscriptSegment:
    """A segment of transcription (usually a sentence)"""
    id: int
    start: float
    end: float
    text: str
    words: list[TranscriptWord] = None


class SubtitleGenerator:
    """
    Generates subtitles using OpenAI's Whisper model running locally.
    
    Model sizes:
    - tiny: ~1GB VRAM, fastest, lowest accuracy
    - base: ~1GB VRAM, good balance
    - small: ~2GB VRAM, better accuracy
    - medium: ~5GB VRAM, high accuracy
    - large: ~10GB VRAM, best accuracy
    """
    
    MODELS = ["tiny", "base", "small", "medium", "large"]
    
    def __init__(self, model_size: str = "base", device: str = "auto"):
        """
        Initialize Whisper model.
        
        Args:
            model_size: Model to use - tiny, base, small, medium, or large
            device: Device to run on - "auto", "cpu", or "cuda"
        """
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "Whisper is not installed. Install with:\n"
                "  pip install openai-whisper\n"
                "Or for faster inference:\n"
                "  pip install whisper-timestamped"
            )
        
        self.model_size = model_size
        self._model = None
        self._device = device
    
    @property
    def model(self):
        """Lazy-load the model"""
        if self._model is None:
            print(f"Loading Whisper model '{self.model_size}'...")
            device = None if self._device == "auto" else self._device
            self._model = whisper.load_model(self.model_size, device=device)
            print("Model loaded.")
        return self._model
    
    def transcribe(
        self,
        audio_path: Path,
        language: str = "en",
        word_timestamps: bool = True
    ) -> list[TranscriptSegment]:
        """
        Transcribe audio file to text with timestamps.
        
        Args:
            audio_path: Path to audio file (MP3, WAV, etc.)
            language: Language code (e.g., "en", "es", "fr")
            word_timestamps: If True, include word-level timing
            
        Returns:
            List of TranscriptSegments
        """
        
        result = self.model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=word_timestamps,
            verbose=False
        )
        
        segments = []
        for i, seg in enumerate(result["segments"]):
            words = None
            if word_timestamps and "words" in seg:
                words = [
                    TranscriptWord(
                        word=w["word"],
                        start=w["start"],
                        end=w["end"],
                        confidence=w.get("probability", 1.0)
                    )
                    for w in seg["words"]
                ]
            
            segments.append(TranscriptSegment(
                id=i + 1,
                start=seg["start"],
                end=seg["end"],
                text=seg["text"].strip(),
                words=words
            ))
        
        return segments
    
    def generate_srt(
        self,
        audio_path: Path,
        output_path: Path,
        language: str = "en",
        max_chars_per_line: int = 42
    ) -> Path:
        """
        Generate an SRT subtitle file from audio.
        
        Args:
            audio_path: Path to audio file
            output_path: Where to save the SRT file
            language: Language code
            max_chars_per_line: Max characters per subtitle line
            
        Returns:
            Path to the generated SRT file
        """
        
        segments = self.transcribe(audio_path, language, word_timestamps=False)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            for seg in segments:
                # Split long text into lines
                text = seg.text
                if len(text) > max_chars_per_line:
                    words = text.split()
                    lines = []
                    current_line = []
                    for word in words:
                        if len(" ".join(current_line + [word])) <= max_chars_per_line:
                            current_line.append(word)
                        else:
                            lines.append(" ".join(current_line))
                            current_line = [word]
                    if current_line:
                        lines.append(" ".join(current_line))
                    text = "\n".join(lines)
                
                f.write(f"{seg.id}\n")
                f.write(f"{self._format_timestamp(seg.start)} --> {self._format_timestamp(seg.end)}\n")
                f.write(f"{text}\n\n")
        
        return output_path
    
    def generate_word_srt(
        self,
        audio_path: Path,
        output_path: Path,
        language: str = "en",
        words_per_caption: int = 3
    ) -> Path:
        """
        Generate word-by-word SRT for TikTok/Reels style captions.
        
        Args:
            audio_path: Path to audio file
            output_path: Where to save the SRT file
            language: Language code
            words_per_caption: Number of words per caption
            
        Returns:
            Path to the generated SRT file
        """
        
        segments = self.transcribe(audio_path, language, word_timestamps=True)
        
        # Flatten all words
        all_words = []
        for seg in segments:
            if seg.words:
                all_words.extend(seg.words)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            caption_id = 1
            for i in range(0, len(all_words), words_per_caption):
                chunk = all_words[i:i + words_per_caption]
                if not chunk:
                    continue
                
                start = chunk[0].start
                end = chunk[-1].end
                text = " ".join(w.word.strip() for w in chunk)
                
                f.write(f"{caption_id}\n")
                f.write(f"{self._format_timestamp(start)} --> {self._format_timestamp(end)}\n")
                f.write(f"{text}\n\n")
                caption_id += 1
        
        return output_path
    
    def generate_json(
        self,
        audio_path: Path,
        output_path: Path,
        language: str = "en"
    ) -> Path:
        """
        Generate JSON with word-level timestamps (useful for animated captions).
        
        Returns:
            Path to the JSON file
        """
        import json
        
        segments = self.transcribe(audio_path, language, word_timestamps=True)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "segments": [
                {
                    "id": seg.id,
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text,
                    "words": [
                        {
                            "word": w.word,
                            "start": w.start,
                            "end": w.end,
                            "confidence": w.confidence
                        }
                        for w in (seg.words or [])
                    ]
                }
                for seg in segments
            ]
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


# Alternative: Use local Whisper without loading the class
def transcribe_audio(audio_path: str, output_srt: str, model: str = "base") -> str:
    """
    Simple function to transcribe audio to SRT.
    
    Args:
        audio_path: Path to audio file
        output_srt: Path for output SRT file
        model: Whisper model size
        
    Returns:
        Path to the generated SRT file
    """
    generator = SubtitleGenerator(model_size=model)
    return str(generator.generate_srt(Path(audio_path), Path(output_srt)))


if __name__ == "__main__":
    if not WHISPER_AVAILABLE:
        print("❌ Whisper is not installed.")
        print("\nInstall with:")
        print("  pip install openai-whisper")
        print("\nOr for GPU acceleration:")
        print("  pip install openai-whisper torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Transcribe: python whisper_local.py transcribe audio.mp3 output.srt")
        print("  Word-level: python whisper_local.py words audio.mp3 output.srt")
        print("  JSON output: python whisper_local.py json audio.mp3 output.json")
        print("\nOptions:")
        print("  --model=base  Model size (tiny, base, small, medium, large)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Parse model from args
    model = "base"
    for arg in sys.argv:
        if arg.startswith("--model="):
            model = arg.split("=")[1]
    
    try:
        generator = SubtitleGenerator(model_size=model)
        
        if command == "transcribe" and len(sys.argv) >= 4:
            audio = sys.argv[2]
            output = sys.argv[3]
            print(f"Transcribing {audio}...")
            result = generator.generate_srt(Path(audio), Path(output))
            print(f"✅ Saved to: {result}")
        
        elif command == "words" and len(sys.argv) >= 4:
            audio = sys.argv[2]
            output = sys.argv[3]
            print(f"Generating word-level captions for {audio}...")
            result = generator.generate_word_srt(Path(audio), Path(output))
            print(f"✅ Saved to: {result}")
        
        elif command == "json" and len(sys.argv) >= 4:
            audio = sys.argv[2]
            output = sys.argv[3]
            print(f"Generating JSON transcript for {audio}...")
            result = generator.generate_json(Path(audio), Path(output))
            print(f"✅ Saved to: {result}")
        
        else:
            print("Invalid command. Use 'transcribe', 'words', or 'json'")
            
    except Exception as e:
        print(f"Error: {e}")
