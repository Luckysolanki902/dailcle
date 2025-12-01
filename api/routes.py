"""
FastAPI routes for the Dailicle API.
Provides endpoints for manual triggering, health checks, and webhooks.
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from services.orchestrator import orchestrator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class GenerateRequest(BaseModel):
    """Request model for manual article generation."""
    topic_seed: Optional[str] = None
    send_email: bool = True
    save_to_storage: bool = True


class GenerateResponse(BaseModel):
    """Response model for article generation."""
    status: str
    topic_title: Optional[str] = None
    notion_url: Optional[str] = None
    email_sent: Optional[bool] = None
    storage_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    timestamp: str
    errors: list[str] = []


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    message: str


@router.post("/generate", response_model=GenerateResponse)
async def generate_article(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Manually trigger article generation.
    
    This endpoint starts the full workflow: generate article, create Notion page,
    send email, and save to storage.
    
    Returns immediately with a task ID, processing happens in background.
    """
    logger.info(f"Manual generation requested: topic_seed={request.topic_seed}")
    
    try:
        # Run in background to avoid timeout
        result = await orchestrator.generate_and_publish(
            topic_seed=request.topic_seed,
            send_email=request.send_email,
            save_to_storage=request.save_to_storage
        )
        
        return GenerateResponse(**result)
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns service status.
    """
    return HealthResponse(
        status="healthy",
        message="Dailicle API is running. Scheduling handled by Render Cron Job."
    )


@router.post("/webhook/generate")
async def webhook_generate(
    token: Optional[str] = Query(None, description="Authentication token"),
    topic_seed: Optional[str] = Query(None, description="Optional topic seed")
):
    """
    Webhook endpoint for external triggers (e.g., IFTTT, Zapier).
    
    Optional token parameter for basic authentication.
    """
    # Simple token-based auth (optional)
    # You can add a WEBHOOK_TOKEN to .env for security
    # if token != settings.webhook_token:
    #     raise HTTPException(status_code=401, detail="Invalid token")
    
    logger.info(f"Webhook triggered: topic_seed={topic_seed}")
    
    try:
        result = await orchestrator.generate_and_publish(
            topic_seed=topic_seed,
            send_email=True,
            save_to_storage=True
        )
        
        return {
            "status": "success",
            "topic_title": result.get("topic_title"),
            "notion_url": result.get("notion_url"),
            "message": "Article generated and published"
        }
        
    except Exception as e:
        logger.error(f"Webhook generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-email")
async def test_email():
    """
    Send a test email to verify email configuration.
    """
    from services.email_service import email_service
    
    logger.info("Test email requested")
    
    try:
        success = await email_service.send_test_email()
        
        if success:
            return {
                "status": "success",
                "message": f"Test email sent to {email_service.to_email}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send test email")
            
    except Exception as e:
        logger.error(f"Test email failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-services")
async def test_services():
    """
    Test all services (OpenAI, Notion, Email, Storage).
    
    Useful for debugging configuration issues.
    """
    logger.info("Service tests requested")
    
    try:
        results = await orchestrator.test_services()
        
        all_passed = all(results.values())
        
        return {
            "status": "success" if all_passed else "partial_failure",
            "services": results,
            "message": "All services OK" if all_passed else "Some services failed"
        }
        
    except Exception as e:
        logger.error(f"Service tests failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-simple")
async def generate_simple_article():
    """
    Generate a simpler article for testing (faster, less complex).
    Uses relaxed validation.
    """
    logger.info("Simple generation requested for testing")
    
    from services.llm_service import llm_service
    
    try:
        # Generate with minimal requirements
        article_data = await llm_service.generate_article("simple test about time management")
        
        return {
            "status": "success",
            "topic_title": article_data.get("topic_title", "Unknown"),
            "has_markdown": "article_markdown" in article_data,
            "word_count": article_data.get("estimated_wordcount", 0),
            "keys_present": list(article_data.keys()),
            "message": "Article generated (check keys_present for what was returned)"
        }
        
    except Exception as e:
        logger.error(f"Simple generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



