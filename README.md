# AI Video Production Pipeline

An autonomous, AI-powered video production system that transforms trending topics into publish-ready videos with minimal human intervention.

**Repository:** https://github.com/phani4393/ai-video-pipeline

---

## What This Does

This pipeline automates the entire video creation process:

```
Trending Topic → Research → Script → Voice → Avatar → Video → Publish
```

| Stage | What Happens | Tool Used |
|-------|--------------|-----------|
| 1. Topic Discovery | Monitor RSS feeds for trending AI/tech news | Feedly + Make.com |
| 2. Topic Scoring | AI rates topics 1-10 for viral potential | OpenAI GPT-4 |
| 3. Research | Generate comprehensive research brief | Perplexity API |
| 4. Script Writing | Create structured script with scene tags | OpenAI GPT-4 |
| 5. Voice Synthesis | Convert script to natural speech | ElevenLabs |
| 6. Avatar Generation | Create talking-head video | HeyGen |
| 7. Subtitles | Generate time-aligned captions | Whisper (local, free) |
| 8. Assembly | Combine all assets into final video | FFmpeg (local, free) |
| 9. Export | Create platform-specific formats | FFmpeg |

**Human involvement:** Only required at topic approval (Step 2). Everything else is automated.

---

## Quick Start (5 Minutes)

### Prerequisites

- Python 3.10+
- OpenAI API key (minimum requirement)

### Installation

```powershell
# Clone the repository
git clone https://github.com/phani4393/ai-video-pipeline.git
cd ai-video-pipeline

# Install minimal dependencies
pip install requests python-dotenv

# Set your OpenAI API key
$env:OPENAI_API_KEY = "sk-your-key-here"

# Run the minimal pipeline
python scripts/minimal_pipeline.py --topic "5 AI tools that save hours every week"
```

This will:
1. Score your topic (is it worth making a video?)
2. Generate a research brief
3. Create a complete video script
4. Save everything to `output/` folder

---

## Project Structure

```
ai-video-pipeline/
│
├── QUICKSTART.md                 # 15-minute setup guide
├── README.md                     # This file
├── requirements.txt              # Python dependencies
│
├── config/
│   └── settings.example.env      # API keys template (copy to .env)
│
├── docs/
│   ├── 00-overview-architecture.md
│   ├── 01-topic-research-pipeline.md
│   ├── 02-research-automation.md
│   ├── 03-script-generation.md
│   ├── 04-avatar-voice-generation.md
│   ├── 05-video-assembly.md
│   ├── MAKE-SETUP-GUIDE.md       # Make.com automation setup
│   └── END-TO-END-GUIDE.md       # Complete usage tutorial
│
├── make-blueprints/
│   └── topic-scanner-scenario.json  # Make.com scenario config
│
├── prompts/
│   └── BRIDGE-FRAMEWORK-PROMPT.md   # Master prompt for AI assistants
│
└── scripts/
    ├── test_run.py               # Simulation (no API keys needed)
    ├── minimal_pipeline.py       # Quick test (OpenAI only)
    ├── orchestrator.py           # Full production pipeline
    │
    └── integrations/             # All API clients
        ├── __init__.py
        ├── openai_client.py      # Topic scoring + script generation
        ├── perplexity.py         # Research brief generation
        ├── elevenlabs.py         # Voice synthesis
        ├── heygen.py             # Avatar video generation
        ├── whisper_local.py      # Local transcription (FREE)
        ├── ffmpeg_assembler.py   # Video composition (FREE)
        └── airtable.py           # Topic queue database
```

---

## Three Ways to Use This

### Option 1: Test Mode (No API Keys)

See how the pipeline works without spending money:

```powershell
python scripts/test_run.py
```

Creates mock outputs showing the complete flow.

### Option 2: Minimal Mode (OpenAI Only)

Test with real AI but minimal cost (~$0.15 per run):

```powershell
$env:OPENAI_API_KEY = "sk-your-key"
python scripts/minimal_pipeline.py --topic "Your video idea"
```

Produces: Topic score, research brief, and complete script.

### Option 3: Full Production Mode

Complete automation with all integrations:

```powershell
# Set all API keys in .env file
python scripts/orchestrator.py --topic-id rec123abc --final
```

Produces: Publish-ready video files for YouTube, Shorts, and LinkedIn.

---

## API Keys Required

| Service | Required? | What It Does | Cost |
|---------|-----------|--------------|------|
| OpenAI | **Yes** | Scoring + Scripts | ~$0.15/video |
| Perplexity | Optional | Deep research | ~$0.05/video |
| ElevenLabs | Optional | Voice synthesis | ~$0.50/min |
| HeyGen | Optional | Avatar videos | ~$2.00/min |
| Airtable | Optional | Topic queue DB | Free tier |

**Minimum to get started:** Just OpenAI (~$0.15 per video concept)

### Setting Up API Keys

1. Copy the example config:
   ```powershell
   Copy-Item config/settings.example.env .env
   ```

2. Edit `.env` with your keys:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   PERPLEXITY_API_KEY=pplx-your-key-here
   ELEVENLABS_API_KEY=your-key-here
   ELEVENLABS_VOICE_ID=your-voice-id
   HEYGEN_API_KEY=your-key-here
   HEYGEN_AVATAR_ID=your-avatar-id
   ```

---

## Individual Tool Usage

Each integration can be used standalone from the command line:

### Score a Topic

```powershell
cd scripts/integrations
python openai_client.py score "Claude 3.5 vs GPT-4: Which is better?"
```

Output:
```
Topic: Claude 3.5 vs GPT-4: Which is better?
Score: 8/10
Approved: Yes
Reasoning: High-interest comparison with strong search intent
Suggested Angles:
  1. Claude 3.5 vs GPT-4: The Honest Truth
  2. I tested both for a week - here's what happened
  3. 5 things Claude does better than GPT-4
```

### Generate Research

```powershell
python perplexity.py "Latest features in Claude 3.5 Sonnet"
```

### Generate Voice

```powershell
python elevenlabs.py voices                    # List available voices
python elevenlabs.py speak "Hello world" test.mp3  # Generate audio
```

### Generate Subtitles (Free)

```powershell
python whisper_local.py transcribe audio.mp3 output.srt
```

### Check FFmpeg

```powershell
python ffmpeg_assembler.py check
```

---

## Automated Topic Discovery (Make.com)

Set up hands-free topic monitoring:

1. **Feedly** monitors RSS feeds (TechCrunch, Verge, Hacker News)
2. **Make.com** filters articles by keywords
3. **OpenAI** scores each topic for viral potential
4. **Slack** alerts you when score ≥ 7
5. **Airtable** stores approved topics

See `docs/MAKE-SETUP-GUIDE.md` for step-by-step setup.

---

## Cost Breakdown

### Per Video Estimate

| Component | Local Option | Cloud Option |
|-----------|--------------|--------------|
| Topic Scoring | - | $0.03 (OpenAI) |
| Research | - | $0.05 (Perplexity) |
| Script | - | $0.10 (OpenAI) |
| Voice (8 min) | Kokoro (free) | $2.40 (ElevenLabs) |
| Avatar (8 min) | Skip | $8.00 (HeyGen) |
| Subtitles | Whisper (free) | - |
| Assembly | FFmpeg (free) | - |
| **Total** | **~$0.18** | **~$10.58** |

### Monthly Estimate (20 videos)

- **Minimal (scripts only):** ~$4/month
- **With voice:** ~$50/month
- **Full production:** ~$200/month

---

## Output Files

After running the pipeline, you get:

```
output/{topic_id}/
├── 01_score.json         # Topic scoring results
├── 02_research.md        # Research brief
├── 03_script.json        # Structured script
├── 03_script.txt         # Readable script
├── voice.mp3             # Audio track
├── avatar.mp4            # Talking head video
├── broll/                # B-roll clips
│   ├── clip_001.mp4
│   └── clip_002.mp4
├── subtitles.srt         # Captions
├── composed.mp4          # Final master
├── exports/              # Platform variants
│   ├── youtube_hd.mp4    # 1920x1080
│   ├── youtube_4k.mp4    # 3840x2160
│   ├── shorts.mp4        # 1080x1920 (vertical)
│   └── linkedin.mp4      # 1080x1080 (square)
└── manifest.json         # Production metadata
```

---

## Troubleshooting

### "OPENAI_API_KEY not set"

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-your-key"

# Or create .env file
echo "OPENAI_API_KEY=sk-your-key" > .env
```

### "FFmpeg not found"

Install FFmpeg:
- **Windows:** `winget install FFmpeg.FFmpeg`
- **Mac:** `brew install ffmpeg`
- **Linux:** `apt install ffmpeg`

### "No module named 'whisper'"

```powershell
pip install openai-whisper
```

### Rate limits

Increase polling interval or add delays between API calls.

---

## Documentation

| Guide | Description |
|-------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | 15-minute setup |
| [END-TO-END-GUIDE.md](docs/END-TO-END-GUIDE.md) | Complete tutorial |
| [MAKE-SETUP-GUIDE.md](docs/MAKE-SETUP-GUIDE.md) | Automation setup |
| [BRIDGE-FRAMEWORK-PROMPT.md](prompts/BRIDGE-FRAMEWORK-PROMPT.md) | Master AI prompt |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI VIDEO PIPELINE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [RSS Feeds]  ──▶  [Make.com]  ──▶  [OpenAI]  ──▶  [Slack]   │
│                                         │                       │
│                                         ▼                       │
│                                   Score ≥ 7?                    │
│                                    │     │                      │
│                                   Yes    No                     │
│                                    │     │                      │
│                                    ▼     ▼                      │
│                              [Airtable] [Log]                   │
│                                    │                            │
│                        ┌──────────┴──────────┐                  │
│                        ▼                     ▼                  │
│                  [Perplexity]          [OpenAI GPT-4]           │
│                   Research                Script                │
│                        │                     │                  │
│                        └──────────┬──────────┘                  │
│                                   ▼                             │
│              ┌────────────────────┼────────────────────┐       │
│              ▼                    ▼                    ▼       │
│        [ElevenLabs]          [HeyGen]           [Kling AI]     │
│          Voice               Avatar              B-Roll        │
│              │                    │                    │       │
│              └────────────────────┼────────────────────┘       │
│                                   ▼                             │
│                          [Whisper + FFmpeg]                     │
│                          Subtitles + Assembly                   │
│                                   │                             │
│                                   ▼                             │
│                         [YouTube / LinkedIn]                    │
│                             Publish                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## License

MIT License - Use freely for personal and commercial projects.

---

## Credits

Inspired by [Vaibhav Sisinty's](https://www.youtube.com/@vaibhavsisinty) autonomous video production workflow.
