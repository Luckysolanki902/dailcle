"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from config import settings
from api.routes import router
from scheduler import scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Starting Dailicle Server")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Timezone: {settings.timezone}")
    logger.info(f"OpenAI Model: {settings.openai_model}")
    logger.info("=" * 60)
    
    # Start scheduler
    scheduler.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Dailicle Server")
    scheduler.stop()


# Create FastAPI app
app = FastAPI(
    title="Dailicle",
    description="AI-Powered Daily Article Generator with Notion Integration and Email Delivery",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["articles"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Dailicle",
        "version": "1.0.0",
        "description": "AI-Powered Daily Article Generator",
        "endpoints": {
            "health": "/api/health",
            "generate": "/api/generate (POST)",
            "webhook": "/api/webhook/generate (POST)",
            "test_email": "/api/test-email (POST)",
            "test_services": "/api/test-services (POST)",
            "scheduler_status": "/api/scheduler/status",
            "scheduler_trigger": "/api/scheduler/trigger (POST)"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health():
    """Simple health check."""
    return {
        "status": "healthy",
        "service": "dailicle",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level="info"
    )
