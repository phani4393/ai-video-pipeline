# Stage 3: Research Automation with Perplexity API

## Overview

Once a topic is approved (score ≥ 7 and human confirmation), this stage automatically generates a comprehensive research brief using the Perplexity API.

## Trigger Flow

```
Airtable "Topic Queue" 
    │
    ├── Status changes to "approved"
    │
    ▼
Make.com Scenario #2
    │
    ├── Fetch topic details
    │
    ▼
Perplexity API
    │
    ├── Deep web research
    │
    ▼
Update Airtable
    │
    └── research_brief field populated
```

## Perplexity API Integration

### API Configuration

```python
import requests
from typing import Optional

class PerplexityResearcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
    def research_topic(self, topic: str, context: Optional[str] = None) -> dict:
        """
        Generate a comprehensive research brief for a video topic.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """You are a research assistant for a tech YouTube channel. 
Your job is to create comprehensive, fact-checked research briefs that will be 
used to write video scripts.

For each topic, provide:
1. EXECUTIVE SUMMARY (2-3 sentences)
2. KEY FACTS (bullet points with sources)
3. TIMELINE/HISTORY (relevant context)
4. STAKEHOLDERS (companies, people involved)
5. IMPLICATIONS (why this matters)
6. COUNTERPOINTS (opposing views or risks)
7. QUOTABLE STATS (numbers that make good hooks)
8. RELATED TOPICS (for potential follow-up videos)

Always cite your sources with URLs."""

        user_prompt = f"""Research the following topic thoroughly:

TOPIC: {topic}

ADDITIONAL CONTEXT: {context or 'None provided'}

Generate a comprehensive research brief that a scriptwriter can use to create 
an engaging, accurate video. Focus on recent developments (last 7 days) but 
include relevant historical context."""

        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "return_citations": True,
            "search_recency_filter": "week"
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload
        )
        
        return response.json()
```

### Research Brief Template

The Perplexity API returns a structured brief like this:

```markdown
# Research Brief: [Topic Title]

## Executive Summary
[2-3 sentence overview of the topic and its significance]

## Key Facts
- Fact 1 [Source: URL]
- Fact 2 [Source: URL]
- Fact 3 [Source: URL]

## Timeline
- **[Date]**: Event 1
- **[Date]**: Event 2
- **[Date]**: Event 3 (most recent)

## Key Stakeholders
| Entity | Role | Relevance |
|--------|------|-----------|
| Company A | Developer | Created the product |
| Person B | CEO | Made announcement |
| Company C | Competitor | Alternative solution |

## Why This Matters
[Explanation of implications for the target audience]

## Counterpoints & Risks
- Risk 1: [Description]
- Alternative view: [Description]

## Quotable Statistics
- "Stat 1" — great for hook
- "Stat 2" — supports main argument
- "Stat 3" — closing impact

## Related Topics for Follow-up
1. [Related topic 1]
2. [Related topic 2]
3. [Related topic 3]

## Sources
1. [Title](URL) - Publication, Date
2. [Title](URL) - Publication, Date
```

## Make.com Scenario #2: Research Trigger

```
[1] Airtable - Watch Records
    ├── Table: Topic Queue
    ├── Trigger: Status = "approved"
    └── Include: title, url, angles, score

[2] HTTP - Perplexity API
    ├── URL: https://api.perplexity.ai/chat/completions
    ├── Method: POST
    ├── Body: [Research prompt with topic details]
    └── Timeout: 60 seconds

[3] Text Parser - Extract Brief
    └── Parse: choices[0].message.content

[4] Airtable - Update Record
    ├── Record ID: {{1.id}}
    ├── research_brief: {{3.content}}
    └── status: "researched"

[5] Slack - Notify Team
    └── Message: "Research complete for: {{1.title}}"
```

## Cost Optimization

### Hybrid Local + Cloud Strategy

For draft iterations and testing:
```python
# Use local LLM for initial drafts (free)
from transformers import pipeline

local_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def local_quick_research(topic: str) -> str:
    """Quick local summary for testing - no API cost"""
    # Scrape top 5 Google results
    # Summarize with local model
    pass
```

For final production:
```python
# Use Perplexity only for approved, final research
if topic.status == "approved" and topic.score >= 8:
    brief = perplexity_researcher.research_topic(topic.title)
```

### Cost Breakdown

| Scenario | API Calls | Cost/Call | Monthly Cost |
|----------|-----------|-----------|--------------|
| All topics researched | 150/month | $0.05 | $7.50 |
| Only score ≥ 7 | 50/month | $0.05 | $2.50 |
| Only score ≥ 8 | 25/month | $0.05 | $1.25 |

## Quality Validation

Before passing to Stage 4 (Scriptwriting), validate:

```python
def validate_research_brief(brief: str) -> bool:
    """Ensure research brief meets quality standards"""
    checks = {
        "has_summary": "## Executive Summary" in brief,
        "has_facts": "## Key Facts" in brief,
        "has_sources": "## Sources" in brief,
        "min_length": len(brief) > 1000,
        "has_citations": brief.count("http") >= 3
    }
    
    return all(checks.values())
```

## Output Format

The research brief is stored in Airtable and passed to Stage 4 as:

```json
{
  "topic_id": "rec123abc",
  "title": "Anthropic launches Claude 3.5 Sonnet",
  "score": 8,
  "approved_angle": "Claude 3.5 vs GPT-4: Which is actually better for coding?",
  "research_brief": "[Full markdown brief]",
  "sources": [
    {"title": "...", "url": "...", "date": "..."},
    {"title": "...", "url": "...", "date": "..."}
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```
