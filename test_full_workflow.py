#!/usr/bin/env python3
"""
Full workflow test: Generate article, create Notion page, and send email.
"""
import asyncio
import json
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from services.orchestrator import orchestrator

async def test():
    print("=" * 70)
    print("🚀 Testing FULL workflow: Generate → Notion → Email")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Generate article with OpenAI (30-60 seconds)")
    print("  2. Create Notion page")
    print("  3. Send HTML email")
    print("  4. Save to local storage")
    print()
    print("⏳ Starting workflow...")
    print()
    
    try:
        result = await orchestrator.generate_and_publish(
            topic_seed="probabilistic thinking",
            send_email=True,
            save_to_storage=True
        )
        
        print()
        print("=" * 70)
        print("✅ FULL WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print(f"📝 Topic: {result.get('topic_title')}")
        wordcount = result.get('word_count', 0)
        print(f"📊 Word count: {wordcount}")
        print(f"⏱️  Reading time: {result.get('reading_time_minutes')} minutes")
        
        # Validate
        if wordcount < 3500:
            print(f"\n⚠️  Article is {wordcount} words (target: 3500-5500)")
        else:
            print(f"\n✨ Article meets length requirements!")
        print()
        print(f"📚 Notion page: {result.get('notion_url')}")
        print(f"📧 Email sent: {result.get('email_sent')}")
        print(f"💾 Storage path: {result.get('storage_path')}")
        print()
        print(f"⏱️  Duration: {result.get('duration_seconds', 0):.2f} seconds")
        print()
        print("=" * 70)
        print("🎉 Check your email and Notion workspace!")
        print("=" * 70)
        
        # Save result for inspection
        with open('workflow_result.json', 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print()
        print("💾 Full result saved to: workflow_result.json")
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Error: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
