#!/usr/bin/env python3
"""
Simple test script to verify your Dailicle setup.
Run this after configuring .env to check everything works.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from services.llm_service import llm_service
from services.notion_service import notion_service
from services.email_service import email_service


async def test_openai():
    """Test OpenAI API connection and article generation."""
    print("🧪 Testing OpenAI API...")
    try:
        print(f"   Model: {settings.openai_model}")
        print(f"   Max tokens: {settings.max_tokens}")
        print("   Generating test article (this takes 30-60 seconds)...")
        
        article = await llm_service.generate_article("test topic")
        
        print(f"   ✅ OpenAI API working!")
        print(f"   Generated: {article['topic_title']}")
        print(f"   Word count: {article['estimated_wordcount']}")
        return True
    except Exception as e:
        print(f"   ❌ OpenAI API failed: {e}")
        return False


async def test_email():
    """Test email configuration."""
    print("\n📧 Testing Email (SMTP)...")
    try:
        print(f"   SMTP host: {settings.smtp_host}")
        print(f"   From: {settings.email_from}")
        print(f"   To: {settings.email_to}")
        print("   Sending test email...")
        
        success = await email_service.send_test_email()
        
        if success:
            print(f"   ✅ Email sent successfully!")
            print(f"   Check inbox: {settings.email_to}")
            return True
        else:
            print(f"   ❌ Email failed to send")
            return False
    except Exception as e:
        print(f"   ❌ Email failed: {e}")
        return False


def test_notion_config():
    """Test Notion configuration (not actual API call)."""
    print("\n📚 Testing Notion Configuration...")
    try:
        print(f"   API key: {'✓ Set' if settings.notion_api_key else '✗ Missing'}")
        print(f"   Parent page ID: {settings.notion_parent_page_id}")
        print(f"   Parent URL: {settings.notion_parent_url}")
        
        if settings.notion_api_key and settings.notion_parent_page_id:
            print("   ✅ Notion configured (will test on actual generation)")
            return True
        else:
            print("   ❌ Notion not fully configured")
            return False
    except Exception as e:
        print(f"   ❌ Notion config error: {e}")
        return False


def test_scheduler_config():
    """Test scheduler configuration."""
    print("\n⏰ Testing Scheduler Configuration...")
    try:
        print(f"   Timezone: {settings.timezone}")
        print(f"   Cron schedule: {settings.cron_schedule}")
        
        # Parse cron to verify format
        parts = settings.cron_schedule.split()
        if len(parts) == 5:
            print(f"   ✅ Cron format valid")
            return True
        else:
            print(f"   ❌ Invalid cron format (should be 5 parts)")
            return False
    except Exception as e:
        print(f"   ❌ Scheduler config error: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Dailicle Configuration Test")
    print("=" * 60)
    
    results = {}
    
    # Test scheduler config (no API call)
    results['scheduler'] = test_scheduler_config()
    
    # Test Notion config (no API call)
    results['notion'] = test_notion_config()
    
    # Test email (API call)
    results['email'] = await test_email()
    
    # Test OpenAI (API call - optional, can be slow)
    print("\n⚠️  OpenAI test will take 30-60 seconds and use ~$0.01 in credits.")
    response = input("   Run OpenAI test? (y/n): ")
    
    if response.lower() == 'y':
        results['openai'] = await test_openai()
    else:
        print("   ⏭️  Skipped OpenAI test")
        results['openai'] = None
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for service, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIP"
        
        print(f"{status} - {service.capitalize()}")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    
    print("\n" + "=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run the server: python main.py")
        print("2. Test API: curl http://localhost:8000/api/health")
        print("3. Generate article: curl -X POST http://localhost:8000/api/generate")
        print("4. Deploy: See DEPLOYMENT.md")
    else:
        print(f"⚠️  {failed} test(s) failed. Check configuration:")
        print("1. Verify .env file has all required values")
        print("2. Check API keys are valid")
        print("3. For email: use Gmail app password")
        print("4. For Notion: share page with integration")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
