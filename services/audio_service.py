"""
Audio Service for generating article narration using OpenAI TTS.
Stores audio files in AWS S3 and serves via CloudFront.
"""
import asyncio
import io
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from openai import OpenAI
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from config import settings

logger = logging.getLogger(__name__)


class AudioService:
    """Service for generating and storing article audio narration."""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.s3_client = None
        self.mongo_client = None
        self.db = None
        self._connected = False
    
    def _init_s3(self):
        """Initialize S3 client."""
        if self.s3_client:
            return
        
        if not all([settings.aws_access_key_id, settings.aws_secret_access_key, settings.aws_bucket]):
            raise ValueError("AWS credentials not configured. Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_BUCKET.")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        logger.info(f"S3 client initialized for bucket: {settings.aws_bucket}")
    
    async def _connect_mongo(self):
        """Connect to MongoDB."""
        if self._connected:
            return
        
        if not settings.mongodb_uri:
            raise ValueError("MongoDB URI not configured.")
        
        self.mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self.mongo_client.dailicle
        self._connected = True
        logger.info("Connected to MongoDB for audio service")
    
    def _clean_markdown_for_speech(self, markdown: str) -> str:
        """
        Clean markdown text for natural speech synthesis.
        Removes formatting that doesn't translate well to audio.
        """
        import re
        
        text = markdown
        
        # Remove markdown headers (## Header -> Header)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove bold/italic markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* -> italic
        text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__ -> bold
        text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_ -> italic
        
        # Remove links but keep text: [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Remove inline code
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # Remove blockquotes marker
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
        
        # Remove horizontal rules
        text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\*\*\*+$', '', text, flags=re.MULTILINE)
        
        # Remove bullet points, replace with natural pause
        text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)
        
        # Remove numbered lists formatting
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Clean up extra whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        text = text.strip()
        
        return text
    
    def _generate_speech_sync(self, text: str, voice: str = "fable") -> bytes:
        """
        Generate speech using OpenAI TTS API (synchronous).
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            Audio bytes in MP3 format
        """
        # OpenAI TTS has a 4096 character limit per request
        # For longer texts, we need to chunk and concatenate
        MAX_CHARS = 4096
        
        if len(text) <= MAX_CHARS:
            response = self.openai_client.audio.speech.create(
                model="tts-1",  # tts-1 for speed, tts-1-hd for quality
                voice=voice,
                input=text,
                response_format="mp3"
            )
            return response.content
        
        # For longer texts, chunk by paragraphs
        logger.info(f"Text length {len(text)} exceeds {MAX_CHARS}, chunking...")
        
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= MAX_CHARS:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Split into {len(chunks)} chunks for TTS")
        
        # Generate audio for each chunk
        audio_parts = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Generating audio chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=chunk,
                response_format="mp3"
            )
            audio_parts.append(response.content)
        
        # Concatenate MP3 files (simple concatenation works for MP3)
        return b''.join(audio_parts)
    
    def _upload_to_s3(self, audio_bytes: bytes, article_id: str) -> str:
        """
        Upload audio file to S3.
        
        Returns:
            S3 key (path) of the uploaded file
        """
        self._init_s3()
        
        # Generate S3 key
        date_prefix = datetime.now(timezone.utc).strftime("%Y/%m")
        s3_key = f"audio/{date_prefix}/{article_id}.mp3"
        
        try:
            self.s3_client.put_object(
                Bucket=settings.aws_bucket,
                Key=s3_key,
                Body=audio_bytes,
                ContentType='audio/mpeg',
                CacheControl='max-age=31536000',  # 1 year cache
            )
            logger.info(f"Uploaded audio to S3: {s3_key}")
            return s3_key
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise
    
    def _get_cloudfront_url(self, s3_key: str) -> str:
        """Get CloudFront URL for the uploaded file."""
        if settings.cloudfront_base_url:
            base = settings.cloudfront_base_url.rstrip('/')
            return f"{base}/{s3_key}"
        else:
            # Return relative path - frontend will prepend CloudFront base URL
            return s3_key
    
    async def generate_audio_for_article(
        self, 
        article_id: str,
        voice: str = "fable",
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate audio narration for an article.
        
        Args:
            article_id: MongoDB ObjectId of the article
            voice: OpenAI TTS voice (alloy, echo, fable, onyx, nova, shimmer)
            force_regenerate: If True, regenerate even if audio exists
            
        Returns:
            Dict with audio_url and metadata
        """
        await self._connect_mongo()
        
        # Fetch article
        article = await self.db.articles.find_one({"_id": ObjectId(article_id)})
        if not article:
            raise ValueError(f"Article not found: {article_id}")
        
        logger.info(f"Generating audio for: {article.get('topic_title')}")
        
        # Check if audio already exists
        if not force_regenerate and article.get('audio_url'):
            logger.info(f"Audio already exists: {article.get('audio_url')}")
            return {
                "audio_url": article.get('audio_url'),
                "audio_duration_seconds": article.get('audio_duration_seconds'),
                "already_exists": True
            }
        
        # Get article text
        markdown = article.get('article_markdown', '')
        if not markdown:
            raise ValueError(f"Article has no content: {article_id}")
        
        # Clean for speech
        speech_text = self._clean_markdown_for_speech(markdown)
        logger.info(f"Cleaned text length: {len(speech_text)} characters")
        
        # Generate speech (run in thread pool since OpenAI client is sync)
        loop = asyncio.get_event_loop()
        audio_bytes = await loop.run_in_executor(
            None, 
            self._generate_speech_sync, 
            speech_text,
            voice
        )
        
        logger.info(f"Generated audio: {len(audio_bytes)} bytes")
        
        # Upload to S3
        s3_key = await loop.run_in_executor(
            None,
            self._upload_to_s3,
            audio_bytes,
            article_id
        )
        
        # Get CloudFront URL
        audio_url = self._get_cloudfront_url(s3_key)
        
        # Estimate duration (rough: ~150 words per minute, ~5 chars per word)
        word_count = len(speech_text.split())
        estimated_duration = int((word_count / 150) * 60)  # seconds
        
        # Update article in MongoDB
        await self.db.articles.update_one(
            {"_id": ObjectId(article_id)},
            {
                "$set": {
                    "audio_url": audio_url,
                    "audio_s3_key": s3_key,
                    "audio_voice": voice,
                    "audio_duration_seconds": estimated_duration,
                    "audio_generated_at": datetime.now(timezone.utc),
                }
            }
        )
        
        logger.info(f"Updated article with audio URL: {audio_url}")
        
        return {
            "audio_url": audio_url,
            "audio_s3_key": s3_key,
            "audio_voice": voice,
            "audio_duration_seconds": estimated_duration,
            "already_exists": False
        }
    
    async def generate_audio_for_new_article(
        self,
        article_id: str,
        article_markdown: str,
        voice: str = "fable"
    ) -> Dict[str, Any]:
        """
        Generate audio for a newly created article (used by orchestrator).
        This method doesn't fetch from DB - it uses the provided markdown directly.
        
        Args:
            article_id: MongoDB ObjectId of the article (as string)
            article_markdown: The article content in markdown
            voice: OpenAI TTS voice (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            Dict with audio_url and metadata
        """
        await self._connect_mongo()
        
        logger.info(f"Generating audio for new article: {article_id}")
        
        # Clean markdown for speech
        speech_text = self._clean_markdown_for_speech(article_markdown)
        logger.info(f"Cleaned text length: {len(speech_text)} characters")
        
        # Generate speech (run in thread pool since OpenAI client is sync)
        loop = asyncio.get_event_loop()
        audio_bytes = await loop.run_in_executor(
            None,
            self._generate_speech_sync,
            speech_text,
            voice
        )
        
        logger.info(f"Generated audio: {len(audio_bytes)} bytes")
        
        # Upload to S3
        s3_key = await loop.run_in_executor(
            None,
            self._upload_to_s3,
            audio_bytes,
            article_id
        )
        
        # Get URL (relative path)
        audio_url = self._get_cloudfront_url(s3_key)
        
        # Estimate duration
        word_count = len(speech_text.split())
        estimated_duration = int((word_count / 150) * 60)
        
        # Update article in MongoDB
        await self.db.articles.update_one(
            {"_id": ObjectId(article_id)},
            {
                "$set": {
                    "audio_url": audio_url,
                    "audio_s3_key": s3_key,
                    "audio_voice": voice,
                    "audio_duration_seconds": estimated_duration,
                    "audio_generated_at": datetime.now(timezone.utc),
                }
            }
        )
        
        logger.info(f"Updated article with audio URL: {audio_url}")
        
        return {
            "audio_url": audio_url,
            "audio_s3_key": s3_key,
            "audio_voice": voice,
            "audio_duration_seconds": estimated_duration,
        }
    
    async def generate_audio_for_all_articles(
        self,
        voice: str = "fable",
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Generate audio for all articles in the database.
        
        Args:
            voice: OpenAI TTS voice to use
            skip_existing: If True, skip articles that already have audio
            
        Returns:
            Summary of results
        """
        await self._connect_mongo()
        
        # Build query
        query = {}
        if skip_existing:
            query["audio_url"] = {"$exists": False}
        
        # Get all articles
        cursor = self.db.articles.find(query).sort("date", -1)
        articles = await cursor.to_list(length=None)
        
        logger.info(f"Found {len(articles)} articles to process")
        
        results = {
            "total": len(articles),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
        for i, article in enumerate(articles):
            article_id = str(article["_id"])
            title = article.get("topic_title", "Unknown")
            
            logger.info(f"[{i+1}/{len(articles)}] Processing: {title}")
            
            try:
                result = await self.generate_audio_for_article(
                    article_id,
                    voice=voice,
                    force_regenerate=not skip_existing
                )
                
                if result.get("already_exists"):
                    results["skipped"] += 1
                    logger.info(f"  → Skipped (already has audio)")
                else:
                    results["success"] += 1
                    logger.info(f"  → Success: {result['audio_url']}")
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"article_id": article_id, "title": title, "error": str(e)})
                logger.error(f"  → Failed: {e}")
        
        logger.info(f"\nCompleted: {results['success']} success, {results['failed']} failed, {results['skipped']} skipped")
        
        return results
    
    async def close(self):
        """Close connections."""
        if self.mongo_client:
            self.mongo_client.close()
            self._connected = False


# Global instance for import
audio_service = AudioService()


# Standalone script for testing
async def main():
    """Generate audio for a specific article or all articles."""
    import sys
    
    # Check for --all flag
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        voice = sys.argv[2] if len(sys.argv) > 2 else "fable"
        print(f"Generating audio for ALL articles using voice: {voice}")
        print("=" * 60)
        
        service = AudioService()
        try:
            result = await service.generate_audio_for_all_articles(voice=voice, skip_existing=True)
            print("\n" + "=" * 60)
            print("✅ Batch audio generation completed!")
            print(f"   Total: {result['total']}")
            print(f"   Success: {result['success']}")
            print(f"   Failed: {result['failed']}")
            print(f"   Skipped: {result['skipped']}")
            if result['errors']:
                print(f"\n   Errors:")
                for err in result['errors']:
                    print(f"     - {err['title']}: {err['error']}")
        finally:
            await service.close()
    else:
        # Single article
        article_id = sys.argv[1] if len(sys.argv) > 1 else "69324f7217364f1f1af55f05"
        voice = sys.argv[2] if len(sys.argv) > 2 else "fable"
        
        print(f"Generating audio for article: {article_id}")
        print(f"Using voice: {voice}")
        
        service = AudioService()
        try:
            result = await service.generate_audio_for_article(article_id, voice=voice)
            print("\n✅ Audio generated successfully!")
            print(f"   URL: {result['audio_url']}")
            print(f"   Duration: ~{result['audio_duration_seconds']} seconds")
            print(f"   Already existed: {result.get('already_exists', False)}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise
        finally:
            await service.close()


if __name__ == "__main__":
    asyncio.run(main())
