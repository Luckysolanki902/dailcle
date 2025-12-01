"""
Optional: Storage service for saving articles to S3 or cloud storage.
This is useful for archiving and backup purposes.
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LocalStorageService:
    """Service for saving articles locally (fallback if no cloud storage)."""
    
    def __init__(self, storage_dir: str = "articles"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    async def save_article(self, article_data: Dict[str, Any], notion_url: str) -> str:
        """
        Save article data to local filesystem.
        
        Args:
            article_data: Article dictionary
            notion_url: URL of Notion page
            
        Returns:
            Path to saved file
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        topic_slug = self._slugify(article_data["topic_title"])
        
        # Save JSON
        json_filename = f"{date_str}-{topic_slug}.json"
        json_path = self.storage_dir / json_filename
        
        # Add metadata
        save_data = {
            **article_data,
            "notion_url": notion_url,
            "saved_at": datetime.now().isoformat()
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        # Save HTML
        if "article_html" in article_data:
            html_filename = f"{date_str}-{topic_slug}.html"
            html_path = self.storage_dir / html_filename
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(article_data["article_html"])
        
        logger.info(f"Saved article locally: {json_path}")
        return str(json_path)
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        text = re.sub(r'^-+|-+$', '', text)
        return text[:100]


# S3 Storage (optional, requires boto3)
class S3StorageService:
    """Service for saving articles to AWS S3."""
    
    def __init__(self, bucket_name: str, access_key: str, secret_key: str):
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
            self.bucket_name = bucket_name
            self.enabled = True
        except ImportError:
            logger.warning("boto3 not installed. S3 storage disabled.")
            self.enabled = False
    
    async def save_article(self, article_data: Dict[str, Any], notion_url: str) -> Optional[str]:
        """
        Save article to S3.
        
        Args:
            article_data: Article dictionary
            notion_url: URL of Notion page
            
        Returns:
            S3 URL of saved file or None if disabled
        """
        if not self.enabled:
            return None
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        topic_slug = self._slugify(article_data["topic_title"])
        
        # Save JSON
        json_key = f"daily_articles/{date_str}/{topic_slug}.json"
        save_data = {
            **article_data,
            "notion_url": notion_url,
            "saved_at": datetime.now().isoformat()
        }
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=json_key,
                Body=json.dumps(save_data, indent=2, ensure_ascii=False),
                ContentType='application/json'
            )
            
            # Save HTML
            if "article_html" in article_data:
                html_key = f"daily_articles/{date_str}/{topic_slug}.html"
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=html_key,
                    Body=article_data["article_html"],
                    ContentType='text/html'
                )
            
            s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{json_key}"
            logger.info(f"Saved article to S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to save to S3: {e}")
            return None
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        text = re.sub(r'^-+|-+$', '', text)
        return text[:100]


# Factory function to create appropriate storage service
def get_storage_service():
    """Get the configured storage service."""
    from config import settings
    
    if settings.s3_bucket_name and settings.aws_access_key_id:
        return S3StorageService(
            settings.s3_bucket_name,
            settings.aws_access_key_id,
            settings.aws_secret_access_key
        )
    else:
        return LocalStorageService()


# Global instance
storage_service = get_storage_service()
