#!/usr/bin/env python3
"""
Elite JobHunter X - Backend API Testing
Comprehensive tests for Phase 6 Application Submission system
"""

import unittest
import sys
import os
import json
import requests
import asyncio
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://21ab4ce4-dee6-40af-9f6c-44f20cce5290.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

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
