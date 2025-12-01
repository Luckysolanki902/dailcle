#!/usr/bin/env python3
"""
Test article generation and email sending only (skip Notion).
"""
import asyncio
import json
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from services.llm_service import llm_service
from services.email_service import email_service

async def test():
    print("=" * 70)
    print("🚀 Testing: Generate Article → Send Email")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Generate article with OpenAI (30-60 seconds)")
    print("  2. Send HTML email")
    print()
    print("⏳ Starting...")
    print()
    
    try:
        # Step 1: Generate article
        print("Step 1/2: Generating article...")
        article = await llm_service.generate_article("decision making under uncertainty")
        
        print(f"✅ Article generated successfully!")
        print(f"   Topic: {article['topic_title']}")
        wordcount = article.get('estimated_wordcount', 0)
        print(f"   Words: {wordcount}")
        print(f"   Reading time: {article.get('reading_time_minutes', 0)} min")
        
        # Validate
        if wordcount < 3500:
            print(f"   ⚠️  Article is {wordcount} words (target: 3500-5500)")
        else:
            print(f"   ✨ Meets length requirements!")
        print()
        
        # Step 2: Send email
        print("Step 2/2: Sending email...")
        fake_notion_url = "https://notion.so/test-page"
        email_sent = await email_service.send_article_email(article, fake_notion_url)
        
        if email_sent:
            print(f"✅ Email sent successfully!")
            print()
            print("=" * 70)
            print("🎉 SUCCESS! Check your email inbox:")
            print(f"   To: {email_service.to_email}")
            print(f"   Subject: {article.get('email_subject', 'Daily Mentor')}")
            print("=" * 70)
        else:
            print("❌ Email failed to send")
        
        # Save article for inspection
        with open('test_article_email.json', 'w') as f:
            json.dump(article, f, indent=2, default=str)
        print()
        print("💾 Article saved to: test_article_email.json")
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Error: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
