#!/usr/bin/env python3
"""
Script to be called by Render Cron Job.
Generates and publishes daily article immediately.
"""
import asyncio
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def main():
    """Run the daily article generation workflow."""
    from services.orchestrator import orchestrator
    
    logger.info("=" * 70)
    logger.info("Starting daily article generation (triggered by Render Cron)")
    logger.info("=" * 70)
    
    try:
        result = await orchestrator.generate_and_publish(
            topic_seed=None,
            send_email=True,
            save_to_storage=True
        )
        
        logger.info("=" * 70)
        logger.info("✅ Article generation completed successfully!")
        logger.info(f"Topic: {result.get('topic_title')}")
        logger.info(f"Notion: {result.get('notion_url')}")
        logger.info(f"Email sent: {result.get('email_sent')}")
        logger.info(f"Duration: {result.get('duration_seconds', 0):.2f}s")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"❌ Article generation failed: {e}")
        logger.error("=" * 70)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
