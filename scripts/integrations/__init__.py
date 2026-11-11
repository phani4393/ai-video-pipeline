"""
AI Video Pipeline Integrations
==============================

This package contains all API integrations for the video production pipeline.

Modules:
    - openai_client: Topic scoring and script generation (GPT-4)
    - perplexity: Deep research brief generation
    - elevenlabs: Neural voice synthesis
    - heygen: AI avatar video generation
    - whisper_local: Local transcription (free)
    - ffmpeg_assembler: Programmatic video composition
    - airtable: Topic queue database

Each module can be used standalone or as part of the full pipeline.

Quick Usage:
    
    # Score a topic
    from integrations.openai_client import TopicScorer
    scorer = TopicScorer()
    result = scorer.score_topic("Your topic here")
    
    # Generate research
    from integrations.perplexity import PerplexityResearcher
    researcher = PerplexityResearcher()
    brief = researcher.research_topic("Your topic")
    
    # Generate script
    from integrations.openai_client import ScriptGenerator
    generator = ScriptGenerator()
    script = generator.generate(topic, angle, research_brief)
    
    # Generate voice
    from integrations.elevenlabs import ElevenLabsVoice
    voice = ElevenLabsVoice()
    voice.generate_speech("Text", Path("output.mp3"))
    
    # Generate subtitles (free, local)
    from integrations.whisper_local import SubtitleGenerator
    gen = SubtitleGenerator()
    gen.generate_srt(Path("audio.mp3"), Path("subs.srt"))
    
    # Assemble video (free, local)
    from integrations.ffmpeg_assembler import FFmpegAssembler
    assembler = FFmpegAssembler()
    assembler.compose_video(voice_audio, output_path)

Environment Variables Required:
    
    OPENAI_API_KEY      - Required for scoring and scripts
    PERPLEXITY_API_KEY  - Optional, for research
    ELEVENLABS_API_KEY  - Optional, for voice
    ELEVENLABS_VOICE_ID - Optional, for voice
    HEYGEN_API_KEY      - Optional, for avatars
    HEYGEN_AVATAR_ID    - Optional, for avatars
    AIRTABLE_API_KEY    - Optional, for queue management
    AIRTABLE_BASE_ID    - Optional, for queue management
"""

# Version
__version__ = "1.0.0"

# Lazy imports to avoid loading everything at once
def __getattr__(name):
    """Lazy import modules"""
    
    if name == "TopicScorer":
        from .openai_client import TopicScorer
        return TopicScorer
    
    if name == "ScriptGenerator":
        from .openai_client import ScriptGenerator
        return ScriptGenerator
    
    if name == "PerplexityResearcher":
        from .perplexity import PerplexityResearcher
        return PerplexityResearcher
    
    if name == "ElevenLabsVoice":
        from .elevenlabs import ElevenLabsVoice
        return ElevenLabsVoice
    
    if name == "HeyGenAvatar":
        from .heygen import HeyGenAvatar
        return HeyGenAvatar
    
    if name == "SubtitleGenerator":
        from .whisper_local import SubtitleGenerator
        return SubtitleGenerator
    
    if name == "FFmpegAssembler":
        from .ffmpeg_assembler import FFmpegAssembler
        return FFmpegAssembler
    
    if name == "VideoExporter":
        from .ffmpeg_assembler import VideoExporter
        return VideoExporter
    
    if name == "TopicQueue":
        from .airtable import TopicQueue
        return TopicQueue
    
    raise AttributeError(f"module 'integrations' has no attribute '{name}'")
