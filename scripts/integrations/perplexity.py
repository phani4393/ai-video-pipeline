"""
Perplexity API Integration
==========================

Generates comprehensive research briefs for video topics using Perplexity's
online search-enabled LLM.

Usage:
    from integrations.perplexity import PerplexityResearcher
    
    researcher = PerplexityResearcher(api_key="pplx-xxx")
    brief = researcher.research_topic("Claude 3.5 vs GPT-4")
    print(brief)
"""

import os
import json
import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class ResearchBrief:
    """Structured research brief output"""
    topic: str
    content: str
    citations: list[dict]
    model: str
    tokens_used: int


class PerplexityResearcher:
    """
    Client for Perplexity API research brief generation.
    
    Perplexity combines LLM reasoning with real-time web search,
    making it ideal for researching current events and trends.
    """
    
    BASE_URL = "https://api.perplexity.ai/chat/completions"
    
    # Available models (as of 2024)
    MODELS = {
        "small": "llama-3.1-sonar-small-128k-online",
        "large": "llama-3.1-sonar-large-128k-online",
        "huge": "llama-3.1-sonar-huge-128k-online"
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Perplexity client.
        
        Args:
            api_key: Perplexity API key. Falls back to PERPLEXITY_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Perplexity API key required. Set PERPLEXITY_API_KEY env var "
                "or pass api_key parameter."
            )
    
    def research_topic(
        self,
        topic: str,
        angle: Optional[str] = None,
        model: str = "large",
        recency: str = "week"
    ) -> ResearchBrief:
        """
        Generate a comprehensive research brief for a video topic.
        
        Args:
            topic: The main topic to research
            angle: Specific angle or perspective (optional)
            model: Model size - "small", "large", or "huge"
            recency: How recent sources should be - "day", "week", "month", "year"
            
        Returns:
            ResearchBrief with structured content and citations
        """
        
        system_prompt = """You are a research assistant for a tech YouTube channel.
Your job is to create comprehensive, fact-checked research briefs that will be 
used to write video scripts.

For each topic, provide a structured brief with:

# Research Brief: [Topic]

## Executive Summary
2-3 sentences summarizing the key points.

## Key Facts
- Bullet points with specific facts
- Include numbers, dates, and names
- Each fact should be verifiable

## Timeline
- Chronological events related to this topic
- Focus on recent developments

## Key Players
| Entity | Role | Why They Matter |
|--------|------|-----------------|
(Companies, people, products involved)

## Why This Matters
Explain the significance for the target audience (tech enthusiasts, developers, creators).

## Counterpoints & Risks
- Alternative viewpoints
- Potential downsides or criticisms

## Quotable Statistics
- Numbers that make good video hooks
- Comparisons that are easy to visualize

## Sources
Numbered list of sources with URLs.

Be thorough, accurate, and cite everything. The brief should give a scriptwriter 
everything they need to create an engaging, factual video."""

        user_prompt = f"""Research this topic thoroughly for a YouTube video:

TOPIC: {topic}
"""
        if angle:
            user_prompt += f"\nSPECIFIC ANGLE: {angle}"
        
        user_prompt += """

Focus on:
1. The most recent developments (last 7 days if applicable)
2. Concrete facts and statistics
3. Multiple perspectives
4. Quotable information for video hooks

Generate a complete research brief."""

        payload = {
            "model": self.MODELS.get(model, model),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "return_citations": True,
            "search_recency_filter": recency
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            self.BASE_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
        
        data = response.json()
        
        return ResearchBrief(
            topic=topic,
            content=data["choices"][0]["message"]["content"],
            citations=data.get("citations", []),
            model=data["model"],
            tokens_used=data.get("usage", {}).get("total_tokens", 0)
        )
    
    def quick_facts(self, query: str) -> str:
        """
        Quick fact lookup without full research brief format.
        Good for verifying specific claims or getting quick stats.
        """
        
        payload = {
            "model": self.MODELS["small"],
            "messages": [
                {
                    "role": "system",
                    "content": "Provide a concise, factual answer with sources. Be brief."
                },
                {"role": "user", "content": query}
            ],
            "temperature": 0.1,
            "return_citations": True
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            self.BASE_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Perplexity API error: {response.status_code}")
        
        return response.json()["choices"][0]["message"]["content"]


# Standalone function for simple usage
def research_topic(topic: str, angle: str = None) -> str:
    """
    Simple function to research a topic.
    Requires PERPLEXITY_API_KEY environment variable.
    
    Returns the research brief as a string.
    """
    researcher = PerplexityResearcher()
    brief = researcher.research_topic(topic, angle)
    return brief.content


if __name__ == "__main__":
    # Test the integration
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python perplexity.py 'Your topic here'")
        print("\nExample: python perplexity.py 'Claude 3.5 Sonnet release'")
        sys.exit(1)
    
    topic = sys.argv[1]
    
    try:
        researcher = PerplexityResearcher()
        print(f"Researching: {topic}\n")
        brief = researcher.research_topic(topic)
        print(brief.content)
        print(f"\n---\nTokens used: {brief.tokens_used}")
        print(f"Citations: {len(brief.citations)}")
    except ValueError as e:
        print(f"Error: {e}")
        print("Set your API key: $env:PERPLEXITY_API_KEY = 'pplx-xxx'")
