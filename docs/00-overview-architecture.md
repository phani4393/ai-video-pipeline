# AI Video Production Pipeline — Architecture Overview

## Executive Summary

This document describes an autonomous AI-powered video production pipeline that transforms trending topics into publish-ready videos with minimal human intervention. The system eliminates traditional camera shooting and manual editing by leveraging:

- **Automated content intelligence** for topic discovery
- **Neural voice cloning** for synthetic speech
- **AI avatars** for talking-head footage
- **Text-to-video diffusion** for B-roll generation
- **Headless video assembly** via FFmpeg scripting

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AI VIDEO PRODUCTION PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ STAGE 1-2: CONTENT INTELLIGENCE (No-Code / Make.com)                      │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                           │ │
│  │  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐            │ │
│  │  │  RSS    │────▶│ Feedly  │────▶│Make.com │────▶│ OpenAI  │            │ │
│  │  │ Feeds   │     │Aggregat.│     │Scenario │     │ Scoring │            │ │
│  │  └─────────┘     └─────────┘     └─────────┘     └────┬────┘            │ │
│  │                                                       │                  │ │
│  │                         ┌─────────────────────────────┤                  │ │
│  │                         ▼                             ▼                  │ │
│  │                  ┌─────────────┐              ┌─────────────┐           │ │
│  │                  │ Score < 7   │              │ Score ≥ 7   │           │ │
│  │                  │   REJECT    │              │   APPROVE   │           │ │
│  │                  └─────────────┘              └──────┬──────┘           │ │
│  │                                                      │                   │ │
│  │                                               ┌──────▼──────┐           │ │
│  │                                               │   Slack     │           │ │
│  │                                               │   Alert     │           │ │
│  │                                               └──────┬──────┘           │ │
│  │                                                      │                   │ │
│  │                                               ┌──────▼──────┐           │ │
│  │                                               │  Airtable   │           │ │
│  │                                               │   Queue     │◀──────────┤ │
│  └───────────────────────────────────────────────┴─────────────┴───────────┘ │
│                                                         │                     │
│                                              Human Approval Required          │
│                                                         │                     │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ STAGE 3-6: PRODUCTION ENGINE (Python Orchestrator)                        │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │                                                         │                  │ │
│  │  ┌─────────────────────────────────────────────────────┼────────────────┐│ │
│  │  │ STAGE 3: RESEARCH                                   ▼                ││ │
│  │  │ ┌─────────────┐                              ┌─────────────┐         ││ │
│  │  │ │ Perplexity  │◀─────────────────────────────│ Approved    │         ││ │
│  │  │ │    API      │                              │   Topic     │         ││ │
│  │  │ └──────┬──────┘                              └─────────────┘         ││ │
│  │  │        │                                                             ││ │
│  │  │        ▼                                                             ││ │
│  │  │ ┌─────────────┐                                                      ││ │
│  │  │ │  Research   │                                                      ││ │
│  │  │ │   Brief     │                                                      ││ │
│  │  │ └──────┬──────┘                                                      ││ │
│  │  └────────┼─────────────────────────────────────────────────────────────┘│ │
│  │           │                                                               │ │
│  │  ┌────────┼─────────────────────────────────────────────────────────────┐│ │
│  │  │ STAGE 4: SCRIPTWRITING                                               ││ │
│  │  │        ▼                                                             ││ │
│  │  │ ┌─────────────┐     ┌─────────────┐     ┌─────────────┐             ││ │
│  │  │ │   GPT-4 /   │────▶│   Script    │────▶│  Validated  │             ││ │
│  │  │ │   Claude    │     │  Generator  │     │   Script    │             ││ │
│  │  │ └─────────────┘     └─────────────┘     └──────┬──────┘             ││ │
│  │  └────────────────────────────────────────────────┼─────────────────────┘│ │
│  │                                                   │                       │ │
│  │  ┌────────────────────────────────────────────────┼─────────────────────┐│ │
│  │  │ STAGE 5: SYNTHETIC MEDIA                       │                     ││ │
│  │  │                    ┌───────────────────────────┼───────────────┐     ││ │
│  │  │                    │                           │               │     ││ │
│  │  │                    ▼                           ▼               ▼     ││ │
│  │  │            ┌─────────────┐            ┌─────────────┐  ┌───────────┐││ │
│  │  │            │ ElevenLabs  │            │   HeyGen /  │  │  Kling /  │││ │
│  │  │            │   Voice     │            │    Hedra    │  │ Seedance  │││ │
│  │  │            └──────┬──────┘            │   Avatar    │  │  B-Roll   │││ │
│  │  │                   │                   └──────┬──────┘  └─────┬─────┘││ │
│  │  │                   │                          │               │      ││ │
│  │  │                   ▼                          ▼               ▼      ││ │
│  │  │            ┌─────────────┐            ┌─────────────┐  ┌───────────┐││ │
│  │  │            │  voice.mp3  │            │ avatar.mp4  │  │ broll/*.  │││ │
│  │  │            └──────┬──────┘            └──────┬──────┘  └─────┬─────┘││ │
│  │  │                   │                          │               │      ││ │
│  │  │                   │    ┌─────────────┐       │               │      ││ │
│  │  │                   └───▶│   Whisper   │◀──────┘               │      ││ │
│  │  │                        │  (Local)    │                       │      ││ │
│  │  │                        └──────┬──────┘                       │      ││ │
│  │  │                               │                              │      ││ │
│  │  │                               ▼                              │      ││ │
│  │  │                        ┌─────────────┐                       │      ││ │
│  │  │                        │subtitles.srt│                       │      ││ │
│  │  │                        └──────┬──────┘                       │      ││ │
│  │  └───────────────────────────────┼──────────────────────────────┼──────┘│ │
│  │                                  │                              │        │ │
│  │  ┌───────────────────────────────┼──────────────────────────────┼──────┐│ │
│  │  │ STAGE 6: ASSEMBLY & PUBLISHING                               │      ││ │
│  │  │                               │                              │      ││ │
│  │  │                               └──────────────┬───────────────┘      ││ │
│  │  │                                              ▼                      ││ │
│  │  │                                       ┌─────────────┐               ││ │
│  │  │                                       │   FFmpeg    │               ││ │
│  │  │                                       │  Assembly   │               ││ │
│  │  │                                       └──────┬──────┘               ││ │
│  │  │                                              │                      ││ │
│  │  │                    ┌─────────────────────────┼─────────────────────┐││ │
│  │  │                    │                         │                     │││ │
│  │  │                    ▼                         ▼                     ▼││ │
│  │  │             ┌─────────────┐          ┌─────────────┐      ┌───────────┐│
│  │  │             │  YouTube    │          │  LinkedIn   │      │ Instagram ││
│  │  │             │  (16:9)     │          │  (1:1)      │      │  (9:16)   ││
│  │  │             └─────────────┘          └─────────────┘      └───────────┘│
│  │  └───────────────────────────────────────────────────────────────────────┘│
│  └───────────────────────────────────────────────────────────────────────────┘│
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Stage | Component | Responsibility | Technology |
|-------|-----------|----------------|------------|
| 1 | RSS Aggregator | Monitor news sources | Feedly |
| 2 | Topic Scorer | Evaluate viral potential | Make.com + OpenAI |
| 2 | Alert System | Notify team of high-scoring topics | Slack |
| 2 | Topic Queue | Store approved topics | Airtable |
| 3 | Researcher | Generate comprehensive briefs | Perplexity API |
| 4 | Scriptwriter | Create structured scripts | GPT-4 / Claude |
| 5 | Voice Engine | Synthesize speech | ElevenLabs / Kokoro |
| 5 | Avatar Engine | Generate talking head | HeyGen / Hedra |
| 5 | B-Roll Engine | Create supporting visuals | Kling / Seedance |
| 5 | Transcriber | Generate subtitles | Whisper (local) |
| 6 | Assembler | Compose final video | FFmpeg |
| 6 | Publisher | Upload to platforms | Platform APIs |

## Data Flow

```
RSS Article (JSON)
    │
    ▼
Scored Topic (JSON)
{
  "title": "...",
  "score": 8,
  "angles": ["...", "..."],
  "url": "..."
}
    │
    ▼
Research Brief (Markdown)
# Research Brief
## Key Facts
- ...
## Sources
- ...
    │
    ▼
Script (JSON)
{
  "sections": [
    {"type": "HOOK", "text": "...", "timecode": "0:00"},
    {"type": "B-ROLL", "description": "..."},
    ...
  ]
}
    │
    ▼
Media Assets (Files)
├── voice.mp3
├── avatar.mp4
├── broll/
│   ├── clip_001.mp4
│   └── clip_002.mp4
└── subtitles.srt
    │
    ▼
Final Video (MP4)
├── youtube_hd.mp4 (1920x1080)
├── shorts.mp4 (1080x1920)
└── linkedin.mp4 (1080x1080)
```

## Cost Model

### Hybrid Strategy: Local + Cloud

| Process | Draft (Local) | Production (Cloud) |
|---------|---------------|-------------------|
| Voice TTS | Kokoro ($0) | ElevenLabs ($0.30-1.00) |
| Transcription | Whisper ($0) | Whisper ($0) |
| Avatar | Skip | HeyGen ($1-3) |
| B-Roll | Skip | Kling ($0.50-2.00) |
| Research | Skip | Perplexity ($0.05) |
| Scripting | Local LLM ($0) | GPT-4 ($0.10) |
| **Total** | **~$0** | **~$3-6 per video** |

### Monthly Budget Projection (20 videos)

| Item | Cost |
|------|------|
| Topic Research (Make.com) | $10 |
| Perplexity Research | $5 |
| Script Generation | $5 |
| Voice Synthesis | $20 |
| Avatar Generation | $60 |
| B-Roll Generation | $20 |
| **Total** | **~$120/month** |

## Human Touchpoints

The system requires human intervention at exactly **one point**:

```
┌─────────────────────────────────────────────────────┐
│                 HUMAN APPROVAL GATE                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  When: After topic scoring (Stage 2)                │
│  Where: Slack channel                               │
│  Action: React with ✅ to approve, ❌ to reject     │
│  Latency: Typically <4 hours during work hours      │
│                                                      │
│  Everything after approval is fully automated.      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Quality Gates

Each stage has validation before proceeding:

| Stage | Validation |
|-------|------------|
| 2 | Score threshold (≥7) |
| 3 | Research brief completeness (facts, sources, length) |
| 4 | Script structure (required tags, sentence length) |
| 5 | Media file existence and format |
| 6 | Video encoding success, file size sanity |

## Failure Recovery

The pipeline supports resumable execution:

```python
# Resume from Stage 4 if Stage 5 failed
python orchestrator.py --topic-id rec123abc --stage 4
```

All intermediate outputs are persisted to disk:
```
output/{topic_id}/
├── pipeline_context.json   # Resumable state
├── research_brief.md       # Stage 3 output
├── script.json             # Stage 4 output
├── voice.mp3               # Stage 5 output
├── avatar.mp4              # Stage 5 output
├── broll/                  # Stage 5 output
├── subtitles.srt           # Stage 5 output
├── composed.mp4            # Stage 6 intermediate
└── exports/                # Stage 6 final
    ├── youtube_hd.mp4
    ├── shorts.mp4
    └── linkedin.mp4
```

## Security Considerations

1. **API Keys**: Stored in `.env`, never committed to version control
2. **Airtable Access**: Read/write scoped to specific base
3. **Publishing Tokens**: OAuth with minimal scopes
4. **Content Review**: Human approval prevents auto-publishing harmful content
