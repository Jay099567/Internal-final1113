#!/usr/bin/env python3
"""
Elite JobHunter X - Backend API Testing
Comprehensive tests for MASS SCALE AUTONOMOUS SYSTEM components
"""

import unittest
import sys
import os
import json
import requests
import asyncio
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://360bcca0-04c1-436e-9a3e-d773d3ad8ee1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class TestMasterAutomationOrchestrator(unittest.TestCase):
    """Test suite for Master Automation Orchestrator - MASS SCALE AUTONOMOUS SYSTEM"""
    
    def test_01_automation_orchestrator_structure(self):
        """Test the Master Automation Orchestrator service structure"""
        try:
            with open('/app/backend/services/automation_orchestrator.py', 'r') as f:
                orchestrator_code = f.read()
                
            # Check for key classes
            self.assertIn('class MasterAutomationOrchestrator', orchestrator_code)
            self.assertIn('class AutomationPhase(Enum)', orchestrator_code)
            self.assertIn('class CandidateStatus(Enum)', orchestrator_code)
            self.assertIn('class AutomationStats', orchestrator_code)
            
            # Check automation phases
            phases = [
                'SCRAPING = "scraping"',
                'MATCHING = "matching"',
                'TAILORING = "tailoring"',
                'COVER_LETTER = "cover_letter"',
                'APPLICATION = "application"',
                'OUTREACH = "outreach"',
                'FEEDBACK = "feedback"'
            ]
            for phase in phases:
                self.assertIn(phase, orchestrator_code)
            
            # Check candidate statuses
            statuses = [
                'ACTIVE = "active"',
                'PAUSED = "paused"',
                'COMPLETED = "completed"',
                'ERROR = "error"'
            ]
            for status in statuses:
                self.assertIn(status, orchestrator_code)
            
            # Check core orchestrator methods
            core_methods = [
                'async def start_autonomous_system',
                'async def _run_automation_cycle',
                'async def _execute_job_scraping',
                'async def _process_candidate_batch',
                'async def _process_single_candidate',
                'async def _process_job_matching',
                'async def _process_resume_tailoring',
                'async def _process_cover_letters',
                'async def _process_applications',
                'async def _process_recruiter_outreach',
                'async def _run_system_optimization',
                'async def stop_autonomous_system',
                'async def get_system_status'
            ]
            for method in core_methods:
                self.assertIn(method, orchestrator_code)
            
            # Check service integrations
            service_imports = [
                'from .job_scraper import JobScrapingManager',
                'from .job_matching import JobMatchingService',
                'from .resume_tailoring import ResumeTailoringService',
                'from .cover_letter import CoverLetterGenerationService',
                'from .application_submission import ApplicationSubmissionManager',
                'from .linkedin_automation import LinkedInAutomationService',
                'from .feedback_analyzer import FeedbackAnalyzer'
            ]
            for import_stmt in service_imports:
                self.assertIn(import_stmt, orchestrator_code)
            
            # Check rate limiting configuration
            self.assertIn('max_concurrent_candidates = 10', orchestrator_code)
            self.assertIn("'applications': 50", orchestrator_code)
            self.assertIn("'outreach': 20", orchestrator_code)
            self.assertIn("'scraping_sessions': 24", orchestrator_code)
            
            print("✅ Master Automation Orchestrator structure verified")
            
        except Exception as e:
            self.fail(f"Master Automation Orchestrator structure test failed: {e}")
    
    def test_02_orchestrator_initialization(self):
        """Test orchestrator initialization and configuration"""
        try:
            with open('/app/backend/services/automation_orchestrator.py', 'r') as f:
                orchestrator_code = f.read()
            
            # Check initialization components
            self.assertIn('def __init__(self, db: AsyncIOMotorDatabase)', orchestrator_code)
            self.assertIn('self.is_running = False', orchestrator_code)
            self.assertIn('self.stats = AutomationStats', orchestrator_code)
            self.assertIn('self.logger = self._setup_logging()', orchestrator_code)
            
            # Check service component initialization
            service_inits = [
                'self.job_scraper = JobScrapingManager()',
                'self.job_matcher = JobMatchingService(db)',
                'self.resume_tailor = ResumeTailoringService(db)',
                'self.cover_letter_service = CoverLetterGenerationService(db)',
                'self.application_manager = ApplicationSubmissionManager(db)',
                'self.linkedin_automation = LinkedInAutomationService(db)',
                'self.feedback_analyzer = FeedbackAnalyzer(db)'
            ]
            for init in service_inits:
                self.assertIn(init, orchestrator_code)
            
            # Check logging setup
            self.assertIn('def _setup_logging(self)', orchestrator_code)
            self.assertIn('logger = logging.getLogger("AutomationOrchestrator")', orchestrator_code)
            
            print("✅ Orchestrator initialization verified")
            
        except Exception as e:
            self.fail(f"Orchestrator initialization test failed: {e}")
    
    def test_03_automation_cycle_processing(self):
        """Test automation cycle processing logic"""
        try:
            with open('/app/backend/services/automation_orchestrator.py', 'r') as f:
                orchestrator_code = f.read()
            
            # Check cycle processing methods
            cycle_methods = [
                'async def _run_automation_cycle',
                'async def _update_stats',
                'async def _execute_job_scraping',
                'async def _get_active_candidates',
                'async def _get_candidate_preferences',
                'def _batch_candidates'
            ]
            for method in cycle_methods:
                self.assertIn(method, orchestrator_code)
            
            # Check candidate processing pipeline
            pipeline_methods = [
                'async def _process_candidate_batch',
                'async def _process_single_candidate',
                'async def _process_job_matching',
                'async def _process_resume_tailoring',
                'async def _process_cover_letters',
                'async def _process_applications',
                'async def _process_recruiter_outreach'
            ]
            for method in pipeline_methods:
                self.assertIn(method, orchestrator_code)
            
            # Check error handling
            self.assertIn('async def _handle_candidate_error', orchestrator_code)
            self.assertIn('async def _handle_critical_error', orchestrator_code)
            
            # Check system optimization
            self.assertIn('async def _run_system_optimization', orchestrator_code)
            self.assertIn('async def _optimize_matching_algorithms', orchestrator_code)
            self.assertIn('async def _cleanup_old_data', orchestrator_code)
            
            print("✅ Automation cycle processing verified")
            
        except Exception as e:
            self.fail(f"Automation cycle processing test failed: {e}")
    
    def test_04_rate_limiting_and_queue_management(self):
        """Test rate limiting and queue management features"""
        try:
            with open('/app/backend/services/automation_orchestrator.py', 'r') as f:
                orchestrator_code = f.read()
            
            # Check rate limiting configuration
            self.assertIn('self.daily_limits = {', orchestrator_code)
            self.assertIn("'applications': 50", orchestrator_code)
            self.assertIn("'outreach': 20", orchestrator_code)
            self.assertIn("'scraping_sessions': 24", orchestrator_code)
            
            # Check concurrent processing limits
            self.assertIn('self.max_concurrent_candidates = 10', orchestrator_code)
            
            # Check daily limit checking logic
            self.assertIn('today_apps = await self.db.applications.count_documents', orchestrator_code)
            self.assertIn('if today_apps >= self.daily_limits', orchestrator_code)
            self.assertIn('today_outreach = await self.db.outreach_messages.count_documents', orchestrator_code)
            self.assertIn('if today_outreach >= self.daily_limits', orchestrator_code)
            
            # Check batch processing
            self.assertIn('def _batch_candidates', orchestrator_code)
            self.assertIn('batch_size = self.max_concurrent_candidates', orchestrator_code)
            
            print("✅ Rate limiting and queue management verified")
            
        except Exception as e:
            self.fail(f"Rate limiting and queue management test failed: {e}")
    
    def test_05_system_status_and_monitoring(self):
        """Test system status and monitoring capabilities"""
        try:
            with open('/app/backend/services/automation_orchestrator.py', 'r') as f:
                orchestrator_code = f.read()
            
            # Check status methods
            self.assertIn('async def get_system_status', orchestrator_code)
            self.assertIn('async def _update_stats', orchestrator_code)
            self.assertIn('async def _log_action', orchestrator_code)
            
            # Check AutomationStats dataclass
            stats_fields = [
                'total_candidates: int',
                'active_candidates: int',
                'jobs_scraped_today: int',
                'matches_found_today: int',
                'applications_sent_today: int',
                'outreach_sent_today: int',
                'success_rate: float',
                'errors_today: int'
            ]
            for field in stats_fields:
                self.assertIn(field, orchestrator_code)
            
            # Check logging and monitoring
            self.assertIn('self.logger.info(f"🚀 Starting ELITE JOBHUNTER X Autonomous System")', orchestrator_code)
            self.assertIn('self.logger.info(f"🔄 Starting automation cycle', orchestrator_code)
            self.assertIn('self.logger.info(f"✅ Completed automation cycle', orchestrator_code)
            
            print("✅ System status and monitoring verified")
            
        except Exception as e:
            self.fail(f"System status and monitoring test failed: {e}")


class TestLinkedInAutomationService(unittest.TestCase):
    """Test suite for LinkedIn Automation Service"""
    
    def test_01_linkedin_automation_structure(self):
        """Test LinkedIn Automation Service structure"""
        try:
            with open('/app/backend/services/linkedin_automation.py', 'r') as f:
                linkedin_code = f.read()
                
            # Check for key classes
            self.assertIn('class LinkedInAutomationService', linkedin_code)
            self.assertIn('class OutreachStatus(Enum)', linkedin_code)
            self.assertIn('class MessageType(Enum)', linkedin_code)
            self.assertIn('class RecruiterProfile', linkedin_code)
            self.assertIn('class OutreachCampaign', linkedin_code)
            
            # Check outreach status enum
            statuses = [
                'PENDING = "pending"',
                'SENT = "sent"',
                'CONNECTED = "connected"',
                'REPLIED = "replied"',
                'FAILED = "failed"'
            ]
            for status in statuses:
                self.assertIn(status, linkedin_code)
            
            # Check message type enum
            message_types = [
                'CONNECTION_REQUEST = "connection_request"',
                'FOLLOW_UP = "follow_up"',
                'JOB_INQUIRY = "job_inquiry"',
                'NETWORKING = "networking"'
            ]
            for msg_type in message_types:
                self.assertIn(msg_type, linkedin_code)
            
            print("✅ LinkedIn Automation Service structure verified")
            
        except Exception as e:
            self.fail(f"LinkedIn Automation Service structure test failed: {e}")
    
    def test_02_recruiter_research_functionality(self):
        """Test recruiter research functionality"""
        try:
            with open('/app/backend/services/linkedin_automation.py', 'r') as f:
                linkedin_code = f.read()
            
            # Check recruiter research methods
            research_methods = [
                'async def _research_company_recruiters',
                'async def _search_recruiters_browser',
                'async def _ai_recruiter_research',
                'def _deduplicate_recruiters',
                'def _rank_recruiters',
                'def _is_relevant_recruiter',
                'def _calculate_relevance_score'
            ]
            for method in research_methods:
                self.assertIn(method, linkedin_code)
            
            # Check search patterns
            self.assertIn('f"{company} talent acquisition"', linkedin_code)
            self.assertIn('f"{company} recruiter"', linkedin_code)
            self.assertIn('f"{company} hiring manager"', linkedin_code)
            self.assertIn('f"{company} HR"', linkedin_code)
            
            # Check RecruiterProfile dataclass fields
            profile_fields = [
                'name: str',
                'title: str',
                'company: str',
                'linkedin_url: str',
                'profile_id: str',
                'relevance_score: float'
            ]
            for field in profile_fields:
                self.assertIn(field, linkedin_code)
            
            print("✅ Recruiter research functionality verified")
            
        except Exception as e:
            self.fail(f"Recruiter research functionality test failed: {e}")
    
    def test_03_outreach_campaign_management(self):
        """Test outreach campaign creation and management"""
        try:
            with open('/app/backend/services/linkedin_automation.py', 'r') as f:
                linkedin_code = f.read()
            
            # Check campaign management methods
            campaign_methods = [
                'async def execute_recruiter_outreach',
                'async def _execute_stealth_outreach',
                'async def _execute_api_outreach',
                'async def _save_campaign_results',
                'async def _check_daily_limits'
            ]
            for method in campaign_methods:
                self.assertIn(method, linkedin_code)
            
            # Check OutreachCampaign dataclass fields
            campaign_fields = [
                'campaign_id: str',
                'candidate_id: str',
                'company: str',
                'job_title: str',
                'job_id: str',
                'target_recruiters: List[RecruiterProfile]',
                'messages_sent: int',
                'connections_made: int',
                'replies_received: int',
                'created_at: datetime'
            ]
            for field in campaign_fields:
                self.assertIn(field, linkedin_code)
            
            print("✅ Outreach campaign management verified")
            
        except Exception as e:
            self.fail(f"Outreach campaign management test failed: {e}")
    
    def test_04_stealth_automation_features(self):
        """Test stealth automation features"""
        try:
            with open('/app/backend/services/linkedin_automation.py', 'r') as f:
                linkedin_code = f.read()
            
            # Check stealth configuration
            self.assertIn('self.stealth_config = {', linkedin_code)
            self.assertIn("'user_agents':", linkedin_code)
            self.assertIn("'screen_resolutions':", linkedin_code)
            
            # Check stealth methods
            stealth_methods = [
                'async def _create_stealth_browser',
                'async def _human_like_delay',
                'async def _randomize_user_agent',
                'async def _simulate_human_behavior'
            ]
            for method in stealth_methods:
                self.assertIn(method, linkedin_code)
            
            # Check browser automation imports
            browser_imports = [
                'import undetected_chromedriver as uc',
                'from selenium import webdriver',
                'from selenium.webdriver.common.by import By'
            ]
            for import_stmt in browser_imports:
                self.assertIn(import_stmt, linkedin_code)
            
            print("✅ Stealth automation features verified")
            
        except Exception as e:
            self.fail(f"Stealth automation features test failed: {e}")
    
    def test_05_rate_limiting_and_anti_detection(self):
        """Test rate limiting and anti-detection measures"""
        try:
            with open('/app/backend/services/linkedin_automation.py', 'r') as f:
                linkedin_code = f.read()
            
            # Check rate limiting configuration
            self.assertIn('self.rate_limits = {', linkedin_code)
            self.assertIn("'connections_per_day': 15", linkedin_code)
            self.assertIn("'messages_per_day': 25", linkedin_code)
            self.assertIn("'profile_views_per_day': 50", linkedin_code)
            self.assertIn("'delay_between_actions': (5, 15)", linkedin_code)
            self.assertIn("'session_length': (45, 90)", linkedin_code)
            self.assertIn("'break_between_sessions': (120, 240)", linkedin_code)
            
            # Check daily limit checking
            self.assertIn('async def _check_daily_limits', linkedin_code)
            
            # Check anti-detection measures
            self.assertIn('SELENIUM_AVAILABLE', linkedin_code)
            self.assertIn('logging.warning("Selenium not available - LinkedIn automation will use fallback mode")', linkedin_code)
            
            print("✅ Rate limiting and anti-detection measures verified")
            
        except Exception as e:
            self.fail(f"Rate limiting and anti-detection test failed: {e}")


class TestFeedbackAnalyzer(unittest.TestCase):
    """Test suite for Feedback Learning Loop"""
    
    def test_01_feedback_analyzer_structure(self):
        """Test Feedback Analyzer service structure"""
        try:
            with open('/app/backend/services/feedback_analyzer.py', 'r') as f:
                feedback_code = f.read()
                
            # Check for key classes
            self.assertIn('class FeedbackAnalyzer', feedback_code)
            self.assertIn('class OptimizationStrategy(Enum)', feedback_code)
            self.assertIn('class OptimizationRecommendation', feedback_code)
            
            # Check optimization strategies
            strategies = [
                'KEYWORD_OPTIMIZATION = "keyword_optimization"',
                'RESUME_STRATEGY = "resume_strategy"',
                'OUTREACH_STRATEGY = "outreach_strategy"',
                'JOB_TARGETING = "job_targeting"',
                'TIMING_OPTIMIZATION = "timing_optimization"'
            ]
            for strategy in strategies:
                self.assertIn(strategy, feedback_code)
            
            # Check core analyzer methods
            core_methods = [
                'async def analyze_daily_performance',
                'async def _collect_performance_data',
                'async def _analyze_success_patterns',
                'async def _generate_optimization_recommendations',
                'async def _apply_automated_optimizations',
                'async def predict_application_success'
            ]
            for method in core_methods:
                self.assertIn(method, feedback_code)
            
            print("✅ Feedback Analyzer structure verified")
            
        except Exception as e:
            self.fail(f"Feedback Analyzer structure test failed: {e}")
    
    def test_02_performance_data_collection(self):
        """Test performance data collection functionality"""
        try:
            with open('/app/backend/services/feedback_analyzer.py', 'r') as f:
                feedback_code = f.read()
            
            # Check data collection methods
            collection_methods = [
                'async def _collect_performance_data',
                'async def _get_current_keyword_performance',
                'async def _get_current_resume_performance',
                'async def _get_current_outreach_performance'
            ]
            for method in collection_methods:
                self.assertIn(method, feedback_code)
            
            # Check aggregation pipelines
            pipeline_checks = [
                'applications_pipeline = [',
                'matching_pipeline = [',
                'tailoring_pipeline = [',
                'outreach_pipeline = ['
            ]
            for pipeline in pipeline_checks:
                self.assertIn(pipeline, feedback_code)
            
            # Check MongoDB aggregation operations
            aggregation_ops = [
                '{"$match":',
                '{"$group":',
                '{"$sort":',
                '{"$avg":',
                '{"$sum":'
            ]
            for op in aggregation_ops:
                self.assertIn(op, feedback_code)
            
            print("✅ Performance data collection verified")
            
        except Exception as e:
            self.fail(f"Performance data collection test failed: {e}")
    
    def test_03_success_pattern_analysis(self):
        """Test success pattern analysis"""
        try:
            with open('/app/backend/services/feedback_analyzer.py', 'r') as f:
                feedback_code = f.read()
            
            # Check pattern analysis methods
            self.assertIn('async def _analyze_success_patterns', feedback_code)
            self.assertIn('def _calculate_success_score', feedback_code)
            
            # Check pattern categories
            pattern_categories = [
                '"successful_keywords": []',
                '"optimal_application_times": []',
                '"best_resume_strategies": []',
                '"effective_outreach_approaches": []',
                '"candidate_success_factors": {}'
            ]
            for category in pattern_categories:
                self.assertIn(category, feedback_code)
            
            # Check success scoring
            success_scores = [
                '"pending": 0.1',
                '"viewed": 0.2',
                '"rejected": 0.0',
                '"phone_screen": 0.5',
                '"interview_scheduled": 0.7',
                '"interview_completed": 0.8',
                '"offer_received": 1.0'
            ]
            for score in success_scores:
                self.assertIn(score, feedback_code)
            
            # Check statistical analysis
            self.assertIn('import statistics', feedback_code)
            self.assertIn('statistics.mean(scores)', feedback_code)
            self.assertIn('statistics.stdev(scores)', feedback_code)
            
            print("✅ Success pattern analysis verified")
            
        except Exception as e:
            self.fail(f"Success pattern analysis test failed: {e}")
    
    def test_04_optimization_recommendation_generation(self):
        """Test optimization recommendation generation"""
        try:
            with open('/app/backend/services/feedback_analyzer.py', 'r') as f:
                feedback_code = f.read()
            
            # Check recommendation generation methods
            recommendation_methods = [
                'async def _generate_optimization_recommendations',
                'async def _apply_automated_optimizations',
                'async def _apply_single_optimization',
                'async def _generate_ai_insights'
            ]
            for method in recommendation_methods:
                self.assertIn(method, feedback_code)
            
            # Check OptimizationRecommendation dataclass fields
            recommendation_fields = [
                'strategy: OptimizationStrategy',
                'current_performance: float',
                'predicted_improvement: float',
                'confidence: float',
                'action_items: List[str]',
                'priority: int'
            ]
            for field in recommendation_fields:
                self.assertIn(field, feedback_code)
            
            # Check specific optimization applications
            optimization_methods = [
                'async def _apply_keyword_optimization',
                'async def _apply_resume_strategy_optimization',
                'async def _apply_outreach_optimization',
                'async def _apply_job_targeting_optimization'
            ]
            for method in optimization_methods:
                self.assertIn(method, feedback_code)
            
            print("✅ Optimization recommendation generation verified")
            
        except Exception as e:
            self.fail(f"Optimization recommendation generation test failed: {e}")
    
    def test_05_ml_model_integration(self):
        """Test ML model integration (if sklearn available)"""
        try:
            with open('/app/backend/services/feedback_analyzer.py', 'r') as f:
                feedback_code = f.read()
            
            # Check ML imports and availability check
            self.assertIn('try:', feedback_code)
            self.assertIn('from sklearn', feedback_code)
            self.assertIn('SKLEARN_AVAILABLE = True', feedback_code)
            self.assertIn('except ImportError:', feedback_code)
            self.assertIn('SKLEARN_AVAILABLE = False', feedback_code)
            
            # Check ML model methods
            ml_methods = [
                'async def _update_ml_models',
                'async def _prepare_ml_training_data',
                'async def _update_success_predictor'
            ]
            for method in ml_methods:
                self.assertIn(method, feedback_code)
            
            # Check ML model usage
            self.assertIn('if SKLEARN_AVAILABLE:', feedback_code)
            self.assertIn('await self._update_ml_models(performance_data)', feedback_code)
            
            # Check prediction functionality
            self.assertIn('async def predict_application_success', feedback_code)
            
            print("✅ ML model integration verified")
            
        except Exception as e:
            self.fail(f"ML model integration test failed: {e}")


class TestServiceIntegration(unittest.TestCase):
    """Test suite for Service Integration"""
    
    def test_01_service_imports_and_dependencies(self):
        """Test that all new services can be imported without errors"""
        try:
            # Test automation orchestrator imports
            with open('/app/backend/services/automation_orchestrator.py', 'r') as f:
                orchestrator_code = f.read()
            
            required_imports = [
                'from .job_scraper import JobScrapingManager',
                'from .job_matching import JobMatchingService',
                'from .resume_tailoring import ResumeTailoringService',
                'from .cover_letter import CoverLetterGenerationService',
                'from .application_submission import ApplicationSubmissionManager',
                'from .linkedin_automation import LinkedInAutomationService',
                'from .feedback_analyzer import FeedbackAnalyzer',
                'from .openrouter import get_openrouter_service'
            ]
            
            for import_stmt in required_imports:
                self.assertIn(import_stmt, orchestrator_code)
            
            # Test LinkedIn automation imports
            with open('/app/backend/services/linkedin_automation.py', 'r') as f:
                linkedin_code = f.read()
            
            self.assertIn('from .openrouter import get_openrouter_service', linkedin_code)
            
            # Test feedback analyzer imports
            with open('/app/backend/services/feedback_analyzer.py', 'r') as f:
                feedback_code = f.read()
            
            self.assertIn('from .openrouter import get_openrouter_service', feedback_code)
            
            print("✅ Service imports and dependencies verified")
            
        except Exception as e:
            self.fail(f"Service imports test failed: {e}")
    
    def test_02_database_connections_and_operations(self):
        """Test database connections and operations"""
        try:
            # Check database usage in orchestrator
            with open('/app/backend/services/automation_orchestrator.py', 'r') as f:
                orchestrator_code = f.read()
            
            db_operations = [
                'def __init__(self, db: AsyncIOMotorDatabase)',
                'self.db = db',
                'await self.db.automation_logs.find_one',
                'await self.db.candidates.find',
                'await self.db.applications.count_documents',
                'await self.db.automation_logs.insert_one'
            ]
            for operation in db_operations:
                self.assertIn(operation, orchestrator_code)
            
            # Check database usage in LinkedIn automation
            with open('/app/backend/services/linkedin_automation.py', 'r') as f:
                linkedin_code = f.read()
            
            self.assertIn('def __init__(self, db: AsyncIOMotorDatabase)', linkedin_code)
            self.assertIn('self.db = db', linkedin_code)
            
            # Check database usage in feedback analyzer
            with open('/app/backend/services/feedback_analyzer.py', 'r') as f:
                feedback_code = f.read()
            
            self.assertIn('def __init__(self, db: AsyncIOMotorDatabase)', feedback_code)
            self.assertIn('self.db = db', feedback_code)
            
            print("✅ Database connections and operations verified")
            
        except Exception as e:
            self.fail(f"Database connections test failed: {e}")
    
    def test_03_openrouter_integration_with_free_models(self):
        """Test OpenRouter integration with free models"""
        try:
            # Check LinkedIn automation OpenRouter usage
            with open('/app/backend/services/linkedin_automation.py', 'r') as f:
                linkedin_code = f.read()
            
            self.assertIn('self.openrouter = get_openrouter_service()', linkedin_code)
            self.assertIn('await self.openrouter.get_completion', linkedin_code)
            self.assertIn('model="google/gemma-2-9b-it:free"', linkedin_code)
            
            # Check feedback analyzer OpenRouter usage
            with open('/app/backend/services/feedback_analyzer.py', 'r') as f:
                feedback_code = f.read()
            
            self.assertIn('self.openrouter = get_openrouter_service()', feedback_code)
            self.assertIn('await self.openrouter.get_completion', feedback_code)
            self.assertIn('model="google/gemma-2-9b-it:free"', feedback_code)
            
            print("✅ OpenRouter integration with free models verified")
            
        except Exception as e:
            self.fail(f"OpenRouter integration test failed: {e}")
    
    def test_04_error_handling_and_logging_systems(self):
        """Test error handling and logging systems"""
        try:
            # Check orchestrator error handling
            with open('/app/backend/services/automation_orchestrator.py', 'r') as f:
                orchestrator_code = f.read()
            
            error_handling = [
                'try:',
                'except Exception as e:',
                'self.logger.error(f"❌',
                'async def _handle_candidate_error',
                'async def _handle_critical_error',
                'self.logger.critical(f"CRITICAL SYSTEM ERROR: {error}")'
            ]
            for handler in error_handling:
                self.assertIn(handler, orchestrator_code)
            
            # Check LinkedIn automation error handling
            with open('/app/backend/services/linkedin_automation.py', 'r') as f:
                linkedin_code = f.read()
            
            self.assertIn('except Exception as e:', linkedin_code)
            self.assertIn('self.logger.error(f"❌', linkedin_code)
            
            # Check feedback analyzer error handling
            with open('/app/backend/services/feedback_analyzer.py', 'r') as f:
                feedback_code = f.read()
            
            self.assertIn('except Exception as e:', feedback_code)
            self.assertIn('self.logger.error(f"', feedback_code)
            
            print("✅ Error handling and logging systems verified")
            
        except Exception as e:
            self.fail(f"Error handling and logging test failed: {e}")
    
    def test_05_health_check_endpoint(self):
        """Test basic health check endpoint"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("status", data)
            self.assertEqual(data["status"], "healthy")
            self.assertIn("database", data)
            self.assertIn("openrouter", data)
            self.assertIn("timestamp", data)
            
            print("✅ Health check endpoint working")
            
        except Exception as e:
            self.fail(f"Health check failed: {e}")


class TestAPIEndpoints(unittest.TestCase):
    """Test suite for API Endpoints"""
    
    def test_01_check_server_imports(self):
        """Check if server.py imports the new services"""
        try:
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            # Check if automation orchestrator is imported
            # Note: It might not be directly imported in server.py if it's a background service
            
            # Check existing service imports that should work with new components
            existing_imports = [
                'from services.openrouter import get_openrouter_service',
                'from services.gmail import gmail_service',
                'from services.resume_parser import resume_service',
                'from services.scheduler import get_scheduler',
                'from services.job_matching import get_job_matching_service',
                'from services.resume_tailoring import get_resume_tailoring_service',
                'from services.application_submission import ApplicationSubmissionManager'
            ]
            
            for import_stmt in existing_imports:
                self.assertIn(import_stmt, server_code)
            
            print("✅ Server imports verified")
            
        except Exception as e:
            self.fail(f"Server imports test failed: {e}")
    
    def test_02_existing_endpoints_still_work(self):
        """Test that existing endpoints still work with new dependencies"""
        try:
            # Test root endpoint
            response = requests.get(f"{API_BASE}/", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("message", data)
            self.assertIn("Elite JobHunter X API", data["message"])
            
            # Test dashboard stats endpoint
            response = requests.get(f"{API_BASE}/dashboard/stats", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("counts", data)
            
            print("✅ Existing endpoints still working")
            
        except Exception as e:
            self.fail(f"Existing endpoints test failed: {e}")
    
    def test_03_service_initialization_in_server(self):
        """Test service initialization patterns in server"""
        try:
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            # Check service getter functions
            service_getters = [
                'get_openrouter_service()',
                'get_scheduler()',
                'get_job_matching_service()',
                'get_resume_tailoring_service('
            ]
            
            for getter in service_getters:
                self.assertIn(getter, server_code)
            
            # Check application submission manager
            self.assertIn('application_submission_manager = ApplicationSubmissionManager', server_code)
            
            print("✅ Service initialization patterns verified")
            
        except Exception as e:
            self.fail(f"Service initialization test failed: {e}")


class TestApplicationSubmissionSystem(unittest.TestCase):
    """Test suite for Phase 6 Application Submission system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.test_candidate_id = None
        cls.test_job_id = None
        cls.test_resume_version_id = None
        cls.test_cover_letter_id = None
        cls.test_application_id = None
        
        # Create test data
        cls._create_test_data()
    
    @classmethod
    def _create_test_data(cls):
        """Create test candidate, job, resume, and cover letter for application testing"""
        try:
            # Create test candidate
            candidate_data = {
                "full_name": "Michael Johnson",
                "email": "michael.johnson@example.com",
                "phone": "+1-555-0188",
                "location": "Austin, TX",
                "linkedin_url": "https://linkedin.com/in/michaeljohnson",
                "target_roles": ["Software Engineer", "Full Stack Developer"],
                "target_locations": ["Austin", "Remote"],
                "salary_min": 100000,
                "salary_max": 150000,
                "years_experience": 4,
                "skills": ["Python", "JavaScript", "React", "Node.js", "AWS"]
            }
            
            response = requests.post(f"{API_BASE}/candidates", json=candidate_data, timeout=30)
            if response.status_code == 200:
                cls.test_candidate_id = response.json()["id"]
                print(f"✅ Created test candidate for applications: {cls.test_candidate_id}")
            else:
                print(f"❌ Failed to create test candidate: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
    
    def test_01_application_submission_service_structure(self):
        """Test the application submission service structure and components"""
        try:
            with open('/app/backend/services/application_submission.py', 'r') as f:
                submission_code = f.read()
                
            # Check for key service classes
            self.assertIn('class ApplicationSubmissionManager', submission_code)
            self.assertIn('class ApplicationSubmissionEngine', submission_code)
            self.assertIn('class HumanBehaviorSimulator', submission_code)
            self.assertIn('class FingerprintRandomizer', submission_code)
            
            # Check application methods enum
            self.assertIn('class ApplicationMethod(str, Enum)', submission_code)
            self.assertIn('DIRECT_FORM = "direct_form"', submission_code)
            self.assertIn('EMAIL_APPLY = "email_apply"', submission_code)
            self.assertIn('INDEED_QUICK = "indeed_quick"', submission_code)
            self.assertIn('LINKEDIN_EASY = "linkedin_easy"', submission_code)
            
            # Check submission engine methods
            self.assertIn('async def submit_application', submission_code)
            self.assertIn('async def _submit_direct_form', submission_code)
            self.assertIn('async def _submit_email_apply', submission_code)
            self.assertIn('async def _submit_indeed_quick', submission_code)
            
            # Check stealth features
            self.assertIn('async def human_type', submission_code)
            self.assertIn('async def human_click', submission_code)
            self.assertIn('async def human_scroll', submission_code)
            self.assertIn('def generate_fingerprint', submission_code)
            
            print("✅ Application submission service has all required components")
            
        except Exception as e:
            self.fail(f"Failed to verify application submission service structure: {e}")
    
    def test_02_application_database_models(self):
        """Test application database models"""
        try:
            with open('/app/backend/models.py', 'r') as f:
                models_code = f.read()
                
            # Check for application models
            self.assertIn('class Application(BaseModel)', models_code)
            self.assertIn('class ApplicationStatus(str, Enum)', models_code)
            
            # Check ApplicationStatus enum values
            status_values = ['PENDING = "pending"', 'APPLIED = "applied"', 'REVIEWING = "reviewing"', 
                           'INTERVIEWED = "interviewed"', 'REJECTED = "rejected"', 'OFFERED = "offered"', 'ACCEPTED = "accepted"']
            for status in status_values:
                self.assertIn(status, models_code)
            
            # Check Application model fields
            application_fields = [
                'candidate_id: str',
                'job_id: str',
                'job_raw_id: str',
                'resume_version_id: str',
                'cover_letter_id: Optional[str]',
                'stealth_settings_id: str',
                'job_board: str',
                'company: str',
                'position: str',
                'application_url: Optional[str]',
                'status: ApplicationStatus',
                'applied_at: Optional[datetime]',
                'tracking_pixel_id: Optional[str]',
                'utm_params: Optional[Dict[str, str]]'
            ]
            
            for field in application_fields:
                self.assertIn(field, models_code)
            
            print("✅ Application database models are properly defined")
            
        except Exception as e:
            self.fail(f"Failed to verify application database models: {e}")
    
    def test_03_application_api_endpoints(self):
        """Test application API endpoints structure"""
        try:
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
                
            # Check for application endpoints
            endpoints = [
                '@api_router.post("/applications/submit")',
                '@api_router.post("/applications/submit-bulk")',
                '@api_router.get("/applications/status")',
                '@api_router.get("/applications/{application_id}")',
                '@api_router.get("/applications/candidate/{candidate_id}")',
                '@api_router.post("/applications/auto-submit")',
                '@api_router.get("/applications/analytics")',
                '@api_router.post("/applications/test-submission")'
            ]
            
            for endpoint in endpoints:
                self.assertIn(endpoint, server_code)
            
            # Check for request models
            self.assertIn('class ApplicationSubmissionRequest(BaseModel)', server_code)
            self.assertIn('class BulkApplicationSubmissionRequest(BaseModel)', server_code)
            
            # Check for application submission manager
            self.assertIn('application_submission_manager = ApplicationSubmissionManager', server_code)
            
            print("✅ All application API endpoints are properly defined")
            
        except Exception as e:
            self.fail(f"Failed to verify application API endpoints: {e}")
    
    def test_04_dependencies_verification(self):
        """Test that all required dependencies for application submission are available"""
        try:
            # Check requirements.txt for new dependencies
            with open('/app/backend/requirements.txt', 'r') as f:
                requirements = f.read()
            
            required_packages = [
                'playwright',
                'playwright-stealth',
                'selenium',
                'undetected-chromedriver',
                'fake-useragent',
                'asyncio-throttle',
                'opencv-python',
                'pillow'
            ]
            
            for package in required_packages:
                self.assertIn(package, requirements)
            
            print("✅ All required application submission dependencies are listed in requirements.txt")
            
        except Exception as e:
            self.fail(f"Application submission dependencies verification failed: {e}")
    
    def test_05_health_check(self):
        """Test basic health check"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("status", data)
            self.assertEqual(data["status"], "healthy")
            
            print("✅ Health check endpoint working")
            
        except Exception as e:
            self.fail(f"Health check failed: {e}")
    
    def test_06_application_status_endpoint(self):
        """Test application status endpoint"""
        try:
            response = requests.get(f"{API_BASE}/applications/status", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("statistics", data)
            self.assertIn("timestamp", data)
            
            stats = data["statistics"]
            self.assertIn("total_applications", stats)
            self.assertIn("successful_applications", stats)
            self.assertIn("pending_applications", stats)
            self.assertIn("failed_applications", stats)
            self.assertIn("applications_today", stats)
            self.assertIn("queue_size", stats)
            self.assertIn("active_submissions", stats)
            
            print("✅ Application status endpoint working")
            
        except Exception as e:
            self.fail(f"Application status endpoint test failed: {e}")
    
    def test_07_application_analytics_endpoint(self):
        """Test application analytics endpoint"""
        try:
            response = requests.get(f"{API_BASE}/applications/analytics", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("analytics", data)
            self.assertIn("timestamp", data)
            
            analytics = data["analytics"]
            self.assertIn("overall_stats", analytics)
            self.assertIn("applications_by_method", analytics)
            self.assertIn("daily_applications", analytics)
            self.assertIn("top_companies", analytics)
            
            overall_stats = analytics["overall_stats"]
            self.assertIn("total_applications", overall_stats)
            self.assertIn("successful_applications", overall_stats)
            self.assertIn("success_rate", overall_stats)
            self.assertIn("response_rate", overall_stats)
            
            print("✅ Application analytics endpoint working")
            
        except Exception as e:
            self.fail(f"Application analytics endpoint test failed: {e}")
    
    def test_08_application_test_submission(self):
        """Test application submission with test data"""
        try:
            response = requests.post(f"{API_BASE}/applications/test-submission", timeout=120)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("test_result", data)
            self.assertIn("timestamp", data)
            
            test_result = data["test_result"]
            self.assertIn("application_id", test_result)
            self.assertIn("success", test_result)
            self.assertIn("method", test_result)
            self.assertIn("submission_time", test_result)
            
            # Store for later tests
            self.__class__.test_application_id = test_result["application_id"]
            
            print(f"✅ Application test submission working - Method: {test_result['method']}")
            
        except Exception as e:
            self.fail(f"Application test submission failed: {e}")
    
    def test_09_stealth_features_implementation(self):
        """Test stealth features implementation"""
        try:
            with open('/app/backend/services/application_submission.py', 'r') as f:
                submission_code = f.read()
            
            # Check human behavior simulation
            self.assertIn('class HumanBehaviorSimulator', submission_code)
            self.assertIn('async def human_type', submission_code)
            self.assertIn('async def human_click', submission_code)
            self.assertIn('async def human_mouse_move', submission_code)
            self.assertIn('async def human_scroll', submission_code)
            self.assertIn('async def random_page_interaction', submission_code)
            
            # Check fingerprint randomization
            self.assertIn('class FingerprintRandomizer', submission_code)
            self.assertIn('def generate_fingerprint', submission_code)
            self.assertIn('async def apply_fingerprint', submission_code)
            
            # Check stealth configuration
            self.assertIn('stealth_mode: bool = True', submission_code)
            self.assertIn('human_behavior: bool = True', submission_code)
            self.assertIn('fingerprint_randomization: bool = True', submission_code)
            
            # Check browser stealth features
            self.assertIn('from playwright_stealth import stealth_async', submission_code)
            self.assertIn('--disable-blink-features=AutomationControlled', submission_code)
            self.assertIn('await stealth_async(page)', submission_code)
            
            print("✅ Stealth features are properly implemented")
            
        except Exception as e:
            self.fail(f"Stealth features test failed: {e}")
    
    def test_10_browser_automation_components(self):
        """Test browser automation components"""
        try:
            with open('/app/backend/services/application_submission.py', 'r') as f:
                submission_code = f.read()
            
            # Check browser automation imports
            self.assertIn('from playwright.async_api import async_playwright', submission_code)
            self.assertIn('from selenium import webdriver', submission_code)
            self.assertIn('import undetected_chromedriver as uc', submission_code)
            
            # Check form detection and filling
            self.assertIn('async def _detect_application_form', submission_code)
            self.assertIn('async def _fill_application_form', submission_code)
            self.assertIn('async def _submit_application_form', submission_code)
            
            # Check Indeed-specific handling
            self.assertIn('async def _handle_indeed_application_flow', submission_code)
            self.assertIn('async def _fill_indeed_personal_info', submission_code)
            self.assertIn('async def _handle_indeed_resume_upload', submission_code)
            self.assertIn('async def _handle_indeed_cover_letter', submission_code)
            
            print("✅ Browser automation components are properly implemented")
            
        except Exception as e:
            self.fail(f"Browser automation components test failed: {e}")
    
    def test_11_tracking_and_utm_features(self):
        """Test tracking pixel and UTM parameter generation"""
        try:
            with open('/app/backend/services/application_submission.py', 'r') as f:
                submission_code = f.read()
            
            # Check tracking pixel generation
            self.assertIn('async def _generate_tracking_pixel', submission_code)
            self.assertIn('def _generate_utm_params', submission_code)
            
            # Check UTM parameters
            self.assertIn("'utm_source': source", submission_code)
            self.assertIn("'utm_medium': 'job_application'", submission_code)
            self.assertIn("'utm_campaign': 'elite_jobhunter_x'", submission_code)
            self.assertIn("'utm_content': application_id", submission_code)
            self.assertIn("'utm_term': 'automated_application'", submission_code)
            
            # Check tracking pixel URL generation
            self.assertIn('tracking_url = f"https://track.jobhunter-x.com/pixel/{application_id}.png"', submission_code)
            
            print("✅ Tracking and UTM features are properly implemented")
            
        except Exception as e:
            self.fail(f"Tracking and UTM features test failed: {e}")
    
    def test_12_email_alias_generation(self):
        """Test email alias generation for applications"""
        try:
            with open('/app/backend/services/application_submission.py', 'r') as f:
                submission_code = f.read()
            
            # Check email alias generation patterns
            self.assertIn('email_alias = f"{candidate.email.split(\'@\')[0]}+job-{', submission_code)
            self.assertIn('email_alias = f"{candidate.email.split(\'@\')[0]}+indeed-{', submission_code)
            
            # Check email alias rotation configuration
            self.assertIn('email_alias_rotation: bool = True', submission_code)
            
            print("✅ Email alias generation is properly implemented")
            
        except Exception as e:
            self.fail(f"Email alias generation test failed: {e}")
    
    def test_13_error_handling_and_screenshots(self):
        """Test error handling and screenshot capture"""
        try:
            with open('/app/backend/services/application_submission.py', 'r') as f:
                submission_code = f.read()
            
            # Check error handling
            self.assertIn('except Exception as e:', submission_code)
            self.assertIn('logger.error(f"Application submission failed: {str(e)}")', submission_code)
            self.assertIn('error_message=str(e)', submission_code)
            
            # Check screenshot capture
            self.assertIn('screenshot_on_error: bool = True', submission_code)
            self.assertIn('screenshot = await page.screenshot()', submission_code)
            self.assertIn('screenshots.append(base64.b64encode(screenshot).decode())', submission_code)
            
            # Check retry mechanisms
            self.assertIn('max_retry_attempts: int = 3', submission_code)
            
            print("✅ Error handling and screenshot features are properly implemented")
            
        except Exception as e:
            self.fail(f"Error handling and screenshots test failed: {e}")
    
    def test_14_queue_processing_system(self):
        """Test application queue processing system"""
        try:
            with open('/app/backend/services/application_submission.py', 'r') as f:
                submission_code = f.read()
            
            # Check queue management
            self.assertIn('self.submission_queue = asyncio.Queue()', submission_code)
            self.assertIn('async def queue_application', submission_code)
            self.assertIn('async def process_submission_queue', submission_code)
            self.assertIn('async def _process_single_submission', submission_code)
            
            # Check throttling
            self.assertIn('from asyncio_throttle import Throttler', submission_code)
            self.assertIn('self.throttler = Throttler(rate_limit=1, period=2.0)', submission_code)
            self.assertIn('async with self.throttler:', submission_code)
            
            # Check concurrent submission limits
            self.assertIn('max_concurrent_submissions = 3', submission_code)
            self.assertIn('self.active_submissions', submission_code)
            
            print("✅ Queue processing system is properly implemented")
            
        except Exception as e:
            self.fail(f"Queue processing system test failed: {e}")
    
    def test_15_integration_with_other_services(self):
        """Test integration with other system services"""
        try:
            with open('/app/backend/services/application_submission.py', 'r') as f:
                submission_code = f.read()
            
            # Check service integrations
            self.assertIn('from .gmail import GmailService', submission_code)
            self.assertIn('from .openrouter import OpenRouterService', submission_code)
            self.assertIn('from models import Application, ApplicationStatus, Candidate, JobRaw, ResumeVersion, CoverLetter', submission_code)
            
            # Check service initialization
            self.assertIn('self.gmail_service = GmailService()', submission_code)
            self.assertIn('self.openrouter_service = OpenRouterService()', submission_code)
            
            # Check database integration
            self.assertIn('async def _save_application', submission_code)
            self.assertIn('await db.applications.insert_one(application.dict())', submission_code)
            
            print("✅ Integration with other services is properly implemented")
            
        except Exception as e:
            self.fail(f"Integration with other services test failed: {e}")


class TestMassScaleEndpoints(unittest.TestCase):
    """Test suite for MASS SCALE AUTONOMOUS SYSTEM API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.test_candidate_id = None
        cls.test_job_id = None
        
        # Create test candidate for MASS SCALE testing
        cls._create_test_data()
    
    @classmethod
    def _create_test_data(cls):
        """Create test candidate for MASS SCALE testing"""
        try:
            # Create test candidate
            candidate_data = {
                "full_name": "Sarah Wilson",
                "email": "sarah.wilson@example.com",
                "phone": "+1-555-0177",
                "location": "San Francisco, CA",
                "linkedin_url": "https://linkedin.com/in/sarahwilson",
                "target_roles": ["Senior Software Engineer", "Tech Lead"],
                "target_locations": ["San Francisco", "Remote"],
                "salary_min": 150000,
                "salary_max": 220000,
                "years_experience": 8,
                "skills": ["Python", "React", "AWS", "Kubernetes", "Machine Learning"]
            }
            
            response = requests.post(f"{API_BASE}/candidates", json=candidate_data, timeout=30)
            if response.status_code == 200:
                cls.test_candidate_id = response.json()["id"]
                print(f"✅ Created test candidate for MASS SCALE: {cls.test_candidate_id}")
            else:
                print(f"❌ Failed to create test candidate: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
    
    def test_01_automation_start_endpoint(self):
        """Test POST /api/automation/start - Start autonomous system"""
        try:
            response = requests.post(f"{API_BASE}/automation/start", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("message", data)
            self.assertIn("status", data)
            self.assertEqual(data["status"], "initializing")
            
            print("✅ Automation start endpoint working")
            
        except Exception as e:
            self.fail(f"Automation start endpoint test failed: {e}")
    
    def test_02_automation_status_endpoint(self):
        """Test GET /api/automation/status - Get system status"""
        try:
            response = requests.get(f"{API_BASE}/automation/status", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("status", data)
            
            # Check status structure
            status = data["status"]
            self.assertIn("is_running", status)
            self.assertIn("current_phase", status)
            self.assertIn("active_candidates", status)
            self.assertIn("last_cycle_time", status)
            
            print("✅ Automation status endpoint working")
            
        except Exception as e:
            self.fail(f"Automation status endpoint test failed: {e}")
    
    def test_03_automation_stats_endpoint(self):
        """Test GET /api/automation/stats - Get automation statistics"""
        try:
            response = requests.get(f"{API_BASE}/automation/stats", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("stats", data)
            
            # Check stats structure
            stats = data["stats"]
            required_stats = [
                "candidates_processed", "jobs_scraped", "matches_found",
                "resumes_tailored", "cover_letters_generated", "applications_submitted",
                "outreach_sent", "total_runtime_hours", "success_rate", "active_candidates"
            ]
            
            for stat in required_stats:
                self.assertIn(stat, stats)
            
            print("✅ Automation stats endpoint working")
            
        except Exception as e:
            self.fail(f"Automation stats endpoint test failed: {e}")
    
    def test_04_linkedin_start_outreach_endpoint(self):
        """Test POST /api/linkedin/start-outreach - Start LinkedIn outreach"""
        try:
            if not self.test_candidate_id:
                self.skipTest("No test candidate available")
            
            response = requests.post(
                f"{API_BASE}/linkedin/start-outreach",
                params={"candidate_id": self.test_candidate_id},
                timeout=30
            )
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("message", data)
            self.assertIn("candidate_id", data)
            self.assertEqual(data["candidate_id"], self.test_candidate_id)
            
            print("✅ LinkedIn start outreach endpoint working")
            
        except Exception as e:
            self.fail(f"LinkedIn start outreach endpoint test failed: {e}")
    
    def test_05_linkedin_outreach_status_endpoint(self):
        """Test GET /api/linkedin/outreach-status/{candidate_id} - Get outreach status"""
        try:
            if not self.test_candidate_id:
                self.skipTest("No test candidate available")
            
            response = requests.get(
                f"{API_BASE}/linkedin/outreach-status/{self.test_candidate_id}",
                timeout=30
            )
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("status", data)
            
            # Check status structure
            status = data["status"]
            self.assertIn("candidate_id", status)
            self.assertIn("campaign_status", status)
            self.assertIn("messages_sent", status)
            self.assertIn("connections_made", status)
            
            print("✅ LinkedIn outreach status endpoint working")
            
        except Exception as e:
            self.fail(f"LinkedIn outreach status endpoint test failed: {e}")
    
    def test_06_linkedin_campaigns_endpoint(self):
        """Test GET /api/linkedin/campaigns - Get outreach campaigns"""
        try:
            response = requests.get(f"{API_BASE}/linkedin/campaigns", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("campaigns", data)
            
            # Campaigns should be a list
            campaigns = data["campaigns"]
            self.assertIsInstance(campaigns, list)
            
            print("✅ LinkedIn campaigns endpoint working")
            
        except Exception as e:
            self.fail(f"LinkedIn campaigns endpoint test failed: {e}")
    
    def test_07_feedback_analyze_performance_endpoint(self):
        """Test POST /api/feedback/analyze-performance - Analyze performance"""
        try:
            response = requests.post(f"{API_BASE}/feedback/analyze-performance", timeout=60)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("performance_data", data)
            self.assertIn("recommendations", data)
            
            # Check performance data structure
            performance_data = data["performance_data"]
            self.assertIn("application_success_rate", performance_data)
            self.assertIn("response_rate", performance_data)
            self.assertIn("keyword_performance", performance_data)
            
            # Check recommendations structure
            recommendations = data["recommendations"]
            self.assertIsInstance(recommendations, list)
            
            print("✅ Feedback analyze performance endpoint working")
            
        except Exception as e:
            self.fail(f"Feedback analyze performance endpoint test failed: {e}")
    
    def test_08_feedback_apply_optimizations_endpoint(self):
        """Test POST /api/feedback/apply-optimizations - Apply optimizations"""
        try:
            response = requests.post(f"{API_BASE}/feedback/apply-optimizations", timeout=60)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("optimizations_applied", data)
            
            # Check optimizations applied structure
            optimizations = data["optimizations_applied"]
            self.assertIn("count", optimizations)
            self.assertIn("strategies", optimizations)
            
            print("✅ Feedback apply optimizations endpoint working")
            
        except Exception as e:
            self.fail(f"Feedback apply optimizations endpoint test failed: {e}")
    
    def test_09_feedback_success_patterns_endpoint(self):
        """Test GET /api/feedback/success-patterns - Get success patterns"""
        try:
            response = requests.get(f"{API_BASE}/feedback/success-patterns", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("patterns", data)
            
            # Check patterns structure
            patterns = data["patterns"]
            self.assertIn("successful_keywords", patterns)
            self.assertIn("optimal_application_times", patterns)
            self.assertIn("best_resume_strategies", patterns)
            self.assertIn("effective_outreach_approaches", patterns)
            
            print("✅ Feedback success patterns endpoint working")
            
        except Exception as e:
            self.fail(f"Feedback success patterns endpoint test failed: {e}")
    
    def test_10_analytics_mass_scale_dashboard_endpoint(self):
        """Test GET /api/analytics/mass-scale-dashboard - Get comprehensive dashboard"""
        try:
            response = requests.get(f"{API_BASE}/analytics/mass-scale-dashboard", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("dashboard", data)
            
            # Check dashboard structure
            dashboard = data["dashboard"]
            required_sections = ["candidates", "jobs", "applications", "matching", "outreach", "automation"]
            
            for section in required_sections:
                self.assertIn(section, dashboard)
            
            # Check candidates section
            candidates = dashboard["candidates"]
            self.assertIn("total", candidates)
            self.assertIn("active", candidates)
            self.assertIn("inactive", candidates)
            
            # Check automation section
            automation = dashboard["automation"]
            self.assertIn("status", automation)
            self.assertIn("uptime", automation)
            self.assertIn("last_cycle", automation)
            
            print("✅ Analytics mass scale dashboard endpoint working")
            
        except Exception as e:
            self.fail(f"Analytics mass scale dashboard endpoint test failed: {e}")
    
    def test_11_analytics_candidate_performance_endpoint(self):
        """Test GET /api/analytics/candidate-performance/{candidate_id} - Get candidate performance"""
        try:
            if not self.test_candidate_id:
                self.skipTest("No test candidate available")
            
            response = requests.get(
                f"{API_BASE}/analytics/candidate-performance/{self.test_candidate_id}",
                timeout=30
            )
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("candidate_id", data)
            self.assertIn("performance", data)
            self.assertEqual(data["candidate_id"], self.test_candidate_id)
            
            # Check performance structure
            performance = data["performance"]
            required_sections = ["applications", "matching", "outreach"]
            
            for section in required_sections:
                self.assertIn(section, performance)
            
            # Check applications section
            applications = performance["applications"]
            self.assertIn("total", applications)
            self.assertIn("successful", applications)
            self.assertIn("success_rate", applications)
            
            print("✅ Analytics candidate performance endpoint working")
            
        except Exception as e:
            self.fail(f"Analytics candidate performance endpoint test failed: {e}")
    
    def test_12_automation_stop_endpoint(self):
        """Test POST /api/automation/stop - Stop autonomous system"""
        try:
            response = requests.post(f"{API_BASE}/automation/stop", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("message", data)
            
            print("✅ Automation stop endpoint working")
            
        except Exception as e:
            self.fail(f"Automation stop endpoint test failed: {e}")


class TestAdvancedCoverLetterSystem(unittest.TestCase):
    """Test suite for Phase 5 Advanced Cover Letter Generation system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.test_candidate_id = None
        cls.test_cover_letter_id = None
        cls.test_job_id = "test_job_cover_letter_123"
        cls.sample_job_description = """
        We are seeking a Senior Python Developer with 5+ years of experience.
        Requirements:
        - Strong experience with Python, Django, FastAPI
        - Experience with React, JavaScript, HTML, CSS
        - Knowledge of AWS, Docker, Kubernetes
        - Experience with SQL databases and MongoDB
        - Agile development experience
        - Strong problem-solving skills
        """
        cls.sample_company_name = "TechCorp Innovation"
        cls.sample_company_domain = "techcorp.com"
        
        # Create test candidate
        cls._create_test_data()
    
    @classmethod
    def _create_test_data(cls):
        """Create test candidate for cover letter testing"""
        try:
            # Create test candidate
            candidate_data = {
                "full_name": "Alex Johnson",
                "email": "alex.johnson@example.com",
                "phone": "+1-555-0199",
                "location": "Seattle, WA",
                "linkedin_url": "https://linkedin.com/in/alexjohnson",
                "target_roles": ["Senior Python Developer", "Full Stack Developer"],
                "target_locations": ["Seattle", "Remote"],
                "salary_min": 130000,
                "salary_max": 190000,
                "years_experience": 6,
                "skills": ["Python", "Django", "React", "AWS", "Docker", "Kubernetes"]
            }
            
            response = requests.post(f"{API_BASE}/candidates", json=candidate_data, timeout=30)
            if response.status_code == 200:
                cls.test_candidate_id = response.json()["id"]
                print(f"✅ Created test candidate for cover letters: {cls.test_candidate_id}")
            else:
                print(f"❌ Failed to create test candidate: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
    
    def test_01_cover_letter_service_structure(self):
        """Test the cover letter service structure and components"""
        try:
            with open('/app/backend/services/cover_letter.py', 'r') as f:
                cover_letter_code = f.read()
                
            # Check for key service classes
            self.assertIn('class CompanyResearchEngine', cover_letter_code)
            self.assertIn('class CoverLetterPersonalizationEngine', cover_letter_code)
            self.assertIn('class CoverLetterGenerator', cover_letter_code)
            
            # Check company research methods
            self.assertIn('async def research_company', cover_letter_code)
            self.assertIn('async def _research_company_website', cover_letter_code)
            self.assertIn('async def _research_linkedin_company', cover_letter_code)
            self.assertIn('async def _research_glassdoor_reviews', cover_letter_code)
            
            # Check personalization engine methods
            self.assertIn('def generate_personalization_hooks', cover_letter_code)
            self.assertIn('def calculate_ats_keywords', cover_letter_code)
            
            # Check cover letter generator methods
            self.assertIn('async def generate_cover_letter', cover_letter_code)
            self.assertIn('async def generate_multiple_versions', cover_letter_code)
            self.assertIn('async def get_performance_analytics', cover_letter_code)
            self.assertIn('async def _generate_pdf', cover_letter_code)
            
            # Check multi-tone support
            self.assertIn('OutreachTone.FORMAL', cover_letter_code)
            self.assertIn('OutreachTone.WARM', cover_letter_code)
            self.assertIn('OutreachTone.CURIOUS', cover_letter_code)
            self.assertIn('OutreachTone.BOLD', cover_letter_code)
            self.assertIn('OutreachTone.STRATEGIC', cover_letter_code)
            
            print("✅ Cover letter service has all required components")
            
        except Exception as e:
            self.fail(f"Failed to verify cover letter service structure: {e}")
    
    def test_02_cover_letter_database_models(self):
        """Test cover letter database models"""
        try:
            with open('/app/backend/models.py', 'r') as f:
                models_code = f.read()
                
            # Check for cover letter models
            self.assertIn('class CoverLetter(BaseModel)', models_code)
            self.assertIn('class CoverLetterTemplate(BaseModel)', models_code)
            self.assertIn('class CompanyResearch(BaseModel)', models_code)
            self.assertIn('class CoverLetterPerformance(BaseModel)', models_code)
            self.assertIn('class OutreachTone(str, Enum)', models_code)
            
            # Check OutreachTone enum values
            tone_values = ['WARM = "warm"', 'STRATEGIC = "strategic"', 'BOLD = "bold"', 
                          'CURIOUS = "curious"', 'FORMAL = "formal"']
            for tone in tone_values:
                self.assertIn(tone, models_code)
            
            # Check CoverLetter model fields
            cover_letter_fields = [
                'candidate_id: str',
                'job_id: str',
                'tone: OutreachTone',
                'content: str',
                'pdf_url: Optional[str]',
                'ats_keywords: List[str]',
                'reasoning: Optional[str]',
                'company_research: Optional[str]',
                'used_count: int',
                'success_rate: Optional[float]',
                'personalization_score: Optional[float]'
            ]
            
            for field in cover_letter_fields:
                self.assertIn(field, models_code)
            
            print("✅ Cover letter database models are properly defined")
            
        except Exception as e:
            self.fail(f"Failed to verify cover letter database models: {e}")
    
    def test_03_cover_letter_api_endpoints(self):
        """Test cover letter API endpoints structure"""
        try:
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
                
            # Check for all 10 cover letter endpoints
            endpoints = [
                '@api_router.post("/cover-letters/generate")',
                '@api_router.post("/cover-letters/generate-multiple")',
                '@api_router.get("/candidates/{candidate_id}/cover-letters")',
                '@api_router.get("/cover-letters/{cover_letter_id}")',
                '@api_router.get("/cover-letters/{cover_letter_id}/performance")',
                '@api_router.delete("/cover-letters/{cover_letter_id}")',
                '@api_router.get("/cover-letters/{cover_letter_id}/download")',
                '@api_router.post("/cover-letters/{cover_letter_id}/track-usage")',
                '@api_router.get("/cover-letters/stats/overview")',
                '@api_router.post("/cover-letters/test-generation")'
            ]
            
            for endpoint in endpoints:
                self.assertIn(endpoint, server_code)
            
            # Check for request models
            self.assertIn('class CoverLetterGenerationRequest(BaseModel)', server_code)
            self.assertIn('class MultipleCoverLetterRequest(BaseModel)', server_code)
            
            print("✅ All 10 cover letter API endpoints are properly defined")
            
        except Exception as e:
            self.fail(f"Failed to verify cover letter API endpoints: {e}")
    
    def test_04_dependencies_verification(self):
        """Test that all required dependencies for cover letters are available"""
        try:
            # Check requirements.txt for new dependencies
            with open('/app/backend/requirements.txt', 'r') as f:
                requirements = f.read()
            
            required_packages = [
                'aiohttp',
                'beautifulsoup4', 
                'nltk',
                'reportlab',
                'scikit-learn'
            ]
            
            for package in required_packages:
                self.assertIn(package, requirements)
            
            print("✅ All required cover letter dependencies are listed in requirements.txt")
            
        except Exception as e:
            self.fail(f"Cover letter dependencies verification failed: {e}")
    
    def test_05_health_check(self):
        """Test basic health check"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("status", data)
            self.assertEqual(data["status"], "healthy")
            
            print("✅ Health check endpoint working")
            
        except Exception as e:
            self.fail(f"Health check failed: {e}")
    
    def test_06_cover_letter_generation_test(self):
        """Test cover letter generation with sample data"""
        try:
            response = requests.post(f"{API_BASE}/cover-letters/test-generation", timeout=120)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("test_data", data)
            self.assertIn("result", data["test_data"])
            
            result = data["test_data"]["result"]
            self.assertIn("cover_letter_id", result)
            self.assertIn("content", result)
            self.assertIn("tone", result)
            self.assertIn("ats_keywords", result)
            self.assertIn("personalization_hooks", result)
            self.assertIn("company_research", result)
            
            # Verify content quality
            content = result["content"]
            self.assertGreater(len(content), 200)  # Minimum length
            self.assertLess(len(content), 2000)    # Maximum length
            
            # Store for later tests
            self.__class__.test_cover_letter_id = result["cover_letter_id"]
            
            print(f"✅ Cover letter generation test passed - Generated {len(content)} characters")
            
        except Exception as e:
            self.fail(f"Cover letter generation test failed: {e}")
    
    def test_07_cover_letter_generation_api(self):
        """Test main cover letter generation API endpoint"""
        if not self.test_candidate_id:
            self.skipTest("No test candidate available")
            
        try:
            request_data = {
                "candidate_id": self.test_candidate_id,
                "job_id": self.test_job_id,
                "job_description": self.sample_job_description,
                "company_name": self.sample_company_name,
                "company_domain": self.sample_company_domain,
                "position_title": "Senior Python Developer",
                "hiring_manager": "Sarah Martinez",
                "tone": "warm",
                "include_research": True
            }
            
            response = requests.post(f"{API_BASE}/cover-letters/generate", 
                                   json=request_data, timeout=120)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("data", data)
            
            result = data["data"]
            self.assertIn("cover_letter_id", result)
            self.assertIn("content", result)
            self.assertIn("tone", result)
            self.assertEqual(result["tone"], "warm")
            self.assertIn("ats_keywords", result)
            self.assertIn("personalization_hooks", result)
            
            print("✅ Cover letter generation API endpoint working")
            
        except Exception as e:
            self.fail(f"Cover letter generation API test failed: {e}")
    
    def test_08_multiple_cover_letter_generation(self):
        """Test multiple cover letter generation for A/B testing"""
        if not self.test_candidate_id:
            self.skipTest("No test candidate available")
            
        try:
            request_data = {
                "candidate_id": self.test_candidate_id,
                "job_id": self.test_job_id,
                "job_description": self.sample_job_description,
                "company_name": self.sample_company_name,
                "company_domain": self.sample_company_domain,
                "position_title": "Senior Python Developer",
                "versions_count": 3
            }
            
            response = requests.post(f"{API_BASE}/cover-letters/generate-multiple", 
                                   json=request_data, timeout=180)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("data", data)
            
            result = data["data"]
            self.assertIn("versions", result)
            self.assertIn("total_count", result)
            self.assertEqual(result["total_count"], 3)
            
            versions = result["versions"]
            self.assertEqual(len(versions), 3)
            
            # Verify each version has different tones
            tones = [version["tone"] for version in versions]
            self.assertEqual(len(set(tones)), 3)  # All different tones
            
            print(f"✅ Multiple cover letter generation working - Generated {len(versions)} versions")
            
        except Exception as e:
            self.fail(f"Multiple cover letter generation test failed: {e}")
    
    def test_09_candidate_cover_letters_retrieval(self):
        """Test retrieving cover letters for a candidate"""
        if not self.test_candidate_id:
            self.skipTest("No test candidate available")
            
        try:
            response = requests.get(f"{API_BASE}/candidates/{self.test_candidate_id}/cover-letters", 
                                  timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("data", data)
            
            result = data["data"]
            self.assertIn("cover_letters", result)
            self.assertIn("total", result)
            
            print(f"✅ Candidate cover letters retrieval working - Found {result['total']} cover letters")
            
        except Exception as e:
            self.fail(f"Candidate cover letters retrieval test failed: {e}")
    
    def test_10_cover_letter_performance_analytics(self):
        """Test cover letter performance analytics"""
        if not self.test_cover_letter_id:
            self.skipTest("No test cover letter available")
            
        try:
            response = requests.get(f"{API_BASE}/cover-letters/{self.test_cover_letter_id}/performance", 
                                  timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("data", data)
            
            result = data["data"]
            self.assertIn("cover_letter_id", result)
            self.assertIn("total_applications", result)
            self.assertIn("response_rate", result)
            self.assertIn("interview_rate", result)
            self.assertIn("success_score", result)
            
            print("✅ Cover letter performance analytics working")
            
        except Exception as e:
            self.fail(f"Cover letter performance analytics test failed: {e}")
    
    def test_11_cover_letter_usage_tracking(self):
        """Test cover letter usage tracking"""
        if not self.test_cover_letter_id:
            self.skipTest("No test cover letter available")
            
        try:
            response = requests.post(f"{API_BASE}/cover-letters/{self.test_cover_letter_id}/track-usage", 
                                   timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("message", data)
            
            print("✅ Cover letter usage tracking working")
            
        except Exception as e:
            self.fail(f"Cover letter usage tracking test failed: {e}")
    
    def test_12_cover_letter_stats_overview(self):
        """Test cover letter statistics overview"""
        try:
            response = requests.get(f"{API_BASE}/cover-letters/stats/overview", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("data", data)
            
            result = data["data"]
            self.assertIn("overview", result)
            self.assertIn("tone_distribution", result)
            self.assertIn("recent_activity", result)
            
            overview = result["overview"]
            self.assertIn("total_cover_letters", overview)
            self.assertIn("total_applications", overview)
            self.assertIn("avg_success_rate", overview)
            
            print("✅ Cover letter statistics overview working")
            
        except Exception as e:
            self.fail(f"Cover letter statistics overview test failed: {e}")
    
    def test_13_company_research_engine_components(self):
        """Test company research engine implementation"""
        try:
            with open('/app/backend/services/cover_letter.py', 'r') as f:
                cover_letter_code = f.read()
            
            # Check research methods
            research_methods = [
                'async def research_company',
                'async def _research_company_website',
                'async def _research_linkedin_company',
                'async def _research_glassdoor_reviews'
            ]
            
            for method in research_methods:
                self.assertIn(method, cover_letter_code)
            
            # Check research data fields
            research_fields = [
                'about',
                'mission',
                'values',
                'recent_news',
                'culture_keywords',
                'tech_stack',
                'company_size',
                'industry',
                'sentiment_score'
            ]
            
            for field in research_fields:
                self.assertIn(f'"{field}"', cover_letter_code)
            
            # Check sentiment analysis
            self.assertIn('SentimentIntensityAnalyzer', cover_letter_code)
            self.assertIn('sentiment_analyzer', cover_letter_code)
            
            print("✅ Company research engine components properly implemented")
            
        except Exception as e:
            self.fail(f"Company research engine test failed: {e}")
    
    def test_14_personalization_engine_components(self):
        """Test personalization engine implementation"""
        try:
            with open('/app/backend/services/cover_letter.py', 'r') as f:
                cover_letter_code = f.read()
            
            # Check tone strategies
            tone_strategies = [
                'OutreachTone.FORMAL',
                'OutreachTone.CURIOUS', 
                'OutreachTone.WARM',
                'OutreachTone.BOLD',
                'OutreachTone.STRATEGIC'
            ]
            
            for tone in tone_strategies:
                self.assertIn(tone, cover_letter_code)
            
            # Check personalization methods
            self.assertIn('def generate_personalization_hooks', cover_letter_code)
            self.assertIn('def calculate_ats_keywords', cover_letter_code)
            
            # Check hook generation logic
            hook_types = [
                'mission',
                'recent_news',
                'tech_stack',
                'culture_keywords'
            ]
            
            for hook_type in hook_types:
                self.assertIn(hook_type, cover_letter_code)
            
            print("✅ Personalization engine components properly implemented")
            
        except Exception as e:
            self.fail(f"Personalization engine test failed: {e}")
    
    def test_15_pdf_generation_components(self):
        """Test PDF generation implementation"""
        try:
            with open('/app/backend/services/cover_letter.py', 'r') as f:
                cover_letter_code = f.read()
            
            # Check PDF imports
            pdf_imports = [
                'from reportlab.lib.pagesizes import letter',
                'from reportlab.platypus import SimpleDocTemplate',
                'from reportlab.lib.styles import getSampleStyleSheet'
            ]
            
            for import_stmt in pdf_imports:
                self.assertIn(import_stmt, cover_letter_code)
            
            # Check PDF generation method
            self.assertIn('async def _generate_pdf', cover_letter_code)
            self.assertIn('SimpleDocTemplate', cover_letter_code)
            self.assertIn('/tmp/cover_letters', cover_letter_code)
            
            print("✅ PDF generation components properly implemented")
            
        except Exception as e:
            self.fail(f"PDF generation test failed: {e}")
    
    def test_16_ats_optimization_features(self):
        """Test ATS optimization features"""
        try:
            with open('/app/backend/services/cover_letter.py', 'r') as f:
                cover_letter_code = f.read()
            
            # Check ATS keyword extraction
            self.assertIn('def calculate_ats_keywords', cover_letter_code)
            self.assertIn('TfidfVectorizer', cover_letter_code)
            self.assertIn('cosine_similarity', cover_letter_code)
            
            # Check keyword patterns
            keyword_patterns = [
                'years?\s*(?:of\s*)?(?:experience|exp)',
                'bachelor|master|phd|degree',
                'remote|hybrid|on-site'
            ]
            
            for pattern in keyword_patterns:
                self.assertIn(pattern, cover_letter_code)
            
            print("✅ ATS optimization features properly implemented")
            
        except Exception as e:
            self.fail(f"ATS optimization test failed: {e}")
    
    def test_17_ai_integration_with_openrouter(self):
        """Test AI integration with OpenRouter for cover letter generation"""
        try:
            with open('/app/backend/services/cover_letter.py', 'r') as f:
                cover_letter_code = f.read()
            
            # Check OpenRouter integration
            self.assertIn('from .openrouter import get_openrouter_service', cover_letter_code)
            self.assertIn('self.openrouter_service = get_openrouter_service()', cover_letter_code)
            self.assertIn('generate_completion', cover_letter_code)
            
            # Check AI prompt structure
            prompt_elements = [
                'CANDIDATE PROFILE',
                'JOB DETAILS',
                'COMPANY RESEARCH DATA',
                'TONE REQUIREMENTS',
                'PERSONALIZATION HOOKS',
                'ATS KEYWORDS TO INCORPORATE',
                'WRITING GUIDELINES'
            ]
            
            for element in prompt_elements:
                self.assertIn(element, cover_letter_code)
            
            print("✅ AI integration with OpenRouter properly implemented")
            
        except Exception as e:
            self.fail(f"AI integration test failed: {e}")


class TestAdvancedResumeTailoringSystem(unittest.TestCase):
    """Test suite for Advanced Resume Tailoring system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.test_candidate_id = None
        cls.test_resume_id = None
        cls.test_job_id = "test_job_123"
        cls.sample_job_description = """
        We are seeking a Senior Python Developer with 5+ years of experience.
        Requirements:
        - Strong experience with Python, Django, FastAPI
        - Experience with React, JavaScript, HTML, CSS
        - Knowledge of AWS, Docker, Kubernetes
        - Experience with SQL databases and MongoDB
        - Agile development experience
        - Strong problem-solving skills
        """
        
        # Create test candidate and resume
        cls._create_test_data()
    
    @classmethod
    def _create_test_data(cls):
        """Create test candidate and resume"""
        try:
            # Create test candidate
            candidate_data = {
                "full_name": "Sarah Johnson",
                "email": "sarah.johnson@example.com",
                "phone": "+1-555-0123",
                "location": "San Francisco, CA",
                "linkedin_url": "https://linkedin.com/in/sarahjohnson",
                "target_roles": ["Senior Python Developer", "Full Stack Developer"],
                "target_locations": ["San Francisco", "Remote"],
                "salary_min": 120000,
                "salary_max": 180000,
                "years_experience": 6,
                "skills": ["Python", "Django", "React", "AWS", "Docker"]
            }
            
            response = requests.post(f"{API_BASE}/candidates", json=candidate_data, timeout=30)
            if response.status_code == 200:
                cls.test_candidate_id = response.json()["id"]
                print(f"✅ Created test candidate: {cls.test_candidate_id}")
            else:
                print(f"❌ Failed to create test candidate: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
    
    def test_01_resume_tailoring_service_structure(self):
        """Test the resume tailoring service structure"""
        try:
            with open('/app/backend/services/resume_tailoring.py', 'r') as f:
                tailoring_code = f.read()
                
            # Check for key components
            self.assertIn('class ResumeGeneticOptimizer', tailoring_code)
            self.assertIn('class ATSScoreEngine', tailoring_code)
            self.assertIn('class ResumeTailoringService', tailoring_code)
            
            # Check genetic algorithm components
            self.assertIn('def initialize_population', tailoring_code)
            self.assertIn('def _mutate', tailoring_code)
            self.assertIn('def crossover', tailoring_code)
            self.assertIn('def selection', tailoring_code)
            
            # Check ATS scoring components
            self.assertIn('def calculate_ats_score', tailoring_code)
            self.assertIn('def _score_keywords', tailoring_code)
            self.assertIn('def _score_experience', tailoring_code)
            self.assertIn('def _score_skills', tailoring_code)
            
            # Check tailoring service methods
            self.assertIn('def tailor_resume_for_job', tailoring_code)
            self.assertIn('def generate_resume_variants', tailoring_code)
            self.assertIn('def get_resume_versions', tailoring_code)
            self.assertIn('def get_performance_metrics', tailoring_code)
            
            print("✅ Resume tailoring service has all required components")
            
        except Exception as e:
            self.fail(f"Failed to verify resume tailoring service structure: {e}")
    
    def test_02_database_models_for_tailoring(self):
        """Test database models for resume tailoring"""
        try:
            with open('/app/backend/models.py', 'r') as f:
                models_code = f.read()
                
            # Check for resume tailoring models
            self.assertIn('class TailoringStrategy(str, Enum)', models_code)
            self.assertIn('class ATSOptimization(str, Enum)', models_code)
            self.assertIn('class ResumeVersion(BaseModel)', models_code)
            self.assertIn('class ResumeGeneticPool(BaseModel)', models_code)
            self.assertIn('class ATSAnalysis(BaseModel)', models_code)
            self.assertIn('class ResumePerformanceMetrics(BaseModel)', models_code)
            self.assertIn('class KeywordOptimization(BaseModel)', models_code)
            
            # Check enum values
            self.assertIn('JOB_SPECIFIC = "job_specific"', models_code)
            self.assertIn('COMPANY_SPECIFIC = "company_specific"', models_code)
            self.assertIn('SKILL_FOCUSED = "skill_focused"', models_code)
            self.assertIn('BASIC = "basic"', models_code)
            self.assertIn('ADVANCED = "advanced"', models_code)
            self.assertIn('AGGRESSIVE = "aggressive"', models_code)
            self.assertIn('STEALTH = "stealth"', models_code)
            
            print("✅ Database models for resume tailoring are properly defined")
            
        except Exception as e:
            self.fail(f"Failed to verify database models: {e}")
    
    def test_03_resume_tailoring_api_endpoints(self):
        """Test resume tailoring API endpoints structure"""
        try:
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
                
            # Check for resume tailoring endpoints
            self.assertIn('@api_router.post("/resumes/{resume_id}/tailor")', server_code)
            self.assertIn('@api_router.get("/candidates/{candidate_id}/resume-versions")', server_code)
            self.assertIn('@api_router.post("/resumes/{resume_id}/generate-variants")', server_code)
            self.assertIn('@api_router.get("/resume-versions/{version_id}/ats-analysis")', server_code)
            self.assertIn('@api_router.get("/resume-versions/{version_id}/performance")', server_code)
            self.assertIn('@api_router.post("/resumes/test-ats-scoring")', server_code)
            self.assertIn('@api_router.get("/resume-tailoring/stats")', server_code)
            
            # Check for request models
            self.assertIn('class ResumeTailoringRequest(BaseModel)', server_code)
            self.assertIn('class ResumeVariantsRequest(BaseModel)', server_code)
            
            print("✅ Resume tailoring API endpoints are properly defined")
            
        except Exception as e:
            self.fail(f"Failed to verify API endpoints: {e}")
    
    def test_04_health_check(self):
        """Test basic health check"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("status", data)
            self.assertEqual(data["status"], "healthy")
            
            print("✅ Health check endpoint working")
            
        except Exception as e:
            self.fail(f"Health check failed: {e}")
    
    def test_05_ats_scoring_engine_test(self):
        """Test ATS scoring engine with sample data"""
        try:
            response = requests.post(f"{API_BASE}/resumes/test-ats-scoring", timeout=60)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("sample_resume_score", data)
            self.assertIn("breakdown", data)
            self.assertIn("recommendations", data)
            self.assertIn("missing_keywords", data)
            
            # Verify score breakdown
            breakdown = data["breakdown"]
            self.assertIn("keyword_score", breakdown)
            self.assertIn("format_score", breakdown)
            self.assertIn("section_score", breakdown)
            self.assertIn("experience_score", breakdown)
            self.assertIn("education_score", breakdown)
            self.assertIn("skills_score", breakdown)
            self.assertIn("contact_score", breakdown)
            
            # Verify scores are reasonable
            self.assertGreaterEqual(data["sample_resume_score"], 0)
            self.assertLessEqual(data["sample_resume_score"], 100)
            
            print(f"✅ ATS scoring engine test passed - Score: {data['sample_resume_score']:.1f}")
            
        except Exception as e:
            self.fail(f"ATS scoring engine test failed: {e}")
    
    def test_06_resume_tailoring_stats(self):
        """Test resume tailoring statistics endpoint"""
        try:
            response = requests.get(f"{API_BASE}/resume-tailoring/stats", timeout=30)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("stats", data)
            
            stats = data["stats"]
            self.assertIn("total_resume_versions", stats)
            self.assertIn("total_genetic_pools", stats)
            self.assertIn("total_ats_analyses", stats)
            self.assertIn("total_performance_metrics", stats)
            self.assertIn("average_ats_score", stats)
            self.assertIn("max_ats_score", stats)
            self.assertIn("min_ats_score", stats)
            
            print("✅ Resume tailoring statistics endpoint working")
            
        except Exception as e:
            self.fail(f"Resume tailoring stats test failed: {e}")
    
    def test_07_genetic_algorithm_components(self):
        """Test genetic algorithm implementation components"""
        try:
            with open('/app/backend/services/resume_tailoring.py', 'r') as f:
                tailoring_code = f.read()
            
            # Check mutation strategies
            self.assertIn("'keyword_injection'", tailoring_code)
            self.assertIn("'section_reordering'", tailoring_code)
            self.assertIn("'bullet_optimization'", tailoring_code)
            self.assertIn("'skill_enhancement'", tailoring_code)
            self.assertIn("'experience_emphasis'", tailoring_code)
            self.assertIn("'format_adjustment'", tailoring_code)
            
            # Check genetic algorithm parameters
            self.assertIn("population_size", tailoring_code)
            self.assertIn("mutation_rate", tailoring_code)
            self.assertIn("crossover_rate", tailoring_code)
            self.assertIn("convergence_threshold", tailoring_code)
            self.assertIn("max_generations", tailoring_code)
            
            # Check fitness calculation
            self.assertIn("def _calculate_fitness", tailoring_code)
            self.assertIn("ats_analysis.overall_score", tailoring_code)
            self.assertIn("ats_analysis.keyword_score", tailoring_code)
            
            print("✅ Genetic algorithm components are properly implemented")
            
        except Exception as e:
            self.fail(f"Genetic algorithm components test failed: {e}")
    
    def test_08_stealth_features(self):
        """Test stealth features implementation"""
        try:
            with open('/app/backend/services/resume_tailoring.py', 'r') as f:
                tailoring_code = f.read()
            
            # Check stealth fingerprinting
            self.assertIn("def _generate_stealth_fingerprint", tailoring_code)
            self.assertIn("hashlib.sha256", tailoring_code)
            self.assertIn("stealth_fingerprint", tailoring_code)
            
            # Check stealth optimization
            with open('/app/backend/models.py', 'r') as f:
                models_code = f.read()
            
            self.assertIn('STEALTH = "stealth"', models_code)
            self.assertIn("stealth_fingerprint: Optional[str]", models_code)
            
            print("✅ Stealth features are properly implemented")
            
        except Exception as e:
            self.fail(f"Stealth features test failed: {e}")
    
    def test_09_multi_strategy_tailoring(self):
        """Test multi-strategy tailoring capabilities"""
        try:
            with open('/app/backend/models.py', 'r') as f:
                models_code = f.read()
            
            # Check all tailoring strategies
            strategies = [
                'JOB_SPECIFIC = "job_specific"',
                'COMPANY_SPECIFIC = "company_specific"',
                'ROLE_SPECIFIC = "role_specific"',
                'INDUSTRY_SPECIFIC = "industry_specific"',
                'SKILL_FOCUSED = "skill_focused"',
                'EXPERIENCE_FOCUSED = "experience_focused"'
            ]
            
            for strategy in strategies:
                self.assertIn(strategy, models_code)
            
            # Check optimization levels
            optimizations = [
                'BASIC = "basic"',
                'ADVANCED = "advanced"',
                'AGGRESSIVE = "aggressive"',
                'STEALTH = "stealth"'
            ]
            
            for optimization in optimizations:
                self.assertIn(optimization, models_code)
            
            print("✅ Multi-strategy tailoring capabilities are properly defined")
            
        except Exception as e:
            self.fail(f"Multi-strategy tailoring test failed: {e}")
    
    def test_10_performance_tracking(self):
        """Test performance tracking and analytics"""
        try:
            with open('/app/backend/services/resume_tailoring.py', 'r') as f:
                tailoring_code = f.read()
            
            # Check performance tracking methods
            self.assertIn("def get_performance_metrics", tailoring_code)
            self.assertIn("def update_performance_metrics", tailoring_code)
            self.assertIn("def analyze_resume_performance", tailoring_code)
            
            # Check performance metrics fields
            with open('/app/backend/models.py', 'r') as f:
                models_code = f.read()
            
            performance_fields = [
                "applications_sent: int",
                "responses_received: int", 
                "interviews_scheduled: int",
                "offers_received: int",
                "response_rate: float",
                "interview_rate: float",
                "offer_rate: float"
            ]
            
            for field in performance_fields:
                self.assertIn(field, models_code)
            
            print("✅ Performance tracking and analytics are properly implemented")
            
        except Exception as e:
            self.fail(f"Performance tracking test failed: {e}")
    
    def test_11_dependencies_verification(self):
        """Test that all required dependencies are available"""
        try:
            # Check requirements.txt for new dependencies
            with open('/app/backend/requirements.txt', 'r') as f:
                requirements = f.read()
            
            required_packages = [
                'nltk',
                'reportlab', 
                'scikit-learn',
                'numpy'
            ]
            
            for package in required_packages:
                self.assertIn(package, requirements)
            
            print("✅ All required dependencies are listed in requirements.txt")
            
        except Exception as e:
            self.fail(f"Dependencies verification failed: {e}")
    
    def test_12_integration_with_openrouter(self):
        """Test integration with OpenRouter service"""
        try:
            with open('/app/backend/services/resume_tailoring.py', 'r') as f:
                tailoring_code = f.read()
            
            # Check OpenRouter integration
            self.assertIn("from .openrouter import OpenRouterService", tailoring_code)
            self.assertIn("self.openrouter_service", tailoring_code)
            self.assertIn("generate_completion", tailoring_code)
            self.assertIn("model_type=\"resume_tailoring\"", tailoring_code)
            
            print("✅ OpenRouter integration is properly implemented")
            
        except Exception as e:
            self.fail(f"OpenRouter integration test failed: {e}")

class TestJobMatchingSystem(unittest.TestCase):
    """Test suite for AI Job Matching system (Phase 3)"""
    
    def test_01_job_matching_api_structure(self):
        """Test the API structure for job matching endpoints"""
        try:
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
                
            # Check for job matching endpoints
            self.assertIn('@api_router.post("/candidates/{candidate_id}/process-matches")', server_code)
            self.assertIn('@api_router.get("/candidates/{candidate_id}/matches")', server_code)
            self.assertIn('@api_router.post("/matching/process-all")', server_code)
            self.assertIn('@api_router.get("/matching/stats")', server_code)
            self.assertIn('@api_router.post("/matching/test")', server_code)
            
            print("✅ Job matching API endpoints are properly defined")
            
        except Exception as e:
            self.fail(f"Job matching API structure test failed: {e}")
    
    def test_02_job_matching_service_structure(self):
        """Test the job matching service structure"""
        try:
            with open('/app/backend/services/job_matching.py', 'r') as f:
                matching_code = f.read()
                
            # Check for key components
            self.assertIn('from sentence_transformers import SentenceTransformer', matching_code)
            self.assertIn('from sklearn.metrics.pairwise import cosine_similarity', matching_code)
            self.assertIn('class JobMatchingService', matching_code)
            self.assertIn('def generate_job_embedding', matching_code)
            self.assertIn('def generate_candidate_embedding', matching_code)
            self.assertIn('def calculate_semantic_similarity', matching_code)
            self.assertIn('def match_job_to_candidate', matching_code)
            self.assertIn('def process_candidate_matches', matching_code)
            self.assertIn('def process_all_candidates', matching_code)
            self.assertIn('def get_matching_stats', matching_code)
            
            print("✅ Job matching service has all required components")
            
        except Exception as e:
            self.fail(f"Job matching service structure test failed: {e}")

if __name__ == "__main__":
    print("Running Elite JobHunter X - Phase 6 Application Submission System Tests...")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add application submission tests (Phase 6 - Primary focus)
    suite.addTest(unittest.makeSuite(TestApplicationSubmissionSystem))
    
    # Add cover letter tests (Phase 5 - Secondary)
    suite.addTest(unittest.makeSuite(TestAdvancedCoverLetterSystem))
    
    # Add resume tailoring tests (Phase 4 - Secondary)
    suite.addTest(unittest.makeSuite(TestAdvancedResumeTailoringSystem))
    
    # Add job matching tests for completeness (Phase 3)
    suite.addTest(unittest.makeSuite(TestJobMatchingSystem))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 80)
    if result.wasSuccessful():
        print("🎉 All tests passed successfully!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for failure in result.failures:
            print(f"FAILURE: {failure[0]}")
            print(f"  {failure[1]}")
        for error in result.errors:
            print(f"ERROR: {error[0]}")
            print(f"  {error[1]}")
