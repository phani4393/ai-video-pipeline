# Quick Start Guide

Get the AI Video Pipeline running in 15 minutes.

## Prerequisites

- Python 3.10+
- FFmpeg installed ([download](https://ffmpeg.org/download.html))
- At least one API key (OpenAI minimum)

## Step 1: Install Dependencies

```powershell
cd c:\Users\PARUCHPH\Documents\Kiro\Corepulse-extensions-claims\ai-video-pipeline

# Create virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install requests python-dotenv
```

**Optional dependencies (install as needed):**

```powershell
# For local transcription (Whisper)
pip install openai-whisper

# For full pipeline
pip install aiohttp loguru pydantic
```

## Step 2: Configure API Keys

Create a `.env` file in the project root:

```powershell
# Copy the example config
Copy-Item config/settings.example.env .env
```

Edit `.env` with your keys (minimum needed):

```env
# Required for scoring and scripts
OPENAI_API_KEY=sk-your-key-here

# Optional: For research (skip if doing manually)
PERPLEXITY_API_KEY=pplx-your-key-here

# Optional: For voice (skip for testing)
ELEVENLABS_API_KEY=your-key-here
ELEVENLABS_VOICE_ID=your-voice-id

# Optional: For avatars (skip for testing)
HEYGEN_API_KEY=your-key-here
HEYGEN_AVATAR_ID=your-avatar-id
```

## Step 3: Test Individual Components

Each integration can be tested standalone:

### Test Topic Scoring (OpenAI)

```powershell
cd scripts/integrations
python openai_client.py score "Claude 3.5 vs GPT-4 benchmark comparison"
```

Expected output:
```
Topic: Claude 3.5 vs GPT-4 benchmark comparison
Score: 8/10
Approved: ✅ Yes
Reasoning: High-interest AI comparison topic with strong search intent
```

### Test Research (Perplexity)

```powershell
python perplexity.py "What are the latest features in Claude 3.5 Sonnet?"
```

### Test Voice Synthesis (ElevenLabs)

```powershell
python elevenlabs.py voices  # List available voices
python elevenlabs.py speak "Hello, this is a test" test_output.mp3
```

### Test Local Transcription (Whisper)

```powershell
python whisper_local.py transcribe audio.mp3 output.srt
```

### Test FFmpeg

```powershell
python ffmpeg_assembler.py check  # Verify FFmpeg is installed
```

## Step 4: Run Test Pipeline

Run the simulation (no API calls):

```powershell
cd c:\Users\PARUCHPH\Documents\Kiro\Corepulse-extensions-claims\ai-video-pipeline
python scripts/test_run.py
```

This creates mock outputs in `output/test_run/` to show the pipeline flow.

## Step 5: Run Real Pipeline (Minimal)

Create a simple end-to-end test with just OpenAI:

```powershell
# Run the minimal pipeline script
python scripts/minimal_pipeline.py --topic "5 AI tools that will save you hours every week"
```

This will:
1. Score your topic
2. Generate a research brief (or use OpenAI if no Perplexity key)
3. Create a video script
4. Output all files to `output/`

---

## Make.com Setup (Optional)

If you want to set up the automated RSS monitoring:

### 1. Create Feedly Account

1. Go to [feedly.com](https://feedly.com)
2. Create a free account
3. Add feeds:
   - `https://techcrunch.com/category/artificial-intelligence/feed/`
   - `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml`
   - `https://news.ycombinator.com/rss`

### 2. Create Make.com Scenario

1. Go to [make.com](https://make.com)
2. Create new scenario
3. Add modules in this order:

```
[Feedly: Watch Articles] 
    → [Filter: Keywords] 
    → [HTTP: OpenAI Scoring] 
    → [Router]
        → Score ≥ 7: [Slack: Send Alert]
        → Score < 7: [Airtable: Log Rejected]
```

See `make-blueprints/topic-scanner-scenario.json` for the full configuration.

### 3. Create Airtable Base

1. Go to [airtable.com](https://airtable.com)
2. Create new base named "Video Pipeline"
3. Create table "Topic Queue" with fields:
   - `Title` (Single line text)
   - `URL` (URL)
   - `Source` (Single select: TechCrunch, Verge, etc.)
   - `Score` (Number)
   - `Reasoning` (Long text)
   - `Angles` (Long text)
   - `Status` (Single select: pending, approved, rejected, researched, produced)
   - `Research Brief` (Long text)

---

## Troubleshooting

### "FFmpeg not found"

Install FFmpeg:
- **Windows:** `winget install FFmpeg.FFmpeg` or download from ffmpeg.org
- **Mac:** `brew install ffmpeg`
- **Linux:** `apt install ffmpeg`

### "No module named 'whisper'"

```powershell
pip install openai-whisper
```

### "OpenAI API error: 401"

Your API key is invalid. Check:
1. Key starts with `sk-`
2. No extra spaces in `.env`
3. Account has credits

### "Rate limit exceeded"

Wait a minute and try again, or upgrade your API plan.

---

## Cost Estimates

| Operation | API | Cost |
|-----------|-----|------|
| Topic scoring | OpenAI GPT-4 | ~$0.03 |
| Research brief | Perplexity | ~$0.05 |
| Script generation | OpenAI GPT-4 | ~$0.10 |
| Voice (1 min) | ElevenLabs | ~$0.30 |
| Avatar (1 min) | HeyGen | ~$1.00 |
| Local transcription | Whisper | FREE |
| Video assembly | FFmpeg | FREE |

**Estimated total per video:** $1.50-5.00 depending on length and features.

---

## Next Steps

1. **Start simple:** Use just OpenAI for scoring and scripts
2. **Add research:** Add Perplexity for better briefs
3. **Add voice:** Add ElevenLabs for audio
4. **Add avatars:** Add HeyGen when you're ready for full automation
5. **Automate:** Set up Make.com for hands-off topic discovery

The pipeline is modular - you can use any subset of the tools.
