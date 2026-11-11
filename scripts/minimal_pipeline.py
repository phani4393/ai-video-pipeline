"""
Minimal Pipeline — Runs with just OpenAI API
=============================================

A simplified pipeline that works with minimal setup.
Only requires: OPENAI_API_KEY

Usage:
    python minimal_pipeline.py --topic "Your video topic here"
    python minimal_pipeline.py --topic "5 AI tools that save hours" --output-dir my_video

"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")


def print_step(step: int, title: str):
    """Print a formatted step header"""
    print(f"\n{'='*60}")
    print(f"  STEP {step}: {title}")
    print(f"{'='*60}\n")


# Fix Windows console encoding
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def main():
    parser = argparse.ArgumentParser(description="Minimal AI Video Pipeline")
    parser.add_argument("--topic", required=True, help="Video topic")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    parser.add_argument("--skip-research", action="store_true", help="Skip Perplexity research")
    args = parser.parse_args()
    
    # Validate OpenAI key
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY not set")
        print("\nSet it with:")
        print('  $env:OPENAI_API_KEY = "sk-your-key-here"')
        print("\nOr create a .env file with:")
        print('  OPENAI_API_KEY=sk-your-key-here')
        sys.exit(1)
    
    # Setup output directory
    topic_slug = args.topic[:30].replace(" ", "_").replace("/", "_")
    output_dir = Path(args.output_dir or f"output/{topic_slug}_{datetime.now().strftime('%Y%m%d_%H%M')}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("  AI VIDEO PIPELINE - MINIMAL MODE")
    print("="*60)
    print(f"\n[TOPIC] {args.topic}")
    print(f"[OUTPUT] {output_dir}")
    
    # =========================================
    # STEP 1: Score the topic
    # =========================================
    print_step(1, "TOPIC SCORING")
    
    from integrations.openai_client import TopicScorer
    
    scorer = TopicScorer()
    score_result = scorer.score_topic(args.topic)
    
    print(f"[SCORE] {score_result.overall_score}/10")
    print(f"[REASONING] {score_result.reasoning}")
    print(f"\n[SUGGESTED ANGLES]")
    for i, angle in enumerate(score_result.suggested_angles, 1):
        print(f"   {i}. {angle}")
    
    if not score_result.is_approved:
        print(f"\n[WARNING] Score below threshold (7). Topic may not perform well.")
        print("   Continuing anyway for demonstration...")
    
    # Save score
    score_file = output_dir / "01_score.json"
    with open(score_file, "w") as f:
        json.dump({
            "topic": score_result.topic,
            "score": score_result.overall_score,
            "dimensions": score_result.dimensions,
            "reasoning": score_result.reasoning,
            "suggested_angles": score_result.suggested_angles,
            "risk_factors": score_result.risk_factors
        }, f, indent=2)
    print(f"\n[SAVED] {score_file}")
    
    # Select best angle
    selected_angle = score_result.suggested_angles[0] if score_result.suggested_angles else args.topic
    print(f"\n[SELECTED ANGLE] {selected_angle}")
    
    # =========================================
    # STEP 2: Research
    # =========================================
    print_step(2, "RESEARCH")
    
    research_brief = None
    
    if not args.skip_research and os.getenv("PERPLEXITY_API_KEY"):
        print("[RESEARCH] Using Perplexity API...")
        try:
            from integrations.perplexity import PerplexityResearcher
            
            researcher = PerplexityResearcher()
            brief = researcher.research_topic(args.topic, selected_angle)
            research_brief = brief.content
            
            # Save research
            research_file = output_dir / "02_research.md"
            with open(research_file, "w", encoding="utf-8") as f:
                f.write(research_brief)
            print(f"[SAVED] {research_file}")
            
        except Exception as e:
            print(f"[WARNING] Perplexity error: {e}")
            print("   Falling back to basic research prompt...")
    
    if not research_brief:
        print("[RESEARCH] Generating basic research with OpenAI...")
        
        # Use OpenAI to generate a research brief
        from integrations.openai_client import OpenAIClient
        
        client = OpenAIClient()
        research_brief = client._call_api(
            system_prompt="You are a research assistant. Generate a comprehensive research brief with facts, statistics, and sources for video content creation.",
            user_prompt=f"""Research this topic for a YouTube video:

TOPIC: {args.topic}
ANGLE: {selected_angle}

Provide:
1. Key facts and statistics
2. Recent developments
3. Different perspectives
4. Quotable information for hooks
5. Potential sources to cite

Be thorough and factual.""",
            temperature=0.3
        )
        
        research_file = output_dir / "02_research.md"
        with open(research_file, "w", encoding="utf-8") as f:
            f.write(f"# Research Brief: {args.topic}\n\n")
            f.write(research_brief)
        print(f"[SAVED] {research_file}")
    
    print(f"\n[RESEARCH BRIEF] {len(research_brief)} characters")
    
    # =========================================
    # STEP 3: Script Generation
    # =========================================
    print_step(3, "SCRIPT GENERATION")
    
    from integrations.openai_client import ScriptGenerator
    
    generator = ScriptGenerator()
    script = generator.generate(
        topic=args.topic,
        angle=selected_angle,
        research_brief=research_brief,
        length_minutes=8,
        topic_id=topic_slug
    )
    
    print(f"[TITLE] {script.title}")
    print(f"[DURATION] {script.estimated_duration} minutes")
    print(f"[SECTIONS] {len(script.sections)}")
    
    # Save script JSON
    script_json = output_dir / "03_script.json"
    with open(script_json, "w") as f:
        json.dump({
            "topic_id": script.topic_id,
            "title": script.title,
            "angle": script.angle,
            "estimated_duration": script.estimated_duration,
            "sections": script.sections,
            "metadata": script.metadata
        }, f, indent=2)
    print(f"[SAVED] {script_json}")
    
    # Save readable script
    script_txt = output_dir / "03_script.txt"
    with open(script_txt, "w", encoding="utf-8") as f:
        f.write(f"# {script.title}\n")
        f.write(f"# Duration: ~{script.estimated_duration} minutes\n")
        f.write(f"# Angle: {script.angle}\n\n")
        f.write("="*60 + "\n\n")
        
        for section in script.sections:
            f.write(f"[{section['type']} - {section['timecode']}]\n")
            if section['type'] == 'B-ROLL':
                f.write(f"  Visual: {section.get('description', '')}\n\n")
            else:
                f.write(f"  {section.get('text', '')}\n\n")
    
    print(f"[SAVED] {script_txt}")
    
    # =========================================
    # STEP 4: Summary
    # =========================================
    print_step(4, "SUMMARY")
    
    # Create manifest
    manifest = {
        "topic": args.topic,
        "angle": selected_angle,
        "score": score_result.overall_score,
        "title": script.title,
        "estimated_duration": script.estimated_duration,
        "generated_at": datetime.now().isoformat(),
        "files": {
            "score": "01_score.json",
            "research": "02_research.md",
            "script_json": "03_script.json",
            "script_txt": "03_script.txt"
        },
        "next_steps": [
            "Generate voice with ElevenLabs (optional)",
            "Generate avatar with HeyGen (optional)",
            "Create B-roll with Kling/Seedance (optional)",
            "Assemble with FFmpeg"
        ]
    }
    
    manifest_file = output_dir / "manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"""
=== PIPELINE COMPLETE ===

Output Directory: {output_dir}

Files Created:
   * 01_score.json    - Topic scoring results
   * 02_research.md   - Research brief
   * 03_script.json   - Structured script
   * 03_script.txt    - Readable script
   * manifest.json    - Pipeline metadata

Script Preview:
   Title: {script.title}
   Duration: ~{script.estimated_duration} minutes
   Score: {score_result.overall_score}/10

Next Steps:
   1. Review the script in 03_script.txt
   2. Add ElevenLabs for voice generation
   3. Add HeyGen for avatar video
   4. Assemble with FFmpeg

Estimated Cost for this run: ~$0.15
""")


if __name__ == "__main__":
    main()
