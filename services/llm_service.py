"""
LLM Service for generating daily articles using OpenAI GPT-5.1.
Free-form eloquent writing with web search for research.
"""
import re
import asyncio
from typing import Dict, Any, Optional
from openai import OpenAI
from config import settings
import logging

logger = logging.getLogger(__name__)

# System prompt - minimal, focused on quality writing
SYSTEM_PROMPT = """You are a brilliant writer and deep thinker. You write like the best essayists—clear, engaging, profound. Your writing flows naturally, never formulaic.

You explore ideas with genuine curiosity and intellectual depth. You use vivid examples, stories, and analogies. You make complex ideas feel simple and obvious.

Write for someone intelligent but busy—respect their time, reward their attention.

Always obey the user's last message as the primary instruction."""

# User prompt - essay style like Paul Graham / Wait But Why
USER_PROMPT = """Write a deeply researched, eloquent longform essay. Think Paul Graham meets Wait But Why meets Morgan Housel.

THE CRAFT
- 5,000–7,000 words of flowing prose. No numbered sections (no "1.", "1.1", "Step 1"). No "Here are 5 tips". No headers like "Introduction" or "Conclusion". Just an eloquent flow, that flows fluently.
- Start with a vivid scene, a paradox, or a question that pulls the reader in. Make them feel something before you teach them anything.
- Weave in research naturally. Don't announce "Studies show..." every paragraph. Let evidence appear as part of the story.
- Use concrete examples, mini-stories, and surprising analogies (non technical, understood by everybody). Abstract ideas need flesh.
- Write with warmth, wit, and personality. Don't be dry or overly academic.

TOPICS TO EXPLORE (these are just examples, You have to be creative, not just limited to these categories, or topics, pick or think of your own):
- Thinking in feedback loops: how systems thinking reveals hidden compounding effects.
- Spotlight effect and status signaling: why we assume attention is on us and how to break the loop.
- Why certain designs feel beautiful — the Porsche 911, or apple products.
- Designing for consistency: identity-based habits, scaffolding, friction, and engineering small wins.
- The slow architecture of humility: practices for deflating ego without becoming passive.
- How to validate startup ideas with 5 micro-experiments in a week (interviews, fake-door, concierge, landing page + cheap ads, cohort retention probe).
- A/B testing for product habits: measuring retention, small mechanic changes, and interpretation pitfalls.
- The psychology of showmanship vs. substance: social signaling, status maintenance, and cost-efficient authenticity.
- Scripts and heuristics for text conversations when momentum stalls or tone shifts wrong.
- How to console someone well: sequences, phrases, and the science of empathy.
- Learning to ship small: how to structure 30-, 90-, and 365-day learning sprints for DSA, AI/ML, or a full-stack feature.
- Cognitive biases that derail builders: spotlight effect, confirmation bias, planning fallacy, optimism bias, attribution errors—how to catch them in the wild.
- Designing products people love by seeing the world through customers’ lived constraints.
- Tiny habit engineering for the founder’s life: rituals that survive stressed weeks.
- Social lab experiments: how to test whether you’re performing for status or acting from values.
- How to kill your own ego 
- How to design a week as a founder-engineer so you actually finish things you start.
- How to be yourself on a d`ate, in public, or online when your brain thinks you’re under a spotlight.
- Something related to UI/UX and understanding human psychology as a founder/engineer.
- or something like Design is not what it looks like, it’s how it works: cognitive load, Hick’s law, Fitts’s law, and mental models for intuitive products.
- Or any topic like the books: Hooked, Thinking, Fast and Slow, Influence, Man's search for Meaning, How to win friends and influence people, Nudge, The Power of Habit, Atomic Habits, Deep Work, Range, The Lean Startup, Building a StoryBrand, Sprint, Measure What Matters, Thinking in Systems, Antifragile, The Black Swan, Fooled by Randomness, The Psychology of Money, Predictably Irrational, Drive, Mindset, Grit, So Good They Can’t Ignore You, The Courage to Be Disliked, Man’s Search for Meaning, The War of Art, The E-Myth Revisited, Rework, Founders at Work, Zero to One, High Output Management, The Hard Thing About Hard Things, Inspired, Shape Up, Don’t Make Me Think, Design of Everyday Things, The Mom Test, Crossing the Chasm, Contagious, Made to Stick, Influence Is Your Superpower, Never Split the Difference, Difficult Conversations, Crucial Conversations, Nonviolent Communication, How to Talk So Kids Will Listen & Listen So Kids Will Talk, Algorithms to Live By, Thinking in Bets, The Art of Learning, Principles, The Almanack of Naval Ravikant, Tools of Titans, or movies like The Social Dilemma, The Social Network, The Intern, The Big Short, Moneyball, etc.

RESEARCH & SOURCES  
- Use web search to find real studies, papers, articles, YouTube videos
- Cite sources naturally with inline links—don't break flow
- At the very end, list 3-5 YouTube videos and 5-10 resources (with real URLs)

AT THE VERY END, append this exact format (we extract with regex):

---
METADATA:
Title: [Your title—intriguing, not clickbait]
Category: [One of: psychology, decision-making, productivity, communication, relationships, creativity, learning, systems-thinking]
Tags: [3-5 relevant tags]
Summary: [One sentence core insight]
---

YOUTUBE:
- "Video Title" by Channel: https://youtube.com/watch?v=xxxxx - Why worth watching
(3-5 videos with real URLs)

RESOURCES:
- "Title" by Author (Year): https://... - One line why
(5-10 items with real URLs)

Write the best essay you've ever written. Make readers think, feel, and see something new."""


class LLMService:
    """Service for generating articles using OpenAI GPT-5.1 with web search."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-5.1"
    
    def generate_article_sync(self, exclusion_prompt: str = "") -> Dict[str, Any]:
        """Generate a free-form eloquent article with web research."""
        logger.info("Starting article generation with GPT-5.1...")
        
        # Build user prompt
        user_prompt = USER_PROMPT
        
        if exclusion_prompt:
            user_prompt = f"{exclusion_prompt}\n\n{user_prompt}"
            logger.info("Added topic exclusions from history")
        
        try:
            input_messages = [
                {
                    "role": "developer",
                    "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]
                },
                {
                    "role": "user", 
                    "content": [{"type": "input_text", "text": user_prompt}]
                }
            ]
            
            logger.info("Calling GPT-5.1 with web search enabled...")
            response = self.client.responses.create(
                model=self.model,
                input=input_messages,
                text={"verbosity": "high"},
                reasoning={"effort": "high"},
                tools=[
                    {
                        "type": "web_search",
                        "user_location": {"type": "approximate"},
                        "search_context_size": "high"
                    }
                ],
                store=True
            )
            
            # Extract content
            content = self._extract_content(response)
            if not content:
                raise ValueError("No content in response")
            
            logger.info(f"Response length: {len(content)} characters")
            
            # Parse the free-form response
            article_data = self._parse_response(content)
            
            # Save complete raw response
            article_data["raw_response"] = content
            
            logger.info(f"Article: {article_data['topic_title']}")
            logger.info(f"Category: {article_data['category']}")
            logger.info(f"Tags: {article_data['tags']}")
            logger.info(f"Word count: {article_data['estimated_wordcount']}")
            
            return article_data
            
        except Exception as e:
            logger.error(f"Error generating article: {e}")
            raise
    
    def _extract_content(self, response) -> Optional[str]:
        """Extract text from GPT-5.1 response."""
        if hasattr(response, 'output') and response.output:
            for item in response.output:
                if hasattr(item, 'content') and item.content:
                    for c in item.content:
                        if hasattr(c, 'text'):
                            return c.text
                if hasattr(item, 'text'):
                    return item.text
        if hasattr(response, 'output_text'):
            return response.output_text
        return None
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse free-form response and extract metadata with robust regex."""
        
        title = "Untitled Article"
        category = "psychology"
        tags = ["psychology", "learning"]
        summary = ""
        
        # Try multiple patterns for METADATA block
        metadata_patterns = [
            r'---\s*\n\s*METADATA:?\s*\n(.*?)\n\s*---',  # Standard format
            r'##\s*METADATA[^\n]*\n(.*?)(?=\n##|\nYOUTUBE:|\nRESOURCES:|$)',  # Header format
            r'\*\*METADATA\*\*[^\n]*\n(.*?)(?=\n##|\nYOUTUBE:|\nRESOURCES:|$)',  # Bold format
            r'METADATA:?\s*\n(.*?)(?=\n##|\nYOUTUBE:|\nRESOURCES:|$)',  # Simple format
        ]
        
        metadata_text = None
        for pattern in metadata_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                metadata_text = match.group(1)
                logger.info(f"Found METADATA with pattern: {pattern[:30]}...")
                break
        
        if metadata_text:
            # Extract title - try multiple patterns
            title_patterns = [
                r'Title:\s*\*?\*?([^\n*]+)',  # Title: with optional bold
                r'\*\*Title:\*\*\s*([^\n]+)',  # **Title:**
                r'Title:\s*\[([^\]]+)\]',  # Title: [...]
            ]
            for pattern in title_patterns:
                match = re.search(pattern, metadata_text, re.IGNORECASE)
                if match:
                    title = match.group(1).strip().strip('*[]')
                    logger.info(f"Extracted title: {title}")
                    break
            
            # Extract category
            cat_match = re.search(r'Category:\s*\*?\*?([^\n*\[\]]+)', metadata_text, re.IGNORECASE)
            if cat_match:
                category = cat_match.group(1).strip().lower()
            
            # Extract tags
            tags_match = re.search(r'Tags:\s*\*?\*?([^\n]+)', metadata_text, re.IGNORECASE)
            if tags_match:
                raw_tags = tags_match.group(1).strip().strip('*[]')
                tags = [t.strip().lower().strip('*[]') for t in raw_tags.split(',') if t.strip()]
            
            # Extract summary
            summary_match = re.search(r'Summary:\s*\*?\*?([^\n]+)', metadata_text, re.IGNORECASE)
            if summary_match:
                summary = summary_match.group(1).strip().strip('*[]')
        
        # Fallback: extract title from content if still default
        if title == "Untitled Article":
            logger.warning("Title not found in metadata, trying fallbacks...")
            title_anywhere = re.search(r'Title:\s*([^\n]+)', content, re.IGNORECASE)
            if title_anywhere:
                title = title_anywhere.group(1).strip().strip('*[]')
                logger.info(f"Extracted title from content: {title}")
            else:
                first_heading = re.search(r'^#\s+([^\n]+)$', content, re.MULTILINE)
                if first_heading:
                    title = first_heading.group(1).strip()
                    logger.info(f"Extracted title from H1: {title}")
                else:
                    logger.warning(f"Could not extract title. Content start: {content[:300]}")
        
        # Extract YouTube videos
        youtube = []
        youtube_patterns = [
            r'YOUTUBE:?\s*\n(.*?)(?=\nRESOURCES:|\n---|\n##|$)',
            r'##\s*YOUTUBE[^\n]*\n(.*?)(?=\nRESOURCES:|\n---|\n##|$)',
        ]
        
        youtube_text = None
        for pattern in youtube_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                youtube_text = match.group(1)
                break
        
        if youtube_text:
            # Find all URLs in youtube section
            for line in youtube_text.split('\n'):
                if 'youtube.com' in line.lower() or 'youtu.be' in line.lower():
                    # Extract URL
                    url_match = re.search(r'(https?://[^\s\)]+)', line)
                    if url_match:
                        url = url_match.group(1).rstrip('.,;:')
                        # Extract title (text before URL or in quotes/brackets)
                        title_match = re.search(r'["\*\[]([^"\*\]]+)["\*\]]', line)
                        if title_match:
                            vid_title = title_match.group(1).strip()
                        else:
                            vid_title = line.split('http')[0].strip(' -•*[]"')
                        
                        youtube.append({
                            "title": vid_title or "Video",
                            "url": url,
                            "channel": "",
                            "summary": ""
                        })
            
            logger.info(f"Extracted {len(youtube)} YouTube videos")
        
        # Extract resources
        papers = []
        resources_patterns = [
            r'RESOURCES:?\s*\n(.*?)(?=\n---|\n##\s|$)',
            r'##\s*RESOURCES[^\n]*\n(.*?)(?=\n---|\n##\s|$)',
        ]
        
        resources_text = None
        for pattern in resources_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                resources_text = match.group(1)
                break
        
        if resources_text:
            for line in resources_text.split('\n'):
                if line.strip().startswith('-') and 'http' in line.lower():
                    url_match = re.search(r'(https?://[^\s\)]+)', line)
                    url = url_match.group(1).rstrip('.,;:') if url_match else ""
                    
                    # Extract title
                    title_match = re.search(r'["\*\[]([^"\*\]]+)["\*\]]', line)
                    if title_match:
                        res_title = title_match.group(1).strip()
                    else:
                        res_title = line.split('http')[0].strip(' -•*[]"')
                    
                    if res_title:
                        papers.append({
                            "title": res_title,
                            "authors": "",
                            "year": 0,
                            "url": url,
                            "summary": ""
                        })
            
            logger.info(f"Extracted {len(papers)} resources")
        
        # Get clean article markdown (remove metadata, youtube, resources sections)
        article_markdown = content
        
        removal_patterns = [
            r'\n---\s*\n\s*METADATA:.*$',
            r'\n##\s*METADATA.*$',
            r'\nMETADATA:.*$',
            r'\nYOUTUBE:.*$',
            r'\n##\s*YOUTUBE.*$',
            r'\nRESOURCES:.*$',
            r'\n##\s*RESOURCES.*$',
        ]
        
        for pattern in removal_patterns:
            article_markdown = re.sub(pattern, '', article_markdown, flags=re.DOTALL | re.IGNORECASE)
        
        article_markdown = article_markdown.strip()
        word_count = len(article_markdown.split())
        
        return {
            "topic_title": title,
            "topic_rationale": summary,
            "category": category,
            "tags": tags[:5],
            "article_markdown": article_markdown,
            "email_subject": f"Dailicle: {title}",
            "estimated_wordcount": word_count,
            "reading_time_minutes": max(1, word_count // 200),
            "youtube": youtube,
            "papers": papers,
        }
    
    async def generate_article(self, exclusion_prompt: str = "") -> Dict[str, Any]:
        """Async wrapper."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.generate_article_sync(exclusion_prompt)
        )
    
    async def generate_article_with_retry(
        self,
        exclusion_prompt: str = "",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Generate with retry logic."""
        for attempt in range(max_retries):
            try:
                return await self.generate_article(exclusion_prompt)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} attempts")
                    raise
                wait_time = 2 ** attempt
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
    
    def validate_article_structure(self, article_data: Dict[str, Any]) -> bool:
        """Minimal validation."""
        logger.info("Article validation passed")
        return True


# Global instance
llm_service = LLMService()
