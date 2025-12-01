"""
Notion Service for creating and managing article pages.
Uses the official Notion SDK to create formatted subpages.
"""
from typing import Dict, Any, List
from notion_client import AsyncClient
from config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class NotionService:
    """Service for creating Notion pages for articles."""
    
    def __init__(self):
        self.client = AsyncClient(auth=settings.notion_api_key)
        self.parent_page_id = settings.notion_parent_page_id
    
    def _convert_markdown_to_blocks(self, markdown: str, max_blocks: int = 100) -> List[Dict]:
        """
        Convert markdown text to Notion blocks.
        Simple converter for headings and paragraphs.
        
        Args:
            markdown: Markdown formatted text
            max_blocks: Maximum number of blocks to create
            
        Returns:
            List of Notion block objects
        """
        blocks = []
        lines = markdown.split('\n')
        current_paragraph = []
        
        for line in lines:
            if len(blocks) >= max_blocks:
                break
                
            line = line.strip()
            
            if not line:
                # Empty line - flush current paragraph
                if current_paragraph:
                    text = ' '.join(current_paragraph)
                    blocks.append(self._create_paragraph_block(text))
                    current_paragraph = []
                continue
            
            # Check for headings
            if line.startswith('### '):
                if current_paragraph:
                    blocks.append(self._create_paragraph_block(' '.join(current_paragraph)))
                    current_paragraph = []
                blocks.append(self._create_heading_block(line[4:], level=3))
            elif line.startswith('## '):
                if current_paragraph:
                    blocks.append(self._create_paragraph_block(' '.join(current_paragraph)))
                    current_paragraph = []
                blocks.append(self._create_heading_block(line[3:], level=2))
            elif line.startswith('# '):
                if current_paragraph:
                    blocks.append(self._create_paragraph_block(' '.join(current_paragraph)))
                    current_paragraph = []
                blocks.append(self._create_heading_block(line[2:], level=1))
            elif line.startswith('> '):
                # Blockquote - convert to callout
                if current_paragraph:
                    blocks.append(self._create_paragraph_block(' '.join(current_paragraph)))
                    current_paragraph = []
                blocks.append(self._create_callout_block(line[2:], "💡"))
            elif line.startswith('- ') or line.startswith('* '):
                # Bullet point
                if current_paragraph:
                    blocks.append(self._create_paragraph_block(' '.join(current_paragraph)))
                    current_paragraph = []
                blocks.append(self._create_bulleted_list_block(line[2:]))
            else:
                # Regular text - accumulate into paragraph
                current_paragraph.append(line)
        
        # Flush any remaining paragraph
        if current_paragraph:
            blocks.append(self._create_paragraph_block(' '.join(current_paragraph)))
        
        return blocks[:max_blocks]
    
    def _create_heading_block(self, text: str, level: int = 2) -> Dict:
        """Create a Notion heading block."""
        heading_type = f"heading_{level}"
        return {
            "type": heading_type,
            heading_type: {
                "rich_text": [{"type": "text", "text": {"content": text[:2000]}}]
            }
        }
    
    def _create_paragraph_block(self, text: str) -> Dict:
        """Create a Notion paragraph block."""
        # Split long paragraphs (Notion has 2000 char limit per block)
        if len(text) > 2000:
            text = text[:1997] + "..."
        
        return {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        }
    
    def _create_bulleted_list_block(self, text: str) -> Dict:
        """Create a Notion bulleted list item block."""
        return {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": text[:2000]}}]
            }
        }
    
    def _create_callout_block(self, text: str, emoji: str = "💡") -> Dict:
        """Create a Notion callout block."""
        return {
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": text[:2000]}}],
                "icon": {"type": "emoji", "emoji": emoji}
            }
        }
    
    async def create_article_page(self, article_data: Dict[str, Any]) -> str:
        """
        Create a new Notion page for the article.
        
        Args:
            article_data: Article dictionary from LLM service
            
        Returns:
            URL of the created Notion page
        """
        notion_page = article_data.get("notion_page", {})
        notion_props = notion_page.get("properties", {})
        
        # Extract values from potentially nested Notion properties structure
        def extract_value(prop, default):
            """Extract value from Notion property structure or return default."""
            if isinstance(prop, str):
                return prop
            if isinstance(prop, dict):
                # Handle nested Notion structures
                if "title" in prop:
                    return prop["title"][0]["text"]["content"] if prop["title"] else default
                if "rich_text" in prop:
                    return prop["rich_text"][0]["text"]["content"] if prop["rich_text"] else default
                if "select" in prop:
                    return prop["select"]["name"] if prop["select"] else default
                if "number" in prop:
                    return prop["number"]
            return default
        
        # Get title
        title = notion_page.get("title", article_data.get("topic_title", "Article"))
        if isinstance(title, dict):
            title = article_data.get("topic_title", "Article")
        
        # Get topic (simple string)
        topic = extract_value(notion_props.get("Topic"), article_data.get("topic_title", "General"))
        
        # Get difficulty
        difficulty = extract_value(notion_props.get("Difficulty"), "Intermediate")
        if difficulty not in ["Beginner", "Intermediate", "Advanced"]:
            difficulty = "Intermediate"
        
        # Prepare properties with simple structure
        # Only use title as that's guaranteed to exist in any Notion page
        properties = {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        }
        
        logger.info(f"Creating Notion page: {article_data['topic_title']}")
        
        try:
            # Use custom blocks if provided, otherwise convert from markdown
            if "content_blocks" in notion_page and notion_page["content_blocks"]:
                blocks = notion_page["content_blocks"][:95]  # Notion API limit (leave room for callout)
            else:
                blocks = self._convert_markdown_to_blocks(
                    article_data.get("article_markdown", ""),
                    max_blocks=95  # Leave room for 24-hour experiment callout
                )
            
            # Add 24-hour experiment as callout
            if "exercises" in article_data and "day24" in article_data["exercises"]:
                experiment = article_data["exercises"]["day24"]
                callout_text = f"24-Hour Experiment: {experiment.get('title', '')}\n\n"
                callout_text += "\n".join(experiment.get("steps", []))
                blocks.insert(0, self._create_callout_block(callout_text, "🧪"))
            
            # Create the page
            response = await self.client.pages.create(
                parent={"page_id": self.parent_page_id},
                properties=properties,
                children=blocks,
                cover=self._get_cover_image(notion_page) if notion_page.get("cover_image_url") else None,
                icon={"type": "emoji", "emoji": "📚"}
            )
            
            page_url = response["url"]
            logger.info(f"Successfully created Notion page: {page_url}")
            return page_url
            
        except Exception as e:
            logger.error(f"Error creating Notion page: {e}")
            raise
    
    def _get_cover_image(self, notion_page: Dict) -> Dict:
        """Get cover image configuration for Notion page."""
        cover_url = notion_page.get("cover_image_url")
        if cover_url:
            return {
                "type": "external",
                "external": {"url": cover_url}
            }
        return None
    
    async def append_blocks_to_page(self, page_id: str, blocks: List[Dict]) -> None:
        """
        Append additional blocks to an existing page.
        Useful for adding references or updates.
        
        Args:
            page_id: Notion page ID
            blocks: List of block objects to append
        """
        try:
            await self.client.blocks.children.append(
                block_id=page_id,
                children=blocks
            )
            logger.info(f"Appended {len(blocks)} blocks to page {page_id}")
        except Exception as e:
            logger.error(f"Error appending blocks: {e}")
            raise
    
    async def update_page_status(self, page_id: str, status: str = "Published") -> None:
        """
        Update the status property of a page.
        
        Args:
            page_id: Notion page ID
            status: New status value
        """
        try:
            await self.client.pages.update(
                page_id=page_id,
                properties={
                    "Status": {"select": {"name": status}}
                }
            )
            logger.info(f"Updated page {page_id} status to {status}")
        except Exception as e:
            logger.error(f"Error updating page status: {e}")
            raise
    
    async def check_duplicate_topic(self, topic_title: str, days: int = 90) -> bool:
        """
        Check if an article with similar topic exists in recent history.
        
        Args:
            topic_title: Topic to check
            days: Number of days to look back
            
        Returns:
            True if duplicate found, False otherwise
        """
        try:
            # Search for pages with similar title
            response = await self.client.databases.query(
                database_id=self.parent_page_id,
                filter={
                    "property": "title",
                    "title": {
                        "contains": topic_title
                    }
                }
            )
            
            if response["results"]:
                logger.warning(f"Found potential duplicate for topic: {topic_title}")
                return True
            
            return False
            
        except Exception as e:
            # If search fails, assume no duplicate (fail safe)
            logger.warning(f"Could not check for duplicates: {e}")
            return False


# Global instance
notion_service = NotionService()
