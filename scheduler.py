"""
Scheduler for running article generation on a cron schedule.
Uses APScheduler for flexible cron-based scheduling.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
import logging
from config import settings
from services.orchestrator import orchestrator

logger = logging.getLogger(__name__)


class ArticleScheduler:
    """Manages scheduled article generation."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.timezone = pytz.timezone(settings.timezone)
        self.cron_schedule = settings.cron_schedule
        self.is_running = False
    
    def start(self):
        """Start the scheduler with configured cron schedule."""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        # Parse cron schedule (format: minute hour day month day_of_week)
        cron_parts = self.cron_schedule.split()
        if len(cron_parts) != 5:
            logger.error(f"Invalid cron schedule: {self.cron_schedule}")
            logger.error("Format should be: minute hour day month day_of_week")
            logger.error("Example: 0 6 * * * (daily at 6 AM)")
            return
        
        minute, hour, day, month, day_of_week = cron_parts
        
        # Create cron trigger
        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            timezone=self.timezone
        )
        
        # Add job
        self.scheduler.add_job(
            self._run_scheduled_generation,
            trigger=trigger,
            id='daily_article_generation',
            name='Daily Article Generation',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        
        # Get next run time
        next_run = self.scheduler.get_job('daily_article_generation').next_run_time
        
        logger.info("=" * 60)
        logger.info("Article Scheduler Started")
        logger.info(f"Schedule: {self.cron_schedule}")
        logger.info(f"Timezone: {settings.timezone}")
        logger.info(f"Next run: {next_run}")
        logger.info("=" * 60)
    
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler not running")
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped")
    
    async def _run_scheduled_generation(self):
        """Internal method called by scheduler to generate article."""
        logger.info("=" * 60)
        logger.info(f"Scheduled article generation triggered at {datetime.now()}")
        logger.info("=" * 60)
        
        try:
            result = await orchestrator.generate_and_publish(
                topic_seed=None,  # Auto-select topic
                send_email=True,
                save_to_storage=True
            )
            
            logger.info(f"Scheduled generation completed: {result['status']}")
            return result
            
        except Exception as e:
            logger.error(f"Scheduled generation failed: {e}", exc_info=True)
            # TODO: Send error notification
    
    def get_next_run_time(self) -> datetime:
        """Get the next scheduled run time."""
        if not self.is_running:
            return None
        
        job = self.scheduler.get_job('daily_article_generation')
        return job.next_run_time if job else None
    
    def trigger_manual_run(self):
        """Trigger an immediate manual run (doesn't affect schedule)."""
        logger.info("Manual trigger requested")
        self.scheduler.add_job(
            self._run_scheduled_generation,
            id='manual_article_generation',
            replace_existing=True
        )


# Global instance
scheduler = ArticleScheduler()
