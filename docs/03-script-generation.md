# Stage 4: Script Generation Engine

## Overview

This stage transforms research briefs into production-ready video scripts optimized for programmatic editing. Scripts include explicit scene tags and sentence boundaries that allow automated video assembly without human editing.

## Script Architecture

### The "Write for the Cut" Principle

Traditional scripts:
```
"So today we're going to talk about something really exciting that just 
happened in the AI world and I think you're going to love it."
```

**Programmatic scripts:**
```
[HOOK - 0:00]
What if I told you GPT-4 just got dethroned?
[/HOOK]

[TRANSITION - 0:03]
[B-ROLL: Side-by-side logos of OpenAI and Anthropic]
[/TRANSITION]

[CONTEXT - 0:05]
Yesterday, Anthropic dropped Claude 3.5 Sonnet.
And the benchmarks are insane.
[/CONTEXT]
```

### Script Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        SCRIPT STRUCTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [HOOK]           0:00 - 0:05    Pattern interrupt/question    │
│  [CONTEXT]        0:05 - 0:30    Setup the situation           │
│  [PROMISE]        0:30 - 0:45    What viewer will learn        │
│  [CREDIBILITY]    0:45 - 1:00    Why you're qualified          │
│  [MAIN_POINT_1]   1:00 - 3:00    First key insight             │
│  [MAIN_POINT_2]   3:00 - 5:00    Second key insight            │
│  [MAIN_POINT_3]   5:00 - 7:00    Third key insight             │
│  [OBJECTION]      7:00 - 8:00    Address counterarguments      │
│  [CTA]            8:00 - 8:30    Call to action                │
│  [OUTRO]          8:30 - 9:00    Sign-off + retention hook     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Prompt Framework: 4-Step Magic Formula

### Structure: RTIO (Role + Task + Instructions + Output)

```
[R] ROLE: You are a viral tech YouTube scriptwriter who has written 
scripts for channels with 10M+ combined subscribers.

[T] TASK: Write a 8-10 minute video script about {{topic}} that will 
maximize watch time and engagement.

[I] INSTRUCTIONS:
- Use the research brief provided as your source of truth
- Write in conversational, second-person voice ("you" not "one")
- Include pattern interrupts every 45-60 seconds
- Embed specific scene tags for programmatic editing
- End sentences at natural breath points
- Include B-roll suggestions for every section

[O] OUTPUT FORMAT:
Return the script in the exact format shown in the example below.
Include timecodes, scene tags, and B-roll notes.
```

## Full Scriptwriting Prompt

```python
SCRIPT_PROMPT = """
You are a viral tech YouTube scriptwriter. Your scripts consistently achieve 
60%+ average view duration because you understand pacing, hooks, and 
audience psychology.

## YOUR TASK
Write a complete video script for the following:

TOPIC: {topic}
ANGLE: {selected_angle}
TARGET LENGTH: {length} minutes
TONE: Informative but conversational, like explaining to a smart friend

## RESEARCH BRIEF
{research_brief}

## SCRIPT REQUIREMENTS

### Structure Rules
1. HOOK (0-5 seconds): Start with a provocative question or surprising statement
2. CONTEXT (5-30 seconds): Set up the situation/news
3. PROMISE (30-45 seconds): Tell viewers exactly what they'll learn
4. 3-5 MAIN POINTS: Each point should be 1-2 minutes with clear transitions
5. OBJECTION HANDLING: Address the biggest counterargument
6. CTA: Clear call to action (subscribe, comment, etc.)
7. RETENTION HOOK: Tease next video or related content

### Writing Rules
1. Write in SHORT sentences. 
2. One idea per sentence.
3. Use "you" and "your" frequently.
4. Include a pattern interrupt (question, analogy, or visual shift) every 45-60 seconds.
5. Numbers should be rounded for speech ("almost 3 million" not "2,847,392")
6. Avoid jargon unless you immediately explain it.
7. Every sentence must be speakable in one breath.

### Scene Tag Format
Use these EXACT tags for programmatic editing:

[HOOK]
Script text here.
[/HOOK]

[B-ROLL: Description of visual]

[TALKING_HEAD]
Script text here.
[/TALKING_HEAD]

[SCREEN_RECORDING: What to show]

[LOWER_THIRD: Text to display]

[TRANSITION: Type - cut/fade/swipe]

## OUTPUT FORMAT

Return ONLY the script with:
- Section headers in [BRACKETS]
- Timecodes at each section start
- B-roll notes inline
- No explanations or meta-commentary

## EXAMPLE FORMAT

[HOOK - 0:00]
What if everything you knew about AI was about to change?
[/HOOK]

[B-ROLL: Dramatic zoom on AI chip]

[CONTEXT - 0:05]
Yesterday, Anthropic dropped a bombshell.
Claude 3.5 Sonnet is here.
And according to the benchmarks, it's beating GPT-4 in almost every category.
[/CONTEXT]

[TALKING_HEAD - 0:20]
Now, I've been testing AI tools for three years.
I've seen a lot of "GPT killers" come and go.
But this one? This one's different.
Let me show you why.
[/TALKING_HEAD]

[TRANSITION: Cut]

[MAIN_POINT_1 - 0:35]
[LOWER_THIRD: "Benchmark Results"]
First, let's talk numbers...
"""
```

## Multi-Angle Generation

For each approved topic, generate 3 script variants:

```python
ANGLES_PROMPT = """
Based on this research brief, generate 3 distinct video angles:

ANGLE 1 - NEWS REACTION
- Format: "Breaking: [What happened] - Here's what it means for you"
- Tone: Urgent, timely
- Best for: First 24 hours after news breaks

ANGLE 2 - TUTORIAL/HOW-TO  
- Format: "How to [do thing] with [new tool/feature]"
- Tone: Practical, actionable
- Best for: Evergreen content

ANGLE 3 - COMPARISON/VS
- Format: "[Thing A] vs [Thing B]: Which is actually better?"
- Tone: Analytical, balanced
- Best for: High search intent

For each angle, provide:
- Title (max 60 characters)
- Thumbnail text (max 4 words)
- 5 hook variations
- Estimated competition level (low/medium/high)
"""
```

## Hook Variations

Generate 5 hooks per angle for A/B testing thumbnails:

```python
HOOKS = [
    # Question hooks
    "What if I told you {surprising_fact}?",
    "Did you know {counterintuitive_fact}?",
    
    # Challenge hooks
    "Everyone's wrong about {topic}.",
    "Stop doing {common_practice}. Here's why.",
    
    # Curiosity hooks
    "{Big company} doesn't want you to know this.",
    "The {topic} secret nobody's talking about.",
    
    # Result hooks
    "I tested {thing} for 30 days. Here's what happened.",
    "This {tool} made me ${amount} in {timeframe}.",
    
    # Urgency hooks
    "{Topic} just changed forever.",
    "You have 48 hours before {consequence}."
]
```

## Short-Form Adaptation

For YouTube Shorts / TikTok / Reels (60-90 seconds):

```python
SHORT_FORM_PROMPT = """
Condense this long-form script into a 60-second version:

RULES:
1. Keep only the single most powerful insight
2. Hook must hit in first 1 second
3. No introduction or credibility section
4. End with open loop (curiosity gap)
5. Include 1-2 B-roll cuts max

FORMAT:
[HOOK - 0:00]
{Immediate pattern interrupt}
[/HOOK]

[MAIN - 0:03]
{Core insight in 45 seconds}
[/MAIN]

[CTA - 0:50]
{Open loop + follow prompt}
[/CTA]
"""
```

## Script Validation

Before passing to Stage 5 (Avatar Generation):

```python
def validate_script(script: str) -> dict:
    """Validate script meets production requirements"""
    
    issues = []
    
    # Check for required sections
    required_tags = ["[HOOK", "[CONTEXT", "[CTA", "[/"]
    for tag in required_tags:
        if tag not in script:
            issues.append(f"Missing required tag: {tag}")
    
    # Check sentence length (speakability)
    sentences = script.split('.')
    long_sentences = [s for s in sentences if len(s.split()) > 25]
    if long_sentences:
        issues.append(f"{len(long_sentences)} sentences too long for speech")
    
    # Check for B-roll coverage
    broll_count = script.count("[B-ROLL:")
    talking_head_count = script.count("[TALKING_HEAD")
    if broll_count < talking_head_count * 0.5:
        issues.append("Insufficient B-roll coverage")
    
    # Estimate duration (150 words per minute)
    word_count = len(script.split())
    estimated_duration = word_count / 150
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "word_count": word_count,
        "estimated_duration_minutes": round(estimated_duration, 1)
    }
```

## Output to Stage 5

```json
{
  "topic_id": "rec123abc",
  "script_version": "v1",
  "format": "long_form",
  "estimated_duration": 8.5,
  "sections": [
    {
      "type": "HOOK",
      "timecode": "0:00",
      "text": "What if I told you GPT-4 just got dethroned?",
      "visual": "talking_head",
      "duration_seconds": 5
    },
    {
      "type": "B-ROLL",
      "timecode": "0:05",
      "description": "Side-by-side logos of OpenAI and Anthropic",
      "duration_seconds": 3
    }
    // ... more sections
  ],
  "metadata": {
    "title": "Claude 3.5 vs GPT-4: The Honest Truth",
    "description": "...",
    "tags": ["AI", "Claude", "GPT-4", "Anthropic"],
    "thumbnail_text": "GPT-4 IS DEAD?"
  }
}
```
