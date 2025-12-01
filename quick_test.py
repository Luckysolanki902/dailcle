"""
Quick test script for article generation.
Tests the LLM service directly without full orchestration.
"""
import asyncio
import json
import logging
from datetime import datetime

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from services.llm_service import llm_service


async def test():
    """Test comprehensive article generation with the new prompt."""
    print("\n" + "=" * 70)
    print("🧪 Testing Comprehensive Article Generation")
    print("=" * 70)
    print("⏳ This may take 2-3 minutes for a high-quality, detailed article...\n")
    
    try:
        # Generate article without topic seed (let AI choose)
        article = await llm_service.generate_article_with_retry()
        
        print("\n✅ Article generated successfully!\n")
        print(f"📝 Topic: {article.get('topic_title', 'N/A')}")
        print(f"💡 Rationale: {article.get('topic_rationale', 'N/A')[:150]}...")
        print(f"\n📊 Word count: {article.get('estimated_wordcount', 0)}")
        print(f"⏱️  Reading time: {article.get('reading_time_minutes', 0)} min")
        
        # Validate minimum length
        wordcount = article.get('estimated_wordcount', 0)
        if wordcount < 3500:
            print(f"\n⚠️  WARNING: Article is {wordcount} words (target: 3500-5500 words)")
        else:
            print(f"\n✨ Excellent! Article meets length requirements")
        
        # Check resources
        youtube_count = len(article.get('youtube', []))
        papers_count = len(article.get('papers', []))
        print(f"\n📚 Resources:")
        print(f"   - YouTube videos: {youtube_count}")
        print(f"   - Papers/Articles: {papers_count}")
        
        # Check exercises
        exercises = article.get('exercises', {})
        print(f"\n💪 Exercises:")
        print(f"   - Beginner: {len(exercises.get('beginner', []))}")
        print(f"   - Intermediate: {len(exercises.get('intermediate', []))}")
        print(f"   - Advanced: {len(exercises.get('advanced', []))}")
        
        # Show article structure
        markdown = article.get('article_markdown', '')
        lines = markdown.split('\n')
        
        print(f"\n📄 Article Structure (Headings):")
        print("-" * 70)
        heading_count = 0
        for line in lines:
            if line.startswith('#'):
                print(line)
                heading_count += 1
                if heading_count >= 15:  # Show first 15 headings
                    break
        print("-" * 70)
        
        # Token usage
        tokens = article.get('generation_metadata', {}).get('tokens_used', 'N/A')
        print(f"\n🔢 Token Usage: {tokens}")
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_article_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(article, f, indent=2)
        
        print(f"\n💾 Full article saved to: {filename}")
        print("\n" + "=" * 70)
        print("🎉 Test completed successfully!")
        print("=" * 70 + "\n")
        
        return article
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(test())
    exit(0 if result else 1)
