# Stage 1 & 2: Automated Topic Research & Filtering Pipeline

## Overview

This document details the implementation of the content intelligence and filtering layer — the foundation of the entire video production pipeline.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        CONTENT INTELLIGENCE LAYER                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │  TechCrunch │    │ Product Hunt│    │ Hacker News │              │
│  │    RSS      │    │    RSS      │    │    RSS      │              │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘              │
│         │                  │                  │                      │
│         └──────────────────┼──────────────────┘                      │
│                            ▼                                         │
│                   ┌─────────────────┐                                │
│                   │     FEEDLY      │                                │
│                   │  (Aggregator)   │                                │
│                   └────────┬────────┘                                │
│                            │ Webhook                                 │
│                            ▼                                         │
├──────────────────────────────────────────────────────────────────────┤
│                        FILTERING LAYER                               │
├──────────────────────────────────────────────────────────────────────┤
│                   ┌─────────────────┐                                │
│                   │    MAKE.COM     │                                │
│                   │   (Scenario)    │                                │
│                   └────────┬────────┘                                │
│                            │                                         │
│         ┌──────────────────┼──────────────────┐                      │
│         ▼                  ▼                  ▼                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │  Keyword    │    │ Duplicate   │    │  Recency    │              │
│  │  Filter     │    │  Check      │    │  Filter     │              │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘              │
│         │                  │                  │                      │
│         └──────────────────┼──────────────────┘                      │
│                            ▼                                         │
│                   ┌─────────────────┐                                │
│                   │   OpenAI API    │                                │
│                   │ (Topic Scoring) │                                │
│                   └────────┬────────┘                                │
│                            │                                         │
│              ┌─────────────┴─────────────┐                           │
│              ▼                           ▼                           │
│     ┌─────────────┐             ┌─────────────┐                      │
│     │  Score ≥ 7  │             │  Score < 7  │                      │
│     │   APPROVE   │             │   REJECT    │                      │
│     └──────┬──────┘             └──────┬──────┘                      │
│            │                           │                             │
│            ▼                           ▼                             │
│     ┌─────────────┐             ┌─────────────┐                      │
│     │   Slack     │             │    Log &    │                      │
│     │   Alert     │             │   Discard   │                      │
│     └──────┬──────┘             └─────────────┘                      │
│            │                                                         │
│            ▼                                                         │
│     ┌─────────────┐                                                  │
│     │  Airtable/  │                                                  │
│     │  Notion DB  │────────────▶ [Stage 3: Research]                │
│     └─────────────┘                                                  │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Feedly Configuration

**Feeds to Monitor:**
```yaml
feeds:
  ai_news:
    - https://techcrunch.com/category/artificial-intelligence/feed/
    - https://www.theverge.com/rss/ai-artificial-intelligence/index.xml
    - https://venturebeat.com/category/ai/feed/
    
  startups:
    - https://techcrunch.com/category/startups/feed/
    - https://www.producthunt.com/feed
    - https://news.ycombinator.com/rss
    
  creator_economy:
    - https://www.tubefilter.com/feed/
    - https://blog.hootsuite.com/feed/
```

**Keyword Triggers:**
```
AI, artificial intelligence, GPT, Claude, LLM, machine learning,
startup, funding, raised, million, billion, unicorn,
creator, YouTube, TikTok, monetization, automation,
tool, app, launch, release, announce
```

### 2. Make.com Scenario Blueprint

**Scenario Name:** `AI-Video-Topic-Scanner`

**Module Sequence:**

```
[1] Feedly - Watch New Articles
    ├── Connection: Feedly API
    ├── Feed: "AI & Tech Master Feed"
    └── Polling: Every 15 minutes

[2] Text Parser - Extract Content
    ├── Input: {{1.content}}
    └── Output: Clean text (strip HTML)

[3] Filter - Keyword Matching
    ├── Condition: Content contains ANY of keywords
    └── Keywords: [AI, startup, tool, launch, funding]

[4] Airtable - Check Duplicates
    ├── Table: "Processed Topics"
    ├── Filter: URL = {{1.url}}
    └── If exists: STOP

[5] HTTP - OpenAI Topic Scoring
    ├── URL: https://api.openai.com/v1/chat/completions
    ├── Method: POST
    ├── Headers: 
    │   └── Authorization: Bearer {{OPENAI_API_KEY}}
    └── Body: [See scoring prompt below]

[6] JSON - Parse Response
    └── Extract: score, reasoning, angles

[7] Router
    ├── Route A (score >= 7):
    │   ├── [8] Slack - Send Alert
    │   └── [9] Airtable - Add to Queue
    └── Route B (score < 7):
        └── [10] Airtable - Log Rejection
```

### 3. Topic Scoring Prompt

```json
{
  "model": "gpt-4-turbo-preview",
  "messages": [
    {
      "role": "system",
      "content": "You are a content strategist for a tech YouTube channel with 500K subscribers. Your audience loves: practical AI tutorials, startup stories, tool reviews, and automation workflows. They engage most with content that saves them time or money.\n\nAnalyze topics for viral potential based on:\n1. RELEVANCE (0-10): How well does this match audience interests?\n2. TIMELINESS (0-10): Is this breaking news or evergreen?\n3. UNIQUENESS (0-10): Are competitors already covering this?\n4. HOOK POTENTIAL (0-10): Can this generate curiosity/emotion?\n\nReturn JSON only."
    },
    {
      "role": "user",
      "content": "TOPIC: {{title}}\n\nSUMMARY: {{description}}\n\nSOURCE: {{source}}\n\nPUBLISHED: {{published_date}}\n\n---\n\nScore this topic and provide:\n1. Overall score (1-10, weighted average)\n2. Individual dimension scores\n3. One-sentence reasoning\n4. 3 potential video angles\n5. Risk factors (if any)"
    }
  ],
  "response_format": { "type": "json_object" },
  "temperature": 0.3
}
```

**Expected Response:**
```json
{
  "topic": "Anthropic launches Claude 3.5 Sonnet",
  "overall_score": 8,
  "dimensions": {
    "relevance": 9,
    "timeliness": 10,
    "uniqueness": 6,
    "hook_potential": 8
  },
  "reasoning": "Major AI release from key player, high audience interest, but expect heavy competition coverage within 48 hours.",
  "video_angles": [
    "Claude 3.5 vs GPT-4: Which is actually better for coding?",
    "I replaced ChatGPT with Claude for a week - here's what happened",
    "5 things Claude 3.5 can do that GPT-4 can't"
  ],
  "risk_factors": [
    "High competition - need to publish within 24 hours",
    "Technical topic may need simplification for broader audience"
  ]
}
```

### 4. Slack Alert Template

```
🔥 *NEW HIGH-POTENTIAL TOPIC DETECTED*

*Topic:* {{title}}
*Score:* {{score}}/10
*Source:* {{source}}

*Reasoning:* {{reasoning}}

*Suggested Angles:*
{{#each angles}}
• {{this}}
{{/each}}

*Risks:* {{risks}}

---
⏰ Detected: {{timestamp}}
🔗 Original: {{url}}

React with ✅ to approve for production
React with ❌ to reject
```

### 5. Airtable Schema

**Table: Topic Queue**

| Field | Type | Description |
|-------|------|-------------|
| `id` | Auto | Unique identifier |
| `title` | Text | Article/topic title |
| `url` | URL | Source URL |
| `source` | Single Select | TechCrunch, Verge, etc. |
| `score` | Number | AI-assigned score (1-10) |
| `reasoning` | Long Text | Why this score |
| `angles` | Long Text | JSON array of video angles |
| `status` | Single Select | pending, approved, rejected, produced |
| `approved_by` | Collaborator | Team member who approved |
| `approved_at` | DateTime | Approval timestamp |
| `research_brief` | Long Text | Perplexity output (Stage 3) |
| `created_at` | DateTime | When topic was captured |

### 6. Cost Estimation

| Component | Calls/Day | Cost/Call | Daily Cost |
|-----------|-----------|-----------|------------|
| Feedly | N/A | $0 (free tier) | $0 |
| Make.com | ~100 ops | $0.001 | $0.10 |
| OpenAI GPT-4 | ~50 topics | $0.03 | $1.50 |
| Airtable | N/A | $0 (free tier) | $0 |
| Slack | N/A | $0 (free) | $0 |
| **TOTAL** | | | **~$1.60/day** |

**Monthly estimate:** ~$50 for topic research layer

---

## Implementation Checklist

- [ ] Create Feedly account and add RSS feeds
- [ ] Set up Make.com account and create scenario
- [ ] Configure OpenAI API key in Make.com
- [ ] Create Airtable base with Topic Queue table
- [ ] Set up Slack workspace and incoming webhook
- [ ] Test end-to-end with sample article
- [ ] Monitor for 48 hours and adjust keyword filters
- [ ] Fine-tune scoring prompt based on initial results
