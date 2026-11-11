"""
OpenAI API Integration
======================

Handles topic scoring and script generation using GPT-4.

Usage:
    from integrations.openai_client import TopicScorer, ScriptGenerator
    
    # Score a topic
    scorer = TopicScorer()
    result = scorer.score_topic("Claude 3.5 launches")
    
    # Generate a script
    generator = ScriptGenerator()
    script = generator.generate(topic, research_brief)
"""

import os
import json
import re
from typing import Optional
from dataclasses import dataclass, asdict
import requests


@dataclass
class TopicScore:
    """Result of topic scoring"""
    topic: str
    overall_score: int
    dimensions: dict
    reasoning: str
    suggested_angles: list[str]
    risk_factors: list[str]
    
    @property
    def is_approved(self) -> bool:
        return self.overall_score >= 7


@dataclass
class ScriptSection:
    """A single section of the video script"""
    type: str  # HOOK, TALKING_HEAD, B-ROLL, CTA, etc.
    timecode: str
    text: str = ""
    description: str = ""  # For B-ROLL
    duration_seconds: int = 5


@dataclass 
class VideoScript:
    """Complete video script with metadata"""
    topic_id: str
    title: str
    angle: str
    estimated_duration: float
    sections: list[dict]
    metadata: dict


class OpenAIClient:
    """Base client for OpenAI API calls"""
    
    BASE_URL = "https://api.openai.com/v1/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var "
                "or pass api_key parameter."
            )
        self.model = model
    
    def _call_api(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        json_mode: bool = False
    ) -> str:
        """Make an API call to OpenAI"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        response = requests.post(
            self.BASE_URL,
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
        
        return response.json()["choices"][0]["message"]["content"]


class TopicScorer(OpenAIClient):
    """
    Scores topics for viral potential using GPT-4.
    
    This replicates the Make.com scoring step for local testing
    and for cases where you want more control over the scoring logic.
    """
    
    SYSTEM_PROMPT = """You are a content strategist for a tech YouTube channel with 500K subscribers.

Your audience loves:
- Practical AI tutorials and tool reviews
- Startup stories and funding news
- Automation workflows and productivity hacks
- Comparisons between competing products

Analyze topics for viral potential based on:
1. RELEVANCE (0-10): How well does this match audience interests?
2. TIMELINESS (0-10): Is this breaking news or evergreen?
3. UNIQUENESS (0-10): Are competitors already covering this?
4. HOOK POTENTIAL (0-10): Can this generate curiosity/emotion?

You MUST respond with valid JSON only. No other text."""

    def score_topic(
        self,
        title: str,
        summary: str = "",
        source: str = "",
        threshold: int = 7
    ) -> TopicScore:
        """
        Score a topic for viral potential.
        
        Args:
            title: Article/topic title
            summary: Brief description or article excerpt
            source: Where the topic came from (e.g., "TechCrunch")
            threshold: Score threshold for approval (default 7)
            
        Returns:
            TopicScore with dimensions, reasoning, and suggested angles
        """
        
        user_prompt = f"""Score this topic:

TITLE: {title}
SUMMARY: {summary or 'Not provided'}
SOURCE: {source or 'Unknown'}

Return JSON with this exact structure:
{{
    "topic": "the topic title",
    "overall_score": 8,
    "dimensions": {{
        "relevance": 9,
        "timeliness": 10,
        "uniqueness": 6,
        "hook_potential": 8
    }},
    "reasoning": "One sentence explaining the score",
    "suggested_angles": [
        "Video angle 1",
        "Video angle 2", 
        "Video angle 3"
    ],
    "risk_factors": [
        "Risk 1",
        "Risk 2"
    ]
}}"""

        response = self._call_api(
            self.SYSTEM_PROMPT,
            user_prompt,
            temperature=0.3,
            json_mode=True
        )
        
        data = json.loads(response)
        
        return TopicScore(
            topic=data.get("topic", title),
            overall_score=data["overall_score"],
            dimensions=data["dimensions"],
            reasoning=data["reasoning"],
            suggested_angles=data["suggested_angles"],
            risk_factors=data.get("risk_factors", [])
        )


class ScriptGenerator(OpenAIClient):
    """
    Generates video scripts with scene tags for programmatic editing.
    """
    
    SYSTEM_PROMPT = """You are a viral tech YouTube scriptwriter. Your scripts consistently achieve 
60%+ average view duration because you understand pacing, hooks, and audience psychology.

SCRIPT STRUCTURE:
1. HOOK (0-5 sec): Pattern interrupt or surprising statement
2. CONTEXT (5-30 sec): Set up the situation
3. PROMISE (30-45 sec): What viewer will learn
4. MAIN POINTS (1-7 min): 3-5 key insights with transitions
5. OBJECTION (7-8 min): Address counterarguments
6. CTA (8-8:30): Call to action
7. RETENTION HOOK: Tease next video

WRITING RULES:
- SHORT sentences. One idea per sentence.
- Use "you" and "your" frequently
- Pattern interrupt every 45-60 seconds
- Round numbers for speech ("almost 3 million" not "2,847,392")
- Every sentence must be speakable in one breath

SCENE TAG FORMAT (use exactly):
[HOOK]
Script text here.
[/HOOK]

[B-ROLL: Description of visual]

[TALKING_HEAD]
Script text here.
[/TALKING_HEAD]

[LOWER_THIRD: Text to display]

Output the complete script with all tags."""

    def generate(
        self,
        topic: str,
        angle: str,
        research_brief: str,
        length_minutes: int = 8,
        topic_id: str = "draft"
    ) -> VideoScript:
        """
        Generate a complete video script.
        
        Args:
            topic: The main topic
            angle: Specific angle/perspective for the video
            research_brief: Research content from Perplexity
            length_minutes: Target video length
            topic_id: Identifier for this topic
            
        Returns:
            VideoScript with parsed sections
        """
        
        user_prompt = f"""Write a {length_minutes}-minute video script.

TOPIC: {topic}
ANGLE: {angle}

RESEARCH BRIEF:
{research_brief[:4000]}  # Truncate if too long

Generate the complete script with:
- All scene tags ([HOOK], [TALKING_HEAD], [B-ROLL: description], [CTA])
- Timecodes at each section
- B-roll suggestions for visual variety
- A compelling hook that grabs attention in 3 seconds
- A clear CTA at the end"""

        raw_script = self._call_api(
            self.SYSTEM_PROMPT,
            user_prompt,
            temperature=0.7
        )
        
        # Parse the script into sections
        sections = self._parse_script(raw_script)
        
        # Calculate duration estimate
        word_count = sum(len(s.get("text", "").split()) for s in sections)
        estimated_duration = round(word_count / 150, 1)  # ~150 words per minute
        
        # Extract title from hook or generate one
        title = self._extract_title(angle, sections)
        
        return VideoScript(
            topic_id=topic_id,
            title=title,
            angle=angle,
            estimated_duration=estimated_duration,
            sections=sections,
            metadata={
                "word_count": word_count,
                "section_count": len(sections),
                "tags": self._generate_tags(topic, angle),
                "thumbnail_text": self._generate_thumbnail_text(angle)
            }
        )
    
    def _parse_script(self, raw_script: str) -> list[dict]:
        """Parse raw script text into structured sections"""
        
        sections = []
        current_timecode = "0:00"
        
        # Pattern to match section tags
        tag_pattern = r'\[(\w+)(?::\s*([^\]]+))?\](.*?)\[/\1\]|\[B-ROLL:\s*([^\]]+)\]'
        
        for match in re.finditer(tag_pattern, raw_script, re.DOTALL | re.IGNORECASE):
            if match.group(4):  # B-ROLL tag
                sections.append({
                    "type": "B-ROLL",
                    "timecode": current_timecode,
                    "description": match.group(4).strip(),
                    "duration_seconds": 5
                })
            else:
                section_type = match.group(1).upper()
                text = match.group(3).strip() if match.group(3) else ""
                
                sections.append({
                    "type": section_type,
                    "timecode": current_timecode,
                    "text": text,
                    "duration_seconds": max(5, len(text.split()) // 3)
                })
        
        # If no sections parsed, create a simple structure
        if not sections:
            sections = [{
                "type": "SCRIPT",
                "timecode": "0:00",
                "text": raw_script,
                "duration_seconds": len(raw_script.split()) // 3
            }]
        
        return sections
    
    def _extract_title(self, angle: str, sections: list) -> str:
        """Generate video title from angle"""
        # Clean up the angle to make a title
        title = angle
        if len(title) > 70:
            title = title[:67] + "..."
        return title
    
    def _generate_tags(self, topic: str, angle: str) -> list[str]:
        """Generate relevant tags"""
        words = (topic + " " + angle).lower().split()
        tags = ["AI", "tech", "tutorial"]
        
        keyword_tags = {
            "gpt": "GPT-4", "claude": "Claude", "openai": "OpenAI",
            "anthropic": "Anthropic", "google": "Google", "gemini": "Gemini",
            "coding": "coding", "programming": "programming",
            "startup": "startups", "funding": "funding"
        }
        
        for word in words:
            for keyword, tag in keyword_tags.items():
                if keyword in word and tag not in tags:
                    tags.append(tag)
        
        return tags[:10]
    
    def _generate_thumbnail_text(self, angle: str) -> str:
        """Generate short thumbnail text"""
        # Extract key phrase for thumbnail
        words = angle.upper().split()
        if len(words) <= 4:
            return angle.upper()
        
        # Try to find a punchy phrase
        for phrase in ["VS", "BETTER", "BEST", "NEW", "FREE", "DEAD"]:
            if phrase in words:
                idx = words.index(phrase)
                return " ".join(words[max(0, idx-1):idx+2])
        
        return " ".join(words[:4]) + "?"


# Convenience functions for simple usage
def score_topic(title: str, summary: str = "") -> TopicScore:
    """Score a topic. Requires OPENAI_API_KEY env var."""
    scorer = TopicScorer()
    return scorer.score_topic(title, summary)


def generate_script(topic: str, angle: str, research: str) -> VideoScript:
    """Generate a script. Requires OPENAI_API_KEY env var."""
    generator = ScriptGenerator()
    return generator.generate(topic, angle, research)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Score topic: python openai_client.py score 'Topic title'")
        print("  Generate script: python openai_client.py script 'Topic' 'Angle'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "score" and len(sys.argv) >= 3:
            topic = sys.argv[2]
            scorer = TopicScorer()
            result = scorer.score_topic(topic)
            print(f"Topic: {result.topic}")
            print(f"Score: {result.overall_score}/10")
            print(f"Approved: {'✅ Yes' if result.is_approved else '❌ No'}")
            print(f"Reasoning: {result.reasoning}")
            print(f"\nSuggested Angles:")
            for i, angle in enumerate(result.suggested_angles, 1):
                print(f"  {i}. {angle}")
        
        elif command == "script" and len(sys.argv) >= 4:
            topic = sys.argv[2]
            angle = sys.argv[3]
            generator = ScriptGenerator()
            script = generator.generate(topic, angle, "Research brief placeholder")
            print(f"Title: {script.title}")
            print(f"Duration: ~{script.estimated_duration} minutes")
            print(f"\nScript ({len(script.sections)} sections):")
            for section in script.sections[:5]:
                print(f"\n[{section['type']} - {section['timecode']}]")
                text = section.get('text') or section.get('description', '')
                print(f"  {text[:100]}...")
        
        else:
            print("Invalid command. Use 'score' or 'script'")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Set your API key: $env:OPENAI_API_KEY = 'sk-xxx'")
