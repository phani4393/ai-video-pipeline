# End-to-End Guide: Creating Your First AI Video

This guide walks you through creating a complete video from idea to publish-ready file.

**Time required:** 30-45 minutes (first time), 10-15 minutes (after setup)

---

## Overview

We'll create a video about "5 AI Tools That Save Hours Every Week" using this flow:

```
Step 1: Setup (one-time)
Step 2: Score the Topic
Step 3: Generate Research
Step 4: Create Script
Step 5: Generate Voice (optional)
Step 6: Generate Subtitles
Step 7: Assemble Video
Step 8: Export for Platforms
```

---

## Step 1: Initial Setup (One-Time)

### 1.1 Install Python Dependencies

```powershell
cd c:\Users\PARUCHPH\Documents\Kiro\Corepulse-extensions-claims\ai-video-pipeline

# Core dependencies (required)
pip install requests python-dotenv

# Optional: For local transcription
pip install openai-whisper

# Optional: For async operations
pip install aiohttp loguru
```

### 1.2 Install FFmpeg

FFmpeg is required for video assembly. Install it:

**Windows (recommended):**
```powershell
winget install FFmpeg.FFmpeg
```

**Or download manually:** https://ffmpeg.org/download.html

Verify installation:
```powershell
ffmpeg -version
```

### 1.3 Configure API Keys

Create your `.env` file:

```powershell
Copy-Item config/settings.example.env .env
```

Edit `.env` with your keys:

```env
# REQUIRED - Minimum to run the pipeline
OPENAI_API_KEY=sk-your-openai-key-here

# OPTIONAL - For better research (skip for testing)
PERPLEXITY_API_KEY=pplx-your-perplexity-key

# OPTIONAL - For voice generation
ELEVENLABS_API_KEY=your-elevenlabs-key
ELEVENLABS_VOICE_ID=your-cloned-voice-id

# OPTIONAL - For avatar videos
HEYGEN_API_KEY=your-heygen-key
HEYGEN_AVATAR_ID=your-avatar-id
```

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Perplexity: https://www.perplexity.ai/settings/api
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys
- HeyGen: https://app.heygen.com/settings

---

## Step 2: Score Your Topic

Before investing time in a video, check if the topic has viral potential.

### 2.1 Run Topic Scoring

```powershell
cd scripts/integrations
python openai_client.py score "5 AI tools that will save you hours every week"
```

### 2.2 Understand the Output

```
Topic: 5 AI tools that will save you hours every week
Score: 8/10
Approved: Yes

Reasoning: High practical value, listicle format performs well, strong 
search intent for productivity tools.

Suggested Angles:
  1. 5 AI Tools That Replaced My $500/Month Software Stack
  2. I Tested 50 AI Tools - These 5 Actually Work
  3. The AI Tools I Use Daily (That You've Never Heard Of)

Risk Factors:
  - Competitive topic - need unique angle
  - Some tools may become outdated quickly
```

**Scoring criteria:**
- **7+**: Good to produce
- **5-6**: Needs a better angle
- **Below 5**: Skip this topic

### 2.3 Save the Score

The score is automatically saved when using the full pipeline. For manual tracking:

```powershell
# Save to file
python openai_client.py score "Your topic" > score_result.txt
```

---

## Step 3: Generate Research Brief

Get comprehensive research to inform your script.

### 3.1 Using Perplexity (Recommended)

If you have a Perplexity API key:

```powershell
python perplexity.py "Best AI productivity tools 2024 features pricing comparison"
```

### 3.2 Using OpenAI (Alternative)

If no Perplexity key, use OpenAI directly:

```powershell
python openai_client.py research "5 AI tools for productivity"
```

### 3.3 What You Get

A structured research brief with:
- Executive summary
- Key facts with sources
- Statistics for hooks
- Comparison data
- Recent developments

**Save the output:**
```powershell
python perplexity.py "Your topic" > research_brief.md
```

---

## Step 4: Create the Script

Generate a structured script optimized for video production.

### 4.1 Run Script Generation

```powershell
python openai_client.py script "5 AI tools that save hours" "5 AI Tools That Replaced My $500/Month Software Stack"
```

Arguments:
1. Topic
2. Selected angle (from Step 2)

### 4.2 Script Structure

The generated script includes scene tags:

```
[HOOK - 0:00]
What if I told you that you could replace $500 worth of monthly 
subscriptions with free AI tools?

[B-ROLL: Money flying away animation]

[TALKING_HEAD - 0:08]
I've been testing AI tools obsessively for the past year. And 
I found 5 that actually deliver on their promises.

[B-ROLL: Screen recording of tool dashboard]

[MAIN_POINT_1 - 0:25]
Number one: Perplexity AI. This replaced my $20/month research 
subscriptions...
```

### 4.3 Save and Review

```powershell
# The script is saved as JSON and readable text
# Check output folder for:
# - script.json (structured data)
# - script.txt (readable version)
```

**Review checklist:**
- [ ] Hook grabs attention in first 3 seconds
- [ ] Each section has clear B-roll suggestions
- [ ] CTA is specific and actionable
- [ ] Total length matches target (8-10 minutes)

---

## Step 5: Generate Voice (Optional)

Convert the script to natural speech audio.

### 5.1 Check Available Voices

```powershell
python elevenlabs.py voices
```

Output:
```
Available voices (25):
  Rachel
    ID: 21m00Tcm4TlvDq8ikWAM
    Category: premade

  Adam
    ID: pNInz6obpgDQGcFmaJgB
    Category: premade
```

### 5.2 Set Your Voice ID

Add to `.env`:
```env
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

### 5.3 Extract Script Text

First, extract only the spoken text from your script:

```python
# Quick Python script to extract spoken text
import json

with open("output/your_topic/03_script.json") as f:
    script = json.load(f)

spoken_text = ""
for section in script["sections"]:
    if section["type"] not in ["B-ROLL", "TRANSITION"]:
        spoken_text += section.get("text", "") + " "

with open("spoken_text.txt", "w") as f:
    f.write(spoken_text)
```

### 5.4 Generate Audio

```powershell
python elevenlabs.py speak "$(Get-Content spoken_text.txt)" voice_output.mp3
```

Or for long scripts, use the streaming endpoint:
```python
from integrations.elevenlabs import ElevenLabsVoice
from pathlib import Path

voice = ElevenLabsVoice()
voice.generate_speech_streaming(
    text=open("spoken_text.txt").read(),
    output_path=Path("voice_output.mp3")
)
```

### 5.5 Check Usage

```powershell
python elevenlabs.py usage
```

Output:
```
Character usage: 12,500 / 100,000
Remaining: 87,500
```

---

## Step 6: Generate Subtitles

Create time-aligned captions from your audio.

### 6.1 Standard Subtitles

```powershell
python whisper_local.py transcribe voice_output.mp3 subtitles.srt
```

### 6.2 Word-Level Captions (TikTok Style)

For animated word-by-word captions:

```powershell
python whisper_local.py words voice_output.mp3 subtitles_animated.srt
```

### 6.3 JSON Format (For Custom Styling)

```powershell
python whisper_local.py json voice_output.mp3 subtitles.json
```

### 6.4 Review the SRT File

```
1
00:00:00,000 --> 00:00:05,000
What if I told you that you could replace
$500 worth of monthly subscriptions?

2
00:00:05,500 --> 00:00:12,000
I've been testing AI tools obsessively
for the past year.
```

---

## Step 7: Assemble the Video

Combine all assets into a final video.

### 7.1 Verify FFmpeg

```powershell
python ffmpeg_assembler.py check
```

Expected output:
```
FFmpeg is available and working!
```

### 7.2 Simple Assembly (Voice + Subtitles)

If you only have voice and subtitles (no avatar):

```powershell
# Create a black background video with your audio and subtitles
python -c "
from pathlib import Path
from integrations.ffmpeg_assembler import FFmpegAssembler

assembler = FFmpegAssembler()

# Create background
assembler.create_color_background(
    Path('background.mp4'),
    duration=480,  # 8 minutes
    color='#1a1a2e'  # Dark blue
)

# Add audio
assembler.replace_audio(
    Path('background.mp4'),
    Path('voice_output.mp3'),
    Path('with_audio.mp4')
)

# Add subtitles
assembler.add_subtitles(
    Path('with_audio.mp4'),
    Path('subtitles.srt'),
    Path('final_video.mp4')
)

print('Video created: final_video.mp4')
"
```

### 7.3 Full Assembly (With Avatar)

If you have an avatar video from HeyGen:

```python
from pathlib import Path
from integrations.ffmpeg_assembler import FFmpegAssembler, BrandConfig

assembler = FFmpegAssembler()

brand = BrandConfig(
    font="Arial",
    font_size=28,
    avatar_scale=0.35,
    avatar_position="bottom-right"
)

assembler.compose_video(
    voice_audio=Path("voice_output.mp3"),
    avatar_video=Path("avatar.mp4"),
    broll_clips=[
        Path("broll/clip_001.mp4"),
        Path("broll/clip_002.mp4")
    ],
    subtitles=Path("subtitles.srt"),
    output_path=Path("composed_video.mp4"),
    brand=brand
)
```

### 7.4 Check the Duration

```powershell
python ffmpeg_assembler.py duration final_video.mp4
```

Output:
```
Duration: 487.32 seconds (8.1 minutes)
```

---

## Step 8: Export for Platforms

Create optimized versions for each platform.

### 8.1 Export All Formats

```powershell
python ffmpeg_assembler.py export final_video.mp4 exports/
```

This creates:
- `youtube_hd.mp4` — 1920x1080 (standard)
- `youtube_4k.mp4` — 3840x2160 (high quality)
- `shorts.mp4` — 1080x1920 (vertical for Shorts/Reels/TikTok)
- `linkedin.mp4` — 1080x1080 (square)

### 8.2 Custom Export

For a specific format:

```python
from pathlib import Path
from integrations.ffmpeg_assembler import FFmpegAssembler

assembler = FFmpegAssembler()

# Create Instagram Reels format
assembler.export_format(
    Path("final_video.mp4"),
    Path("instagram_reel.mp4"),
    width=1080,
    height=1920,
    fps=30,
    bitrate="8M"
)
```

---

## Step 9: Review Final Output

### 9.1 Output Folder Structure

```
output/5_AI_tools_20241115/
├── 01_score.json           # Topic scoring
├── 02_research.md          # Research brief
├── 03_script.json          # Structured script
├── 03_script.txt           # Readable script
├── voice_output.mp3        # Voice track
├── subtitles.srt           # Captions
├── final_video.mp4         # Master file
├── exports/
│   ├── youtube_hd.mp4      # 1920x1080
│   ├── youtube_4k.mp4      # 3840x2160
│   ├── shorts.mp4          # 1080x1920
│   └── linkedin.mp4        # 1080x1080
└── manifest.json           # Production metadata
```

### 9.2 Quality Checklist

Before publishing, verify:

- [ ] Audio is clear and properly leveled
- [ ] Subtitles are synchronized
- [ ] No encoding artifacts
- [ ] Correct aspect ratio for each platform
- [ ] File size is reasonable (< 2GB for YouTube)

---

## Complete Command Reference

### Quick Pipeline (Minimal)

```powershell
# One command to generate score + research + script
python scripts/minimal_pipeline.py --topic "Your video idea"
```

### Individual Steps

```powershell
# 1. Score topic
python scripts/integrations/openai_client.py score "Topic"

# 2. Research
python scripts/integrations/perplexity.py "Topic details"

# 3. Generate script
python scripts/integrations/openai_client.py script "Topic" "Angle"

# 4. Generate voice
python scripts/integrations/elevenlabs.py speak "Text" output.mp3

# 5. Generate subtitles
python scripts/integrations/whisper_local.py transcribe audio.mp3 subs.srt

# 6. Check video duration
python scripts/integrations/ffmpeg_assembler.py duration video.mp4

# 7. Add subtitles to video
python scripts/integrations/ffmpeg_assembler.py subs video.mp4 subs.srt output.mp4

# 8. Export all formats
python scripts/integrations/ffmpeg_assembler.py export video.mp4 exports/
```

---

## Cost Summary for This Video

| Step | API | Cost |
|------|-----|------|
| Topic Scoring | OpenAI GPT-4 | $0.03 |
| Research | Perplexity | $0.05 |
| Script Generation | OpenAI GPT-4 | $0.10 |
| Voice (8 min) | ElevenLabs | $2.40 |
| Subtitles | Whisper (local) | FREE |
| Video Assembly | FFmpeg (local) | FREE |
| **TOTAL** | | **$2.58** |

*Without voice generation (using your own recording): $0.18*

---

## Next Steps

1. **Automate topic discovery:** Set up Make.com to monitor RSS feeds
   - See: `docs/MAKE-SETUP-GUIDE.md`

2. **Create an avatar:** Record 2-3 minutes of footage for HeyGen
   - This enables fully automated talking-head videos

3. **Clone your voice:** Upload samples to ElevenLabs
   - Creates consistent voice across all videos

4. **Set up Airtable:** Track your topic queue
   - See: `scripts/integrations/airtable.py`

---

## Troubleshooting

### "Rate limit exceeded"

Add delays between API calls:
```python
import time
time.sleep(2)  # Wait 2 seconds between calls
```

### "Audio too long for ElevenLabs"

Split the script into chunks:
```python
# Generate in parts
chunks = script_text.split("\n\n")
for i, chunk in enumerate(chunks):
    voice.generate_speech(chunk, Path(f"part_{i}.mp3"))
```

### "Video has no audio"

Check that your audio file exists and has content:
```powershell
ffprobe -v error -show_entries format=duration voice_output.mp3
```

### "Subtitles not showing"

Verify the SRT file format:
- Sequence numbers start at 1
- Timestamps use comma for milliseconds (00:00:00,000)
- Blank line between entries

---

## Example: Full Session

```powershell
# Start a new video project
cd c:\Users\PARUCHPH\Documents\Kiro\Corepulse-extensions-claims\ai-video-pipeline

# Set API key (or use .env)
$env:OPENAI_API_KEY = "sk-xxx"

# Run minimal pipeline
python scripts/minimal_pipeline.py --topic "How to use Claude for coding"

# Check the output
Get-ChildItem output/How_to_use_Claude*

# Review the script
Get-Content output/How_to_use_Claude*/03_script.txt

# Generate voice (if you have ElevenLabs)
$env:ELEVENLABS_API_KEY = "xxx"
$env:ELEVENLABS_VOICE_ID = "xxx"
python scripts/integrations/elevenlabs.py speak "$(Get-Content output/How_to_use_Claude*/03_script.txt)" voice.mp3

# Generate subtitles
python scripts/integrations/whisper_local.py transcribe voice.mp3 subtitles.srt

# Done! You have a script, voice, and subtitles ready for editing
```

---

That's it! You've created your first AI-generated video content. The more you use the pipeline, the faster it gets.
