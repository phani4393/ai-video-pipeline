# Make.com Scenario Setup Guide

Step-by-step guide to setting up the automated topic research pipeline in Make.com.

## Overview

This scenario monitors RSS feeds for AI/tech news, scores topics using GPT-4, and alerts you via Slack when high-potential topics are found.

**What it does:**
```
RSS Feeds → Keyword Filter → GPT-4 Scoring → Score ≥7? → Slack Alert + Airtable
```

## Prerequisites

- Make.com account (free tier works)
- OpenAI API key
- Slack workspace with incoming webhooks
- Airtable account (optional, for queue management)
- Feedly account (optional, or use native RSS module)

---

## Step 1: Create New Scenario

1. Log into [make.com](https://make.com)
2. Click **"Create a new scenario"**
3. Name it: `AI-Video-Topic-Scanner`

---

## Step 2: Add RSS Module (Trigger)

**Module:** RSS → Watch RSS feed items

**Configuration:**
```
URL: https://techcrunch.com/category/artificial-intelligence/feed/
Max results: 10
```

Click the clock icon to set schedule: **Every 15 minutes**

> **Tip:** To monitor multiple feeds, duplicate this module or use Feedly to aggregate.

---

## Step 3: Add Filter (Keyword Check)

Click the **"+"** between modules and select **"Set up a filter"**

**Condition:**
```
{{1.title}} contains AI
OR
{{1.title}} contains GPT
OR  
{{1.title}} contains Claude
OR
{{1.title}} contains startup
OR
{{1.title}} contains funding
OR
{{1.title}} contains launch
```

Label: `Keyword Filter`

---

## Step 4: Add HTTP Module (OpenAI Scoring)

**Module:** HTTP → Make a request

**Configuration:**
```yaml
URL: https://api.openai.com/v1/chat/completions
Method: POST
Headers:
  - Authorization: Bearer {{YOUR_OPENAI_API_KEY}}
  - Content-Type: application/json
```

**Body (JSON):**
```json
{
  "model": "gpt-4-turbo-preview",
  "messages": [
    {
      "role": "system",
      "content": "You are a content strategist for a tech YouTube channel with 500K subscribers. Score topics for viral potential. Return JSON only with: topic, overall_score (1-10), reasoning, suggested_angles (array of 3), risk_factors (array)."
    },
    {
      "role": "user",
      "content": "Score this topic:\n\nTITLE: {{1.title}}\n\nSUMMARY: {{1.description}}\n\nSOURCE: TechCrunch"
    }
  ],
  "response_format": {"type": "json_object"},
  "temperature": 0.3
}
```

**Parse response:** Yes

---

## Step 5: Add JSON Module (Parse Score)

**Module:** JSON → Parse JSON

**JSON String:**
```
{{2.data.choices[].message.content}}
```

This extracts the scoring data from OpenAI's response.

---

## Step 6: Add Router (Score Threshold)

**Module:** Flow control → Router

Add two routes:

### Route 1: High Score (≥7)
**Condition:** `{{3.overall_score}} >= 7`
**Label:** `Approved`

### Route 2: Low Score (<7)
**Condition:** `{{3.overall_score}} < 7`
**Label:** `Rejected`

---

## Step 7: Add Slack Alert (High Score Route)

**Module:** Slack → Create a message

**Connection:** Connect your Slack workspace

**Channel:** Select or enter your channel ID

**Text/Blocks:**
```json
[
  {
    "type": "header",
    "text": {
      "type": "plain_text",
      "text": "🔥 NEW HIGH-POTENTIAL TOPIC DETECTED"
    }
  },
  {
    "type": "section",
    "fields": [
      {
        "type": "mrkdwn",
        "text": "*Topic:*\n{{1.title}}"
      },
      {
        "type": "mrkdwn",
        "text": "*Score:*\n{{3.overall_score}}/10"
      }
    ]
  },
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "*Reasoning:* {{3.reasoning}}"
    }
  },
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "*Suggested Angles:*\n• {{3.suggested_angles[1]}}\n• {{3.suggested_angles[2]}}\n• {{3.suggested_angles[3]}}"
    }
  },
  {
    "type": "context",
    "elements": [
      {
        "type": "mrkdwn",
        "text": "🔗 <{{1.link}}|Read Article>"
      }
    ]
  }
]
```

---

## Step 8: Add Airtable (Optional - Queue Storage)

**Module:** Airtable → Create a record

**Connection:** Connect your Airtable account

**Base:** Select your Video Pipeline base

**Table:** Topic Queue

**Fields:**
```
Title: {{1.title}}
URL: {{1.link}}
Source: TechCrunch
Score: {{3.overall_score}}
Reasoning: {{3.reasoning}}
Angles: {{toString(3.suggested_angles)}}
Status: pending
```

---

## Step 9: Add Logging for Rejected Topics (Low Score Route)

**Module:** Airtable → Create a record

**Table:** Rejected Topics (create if needed)

**Fields:**
```
Title: {{1.title}}
Score: {{3.overall_score}}
Reasoning: {{3.reasoning}}
Rejected At: {{now}}
```

---

## Step 10: Test and Activate

1. Click **"Run once"** to test with live data
2. Check Slack for alerts
3. Verify Airtable records
4. If working, click **"Turn on"** to activate

---

## Final Scenario Flow

```
┌─────────────────┐
│  RSS: Watch     │ (Every 15 min)
│  TechCrunch AI  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Filter:        │
│  Contains AI,   │
│  GPT, startup,  │
│  etc.           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP: OpenAI   │
│  Score Topic    │
│  (GPT-4)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JSON: Parse    │
│  Score Response │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Router:        │
│  Score Check    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│Score  │ │Score  │
│ ≥7    │ │ <7    │
└───┬───┘ └───┬───┘
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│Slack  │ │Log to │
│Alert  │ │Rejected│
│+      │ │Table  │
│Airtable│ └───────┘
└───────┘
```

---

## Adding More RSS Feeds

To monitor multiple sources, you have two options:

### Option A: Duplicate Modules
1. Right-click the RSS module
2. Select "Clone"
3. Change the URL to a new feed
4. Connect to the same filter

### Option B: Use Feedly (Recommended)
1. Create Feedly account
2. Add all your feeds to a "Board"
3. Use Feedly module instead of RSS module
4. Monitor the entire board at once

**Recommended Feeds:**
- TechCrunch AI: `https://techcrunch.com/category/artificial-intelligence/feed/`
- The Verge AI: `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml`
- VentureBeat AI: `https://venturebeat.com/category/ai/feed/`
- Hacker News: `https://news.ycombinator.com/rss`
- Product Hunt: `https://www.producthunt.com/feed`

---

## Troubleshooting

### "Connection refused" on RSS
The feed URL might be blocking bots. Try:
- Using Feedly to aggregate instead
- Adding a User-Agent header

### "Invalid API key" on OpenAI
Check that your key:
- Starts with `sk-`
- Has no extra spaces
- Has available credits

### Slack not receiving messages
- Verify the channel ID is correct
- Check that the Slack app has permission to post
- Test with a simple text message first

### Rate limits
- Increase polling interval to 30 minutes
- Batch process multiple articles per run

---

## Cost Estimate

| Component | Operations/Day | Cost/Day |
|-----------|----------------|----------|
| Make.com | ~100 ops | ~$0 (free tier) |
| OpenAI GPT-4 | ~50 calls | ~$1.50 |
| Airtable | Unlimited | $0 (free tier) |
| Slack | Unlimited | $0 (free) |
| **Total** | | **~$1.50/day** |

**Monthly estimate:** ~$45 for automated topic research
