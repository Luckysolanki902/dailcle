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
import markdown

logger = logging.getLogger(__name__)

# System prompt - minimal, focused on quality writing
SYSTEM_PROMPT = """You are a brilliant writer and deep thinker. You write like the best essayists—clear, engaging, profound. Your writing flows naturally, never formulaic.

You explore ideas with genuine curiosity and intellectual depth. You use vivid examples, stories, and analogies. You make complex ideas feel simple and obvious.

Write for someone intelligent but busy—respect their time, reward their attention."""

# User prompt - focused on what we want, not how
USER_PROMPT = """Write a deeply researched, eloquent article on a fascinating topic.

Pick something that will genuinely help the reader think better, live better, or understand the world more clearly. Topics like:
- How humans actually make decisions (and why we're often wrong)
- The psychology behind why we do what we do
- Mental models that change how you see everything
- Communication insights that transform relationships
- Principles from engineering, science, or philosophy that apply to daily life
- Counterintuitive truths about productivity, creativity, or success

YOUR ARTICLE SHOULD:
- Be genuinely interesting to read, not a list or summary
- Go deep—explore the why, the mechanisms, the nuances
- Use real stories, research, and examples
- Have a natural flow—no rigid structure or forced sections
- Be 4000-6000 words—this is a substantial piece worth reading
- Make the reader think "I never saw it that way before"

AT THE END OF YOUR ARTICLE, add this metadata section (I'll extract it with regex):

---
METADATA:
Title: [Your article title]
Category: [One of: psychology, decision-making, leadership, productivity, communication, relationships, cognitive-biases, systems-thinking, learning, creativity, emotional-intelligence, motivation]
Tags: [3-5 comma-separated tags from the category list above]
Summary: [One compelling sentence about what makes this article worth reading]
---

Also find and recommend:
- 5-8 YouTube videos related to this topic (with real URLs from your web search)
- 5-10 articles, papers, or books for further reading

Format these as:
YOUTUBE:
- "Video Title" by Channel Name: https://youtube.com/watch?v=... - Brief description
[repeat]

RESOURCES:
- "Title" by Author (Year): URL - Why it's worth reading
[repeat]"""


class LLMService:
    """Service for generating articles using OpenAI GPT-5.1 with web search."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-5.1"
    
    def generate_article_sync(self, topic_seed: Optional[str] = None, exclusion_prompt: str = "") -> Dict[str, Any]:
        """Generate a free-form eloquent article with web search."""
        logger.info(f"Starting article generation with GPT-5.1, seed: {topic_seed}")
        
        # Build user prompt
        user_prompt = USER_PROMPT
        
        if exclusion_prompt:
            user_prompt = f"{exclusion_prompt}\n\n{user_prompt}"
            logger.info("Added topic exclusions from history")
        
        if topic_seed:
            user_prompt = f"Consider exploring: {topic_seed}\n\n{user_prompt}"
        
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
            
            logger.info(f"Article: {article_data['topic_title']}")
            logger.info(f"Category: {article_data['category']}")
            logger.info(f"Tags: {article_data['tags']}")
            logger.info(f"Word count: {article_data['estimated_wordcount']}")
            
            article_data["generation_metadata"] = {
                "model": self.model,
                "api": "responses",
                "web_search": True,
                "topic_seed": topic_seed
            }
            
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
        """Parse free-form response and extract metadata with regex."""
        
        # Extract metadata block
        metadata_match = re.search(
            r'---\s*\nMETADATA:\s*\n(.*?)\n---',
            content, re.DOTALL | re.IGNORECASE
        )
        
        title = "Untitled Article"
        category = "psychology"
        tags = ["psychology", "learning"]
        summary = ""
        
        if metadata_match:
            metadata_text = metadata_match.group(1)
            
            # Extract title
            title_match = re.search(r'Title:\s*(.+)', metadata_text)
            if title_match:
                title = title_match.group(1).strip()
            
            # Extract category
            cat_match = re.search(r'Category:\s*(.+)', metadata_text)
            if cat_match:
                category = cat_match.group(1).strip().lower()
            
            # Extract tags
            tags_match = re.search(r'Tags:\s*(.+)', metadata_text)
            if tags_match:
                tags = [t.strip().lower() for t in tags_match.group(1).split(',')]
            
            # Extract summary
            summary_match = re.search(r'Summary:\s*(.+)', metadata_text)
            if summary_match:
                summary = summary_match.group(1).strip()
        
        # Extract YouTube videos
        youtube = []
        youtube_section = re.search(r'YOUTUBE:\s*\n(.*?)(?=RESOURCES:|$)', content, re.DOTALL | re.IGNORECASE)
        if youtube_section:
            video_pattern = r'-\s*"([^"]+)"\s*by\s*([^:]+):\s*(https?://[^\s]+)\s*-?\s*(.+)?'
            for match in re.finditer(video_pattern, youtube_section.group(1)):
                youtube.append({
                    "title": match.group(1).strip(),
                    "channel": match.group(2).strip(),
                    "url": match.group(3).strip(),
                    "summary": (match.group(4) or "").strip()
                })
        
        # Extract resources
        papers = []
        resources_section = re.search(r'RESOURCES:\s*\n(.+?)(?=---|$)', content, re.DOTALL | re.IGNORECASE)
        if resources_section:
            resource_pattern = r'-\s*"([^"]+)"\s*by\s*([^(]+)\s*\((\d+)\):\s*(https?://[^\s]+)\s*-?\s*(.+)?'
            for match in re.finditer(resource_pattern, resources_section.group(1)):
                papers.append({
                    "title": match.group(1).strip(),
                    "authors": match.group(2).strip(),
                    "year": int(match.group(3)),
                    "url": match.group(4).strip(),
                    "summary": (match.group(5) or "").strip()
                })
        
        # Get main article (everything before METADATA)
        article_markdown = content
        metadata_start = content.find('---\nMETADATA')
        if metadata_start == -1:
            metadata_start = content.find('---\n\nMETADATA')
        if metadata_start > 0:
            article_markdown = content[:metadata_start].strip()
        
        # Also remove YOUTUBE and RESOURCES sections from article
        article_markdown = re.sub(r'\nYOUTUBE:.*', '', article_markdown, flags=re.DOTALL | re.IGNORECASE)
        article_markdown = re.sub(r'\nRESOURCES:.*', '', article_markdown, flags=re.DOTALL | re.IGNORECASE)
        article_markdown = article_markdown.strip()
        
        # Calculate word count
        word_count = len(article_markdown.split())
        
        # Convert to HTML for email
        article_html = self._markdown_to_html(article_markdown, title)
        
        return {
            "topic_title": title,
            "topic_rationale": summary,
            "category": category,
            "tags": tags[:5],
            "article_markdown": article_markdown,
            "article_html": article_html,
            "email_subject": f"Daily Mentor: {title}",
            "estimated_wordcount": word_count,
            "reading_time_minutes": max(1, word_count // 200),
            "youtube": youtube,
            "papers": papers,
            "exercises": {"beginner": [], "intermediate": [], "advanced": []},
            "notion_page": {"title": title, "blocks": []}
        }
    
    def _markdown_to_html(self, md_content: str, title: str) -> str:
        """Convert markdown to email-safe HTML."""
        try:
            html_body = markdown.markdown(md_content, extensions=['extra'])
        except:
            html_body = f"<pre>{md_content}</pre>"
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Georgia, serif; max-width: 680px; margin: 0 auto; padding: 20px; line-height: 1.7; color: #333;">
    <h1 style="font-size: 28px; color: #1a1a1a; margin-bottom: 30px;">{title}</h1>
    {html_body}
    <hr style="margin: 40px 0; border: none; border-top: 1px solid #ddd;">
    <p style="font-size: 14px; color: #666;">Daily Mentor - Your daily dose of wisdom</p>
</body>
</html>"""
    
    async def generate_article(self, topic_seed: Optional[str] = None, exclusion_prompt: str = "") -> Dict[str, Any]:
        """Async wrapper."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.generate_article_sync(topic_seed, exclusion_prompt)
        )
    
    async def generate_article_with_retry(
        self,
        topic_seed: Optional[str] = None,
        exclusion_prompt: str = "",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Generate with retry logic."""
        for attempt in range(max_retries):
            try:
                return await self.generate_article(topic_seed, exclusion_prompt)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} attempts")
                    raise
                wait_time = 2 ** attempt
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
    
    def validate_article_structure(self, article_data: Dict[str, Any]) -> bool:
        """Minimal validation - we trust the free-form output."""
        logger.info("Article validation passed")
        return True


# Global instance
llm_service = LLMService()
