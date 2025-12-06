"""
Orchestrator service that coordinates all services to generate and distribute articles.
"""
from typing import Dict, Any, Optional
from services.llm_service import llm_service
from services.email_service import email_service
from services.storage_service import storage_service
from services.topic_history_service import topic_history
from config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Lazy import for audio service (optional dependency)
def get_audio_service():
    """Lazily import audio service to avoid import errors if AWS not configured."""
    try:
        from services.audio_service import audio_service
        return audio_service
    except Exception as e:
        logger.warning(f"Audio service not available: {e}")
        return None


class ArticleOrchestrator:
    """Coordinates the entire article generation and distribution workflow."""
    
    async def generate_and_publish(
        self,
        send_email: bool = True
    ) -> Dict[str, Any]:
        """
        Full workflow: generate article, save to MongoDB, send email, generate audio.
        
        Args:
            send_email: Whether to send email notification
            
        Returns:
            Dictionary with workflow results
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
            logger.info("Step 1/4: Generating article with OpenAI...")
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
            
            # Step 2: Save to MongoDB (article + topic history)
            article_id = None
            if settings.mongodb_uri:
                try:
                    logger.info("Step 2/4: Saving article to MongoDB...")
                    
                    # Save to topic history first
                    tags = article_data.get("tags", [])
                    category = article_data.get("category") or (tags[0] if tags else "psychology")
                    
                    topic_history_id = await topic_history.save_topic(
                        topic_title=article_data["topic_title"],
                        tags=tags,
                        category=category,
                        word_count=article_data.get("estimated_wordcount", 0),
                        notion_url=""  # No longer using Notion
                    )
                    logger.info(f"  ✓ Topic saved to history (id: {topic_history_id})")
                    
                    # Save full article
                    article_id = await storage_service.save_article(
                        article_data, 
                        notion_url="",  # No longer using Notion
                        topic_history_id=topic_history_id
                    )
                    result["article_id"] = article_id
                    logger.info(f"✓ Article saved to MongoDB (id: {article_id})")
                except Exception as e:
                    logger.error(f"✗ Could not save article to MongoDB: {e}")
                    result["errors"].append(f"MongoDB save failed: {str(e)}")
                    raise  # This is critical - article must be saved
            
            # Step 3: Send email notification (optional, non-critical)
            if send_email:
                try:
                    logger.info("Step 3/4: Sending email notification...")
                    # Build article URL for email
                    article_url = f"https://dailicle.com/read/{article_id}" if article_id else ""
                    email_sent = await email_service.send_article_email(article_data, article_url)
                    result["email_sent"] = email_sent
                    
                    if email_sent:
                        logger.info("✓ Email sent successfully")
                    else:
                        logger.warning("✗ Email sending failed")
                        result["errors"].append("Email sending failed")
                except Exception as e:
                    logger.warning(f"✗ Email sending failed (non-critical): {e}")
                    result["email_sent"] = False
                    result["errors"].append(f"Email failed: {str(e)}")
            else:
                result["email_sent"] = False
                logger.info("Step 3/4: Email sending skipped")
            
            # Step 4: Generate audio narration (optional, non-critical)
            if article_id and settings.aws_access_key_id and settings.aws_bucket:
                try:
                    logger.info("Step 4/4: Generating audio narration...")
                    audio_svc = get_audio_service()
                    if audio_svc:
                        audio_result = await audio_svc.generate_audio_for_new_article(
                            article_id=article_id,
                            article_markdown=article_data.get("article_markdown", ""),
                            voice="fable"
                        )
                        result["audio_url"] = audio_result.get("audio_url")
                        result["audio_duration"] = audio_result.get("audio_duration_seconds")
                        logger.info(f"✓ Audio generated: {audio_result.get('audio_url')}")
                    else:
                        logger.warning("✗ Audio service not available")
                        result["errors"].append("Audio service not available")
                except Exception as e:
                    # Audio generation failure should NOT fail the entire workflow
                    logger.warning(f"✗ Audio generation failed (non-critical): {e}")
                    result["errors"].append(f"Audio generation failed: {str(e)}")
                    result["audio_url"] = None
            else:
                if not article_id:
                    logger.info("Step 4/4: Skipping audio (no article_id)")
                else:
                    logger.info("Step 4/4: Skipping audio (AWS not configured)")
            
            # Calculate duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result["status"] = "success"
            result["duration_seconds"] = duration
            result["completed_at"] = end_time.isoformat()
            
            logger.info("=" * 60)
            logger.info(f"✓ Workflow completed successfully in {duration:.2f}s")
            logger.info(f"Topic: {article_data['topic_title']}")
            logger.info(f"Article ID: {article_id}")
            logger.info(f"Email sent: {result.get('email_sent', False)}")
            logger.info(f"Audio: {result.get('audio_url', 'Not generated')}")
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
