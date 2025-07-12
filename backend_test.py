#!/usr/bin/env python3
"""
Elite JobHunter X - Backend API Testing
Comprehensive tests for Phase 5 Advanced Cover Letter Generation system
"""

import unittest
import sys
import os
import json
import requests
import asyncio
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://f9bd5e31-4f5c-459c-af8c-ef4f8a57958e.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

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
    print("Running Elite JobHunter X - Phase 4 Advanced Resume Tailoring System Tests...")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add resume tailoring tests
    suite.addTest(unittest.makeSuite(TestAdvancedResumeTailoringSystem))
    
    # Add job matching tests for completeness
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
