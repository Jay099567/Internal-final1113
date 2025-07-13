"""
Elite JobHunter X - Master Automation Orchestrator
MASS SCALE AUTONOMOUS SYSTEM for 100+ candidates

This service coordinates all phases of the job hunting automation process:
1. Continuous job scraping
2. AI job matching for all candidates
3. Resume tailoring for matches
4. Cover letter generation
5. Application submission
6. Recruiter outreach
7. Feedback tracking and learning
8. Performance optimization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from dataclasses import dataclass
from enum import Enum
import uuid
import json
from pymongo import DESCENDING

from .job_scraper import JobScrapingManager
from .job_matching import JobMatchingService
from .resume_tailoring import ResumeTailoringService
from .cover_letter import CoverLetterGenerationService
from .application_submission import ApplicationSubmissionManager
from .linkedin_automation import LinkedInAutomationService
from .feedback_analyzer import FeedbackAnalyzer
from .openrouter import get_openrouter_service

class AutomationPhase(Enum):
    SCRAPING = "scraping"
    MATCHING = "matching"
    TAILORING = "tailoring"
    COVER_LETTER = "cover_letter"
    APPLICATION = "application"
    OUTREACH = "outreach"
    FEEDBACK = "feedback"

class CandidateStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AutomationStats:
    total_candidates: int
    active_candidates: int
    jobs_scraped_today: int
    matches_found_today: int
    applications_sent_today: int
    outreach_sent_today: int
    success_rate: float
    errors_today: int

class MasterAutomationOrchestrator:
    """
    INDUSTRIAL-STRENGTH AUTOMATION ORCHESTRATOR
    Manages autonomous job hunting for 100+ candidates
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.is_running = False
        self.stats = AutomationStats(0, 0, 0, 0, 0, 0, 0.0, 0)
        self.logger = self._setup_logging()
        
        # Initialize all service components
        self.job_scraper = JobScrapingManager()
        self.job_matcher = JobMatchingService(db)
        self.resume_tailor = ResumeTailoringService(db)
        self.cover_letter_service = CoverLetterGenerationService(db)
        self.application_manager = ApplicationSubmissionManager(db)
        self.linkedin_automation = LinkedInAutomationService(db)
        self.feedback_analyzer = FeedbackAnalyzer(db)
        
        # Rate limiting and queue management
        self.max_concurrent_candidates = 10
        self.daily_limits = {
            'applications': 50,  # Per candidate
            'outreach': 20,      # Per candidate
            'scraping_sessions': 24  # System-wide
        }
        
    def _setup_logging(self):
        """Setup comprehensive logging for automation tracking"""
        logger = logging.getLogger("AutomationOrchestrator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def start_autonomous_system(self):
        """
        START THE AUTONOMOUS SYSTEM
        Main loop that continuously processes all candidates
        """
        self.logger.info("🚀 Starting ELITE JOBHUNTER X Autonomous System")
        self.is_running = True
        
        try:
            while self.is_running:
                await self._run_automation_cycle()
                await asyncio.sleep(300)  # 5-minute cycles
                
        except Exception as e:
            self.logger.error(f"❌ Critical error in autonomous system: {e}")
            await self._handle_critical_error(e)
    
    async def _run_automation_cycle(self):
        """Run one complete automation cycle for all candidates"""
        try:
            cycle_id = str(uuid.uuid4())
            self.logger.info(f"🔄 Starting automation cycle {cycle_id}")
            
            # Update statistics
            await self._update_stats()
            
            # Phase 1: Continuous Job Scraping
            await self._execute_job_scraping()
            
            # Phase 2: Process all active candidates
            active_candidates = await self._get_active_candidates()
            
            # Process candidates in batches for scalability
            for batch in self._batch_candidates(active_candidates):
                await self._process_candidate_batch(batch, cycle_id)
            
            # Phase 3: System optimization and learning
            await self._run_system_optimization()
            
            self.logger.info(f"✅ Completed automation cycle {cycle_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Error in automation cycle: {e}")
            self.stats.errors_today += 1
    
    async def _execute_job_scraping(self):
        """Execute job scraping based on schedule and demand"""
        try:
            # Check if scraping is needed
            last_scrape = await self.db.automation_logs.find_one(
                {"action": "job_scraping"},
                sort=[("timestamp", DESCENDING)]
            )
            
            should_scrape = (
                not last_scrape or 
                datetime.utcnow() - last_scrape["timestamp"] > timedelta(hours=2)
            )
            
            if should_scrape:
                self.logger.info("🔍 Executing job scraping session")
                
                # Get all unique candidate preferences for targeted scraping
                candidate_prefs = await self._get_candidate_preferences()
                
                for pref in candidate_prefs:
                    await self.job_scraper.scrape_jobs_async(
                        keywords=pref["keywords"],
                        location=pref["location"],
                        max_jobs=50
                    )
                
                self.stats.jobs_scraped_today += 1
                await self._log_action("job_scraping", {"status": "completed"})
                
        except Exception as e:
            self.logger.error(f"❌ Job scraping error: {e}")
    
    async def _process_candidate_batch(self, candidates: List[Dict], cycle_id: str):
        """Process a batch of candidates through the entire pipeline"""
        tasks = []
        
        for candidate in candidates:
            task = self._process_single_candidate(candidate, cycle_id)
            tasks.append(task)
        
        # Execute batch processing with concurrency control
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_single_candidate(self, candidate: Dict, cycle_id: str):
        """Process single candidate through all automation phases"""
        candidate_id = candidate["_id"]
        
        try:
            self.logger.info(f"👤 Processing candidate {candidate_id}")
            
            # Phase 2: Job Matching
            matches = await self._process_job_matching(candidate_id)
            
            if not matches:
                self.logger.info(f"No new matches for candidate {candidate_id}")
                return
            
            # Phase 3: Resume Tailoring
            tailored_resumes = await self._process_resume_tailoring(candidate_id, matches)
            
            # Phase 4: Cover Letter Generation
            cover_letters = await self._process_cover_letters(candidate_id, matches)
            
            # Phase 5: Application Submission
            applications = await self._process_applications(candidate_id, matches)
            
            # Phase 6: Recruiter Outreach
            outreach_results = await self._process_recruiter_outreach(candidate_id, matches)
            
            # Phase 7: Update candidate progress
            await self._update_candidate_progress(candidate_id, {
                "matches": len(matches),
                "applications": len(applications),
                "outreach": len(outreach_results),
                "last_processed": datetime.utcnow(),
                "cycle_id": cycle_id
            })
            
            self.logger.info(f"✅ Completed processing candidate {candidate_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing candidate {candidate_id}: {e}")
            await self._handle_candidate_error(candidate_id, e)
    
    async def _process_job_matching(self, candidate_id: str) -> List[Dict]:
        """Process job matching for candidate"""
        try:
            # Find new jobs to match
            candidate_data = await self.db.candidates.find_one({"_id": candidate_id})
            if not candidate_data:
                return []
            
            # Get candidate's recent applications to avoid duplicates
            recent_apps = await self.db.applications.find({
                "candidate_id": candidate_id,
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }).to_list(None)
            
            applied_job_ids = [app["job_id"] for app in recent_apps]
            
            # Find matching jobs
            matches = await self.job_matcher.match_jobs_for_candidate(
                candidate_id, 
                exclude_job_ids=applied_job_ids,
                min_score=0.7,
                max_matches=10
            )
            
            self.stats.matches_found_today += len(matches)
            return matches
            
        except Exception as e:
            self.logger.error(f"Job matching error for {candidate_id}: {e}")
            return []
    
    async def _process_resume_tailoring(self, candidate_id: str, matches: List[Dict]) -> List[Dict]:
        """Process resume tailoring for job matches"""
        tailored_resumes = []
        
        try:
            for match in matches[:3]:  # Limit to top 3 matches per cycle
                job_data = match["job"]
                
                # Generate tailored resume
                tailored_resume = await self.resume_tailor.tailor_resume_for_job(
                    candidate_id=candidate_id,
                    job_description=job_data.get("description", ""),
                    job_title=job_data.get("title", ""),
                    company=job_data.get("company", ""),
                    strategy="job_specific"
                )
                
                if tailored_resume:
                    tailored_resumes.append({
                        "job_id": match["job_id"],
                        "resume_version_id": tailored_resume["version_id"],
                        "ats_score": tailored_resume.get("ats_score", 0)
                    })
            
            return tailored_resumes
            
        except Exception as e:
            self.logger.error(f"Resume tailoring error for {candidate_id}: {e}")
            return []
    
    async def _process_cover_letters(self, candidate_id: str, matches: List[Dict]) -> List[Dict]:
        """Process cover letter generation for job matches"""
        cover_letters = []
        
        try:
            for match in matches[:3]:  # Limit to top 3 matches per cycle
                job_data = match["job"]
                
                # Generate cover letter
                cover_letter = await self.cover_letter_service.generate_cover_letter(
                    candidate_id=candidate_id,
                    job_id=match["job_id"],
                    tone="professional",
                    company_name=job_data.get("company", ""),
                    job_title=job_data.get("title", "")
                )
                
                if cover_letter:
                    cover_letters.append({
                        "job_id": match["job_id"],
                        "cover_letter_id": cover_letter["_id"],
                        "tone": cover_letter["tone"]
                    })
            
            return cover_letters
            
        except Exception as e:
            self.logger.error(f"Cover letter generation error for {candidate_id}: {e}")
            return []
    
    async def _process_applications(self, candidate_id: str, matches: List[Dict]) -> List[Dict]:
        """Process job applications submission"""
        applications = []
        
        try:
            # Check daily application limit
            today_apps = await self.db.applications.count_documents({
                "candidate_id": candidate_id,
                "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
            })
            
            if today_apps >= self.daily_limits['applications']:
                self.logger.info(f"Daily application limit reached for {candidate_id}")
                return []
            
            # Submit applications for top matches
            remaining_apps = self.daily_limits['applications'] - today_apps
            
            for match in matches[:min(remaining_apps, 2)]:  # Max 2 applications per cycle
                job_data = match["job"]
                
                # Submit application
                application_result = await self.application_manager.submit_application(
                    candidate_id=candidate_id,
                    job_id=match["job_id"],
                    job_url=job_data.get("url", ""),
                    method="auto_detect"
                )
                
                if application_result and application_result.get("status") == "submitted":
                    applications.append({
                        "job_id": match["job_id"],
                        "application_id": application_result["application_id"],
                        "method": application_result["method"]
                    })
                    
                    self.stats.applications_sent_today += 1
            
            return applications
            
        except Exception as e:
            self.logger.error(f"Application submission error for {candidate_id}: {e}")
            return []
    
    async def _process_recruiter_outreach(self, candidate_id: str, matches: List[Dict]) -> List[Dict]:
        """Process recruiter outreach for job opportunities"""
        outreach_results = []
        
        try:
            # Check daily outreach limit
            today_outreach = await self.db.outreach_messages.count_documents({
                "candidate_id": candidate_id,
                "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
            })
            
            if today_outreach >= self.daily_limits['outreach']:
                self.logger.info(f"Daily outreach limit reached for {candidate_id}")
                return []
            
            # Execute outreach for top companies
            remaining_outreach = self.daily_limits['outreach'] - today_outreach
            
            for match in matches[:min(remaining_outreach, 3)]:  # Max 3 outreach per cycle
                job_data = match["job"]
                company = job_data.get("company", "")
                
                if company:
                    # Find and contact recruiters
                    outreach_result = await self.linkedin_automation.execute_recruiter_outreach(
                        candidate_id=candidate_id,
                        company=company,
                        job_title=job_data.get("title", ""),
                        job_id=match["job_id"]
                    )
                    
                    if outreach_result:
                        outreach_results.append({
                            "job_id": match["job_id"],
                            "company": company,
                            "contacts_reached": outreach_result.get("contacts_reached", 0),
                            "messages_sent": outreach_result.get("messages_sent", 0)
                        })
                        
                        self.stats.outreach_sent_today += outreach_result.get("messages_sent", 0)
            
            return outreach_results
            
        except Exception as e:
            self.logger.error(f"Recruiter outreach error for {candidate_id}: {e}")
            return []
    
    async def _run_system_optimization(self):
        """Run system optimization and learning algorithms"""
        try:
            # Analyze performance and optimize strategies
            await self.feedback_analyzer.analyze_daily_performance()
            
            # Optimize AI model parameters based on success rates
            await self._optimize_matching_algorithms()
            
            # Clean up old data and optimize database
            await self._cleanup_old_data()
            
        except Exception as e:
            self.logger.error(f"System optimization error: {e}")
    
    async def _get_active_candidates(self) -> List[Dict]:
        """Get all active candidates for processing"""
        cursor = self.db.candidates.find({
            "status": "active",
            "automation_enabled": True
        })
        
        candidates = await cursor.to_list(None)
        self.stats.active_candidates = len(candidates)
        
        return candidates
    
    async def _get_candidate_preferences(self) -> List[Dict]:
        """Get unique candidate preferences for targeted scraping"""
        pipeline = [
            {"$match": {"status": "active", "automation_enabled": True}},
            {"$group": {
                "_id": {
                    "keywords": "$job_preferences.keywords",
                    "location": "$job_preferences.location"
                },
                "count": {"$sum": 1}
            }},
            {"$project": {
                "keywords": "$_id.keywords",
                "location": "$_id.location",
                "candidate_count": "$count"
            }}
        ]
        
        cursor = self.db.candidates.aggregate(pipeline)
        prefs = await cursor.to_list(None)
        
        return prefs
    
    def _batch_candidates(self, candidates: List[Dict]) -> List[List[Dict]]:
        """Split candidates into batches for concurrent processing"""
        batch_size = self.max_concurrent_candidates
        
        for i in range(0, len(candidates), batch_size):
            yield candidates[i:i + batch_size]
    
    async def _update_stats(self):
        """Update real-time system statistics"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0)
        
        # Update daily counters
        self.stats.total_candidates = await self.db.candidates.count_documents({})
        self.stats.jobs_scraped_today = await self.db.automation_logs.count_documents({
            "action": "job_scraping",
            "timestamp": {"$gte": today}
        })
        
        # Calculate success rate
        total_apps = await self.db.applications.count_documents({
            "created_at": {"$gte": today}
        })
        successful_apps = await self.db.applications.count_documents({
            "created_at": {"$gte": today},
            "status": {"$in": ["interview_scheduled", "offer_received"]}
        })
        
        self.stats.success_rate = (successful_apps / total_apps * 100) if total_apps > 0 else 0.0
    
    async def _log_action(self, action: str, data: Dict[str, Any]):
        """Log automation actions for tracking and analysis"""
        await self.db.automation_logs.insert_one({
            "_id": str(uuid.uuid4()),
            "action": action,
            "data": data,
            "timestamp": datetime.utcnow()
        })
    
    async def _update_candidate_progress(self, candidate_id: str, progress_data: Dict):
        """Update candidate automation progress"""
        await self.db.candidates.update_one(
            {"_id": candidate_id},
            {
                "$set": {
                    "automation_progress": progress_data,
                    "last_processed": datetime.utcnow()
                }
            }
        )
    
    async def _handle_candidate_error(self, candidate_id: str, error: Exception):
        """Handle candidate-specific errors"""
        await self.db.candidates.update_one(
            {"_id": candidate_id},
            {
                "$inc": {"error_count": 1},
                "$set": {
                    "last_error": str(error),
                    "last_error_time": datetime.utcnow()
                }
            }
        )
    
    async def _handle_critical_error(self, error: Exception):
        """Handle critical system errors"""
        self.logger.critical(f"CRITICAL SYSTEM ERROR: {error}")
        self.is_running = False
        
        # Log critical error
        await self._log_action("critical_error", {
            "error": str(error),
            "system_status": "stopped"
        })
    
    async def stop_autonomous_system(self):
        """Stop the autonomous system gracefully"""
        self.logger.info("🛑 Stopping ELITE JOBHUNTER X Autonomous System")
        self.is_running = False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "is_running": self.is_running,
            "stats": self.stats.__dict__,
            "last_update": datetime.utcnow(),
            "active_phases": [phase.value for phase in AutomationPhase],
            "rate_limits": self.daily_limits
        }
    
    async def _optimize_matching_algorithms(self):
        """Optimize job matching algorithms based on performance data"""
        try:
            # Analyze successful matches vs unsuccessful ones
            successful_matches = await self.db.applications.find({
                "status": {"$in": ["interview_scheduled", "offer_received"]},
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
            }).to_list(None)
            
            # Extract patterns from successful matches
            # This would include analyzing keywords, job types, companies, etc.
            # For now, we'll log the optimization attempt
            
            await self._log_action("algorithm_optimization", {
                "successful_matches_analyzed": len(successful_matches),
                "optimization_type": "matching_algorithm"
            })
            
        except Exception as e:
            self.logger.error(f"Algorithm optimization error: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old automation data to maintain performance"""
        try:
            # Remove logs older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            deleted_logs = await self.db.automation_logs.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            # Remove old temporary files
            deleted_temp = await self.db.temp_files.delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            
            self.logger.info(f"🧹 Cleaned up {deleted_logs.deleted_count} logs and {deleted_temp.deleted_count} temp files")
            
        except Exception as e:
            self.logger.error(f"Data cleanup error: {e}")

# Global orchestrator instance
automation_orchestrator = None

async def get_automation_orchestrator(db: AsyncIOMotorDatabase) -> MasterAutomationOrchestrator:
    """Get or create the global automation orchestrator instance"""
    global automation_orchestrator
    
    if automation_orchestrator is None:
        automation_orchestrator = MasterAutomationOrchestrator(db)
    
    return automation_orchestrator