"""
Orchestrator service that coordinates all services to generate and distribute articles.
"""
from typing import Dict, Any, Optional
from services.llm_service import llm_service
from services.notion_service import notion_service
from services.email_service import email_service
from services.storage_service import storage_service
from services.topic_history_service import topic_history
from config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ArticleOrchestrator:
    """Coordinates the entire article generation and distribution workflow."""
    
    async def generate_and_publish(
        self,
        send_email: bool = True
    ) -> Dict[str, Any]:
        """
        Full workflow: generate article, create Notion page, send email, save to MongoDB.
        
        Args:
            send_email: Whether to send email notification
            
        Returns:
            Dictionary with workflow results and URLs
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info(f"Starting article generation workflow at {start_time}")
        logger.info("=" * 60)
        
        result = {
            "status": "started",
            "timestamp": start_time.isoformat(),
            "errors": []
        }
        
        try:
            # Step 0: Get topic exclusions from history (MongoDB)
            exclusion_prompt = ""
            if settings.mongodb_uri:
                try:
                    logger.info("Step 0: Fetching topic history from MongoDB...")
                    exclusion_prompt = await topic_history.build_exclusion_prompt()
                    if exclusion_prompt:
                        logger.info("✓ Topic diversity exclusions loaded (ALL past topics)")
                    else:
                        logger.info("✓ No exclusions (first run or empty history)")
                except Exception as e:
                    logger.warning(f"Could not fetch topic history: {e}. Continuing without exclusions.")
            
            # Step 1: Generate article using LLM
            logger.info("Step 1/5: Generating article with OpenAI...")
            article_data = await llm_service.generate_article_with_retry(exclusion_prompt)
            
            result["topic_title"] = article_data["topic_title"]
            result["word_count"] = article_data["estimated_wordcount"]
            result["reading_time_minutes"] = article_data["reading_time_minutes"]
            result["tags"] = article_data.get("tags", [])
            result["category"] = article_data.get("category", "")
            
            logger.info(f"✓ Article generated: {article_data['topic_title']}")
            logger.info(f"  Word count: {article_data['estimated_wordcount']}")
            logger.info(f"  Reading time: {article_data['reading_time_minutes']} min")
            
            # Validate article structure
            llm_service.validate_article_structure(article_data)
            
            # Step 2: Create Notion page
            logger.info("Step 2/5: Creating Notion page...")
            notion_url = await notion_service.create_article_page(article_data)
            result["notion_url"] = notion_url
            logger.info(f"✓ Notion page created: {notion_url}")
            
            # Step 3: Send email (optional)
            if send_email:
                logger.info("Step 3/5: Sending email notification...")
                email_sent = await email_service.send_article_email(article_data, notion_url)
                result["email_sent"] = email_sent
                
                if email_sent:
                    logger.info("✓ Email sent successfully")
                else:
                    logger.warning("✗ Email sending failed")
                    result["errors"].append("Email sending failed")
            else:
                result["email_sent"] = False
                logger.info("Step 3/5: Email sending skipped")
            
            # Step 4: Save topic to MongoDB history for diversity
            topic_history_id = None
            if settings.mongodb_uri:
                try:
                    logger.info("Step 4/5: Saving to topic history (MongoDB)...")
                    tags = article_data.get("tags", [])
                    category = article_data.get("category") or (tags[0] if tags else "psychology")
                    
                    topic_history_id = await topic_history.save_topic(
                        topic_title=article_data["topic_title"],
                        tags=tags,
                        category=category,
                        word_count=article_data.get("estimated_wordcount", 0),
                        notion_url=notion_url
                    )
                    logger.info(f"✓ Topic saved to history (id: {topic_history_id})")
                except Exception as e:
                    logger.warning(f"Could not save to topic history: {e}")
            
            # Step 5: Save full article to MongoDB (linked to topic_history)
            if settings.mongodb_uri:
                try:
                    logger.info("Step 5/5: Saving full article to MongoDB...")
                    article_id = await storage_service.save_article(
                        article_data, 
                        notion_url,
                        topic_history_id=topic_history_id
                    )
                    result["article_id"] = article_id
                    logger.info(f"✓ Article saved to MongoDB (id: {article_id})")
                except Exception as e:
                    logger.warning(f"Could not save article to MongoDB: {e}")
            
            # Calculate duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result["status"] = "success"
            result["duration_seconds"] = duration
            result["completed_at"] = end_time.isoformat()
            
            logger.info("=" * 60)
            logger.info(f"✓ Workflow completed successfully in {duration:.2f}s")
            logger.info(f"Topic: {article_data['topic_title']}")
            logger.info(f"Notion: {notion_url}")
            logger.info(f"Email sent: {result.get('email_sent', False)}")
            logger.info("=" * 60)
            
            return result
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"✗ Workflow failed: {e}")
            logger.error("=" * 60)
            
            result["status"] = "failed"
            result["error"] = str(e)
            result["errors"].append(str(e))
            
            raise


# Global instance
orchestrator = ArticleOrchestrator()
