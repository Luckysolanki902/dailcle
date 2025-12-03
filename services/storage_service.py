"""
Storage Service using MongoDB.
Saves full article data to a separate collection, linked to topic_history.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from config import settings
import logging

logger = logging.getLogger(__name__)


class MongoStorageService:
    """Service for saving full article data to MongoDB."""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connected = False
    
    async def connect(self):
        """Connect to MongoDB."""
        if self._connected:
            return
        
        if not settings.mongodb_uri:
            logger.warning("MongoDB URI not configured. Storage disabled.")
            return
        
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_uri)
            self.db = self.client.dailicle
            self.collection = self.db.articles  # Full article storage
            
            # Test connection
            await self.client.admin.command('ping')
            self._connected = True
            logger.info("Connected to MongoDB articles collection")
            
            # Create indexes
            await self.collection.create_index("date")
            await self.collection.create_index("topic_history_id")
            await self.collection.create_index("topic_title")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
    
    async def save_article(
        self, 
        article_data: Dict[str, Any], 
        notion_url: str,
        topic_history_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Save full article data to MongoDB.
        
        Args:
            article_data: Full article dictionary from LLM
            notion_url: URL of created Notion page
            topic_history_id: ID from topic_history collection (for linking)
            
        Returns:
            Inserted document ID or None if storage disabled
        """
        await self.connect()
        
        if not self._connected:
            logger.warning("MongoDB not connected. Skipping article storage.")
            return None
        
        try:
            doc = {
                "topic_title": article_data.get("topic_title"),
                "topic_rationale": article_data.get("topic_rationale"),
                "category": article_data.get("category"),
                "tags": article_data.get("tags", []),
                "article_markdown": article_data.get("article_markdown"),
                "raw_response": article_data.get("raw_response"),
                "email_subject": article_data.get("email_subject"),
                "estimated_wordcount": article_data.get("estimated_wordcount", 0),
                "reading_time_minutes": article_data.get("reading_time_minutes", 0),
                "youtube": article_data.get("youtube", []),
                "papers": article_data.get("papers", []),
                "notion_url": notion_url,
                "date": datetime.utcnow(),
                "date_str": datetime.utcnow().strftime("%Y-%m-%d"),
            }
            
            # Link to topic_history if provided
            if topic_history_id:
                doc["topic_history_id"] = topic_history_id
            
            result = await self.collection.insert_one(doc)
            article_id = str(result.inserted_id)
            
            logger.info(f"Saved article to MongoDB: {article_data.get('topic_title')} (id: {article_id})")
            return article_id
            
        except Exception as e:
            logger.error(f"Failed to save article to MongoDB: {e}")
            return None
    
    async def get_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Get article by ID."""
        await self.connect()
        
        if not self._connected:
            return None
        
        try:
            doc = await self.collection.find_one({"_id": ObjectId(article_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception as e:
            logger.error(f"Failed to get article: {e}")
            return None
    
    async def get_article_by_date(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Get article by date string (YYYY-MM-DD)."""
        await self.connect()
        
        if not self._connected:
            return None
        
        try:
            doc = await self.collection.find_one({"date_str": date_str})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception as e:
            logger.error(f"Failed to get article by date: {e}")
            return None
    
    async def get_recent_articles(self, limit: int = 10) -> list:
        """Get most recent articles."""
        await self.connect()
        
        if not self._connected:
            return []
        
        try:
            cursor = self.collection.find({}).sort("date", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
            for doc in docs:
                doc["_id"] = str(doc["_id"])
            return docs
        except Exception as e:
            logger.error(f"Failed to get recent articles: {e}")
            return []
    
    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self._connected = False


# Global instance
storage_service = MongoStorageService()
