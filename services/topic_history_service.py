"""
Topic History Service using MongoDB.
Tracks past topics to ensure variety and avoid repetition.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import logging

logger = logging.getLogger(__name__)


class TopicHistoryService:
    """Manages topic history in MongoDB to ensure variety."""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connected = False
    
    async def connect(self):
        """Connect to MongoDB."""
        if self._connected:
            return
        
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_uri)
            self.db = self.client.dailicle
            self.collection = self.db.topic_history
            
            # Test connection
            await self.client.admin.command('ping')
            self._connected = True
            logger.info("Connected to MongoDB successfully")
            
            # Create index on date for efficient queries
            await self.collection.create_index("date")
            await self.collection.create_index("category")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            raise
    
    async def save_topic(self, topic_title: str, tags: List[str], category: str, 
                         word_count: int = 0, notion_url: str = None) -> str:
        """
        Save a generated topic to history.
        
        Args:
            topic_title: The article title
            tags: List of tags/keywords like decision-making, purpose, productivity, startup, Design, UI/UX, human behavior, reading emotions, etc.
            category: Main category (psychology, leadership, etc.)
            word_count: Article word count
            notion_url: Link to Notion page
            
        Returns:
            Inserted document ID
        """
        await self.connect()
        
        doc = {
            "topic_title": topic_title,
            "tags": tags,
            "category": category,
            "word_count": word_count,
            "notion_url": notion_url,
            "date": datetime.utcnow(),
            "date_str": datetime.utcnow().strftime("%Y-%m-%d")
        }
        
        result = await self.collection.insert_one(doc)
        logger.info(f"Saved topic to history: {topic_title} (category: {category})")
        return str(result.inserted_id)
    
    async def get_recent_topics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get topics from the last N days."""
        await self.connect()
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        cursor = self.collection.find(
            {"date": {"$gte": cutoff}},
            {"_id": 0, "topic_title": 1, "tags": 1, "category": 1, "date_str": 1}
        ).sort("date", -1)
        
        return await cursor.to_list(length=100)
    
    async def get_recent_categories(self, days: int = 7) -> List[str]:
        """Get categories used in the last N days."""
        await self.connect()
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        cursor = self.collection.find(
            {"date": {"$gte": cutoff}},
            {"_id": 0, "category": 1}
        )
        
        docs = await cursor.to_list(length=100)
        return [doc["category"] for doc in docs if "category" in doc]
    
    async def get_all_past_titles(self) -> List[str]:
        """Get all past topic titles to avoid exact repetition."""
        await self.connect()
        
        cursor = self.collection.find({}, {"_id": 0, "topic_title": 1})
        docs = await cursor.to_list(length=1000)
        return [doc["topic_title"] for doc in docs if "topic_title" in doc]
    
    async def get_all_topics(self) -> List[Dict[str, Any]]:
        """Get ALL past topics with full details."""
        await self.connect()
        
        cursor = self.collection.find(
            {},
            {"_id": 0, "topic_title": 1, "tags": 1, "category": 1, "date_str": 1}
        ).sort("date", -1)
        
        return await cursor.to_list(length=1000)
    
    async def build_exclusion_prompt(self) -> str:
        """
        Build a prompt section that tells the LLM what to avoid.
        
        Returns:
            String to append to the prompt with exclusion instructions
        """
        await self.connect()
        
        # Get ALL past topics (for complete exclusion)
        all_topics = await self.get_all_topics()
        
        # Get categories from last 15 days (to avoid same category)
        recent_categories = await self.get_recent_categories(days=15)
        
        # Get all past titles
        all_titles = await self.get_all_past_titles()
        
        if not all_topics:
            return ""
        
        exclusion_parts = []
        
        # Add recent category exclusions (last 15 days)
        if recent_categories:
            unique_recent = list(set(recent_categories))
            exclusion_parts.append(
                f"AVOID these categories (used in last 15 days): {', '.join(unique_recent)}"
            )
        
        # Add ALL past topic exclusions
        if all_topics:
            all_titles = [t["topic_title"] for t in all_topics]
            all_tags = []
            for t in all_topics:
                all_tags.extend(t.get("tags", []))
            unique_tags = list(set(all_tags))
            
            exclusion_parts.append(
                f"NEVER repeat these past topics: {', '.join(all_titles)}"
            )
            if unique_tags:
                exclusion_parts.append(
                    f"Be mindful of these previously covered tags (you can still use them, but bring fresh angles): {', '.join(unique_tags)}"
                )
        
        # Build final exclusion prompt
        exclusion_prompt = "\n\n## IMPORTANT - Topic Diversity Requirements\n"
        exclusion_prompt += "To ensure variety, follow these rules:\n"
        for part in exclusion_parts:
            exclusion_prompt += f"- {part}\n"
        
        exclusion_prompt += "\nChoose a FRESH topic from an UNDERREPRESENTED category. "
        exclusion_prompt += "Rotate through different domains: psychology, relationships, "
        exclusion_prompt += "communication, leadership, productivity, decision-making, "
        exclusion_prompt += "cognitive biases, creativity, learning, negotiation, "
        exclusion_prompt += "emotional intelligence, systems thinking, habit formation, etc.\n"
        
        return exclusion_prompt
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about topic history."""
        await self.connect()
        
        total = await self.collection.count_documents({})
        
        # Category distribution
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        cursor = self.collection.aggregate(pipeline)
        category_counts = await cursor.to_list(length=50)
        
        return {
            "total_articles": total,
            "category_distribution": {c["_id"]: c["count"] for c in category_counts if c["_id"]}
        }
    
    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self._connected = False


# Global instance
topic_history = TopicHistoryService()
