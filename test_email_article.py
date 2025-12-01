#!/usr/bin/env python3
"""
Quick test: Send a pre-made article via email to verify the full flow.
This bypasses OpenAI to test Notion + Email delivery.
"""
import asyncio
import sys
from datetime import datetime

sys.path.insert(0, '.')

async def test_email_flow():
    """Test sending a mock article via email and Notion."""
    from services.email_service import email_service
    from services.notion_service import notion_service
    
    print("🧪 Testing Article Email & Notion Flow")
    print("=" * 60)
    
    # Mock article data (minimal version)
    article_data = {
        "topic_title": "Test Article: Time Management for Founders",
        "topic_rationale": "Time management is crucial for founders to balance multiple priorities and maintain productivity.",
        "article_markdown": """# Test Article: Time Management for Founders

## Executive Overview
This is a test article to verify the email and Notion integration works correctly.

## Key Points
- Focus on high-impact activities
- Use time blocking
- Delegate effectively

## Summary
Time management is essential for founder success.
""",
        "article_html": """<h2>Executive Overview</h2>
<p>This is a test article to verify the email and Notion integration works correctly.</p>
<h2>Key Points</h2>
<ul>
<li>Focus on high-impact activities</li>
<li>Use time blocking</li>
<li>Delegate effectively</li>
</ul>
<h2>Summary</h2>
<p>Time management is essential for founder success.</p>""",
        "youtube": [
            {
                "title": "Time Management for Entrepreneurs",
                "channel": "Test Channel",
                "url": "https://youtube.com",
                "why": "Great introduction to time management"
            }
        ],
        "papers": [
            {
                "title": "The Science of Time Management",
                "authors": "Test Author",
                "year": 2024,
                "url": "https://example.com",
                "summary": "Research on productivity",
                "essential": True
            }
        ],
        "exercises": {
            "beginner": [{"title": "Track your time", "duration_minutes": 15, "steps": ["Use a timer"], "context_tags": ["founder"]}],
            "intermediate": [{"title": "Time blocking", "duration_minutes": 30, "steps": ["Block calendar"], "context_tags": ["product"]}],
            "advanced": [{"title": "Delegate tasks", "duration_minutes": 60, "steps": ["Identify tasks"], "context_tags": ["leadership"]}],
            "day24": {
                "title": "Track one full day",
                "duration_hours": 24,
                "steps": ["Log every activity", "Review at end of day"],
                "metrics_to_watch": ["Time spent on high-value work", "Interruptions count"]
            }
        },
        "notion_page": {
            "parent_url": "https://www.notion.so/luckysolanki-personal/Daily-articles-2bbe80b58b6a8017854ce39c2109eedb",
            "title": "Test Article: Time Management",
            "properties": {
                "Topic": "Time Management",
                "Date": datetime.now().isoformat(),
                "Tags": ["productivity", "founder", "test"],
                "Difficulty": "Beginner",
                "TimeToRead": 5,
                "Author": "AI Mentor",
                "Status": "Draft"
            },
            "content_blocks": [],
            "cover_image_url": "https://images.unsplash.com/photo-1501139083538-0139583c060f?w=800"
        },
        "email_subject": "Daily Mentor: Time Management for Founders (Test)",
        "tags": ["productivity", "founder", "test"],
        "estimated_wordcount": 150,
        "reading_time_minutes": 5
    }
    
    print("\n📚 Step 1: Creating Notion Page...")
    try:
        notion_url = await notion_service.create_article_page(article_data)
        print(f"✅ Notion page created: {notion_url}")
    except Exception as e:
        print(f"❌ Notion failed: {e}")
        notion_url = "https://notion.so/test"
    
    print("\n📧 Step 2: Sending Email...")
    try:
        email_sent = await email_service.send_article_email(article_data, notion_url)
        if email_sent:
            print(f"✅ Email sent to luckysolanki902@gmail.com")
            print(f"   Check your inbox!")
        else:
            print("❌ Email sending failed")
    except Exception as e:
        print(f"❌ Email error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("\nCheck:")
    print("1. Your email inbox for the article")
    print("2. Notion workspace for the new page")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_email_flow())
