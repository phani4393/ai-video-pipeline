"""
AI Video Pipeline Orchestrator
==============================

Master orchestration script that ties together all 6 stages of the pipeline.
This script is the entry point for producing videos from approved topics.

Usage:
    python orchestrator.py --topic-id rec123abc
    python orchestrator.py --topic-id rec123abc --stage 3  # Start from stage 3
    python orchestrator.py --batch  # Process all approved topics

"""

import asyncio
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict
from enum import Enum

from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PipelineStage(Enum):
    RESEARCH = 3  # Stages 1-2 handled by Make.com
    SCRIPT = 4
    MEDIA = 5
    ASSEMBLY = 6


@dataclass
class PipelineContext:
    """Shared context passed between pipeline stages"""
    topic_id: str
    topic_title: str
    selected_angle: str
    work_dir: Path
    research_brief: Optional[str] = None
    script: Optional[dict] = None
    voice_path: Optional[Path] = None
    avatar_path: Optional[Path] = None
    broll_paths: Optional[list[Path]] = None
    subtitle_path: Optional[Path] = None
    final_video_path: Optional[Path] = None
    publish_results: Optional[dict] = None
    
    def save(self):
        """Persist context to disk for resumability"""
        context_file = self.work_dir / "pipeline_context.json"
        data = asdict(self)
        # Convert Path objects to strings
        for key, value in data.items():
            if isinstance(value, Path):
                data[key] = str(value)
            elif isinstance(value, list) and value and isinstance(value[0], Path):
                data[key] = [str(p) for p in value]
        
        with open(context_file, "w") as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, work_dir: Path) -> "PipelineContext":
        """Load context from disk"""
        context_file = work_dir / "pipeline_context.json"
        with open(context_file) as f:
            data = json.load(f)
        
        # Convert strings back to Path objects
        data["work_dir"] = Path(data["work_dir"])
        if data.get("voice_path"):
            data["voice_path"] = Path(data["voice_path"])
        if data.get("avatar_path"):
            data["avatar_path"] = Path(data["avatar_path"])
        if data.get("broll_paths"):
            data["broll_paths"] = [Path(p) for p in data["broll_paths"]]
        if data.get("subtitle_path"):
            data["subtitle_path"] = Path(data["subtitle_path"])
        if data.get("final_video_path"):
            data["final_video_path"] = Path(data["final_video_path"])
        
        return cls(**data)


class VideoPipeline:
    """
    Master orchestrator for the AI video production pipeline.
    
    Stages:
    1-2: Handled by Make.com (RSS → Scoring → Alerts)
    3: Research generation via Perplexity
    4: Script generation via LLM
    5: Synthetic media generation (voice, avatar, B-roll)
    6: Video assembly and publishing
    """
    
    def __init__(self):
        self.output_base = Path(os.getenv("OUTPUT_DIR", "./output"))
        self.use_local_drafts = os.getenv("USE_LOCAL_FOR_DRAFTS", "true").lower() == "true"
        self.daily_budget = float(os.getenv("DAILY_API_BUDGET", "10.00"))
        
        # Track API costs
        self.session_cost = 0.0
        
    async def produce_video(
        self,
        topic_id: str,
        start_stage: PipelineStage = PipelineStage.RESEARCH,
        is_final: bool = False
    ) -> PipelineContext:
        """
        Execute the video production pipeline for a given topic.
        
        Args:
            topic_id: Unique identifier for the topic (from Airtable)
            start_stage: Which stage to begin from (for resuming failed runs)
            is_final: If True, use paid APIs for production quality
            
        Returns:
            PipelineContext with all generated assets
        """
        
        logger.info(f"Starting pipeline for topic: {topic_id}")
        
        # Initialize or load context
        work_dir = self.output_base / topic_id
        work_dir.mkdir(parents=True, exist_ok=True)
        
        context_file = work_dir / "pipeline_context.json"
        if context_file.exists() and start_stage != PipelineStage.RESEARCH:
            context = PipelineContext.load(work_dir)
            logger.info(f"Resuming from saved context")
        else:
            # Fetch topic details from Airtable
            topic_data = await self._fetch_topic(topic_id)
            context = PipelineContext(
                topic_id=topic_id,
                topic_title=topic_data["title"],
                selected_angle=topic_data.get("approved_angle", topic_data["angles"][0]),
                work_dir=work_dir
            )
        
        # Execute stages sequentially
        stages = [
            (PipelineStage.RESEARCH, self._stage_research),
            (PipelineStage.SCRIPT, self._stage_script),
            (PipelineStage.MEDIA, self._stage_media),
            (PipelineStage.ASSEMBLY, self._stage_assembly),
        ]
        
        for stage, handler in stages:
            if stage.value >= start_stage.value:
                logger.info(f"Executing Stage {stage.value}: {stage.name}")
                context = await handler(context, is_final)
                context.save()
                
                # Check budget
                if self.session_cost >= self.daily_budget:
                    logger.warning(f"Daily budget exceeded: ${self.session_cost:.2f}")
                    break
        
        logger.success(f"Pipeline complete for topic: {topic_id}")
        return context
    
    async def _fetch_topic(self, topic_id: str) -> dict:
        """Fetch topic details from Airtable"""
        
        # TODO: Implement Airtable API call
        # For now, return mock data
        return {
            "id": topic_id,
            "title": "Claude 3.5 Sonnet Launches with 200K Context",
            "angles": [
                "Claude 3.5 vs GPT-4: Which is actually better for coding?",
                "I replaced ChatGPT with Claude for a week",
                "5 things Claude 3.5 can do that GPT-4 can't"
            ],
            "score": 8,
            "research_brief": None
        }
    
    async def _stage_research(
        self, 
        context: PipelineContext, 
        is_final: bool
    ) -> PipelineContext:
        """Stage 3: Generate research brief via Perplexity"""
        
        from integrations.perplexity import PerplexityResearcher
        
        researcher = PerplexityResearcher(
            api_key=os.getenv("PERPLEXITY_API_KEY")
        )
        
        result = researcher.research_topic(
            topic=context.topic_title,
            context=context.selected_angle
        )
        
        context.research_brief = result["choices"][0]["message"]["content"]
        
        # Save research brief to file
        brief_path = context.work_dir / "research_brief.md"
        with open(brief_path, "w") as f:
            f.write(context.research_brief)
        
        self.session_cost += 0.05  # Estimated Perplexity cost
        logger.info(f"Research brief generated ({len(context.research_brief)} chars)")
        
        return context
    
    async def _stage_script(
        self,
        context: PipelineContext,
        is_final: bool
    ) -> PipelineContext:
        """Stage 4: Generate video script via LLM"""
        
        from integrations.openai_client import generate_script
        
        script = await generate_script(
            topic=context.topic_title,
            angle=context.selected_angle,
            research_brief=context.research_brief,
            length_minutes=8
        )
        
        context.script = script
        
        # Save script to file
        script_path = context.work_dir / "script.json"
        with open(script_path, "w") as f:
            json.dump(script, f, indent=2)
        
        # Also save readable version
        readable_path = context.work_dir / "script.txt"
        with open(readable_path, "w") as f:
            for section in script["sections"]:
                f.write(f"[{section['type']} - {section['timecode']}]\n")
                f.write(f"{section['text']}\n\n")
        
        self.session_cost += 0.10  # Estimated GPT-4 cost
        logger.info(f"Script generated ({script['estimated_duration']} minutes)")
        
        return context
    
    async def _stage_media(
        self,
        context: PipelineContext,
        is_final: bool
    ) -> PipelineContext:
        """Stage 5: Generate synthetic media (voice, avatar, B-roll)"""
        
        # Parallel generation for efficiency
        tasks = [
            self._generate_voice(context, is_final),
            self._generate_broll(context, is_final),
        ]
        
        results = await asyncio.gather(*tasks)
        context.voice_path, context.broll_paths = results
        
        # Avatar generation (depends on voice)
        context.avatar_path = await self._generate_avatar(context, is_final)
        
        # Subtitle generation (local Whisper)
        context.subtitle_path = await self._generate_subtitles(context)
        
        return context
    
    async def _generate_voice(
        self,
        context: PipelineContext,
        is_final: bool
    ) -> Path:
        """Generate voice track"""
        
        output_path = context.work_dir / "voice.mp3"
        
        # Extract spoken text from script
        spoken_text = " ".join([
            s["text"] for s in context.script["sections"]
            if s["type"] not in ["B-ROLL", "TRANSITION", "SCREEN_RECORDING"]
        ])
        
        if is_final:
            from integrations.elevenlabs import ElevenLabsVoice
            voice = ElevenLabsVoice(
                api_key=os.getenv("ELEVENLABS_API_KEY"),
                voice_id=os.getenv("ELEVENLABS_VOICE_ID")
            )
            self.session_cost += 0.50  # Estimated cost
        else:
            from integrations.local_tts import LocalVoice
            voice = LocalVoice()
        
        voice.generate_speech(spoken_text, output_path)
        logger.info(f"Voice track generated: {output_path}")
        
        return output_path
    
    async def _generate_avatar(
        self,
        context: PipelineContext,
        is_final: bool
    ) -> Path:
        """Generate avatar video"""
        
        output_path = context.work_dir / "avatar.mp4"
        
        if is_final:
            from integrations.heygen import HeyGenAvatar
            avatar = HeyGenAvatar(api_key=os.getenv("HEYGEN_API_KEY"))
            
            # Extract talking head sections
            talking_sections = [
                s["text"] for s in context.script["sections"]
                if s["type"] == "TALKING_HEAD" or s["type"] == "HOOK"
            ]
            script_text = " ".join(talking_sections)
            
            video_url = avatar.create_video(
                script_text=script_text,
                avatar_id=os.getenv("HEYGEN_AVATAR_ID"),
                voice_id=os.getenv("HEYGEN_VOICE_ID", "default")
            )
            
            # Download video
            await self._download_file(video_url, output_path)
            self.session_cost += 2.00  # Estimated cost
        else:
            # For drafts, create placeholder
            logger.info("Skipping avatar generation for draft (use --final for production)")
            return None
        
        logger.info(f"Avatar video generated: {output_path}")
        return output_path
    
    async def _generate_broll(
        self,
        context: PipelineContext,
        is_final: bool
    ) -> list[Path]:
        """Generate B-roll clips"""
        
        broll_dir = context.work_dir / "broll"
        broll_dir.mkdir(exist_ok=True)
        
        broll_sections = [
            s for s in context.script["sections"]
            if s["type"] == "B-ROLL"
        ]
        
        if not is_final:
            logger.info(f"Skipping B-roll generation for draft ({len(broll_sections)} clips)")
            return []
        
        from integrations.broll_generator import BRollGenerator
        generator = BRollGenerator(
            api_key=os.getenv("KLING_API_KEY"),
            provider="kling"
        )
        
        paths = []
        for i, section in enumerate(broll_sections):
            output_path = broll_dir / f"clip_{i:03d}.mp4"
            clip_url = generator.generate_clip(
                description=section["description"],
                duration=section.get("duration_seconds", 5)
            )
            await self._download_file(clip_url, output_path)
            paths.append(output_path)
            self.session_cost += 0.30  # Estimated cost per clip
        
        logger.info(f"Generated {len(paths)} B-roll clips")
        return paths
    
    async def _generate_subtitles(self, context: PipelineContext) -> Path:
        """Generate subtitles using local Whisper"""
        
        output_path = context.work_dir / "subtitles.srt"
        
        if not context.voice_path or not context.voice_path.exists():
            logger.warning("No voice track available for subtitle generation")
            return None
        
        from integrations.whisper_local import SubtitleGenerator
        
        generator = SubtitleGenerator(
            model_size=os.getenv("WHISPER_MODEL", "base")
        )
        
        generator.generate_srt(context.voice_path, output_path)
        logger.info(f"Subtitles generated: {output_path}")
        
        return output_path
    
    async def _stage_assembly(
        self,
        context: PipelineContext,
        is_final: bool
    ) -> PipelineContext:
        """Stage 6: Assemble final video and publish"""
        
        from integrations.ffmpeg_assembler import FFmpegAssembler, VideoExporter
        
        assembler = FFmpegAssembler()
        
        # Compose video
        composed_path = context.work_dir / "composed.mp4"
        
        assembler.compose_video(
            avatar_video=context.avatar_path,
            voice_audio=context.voice_path,
            broll_clips=context.broll_paths or [],
            subtitles=context.subtitle_path,
            output_path=composed_path,
            brand_config={
                "avatar_scale": 0.35,
                "font": "Arial",
                "font_size": 24
            }
        )
        
        # Export formats
        exporter = VideoExporter()
        exports_dir = context.work_dir / "exports"
        exports = exporter.export_all(composed_path, exports_dir)
        
        context.final_video_path = exports.get("youtube_hd")
        
        # Publish if configured
        if is_final and os.getenv("AUTO_PUBLISH", "false").lower() == "true":
            context.publish_results = await self._publish(context, exports)
        
        logger.success(f"Final video ready: {context.final_video_path}")
        return context
    
    async def _publish(
        self,
        context: PipelineContext,
        exports: dict[str, Path]
    ) -> dict:
        """Publish to platforms"""
        
        # TODO: Implement publishing logic
        logger.info("Publishing skipped (implement platform integrations)")
        return {"status": "not_implemented"}
    
    async def _download_file(self, url: str, output_path: Path):
        """Download file from URL"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with open(output_path, "wb") as f:
                    f.write(await response.read())


async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Video Pipeline Orchestrator")
    parser.add_argument("--topic-id", required=True, help="Topic ID from Airtable")
    parser.add_argument("--stage", type=int, default=3, help="Starting stage (3-6)")
    parser.add_argument("--final", action="store_true", help="Production quality (paid APIs)")
    
    args = parser.parse_args()
    
    pipeline = VideoPipeline()
    
    context = await pipeline.produce_video(
        topic_id=args.topic_id,
        start_stage=PipelineStage(args.stage),
        is_final=args.final
    )
    
    print(f"\n{'='*50}")
    print(f"Pipeline Complete!")
    print(f"Topic: {context.topic_title}")
    print(f"Output: {context.work_dir}")
    print(f"Final Video: {context.final_video_path}")
    print(f"Session Cost: ${pipeline.session_cost:.2f}")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())
