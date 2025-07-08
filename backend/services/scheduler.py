"""
Elite JobHunter X - Job Scraping Scheduler
Advanced automation system for regular job scraping with APScheduler
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import os
import uuid
from pymongo import MongoClient
import json

from .job_scraper import JobScrapingManager, StealthScrapingConfig
from .scraper_indeed import IndeedScraper, create_tech_job_search

logger = logging.getLogger(__name__)

class ScrapingScheduler:
    """Advanced scheduler for automated job scraping"""
    
    def __init__(self):
        self.scheduler = None
        self.scraping_manager = None
        self.is_running = False
        self.session_id = str(uuid.uuid4())
        
        # Database connection
        self.db_client = MongoClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
        self.db = self.db_client[os.environ.get('DB_NAME', 'jobhunter_x_db')]
        self.schedules_collection = self.db['scraping_schedules']
        self.logs_collection = self.db['scraping_logs']
        
        # Default scraping configurations
        self.default_configs = {
            'indeed_software': {
                'scraper': 'indeed',
                'params': create_tech_job_search(
                    title="Software Developer",
                    location="Remote",
                    max_pages=3
                ),
                'enabled': True,
                'interval_hours': 6
            },
            'indeed_frontend': {
                'scraper': 'indeed',
                'params': create_tech_job_search(
                    title="Frontend Developer",
                    location="Remote",
                    max_pages=2
                ),
                'enabled': True,
                'interval_hours': 8
            },
            'indeed_backend': {
                'scraper': 'indeed',
                'params': create_tech_job_search(
                    title="Backend Developer",
                    location="Remote",
                    max_pages=2
                ),
                'enabled': True,
                'interval_hours': 8
            },
            'indeed_fullstack': {
                'scraper': 'indeed',
                'params': create_tech_job_search(
                    title="Full Stack Developer",
                    location="Remote",
                    max_pages=3
                ),
                'enabled': True,
                'interval_hours': 6
            }
        }
        
        self.setup_scheduler()
    
    def setup_scheduler(self):
        """Initialize the APScheduler"""
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': AsyncIOExecutor()
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        # Add event listeners
        self.scheduler.add_listener(self.job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self.job_error, EVENT_JOB_ERROR)
        
        # Initialize scraping manager
        self.scraping_manager = JobScrapingManager()
        self.scraping_manager.register_scraper('indeed', IndeedScraper)
        
        logger.info("Scheduler initialized successfully")
    
    def job_executed(self, event):
        """Handle successful job execution"""
        logger.info(f"Job {event.job_id} executed successfully")
        
        # Log to database
        self.log_scraping_event(
            job_id=event.job_id,
            status='success',
            message=f"Job executed successfully at {datetime.now()}"
        )
    
    def job_error(self, event):
        """Handle job execution errors"""
        logger.error(f"Job {event.job_id} failed: {event.exception}")
        
        # Log to database
        self.log_scraping_event(
            job_id=event.job_id,
            status='error',
            message=f"Job failed: {event.exception}",
            error_details=str(event.exception)
        )
    
    def log_scraping_event(self, job_id: str, status: str, message: str, error_details: str = None):
        """Log scraping events to database"""
        try:
            log_entry = {
                '_id': str(uuid.uuid4()),
                'job_id': job_id,
                'session_id': self.session_id,
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'error_details': error_details
            }
            
            self.logs_collection.insert_one(log_entry)
            
        except Exception as e:
            logger.error(f"Failed to log scraping event: {e}")
    
    async def scrape_jobs_task(self, config_name: str, scraper_name: str, search_params: Dict[str, Any]):
        """Task function for scheduled job scraping"""
        try:
            logger.info(f"Starting scheduled scraping task: {config_name}")
            
            # Log start
            self.log_scraping_event(
                job_id=config_name,
                status='started',
                message=f"Starting scraping for {config_name} with {scraper_name}"
            )
            
            # Run scraper
            results = await self.scraping_manager.run_scraper(scraper_name, search_params)
            
            # Log results
            self.log_scraping_event(
                job_id=config_name,
                status='completed',
                message=f"Scraping completed for {config_name}: {results}"
            )
            
            logger.info(f"Completed scraping task: {config_name}, Results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in scraping task {config_name}: {e}")
            self.log_scraping_event(
                job_id=config_name,
                status='error',
                message=f"Scraping failed for {config_name}",
                error_details=str(e)
            )
            raise
    
    def add_scraping_schedule(self, config_name: str, config: Dict[str, Any]):
        """Add a new scraping schedule"""
        try:
            if not config.get('enabled', True):
                logger.info(f"Skipping disabled schedule: {config_name}")
                return
            
            scraper_name = config.get('scraper', 'indeed')
            search_params = config.get('params', {})
            interval_hours = config.get('interval_hours', 6)
            
            # Create interval trigger
            trigger = IntervalTrigger(
                hours=interval_hours,
                start_date=datetime.now() + timedelta(seconds=30)  # Start in 30 seconds
            )
            
            # Add job to scheduler
            self.scheduler.add_job(
                func=self.scrape_jobs_task,
                trigger=trigger,
                args=[config_name, scraper_name, search_params],
                id=config_name,
                name=f"Scrape {config_name}",
                replace_existing=True
            )
            
            # Save schedule to database
            schedule_doc = {
                '_id': config_name,
                'scraper': scraper_name,
                'params': search_params,
                'interval_hours': interval_hours,
                'enabled': True,
                'created_at': datetime.now().isoformat(),
                'session_id': self.session_id
            }
            
            self.schedules_collection.replace_one(
                {'_id': config_name}, 
                schedule_doc, 
                upsert=True
            )
            
            logger.info(f"Added scraping schedule: {config_name} (every {interval_hours} hours)")
            
        except Exception as e:
            logger.error(f"Failed to add scraping schedule {config_name}: {e}")
    
    def remove_scraping_schedule(self, config_name: str):
        """Remove a scraping schedule"""
        try:
            self.scheduler.remove_job(config_name)
            self.schedules_collection.delete_one({'_id': config_name})
            logger.info(f"Removed scraping schedule: {config_name}")
            
        except Exception as e:
            logger.error(f"Failed to remove scraping schedule {config_name}: {e}")
    
    def update_scraping_schedule(self, config_name: str, config: Dict[str, Any]):
        """Update an existing scraping schedule"""
        try:
            # Remove existing schedule
            self.remove_scraping_schedule(config_name)
            
            # Add updated schedule
            self.add_scraping_schedule(config_name, config)
            
            logger.info(f"Updated scraping schedule: {config_name}")
            
        except Exception as e:
            logger.error(f"Failed to update scraping schedule {config_name}: {e}")
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs"""
        jobs = []
        
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                'args': job.args
            })
        
        return jobs
    
    def get_scraping_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent scraping logs"""
        logs = list(self.logs_collection.find().sort([('timestamp', -1)]).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for log in logs:
            if '_id' in log:
                log['_id'] = str(log['_id'])
        
        return logs
    
    def get_scraping_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        try:
            # Get stats from last 24 hours
            since_time = datetime.now() - timedelta(hours=24)
            
            total_runs = self.logs_collection.count_documents({
                'timestamp': {'$gte': since_time.isoformat()}
            })
            
            successful_runs = self.logs_collection.count_documents({
                'status': 'completed',
                'timestamp': {'$gte': since_time.isoformat()}
            })
            
            failed_runs = self.logs_collection.count_documents({
                'status': 'error',
                'timestamp': {'$gte': since_time.isoformat()}
            })
            
            # Get job counts from database
            jobs_collection = self.db['jobs_raw']
            total_jobs = jobs_collection.count_documents({})
            
            recent_jobs = jobs_collection.count_documents({
                'scraped_at': {'$gte': since_time.isoformat()}
            })
            
            return {
                'total_scheduled_jobs': len(self.scheduler.get_jobs()),
                'total_runs_24h': total_runs,
                'successful_runs_24h': successful_runs,
                'failed_runs_24h': failed_runs,
                'success_rate': (successful_runs / total_runs * 100) if total_runs > 0 else 0,
                'total_jobs_scraped': total_jobs,
                'jobs_scraped_24h': recent_jobs,
                'is_running': self.is_running,
                'session_id': self.session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get scraping stats: {e}")
            return {}
    
    async def run_manual_scraping(self, config_name: str, scraper_name: str, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Run manual scraping job"""
        try:
            logger.info(f"Starting manual scraping: {config_name}")
            
            # Log start
            self.log_scraping_event(
                job_id=f"manual_{config_name}",
                status='started',
                message=f"Manual scraping started for {config_name}"
            )
            
            # Run scraper
            results = await self.scraping_manager.run_scraper(scraper_name, search_params)
            
            # Log completion
            self.log_scraping_event(
                job_id=f"manual_{config_name}",
                status='completed',
                message=f"Manual scraping completed for {config_name}: {results}"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Manual scraping failed for {config_name}: {e}")
            self.log_scraping_event(
                job_id=f"manual_{config_name}",
                status='error',
                message=f"Manual scraping failed for {config_name}",
                error_details=str(e)
            )
            raise
    
    def start(self):
        """Start the scheduler"""
        try:
            if not self.is_running:
                # Add default schedules
                for config_name, config in self.default_configs.items():
                    self.add_scraping_schedule(config_name, config)
                
                # Start scheduler
                self.scheduler.start()
                self.is_running = True
                
                logger.info("Scraping scheduler started successfully")
                
                # Log start event
                self.log_scraping_event(
                    job_id='scheduler',
                    status='started',
                    message=f"Scheduler started with {len(self.default_configs)} default schedules"
                )
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                
                logger.info("Scraping scheduler stopped")
                
                # Log stop event
                self.log_scraping_event(
                    job_id='scheduler',
                    status='stopped',
                    message="Scheduler stopped"
                )
        
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
    
    def restart(self):
        """Restart the scheduler"""
        self.stop()
        self.start()
    
    def close(self):
        """Close scheduler and database connections"""
        try:
            self.stop()
            if self.db_client:
                self.db_client.close()
                logger.info("Database connection closed")
        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Global scheduler instance
scheduler_instance = None

def get_scheduler() -> ScrapingScheduler:
    """Get or create the global scheduler instance"""
    global scheduler_instance
    
    if scheduler_instance is None:
        scheduler_instance = ScrapingScheduler()
    
    return scheduler_instance

async def start_scheduler():
    """Start the global scheduler"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler

async def stop_scheduler():
    """Stop the global scheduler"""
    scheduler = get_scheduler()
    scheduler.stop()

def create_custom_schedule(
    name: str,
    scraper: str,
    query: str,
    location: str = "Remote",
    interval_hours: int = 6,
    max_pages: int = 3
) -> Dict[str, Any]:
    """Create a custom scraping schedule configuration"""
    
    if scraper == 'indeed':
        params = create_tech_job_search(
            title=query,
            location=location,
            max_pages=max_pages
        )
    else:
        params = {
            'q': query,
            'l': location,
            'max_pages': max_pages
        }
    
    return {
        'scraper': scraper,
        'params': params,
        'enabled': True,
        'interval_hours': interval_hours
    }