#!/usr/bin/env python3
"""
Script to be called by Render Cron Job.
Generates and publishes daily article immediately.
"""
import asyncio
import sys
import os

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

def log(msg):
    """Print with immediate flush."""
    print(msg, flush=True)
    sys.stdout.flush()

async def main():
    """Run the daily article generation workflow."""
    log("=" * 70)
    log("CRON JOB STARTED - Dailicle Article Generation")
    log("=" * 70)
    
    try:
        # Import here to avoid issues at module level
        log("Importing orchestrator...")
        from services.orchestrator import orchestrator
        log("Orchestrator imported successfully")
        
        log("Starting article generation workflow...")
        log("This will take 3-5 minutes for OpenAI to generate the article...")
        
        result = await orchestrator.generate_and_publish(
            topic_seed=None,
            send_email=True,
            save_to_storage=True
        )
        
        log("=" * 70)
        log("SUCCESS! Article generation completed!")
        log(f"Topic: {result.get('topic_title')}")
        log(f"Notion: {result.get('notion_url')}")
        log(f"Email sent: {result.get('email_sent')}")
        log(f"Duration: {result.get('duration_seconds', 0):.2f}s")
        log("=" * 70)
        
        return 0
        
    except Exception as e:
        log("=" * 70)
        log(f"FAILED! Error: {e}")
        log("=" * 70)
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return 1

if __name__ == "__main__":
    log("Script starting...")
    log(f"Python version: {sys.version}")
    
    # Run with proper event loop
    try:
        exit_code = asyncio.run(main())
    except KeyboardInterrupt:
        log("Interrupted by user")
        exit_code = 1
    except Exception as e:
        log(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
    
    log(f"Script finished with exit code: {exit_code}")
    sys.exit(exit_code)
