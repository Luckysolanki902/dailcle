"""
Orchestrator service that coordinates all services to generate and distribute articles.
"""
from typing import Dict, Any, Optional
from services.llm_service import llm_service
from services.notion_service import notion_service
from services.email_service import email_service
from services.storage_service import storage_service
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ArticleOrchestrator:
    """Coordinates the entire article generation and distribution workflow."""
    
    async def generate_and_publish(
        self,
        topic_seed: Optional[str] = None,
        send_email: bool = True,
        save_to_storage: bool = True
    ) -> Dict[str, Any]:
        """
        Full workflow: generate article, create Notion page, send email, and save to storage.
        
        Args:
            topic_seed: Optional topic hint for LLM
            send_email: Whether to send email notification
            save_to_storage: Whether to save article to cloud/local storage
            
        Returns:
            Dictionary with workflow results and URLs
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info(f"Starting article generation workflow at {start_time}")
        logger.info(f"Topic seed: {topic_seed or 'None (auto-select)'}")
        logger.info("=" * 60)
        
        result = {
            "status": "started",
            "topic_seed": topic_seed,
            "timestamp": start_time.isoformat(),
            "errors": []
        }
        
        try:
            # Step 1: Generate article using LLM
            logger.info("Step 1/4: Generating article with OpenAI...")
            article_data = await llm_service.generate_article_with_retry(topic_seed)
            
            result["topic_title"] = article_data["topic_title"]
            result["word_count"] = article_data["estimated_wordcount"]
            result["reading_time_minutes"] = article_data["reading_time_minutes"]
            result["tags"] = article_data.get("tags", [])
            
            logger.info(f"✓ Article generated: {article_data['topic_title']}")
            logger.info(f"  Word count: {article_data['estimated_wordcount']}")
            logger.info(f"  Reading time: {article_data['reading_time_minutes']} min")
            
            # Validate article structure
            llm_service.validate_article_structure(article_data)
            
            # Step 2: Create Notion page
            logger.info("Step 2/4: Creating Notion page...")
            notion_url = await notion_service.create_article_page(article_data)
            result["notion_url"] = notion_url
            logger.info(f"✓ Notion page created: {notion_url}")
            
            # Step 3: Send email (optional)
            if send_email:
                logger.info("Step 3/4: Sending email notification...")
                email_sent = await email_service.send_article_email(article_data, notion_url)
                result["email_sent"] = email_sent
                
                if email_sent:
                    logger.info(f"✓ Email sent to {email_service.to_email}")
                else:
                    logger.warning("✗ Email sending failed")
                    result["errors"].append("Email sending failed")
            else:
                result["email_sent"] = False
                logger.info("Step 3/4: Email sending skipped")
            
            # Step 4: Save to storage (optional)
            if save_to_storage:
                logger.info("Step 4/4: Saving to storage...")
                storage_path = await storage_service.save_article(article_data, notion_url)
                result["storage_path"] = storage_path
                logger.info(f"✓ Article saved: {storage_path}")
            else:
                logger.info("Step 4/4: Storage saving skipped")
            
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
    
    async def test_services(self) -> Dict[str, bool]:
        """
        Test all services to verify configuration.
        
        Returns:
            Dictionary of service test results
        """
        logger.info("Testing all services...")
        
        results = {
            "openai": False,
            "notion": False,
            "email": False,
            "storage": False
        }
        
        # Test OpenAI
        try:
            test_article = await llm_service.generate_article("test topic")
            results["openai"] = bool(test_article)
            logger.info("✓ OpenAI service: OK")
        except Exception as e:
            logger.error(f"✗ OpenAI service failed: {e}")
        
        # Test Email
        try:
            email_sent = await email_service.send_test_email()
            results["email"] = email_sent
            if email_sent:
                logger.info("✓ Email service: OK")
            else:
                logger.error("✗ Email service: Failed")
        except Exception as e:
            logger.error(f"✗ Email service failed: {e}")
        
        # Notion and Storage tests would require actual data
        logger.info("ℹ Notion and Storage services require actual article data to test")
        
        return results


# Global instance
orchestrator = ArticleOrchestrator()
