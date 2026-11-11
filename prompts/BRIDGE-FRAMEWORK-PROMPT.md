# Bridge Framework Prompt: AI Video Production Pipeline

## The BRIDGE Framework

**B** - Background (Context & Situation)  
**R** - Role (Who the AI should be)  
**I** - Intent (What you want to achieve)  
**D** - Details (Specific requirements & constraints)  
**G** - Guidelines (Rules, format, style)  
**E** - Examples (Reference outputs)

---

## 🎯 MASTER PROMPT: Autonomous AI Video Content Engine

### **B — BACKGROUND**

I am building an autonomous AI-powered video production pipeline that eliminates traditional camera shooting and manual editing. The system should function as a complete content factory that:

- Monitors trending topics in AI, technology, and startups 24/7
- Automatically filters and scores topic ideas based on viral potential
- Generates research briefs for approved topics
- Produces scripts optimized for programmatic video assembly
- Creates synthetic talking-head videos using digital avatars
- Assembles final videos with B-roll, captions, and branding
- Publishes directly to YouTube, LinkedIn, and Instagram

**Current State:** Manual research, writing, and video production taking 8-15 hours per video.

**Target State:** Automated pipeline producing publish-ready videos in under 2 hours with minimal human intervention (only topic approval required).

**Technology Stack Available:**
- Feedly (RSS aggregation)
- Make.com or n8n (workflow automation)
- OpenAI GPT-4 / Claude (LLM processing)
- Perplexity API (deep research)
- ElevenLabs / Kokoro TTS (voice synthesis)
- HeyGen / Hedra / Zois (avatar generation)
- FFmpeg / HyperFrames (video assembly)
- Whisper (local transcription)

---

### **R — ROLE**

Act as a **Senior AI Systems Architect** specializing in:
- Content automation pipelines
- No-code/low-code workflow orchestration
- Synthetic media production (avatars, voice cloning)
- API integration and cost optimization
- Claude Code / Python scripting for pipeline orchestration

You have deep expertise in building scalable creator economy infrastructure and understand both the technical implementation and the content strategy implications of each architectural decision.

---

### **I — INTENT**

Design and help me implement a **6-stage autonomous video production engine**:

1. **Stage 1: Content Intelligence Layer**
   - RSS feed monitoring for AI/tech/startup news
   - Keyword filtering and deduplication
   - Integration with Make.com webhook triggers

2. **Stage 2: AI Topic Scoring & Filtering**
   - LLM-powered viral potential scoring (1-10 scale)
   - Historical performance comparison against past top videos
   - Automatic Slack/Discord alerts for high-scoring topics (≥7)
   - Topic rejection for low scores (<7)

3. **Stage 3: Research Automation**
   - Perplexity API integration for deep topic research
   - Automated research brief generation
   - Source citation and fact-checking layer

4. **Stage 4: Script Generation Engine**
   - Structured prompt framework (Context + Task + Instructions + Delta)
   - Scene tags and sentence boundaries for programmatic editing
   - Multiple angle generation (3 angles × 5 hooks each)
   - Short-form (60s) and long-form (8-12 min) script variants

5. **Stage 5: Synthetic Media Production**
   - Avatar video generation via HeyGen/Hedra API
   - Neural voice synthesis via ElevenLabs
   - B-roll generation prompts for Seedance/Kling AI
   - Local Whisper transcription for subtitle generation

6. **Stage 6: Headless Assembly & Publishing**
   - FFmpeg-based programmatic video composition
   - Dynamic caption overlay with brand styling
   - Automated metadata generation (titles, descriptions, tags)
   - Direct API publishing to YouTube/LinkedIn/Instagram

---

### **D — DETAILS**

**Technical Constraints:**
- Prefer local/open-source tools where possible to minimize API costs
- System must run on Windows 11 with PowerShell
- Budget: $50-100/month for cloud APIs (optimize for hybrid local+cloud)
- Must support batch processing (5-10 videos per week)
- Human-in-the-loop approval only at topic selection stage

**Content Requirements:**
- Primary topics: AI tools, tech startups, creator economy, automation
- Tone: Informative, engaging, accessible (not overly technical)
- Target platforms: YouTube (primary), LinkedIn, Instagram Reels
- Video lengths: 60-90 seconds (short-form), 8-12 minutes (long-form)

**Integration Points:**
- Input: RSS feeds from TechCrunch, The Verge, Product Hunt, Hacker News
- Processing: Make.com scenarios, OpenAI API, Perplexity API
- Output: MP4 files with .SRT subtitles, JSON metadata
- Publishing: YouTube Data API, LinkedIn API, Instagram Graph API

**Performance Targets:**
- Topic scoring latency: <30 seconds
- Research brief generation: <2 minutes
- Script generation: <1 minute
- Avatar video rendering: <10 minutes (via cloud API)
- Total pipeline runtime: <30 minutes per video (excluding human approval wait)

---

### **G — GUIDELINES**

**Architecture Principles:**
1. **Modularity** — Each stage should be independently testable and replaceable
2. **Idempotency** — Re-running any stage should produce consistent results
3. **Cost Awareness** — Local processing for drafts, cloud APIs only for final renders
4. **Observability** — Log every API call, credit consumption, and stage completion
5. **Graceful Degradation** — If one API fails, queue the task and alert; don't crash

**Code Style:**
- Python 3.11+ with type hints
- Use `asyncio` for concurrent API calls
- Configuration via `.env` files and `pydantic` settings
- Comprehensive error handling with retry logic
- Structured logging with `loguru`

**Documentation:**
- Every script must have a docstring explaining its role in the pipeline
- API integrations must document rate limits and cost per call
- Include example inputs/outputs for each stage

**Security:**
- Never hardcode API keys
- Use environment variables or secret managers
- Validate all external inputs before processing

---

### **E — EXAMPLES**

**Example 1: Topic Scoring Prompt**
```
You are a content strategist analyzing viral potential for a tech YouTube channel.

HISTORICAL DATA: The top 10 performing videos were about:
1. "ChatGPT alternatives that are actually better" (2.1M views)
2. "Free AI tools replacing $500/month software" (1.8M views)
3. "How this 22-year-old built a $10M AI startup" (1.5M views)
...

NEW TOPIC: "Anthropic launches Claude 4 with 1M token context window"

Score this topic from 1-10 based on:
- Relevance to audience interests
- Timeliness and news value
- Competitive gap (not over-covered)
- Emotional hook potential

Output JSON:
{
  "topic": "...",
  "score": 8,
  "reasoning": "...",
  "suggested_angles": ["...", "..."],
  "risk_factors": ["..."]
}
```

**Example 2: Script Scene Tags**
```
[HOOK - 0:00-0:05]
What if I told you that you can now run GPT-4 level AI completely offline on your laptop?

[CONTEXT - 0:05-0:30]
Last week, a small startup called Ollama released something that changes everything...
[B-ROLL: Screen recording of Ollama installation]

[MAIN POINT 1 - 0:30-1:30]
Here's why this matters for creators like you and me...
[B-ROLL: Side-by-side comparison chart]
```

**Example 3: Make.com Scenario Structure**
```
Trigger: Feedly → New Article (RSS)
  ↓
Filter: Contains keywords (AI, startup, funding)
  ↓
HTTP Request: POST to OpenAI API (topic scoring)
  ↓
Router:
  - IF score >= 7 → Slack notification + Add to Airtable queue
  - IF score < 7 → Log and discard
  ↓
Perplexity API: Generate research brief (triggered by Airtable new record)
```

---

## 🚀 IMPLEMENTATION STARTING POINT

Given this framework, please help me:

1. **First**: Design the Make.com scenario for Stage 1 & 2 (RSS → Scoring → Alerts)
2. **Second**: Create the Python orchestration script that ties stages 3-6 together
3. **Third**: Build the prompt templates for research and scriptwriting
4. **Fourth**: Set up the local Whisper + FFmpeg assembly pipeline

Start with Stage 1 & 2 — the Automated Topic Research & Filtering system — as this is the foundation that feeds everything else.

---

## 📋 CHECKLIST FOR VALIDATION

Before considering each stage complete, verify:

- [ ] All API integrations tested with sample data
- [ ] Error handling covers rate limits, timeouts, and malformed responses
- [ ] Costs estimated and logged per operation
- [ ] Manual override capability exists for each automated decision
- [ ] Output format validated against downstream stage requirements
- [ ] Documentation includes troubleshooting guide
