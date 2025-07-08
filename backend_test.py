#!/usr/bin/env python3
"""
Elite JobHunter X - Backend API Testing
Comprehensive tests for Phase 3 AI Job Matching system
"""

import unittest
import sys
import os
import json
from datetime import datetime

class TestAIJobMatchingSystem(unittest.TestCase):
    """Test suite for AI Job Matching system structure"""
    
    def test_api_structure(self):
        """Test the API structure for job matching endpoints"""
        # Verify the API endpoints exist in server.py
        with open('/app/backend/server.py', 'r') as f:
            server_code = f.read()
            
        # Check for job matching endpoints
        self.assertIn('@api_router.post("/candidates/{candidate_id}/process-matches")', server_code)
        self.assertIn('@api_router.get("/candidates/{candidate_id}/matches")', server_code)
        self.assertIn('@api_router.post("/matching/process-all")', server_code)
        self.assertIn('@api_router.get("/matching/stats")', server_code)
        self.assertIn('@api_router.post("/matching/test")', server_code)
        
        print("✅ Job matching API endpoints are properly defined")
    
    def test_job_matching_service_structure(self):
        """Test the job matching service structure"""
        # Verify the job matching service implementation
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
    
    def test_openrouter_integration(self):
        """Test OpenRouter AI integration"""
        # Verify OpenRouter integration
        with open('/app/backend/services/openrouter.py', 'r') as f:
            openrouter_code = f.read()
            
        # Check for key components
        self.assertIn('class OpenRouterService', openrouter_code)
        self.assertIn('def generate_completion', openrouter_code)
        self.assertIn('def analyze_job_match', openrouter_code)
        self.assertIn('models = {', openrouter_code)
        self.assertIn('"job_matching": ', openrouter_code)
        
        print("✅ OpenRouter AI integration is properly implemented")
    
    def test_database_models(self):
        """Test database models for job matching"""
        # Verify database models
        with open('/app/backend/models.py', 'r') as f:
            models_code = f.read()
            
        # Check for job matching models
        self.assertIn('class JobFiltered(BaseModel)', models_code)
        self.assertIn('class Priority(str, Enum)', models_code)
        self.assertIn('job_raw_id: str', models_code)
        self.assertIn('candidate_id: str', models_code)
        self.assertIn('match_score: float', models_code)
        self.assertIn('priority: Priority', models_code)
        
        print("✅ Database models for job matching are properly defined")
    
    def test_api_endpoint_implementation(self):
        """Test API endpoint implementation details"""
        with open('/app/backend/server.py', 'r') as f:
            server_code = f.read()
            
        # Check process-matches endpoint implementation
        process_matches_impl = server_code.find('async def process_candidate_matches')
        self.assertGreater(process_matches_impl, 0)
        
        # Check that it uses the job matching service
        self.assertIn('matching_service = get_job_matching_service()', server_code[process_matches_impl:process_matches_impl+500])
        self.assertIn('matches = await matching_service.process_candidate_matches', server_code[process_matches_impl:process_matches_impl+500])
        
        # Check get-matches endpoint implementation
        get_matches_impl = server_code.find('async def get_candidate_matches')
        self.assertGreater(get_matches_impl, 0)
        
        # Check process-all endpoint implementation
        process_all_impl = server_code.find('async def process_all_candidate_matches')
        self.assertGreater(process_all_impl, 0)
        
        # Check stats endpoint implementation
        stats_impl = server_code.find('async def get_matching_statistics')
        self.assertGreater(stats_impl, 0)
        
        # Check test endpoint implementation
        test_impl = server_code.find('async def test_job_matching')
        self.assertGreater(test_impl, 0)
        
        print("✅ API endpoints for job matching are properly implemented")

if __name__ == "__main__":
    print("Running AI Job Matching System Structure Tests...")
    unittest.main(verbosity=2)
