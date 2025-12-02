#!/usr/bin/env python3
"""
Script to be called by Render Cron Job.
Generates and publishes daily article immediately.
"""
import asyncio
import sys
import logging

# Configure logging - flush immediately
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)

# Make sure logs are flushed immediately
for handler in logging.root.handlers:
    handler.flush()

logger = logging.getLogger(__name__)

async def main():
    """Run the daily article generation workflow."""
    print("=" * 70, flush=True)
    print("CRON JOB STARTED - Dailicle Article Generation", flush=True)
    print("=" * 70, flush=True)
    
    # Import here to avoid issues
    from services.orchestrator import orchestrator
    
    print("Orchestrator imported successfully", flush=True)
    print("Starting article generation workflow...", flush=True)
    
    try:
        result = await orchestrator.generate_and_publish(
            topic_seed=None,
            send_email=True,
            save_to_storage=True
        )
        
        print("=" * 70, flush=True)
        print("SUCCESS! Article generation completed!", flush=True)
        print(f"Topic: {result.get('topic_title')}", flush=True)
        print(f"Notion: {result.get('notion_url')}", flush=True)
        print(f"Email sent: {result.get('email_sent')}", flush=True)
        print(f"Duration: {result.get('duration_seconds', 0):.2f}s", flush=True)
        print("=" * 70, flush=True)
        
        return 0
        
    except Exception as e:
        print("=" * 70, flush=True)
        print(f"FAILED! Error: {e}", flush=True)
        print("=" * 70, flush=True)
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return 1

if __name__ == "__main__":
    print("Script starting...", flush=True)
    exit_code = asyncio.run(main())
    print(f"Script finished with exit code: {exit_code}", flush=True)
    sys.exit(exit_code)
