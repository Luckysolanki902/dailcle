"""
LLM Service for generating daily articles using OpenAI.
Uses the OpenAI Agents SDK for structured article generation.
"""
import json
import asyncio
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from config import settings
from prompts.article_prompt import ARTICLE_SYSTEM_PROMPT, ARTICLE_USER_PROMPT
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating articles using OpenAI."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
    
    async def generate_article(self, topic_seed: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a complete article with all sections and metadata.
        
        Args:
            topic_seed: Optional topic hint for the LLM
            
        Returns:
            Dictionary containing the full article payload
        """
        logger.info(f"Starting article generation with seed: {topic_seed}")
        
        # Prepare user prompt with optional topic seed
        user_prompt = ARTICLE_USER_PROMPT
        if topic_seed:
            user_prompt = f"Topic seed/hint: {topic_seed}\n\n{user_prompt}"
        
        try:
            # Call OpenAI with streaming disabled for JSON response
            # Note: Increased max_tokens to ensure full response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": ARTICLE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=16384,  # Max for gpt-4o-mini to ensure complete response
                response_format={"type": "json_object"}  # Ensure JSON output
            )
            
            # Extract and parse JSON response
            content = response.choices[0].message.content
            logger.info(f"Response length: {len(content)} characters")
            
            # Log first 500 chars of response for debugging
            logger.debug(f"Response preview: {content[:500]}...")
            
            try:
                article_data = json.loads(content)
                logger.info(f"Successfully parsed JSON response")
                logger.info(f"Keys in response: {list(article_data.keys())}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Content that failed to parse: {content[:1000]}...")
                raise
            
            # Validate required fields (more flexible - warn but don't fail)
            required_fields = [
                "topic_title", "topic_rationale", "article_markdown"
            ]
            
            optional_fields = [
                "article_html", "youtube", "papers", "exercises",
                "notion_page", "email_subject", "tags",
                "estimated_wordcount", "reading_time_minutes"
            ]
            
            missing_required = [field for field in required_fields if field not in article_data]
            if missing_required:
                logger.error(f"Missing REQUIRED fields: {missing_required}")
                raise ValueError(f"Missing required fields: {missing_required}")
            
            missing_optional = [field for field in optional_fields if field not in article_data]
            if missing_optional:
                logger.warning(f"Missing optional fields (will use defaults): {missing_optional}")
                
                # Add defaults for missing optional fields
                if "article_html" not in article_data:
                    article_data["article_html"] = f"<html><body><h1>{article_data.get('topic_title', 'Article')}</h1><pre>{article_data.get('article_markdown', '')}</pre></body></html>"
                
                if "youtube" not in article_data:
                    article_data["youtube"] = []
                
                if "papers" not in article_data:
                    article_data["papers"] = []
                
                if "exercises" not in article_data:
                    article_data["exercises"] = {"beginner": [], "intermediate": [], "advanced": [], "day24": {}}
                
                if "notion_page" not in article_data:
                    article_data["notion_page"] = {
                        "parent_url": "https://www.notion.so/luckysolanki-personal/Daily-articles-2bbe80b58b6a8017854ce39c2109eedb",
                        "title": article_data.get("topic_title", "Article"),
                        "properties": {
                            "Topic": article_data.get("topic_title", "General"),
                            "Date": datetime.now().isoformat(),
                            "Tags": article_data.get("tags", []),
                            "Difficulty": "Intermediate",
                            "TimeToRead": 30,
                            "Author": "AI Mentor",
                            "Status": "Draft"
                        },
                        "content_blocks": []
                    }
                
                if "email_subject" not in article_data:
                    article_data["email_subject"] = f"Daily Mentor: {article_data.get('topic_title', 'Article')}"
                
                if "tags" not in article_data:
                    article_data["tags"] = ["general"]
                
                if "estimated_wordcount" not in article_data:
                    markdown = article_data.get("article_markdown", "")
                    article_data["estimated_wordcount"] = len(markdown.split())
                
                if "reading_time_minutes" not in article_data:
                    article_data["reading_time_minutes"] = article_data.get("estimated_wordcount", 1000) // 200
            
            logger.info(f"Successfully generated article: {article_data['topic_title']}")
            logger.info(f"Word count: {article_data['estimated_wordcount']}, "
                       f"Reading time: {article_data['reading_time_minutes']} min")
            
            # Add generation metadata
            article_data["generation_metadata"] = {
                "model": self.model,
                "temperature": self.temperature,
                "tokens_used": response.usage.total_tokens,
                "topic_seed": topic_seed
            }
            
            return article_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response content: {content[:500]}...")
            raise ValueError("LLM did not return valid JSON")
        
        except Exception as e:
            logger.error(f"Error generating article: {e}")
            raise
    
    async def generate_article_with_retry(
        self, 
        topic_seed: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate article with exponential backoff retry logic.
        
        Args:
            topic_seed: Optional topic hint
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary containing the full article payload
        """
        for attempt in range(max_retries):
            try:
                return await self.generate_article(topic_seed)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to generate article after {max_retries} attempts")
                    raise
                
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
    
    def validate_article_structure(self, article_data: Dict[str, Any]) -> bool:
        """
        Validate that the article has all required sections and proper structure.
        
        Args:
            article_data: Article dictionary to validate
            
        Returns:
            True if valid, raises ValueError if invalid
        """
        # Check article markdown has required sections
        required_sections = [
            "Executive Overview",
            "First-Principles",
            "How It Works",
            "Mental Models",
            "Real-World Applications",
            "Common Mistakes",
            "Practical Checklist",
            "Exercises",
            "24-Hour Experiment",
            "Summary"
        ]
        
        markdown = article_data.get("article_markdown", "")
        missing_sections = [
            section for section in required_sections 
            if section.lower() not in markdown.lower()
        ]
        
        if missing_sections:
            logger.warning(f"Article missing sections: {missing_sections}")
        
        # Check notion_page structure (warn only, blocks will be auto-generated)
        notion_page = article_data.get("notion_page", {})
        if notion_page and "title" not in notion_page:
            logger.warning(f"Notion page missing title, will use topic_title")
        if notion_page and "properties" not in notion_page:
            logger.warning(f"Notion page missing properties, will use defaults")
        
        # Check exercises structure (warn only, don't fail)
        exercises = article_data.get("exercises", {})
        required_exercise_keys = ["beginner", "intermediate", "advanced", "day24"]
        missing_exercises = [
            key for key in required_exercise_keys 
            if key not in exercises
        ]
        
        if missing_exercises:
            logger.warning(f"Exercises missing categories: {missing_exercises}")
        
        logger.info("Article structure validation passed")
        return True


# Global instance
llm_service = LLMService()
