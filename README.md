# AI Video Production Pipeline

An automated, end-to-end AI video production system inspired by Vaibhav Sisinty's workflow. This project focuses on building a scalable content creation engine that automates topic research, scriptwriting, avatar generation, and video assembly.

## Project Overview

This system transforms manual video production into an autonomous pipeline using:
- **Automated Topic Research** - RSS monitoring + AI-powered filtering
- **Neural Voice Cloning** - Synthetic voice generation
- **Digital Avatar Creation** - AI-powered talking head videos
- **Headless Video Assembly** - Programmatic editing without traditional software
- **Automated Publishing** - Direct posting to social platforms

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   RSS Feeds     │────▶│   Make.com      │────▶│   OpenAI API    │
│   (Feedly)      │     │   (Automation)  │     │   (Filtering)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Perplexity    │◀────│   Slack Alert   │◀────│   Score ≥ 7     │
│   (Research)    │     │   (Approval)    │     │   Filter        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │
        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Script        │────▶│   Avatar/Voice  │────▶│   Video         │
│   Generation    │     │   Generation    │     │   Assembly      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │   Auto Publish  │
                                                │   (YouTube/etc) │
                                                └─────────────────┘
```

## Getting Started

See the `/docs` folder for detailed setup guides and the `/prompts` folder for the Bridge Framework implementation prompt.

## Cost Structure

| Component | Free/Local Option | Paid Option |
|-----------|-------------------|-------------|
| Voice TTS | Kokoro TTS (local) | ElevenLabs ($5-22/mo) |
| Transcription | Whisper (local) | Cloud APIs |
| Avatar | Hedra (free tier) | HeyGen ($89/mo) |
| Automation | n8n (self-hosted) | Make.com ($9-16/mo) |
| Research | Manual | Perplexity API |
| Video Assembly | FFmpeg (free) | ChatCut |

## License

MIT
