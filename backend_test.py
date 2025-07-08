#!/usr/bin/env python3
"""
Elite JobHunter X - Backend API Testing
Comprehensive tests for Phase 3 AI Job Matching system
"""

import requests
import json
import uuid
import time
import os
import sys
from typing import Dict, Any, List, Optional
import unittest

# Get backend URL from frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"\'')
            break

# API base URL
API_URL = f"{BACKEND_URL}/api"

print(f"Using API URL: {API_URL}")

# Test API connection
try:
    response = requests.get(f"{API_URL}/health", timeout=10)
    if response.status_code != 200:
        print(f"API health check failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
    print("API connection successful!")
except Exception as e:
    print(f"Failed to connect to API: {str(e)}")
    print("Using local development URL instead")
    API_URL = "http://localhost:8001/api"
    print(f"Trying local API URL: {API_URL}")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("Local API connection successful!")
        else:
            print(f"Local API health check failed with status code: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to connect to local API: {str(e)}")
        sys.exit(1)

class TestEliteJobHunterX(unittest.TestCase):
    """Test suite for Elite JobHunter X backend API"""

    def setUp(self):
        """Set up test data"""
        # Test candidate data
        self.test_candidate = {
            "full_name": "Alex Johnson",
            "email": "alex.johnson@example.com",
            "phone": "555-123-4567",
            "location": "San Francisco, CA",
            "linkedin_url": "https://linkedin.com/in/alexjohnson",
            "github_url": "https://github.com/alexjohnson",
            "portfolio_url": "https://alexjohnson.dev",
            "target_roles": ["Software Engineer", "Full Stack Developer", "Backend Developer"],
            "target_companies": ["Google", "Microsoft", "Amazon"],
            "target_locations": ["San Francisco", "Seattle", "Remote"],
            "salary_min": 120000,
            "salary_max": 180000,
            "visa_sponsorship_required": False,
            "work_authorization": "US Citizen",
            "years_experience": 5,
            "skills": ["Python", "JavaScript", "React", "Node.js", "FastAPI", "MongoDB", "AWS"]
        }
        
        # Test job data
        self.test_job = {
            "title": "Senior Software Engineer",
            "company": "TechCorp Inc.",
            "location": "San Francisco, CA",
            "description": """
            We are looking for a Senior Software Engineer to join our team. 
            The ideal candidate will have 5+ years of experience in software development,
            with expertise in Python, JavaScript, and cloud technologies.
            
            Responsibilities:
            - Design and implement scalable backend services
            - Work with frontend developers to integrate APIs
            - Optimize database queries and performance
            - Participate in code reviews and technical discussions
            
            Requirements:
            - 5+ years of experience in software development
            - Strong knowledge of Python and JavaScript
            - Experience with React, Node.js, and MongoDB
            - Familiarity with AWS or other cloud platforms
            - Excellent problem-solving and communication skills
            """,
            "experience_level": "senior",
            "skills": ["Python", "JavaScript", "React", "Node.js", "MongoDB", "AWS"],
            "remote": True,
            "salary": "$140,000 - $180,000"
        }
        
        # Create a test candidate
        response = requests.post(f"{API_URL}/candidates", json=self.test_candidate)
        if response.status_code == 200:
            self.candidate_id = response.json()["id"]
            print(f"Created test candidate with ID: {self.candidate_id}")
        else:
            raise Exception(f"Failed to create test candidate: {response.text}")

    def tearDown(self):
        """Clean up after tests"""
        # We're not deleting the candidate as it might be useful for other tests
        pass

    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{API_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")
        self.assertIn("openrouter", data)
        print("✅ Health endpoint is working")

    def test_job_matching_service_initialization(self):
        """Test job matching service initialization via test endpoint"""
        response = requests.post(
            f"{API_URL}/matching/test",
            params={
                "candidate_id": self.candidate_id,
                "job_title": "Test Job",
                "job_description": "This is a test job description"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("success", data)
        self.assertIn("match", data)
        self.assertIn("sample_job", data)
        print("✅ Job matching service initialization successful")

    def test_matching_with_sample_data(self):
        """Test job matching with sample data"""
        response = requests.post(
            f"{API_URL}/matching/test",
            params={
                "candidate_id": self.candidate_id,
                "job_title": self.test_job["title"],
                "job_description": self.test_job["description"]
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        
        # Verify match data structure
        match = data["match"]
        self.assertIn("match_score", match)
        self.assertIn("priority", match)
        self.assertIn("should_apply", match)
        self.assertIn("explanation", match)
        self.assertIn("salary_match", match)
        self.assertIn("location_match", match)
        self.assertIn("visa_match", match)
        self.assertIn("skills_match_score", match)
        self.assertIn("experience_match", match)
        self.assertIn("keywords_matched", match)
        self.assertIn("strengths", match)
        self.assertIn("missing_requirements", match)
        self.assertIn("reasoning", match)
        
        # Verify match score is reasonable
        self.assertGreaterEqual(match["match_score"], 0.0)
        self.assertLessEqual(match["match_score"], 1.0)
        
        print(f"✅ Job matching with sample data successful. Match score: {match['match_score']}")

    def test_process_candidate_matches(self):
        """Test processing matches for a candidate"""
        response = requests.post(
            f"{API_URL}/candidates/{self.candidate_id}/process-matches",
            params={"max_jobs": 10}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("candidate_id", data)
        self.assertIn("candidate_name", data)
        self.assertIn("matches_processed", data)
        self.assertIn("high_priority_matches", data)
        self.assertIn("should_apply_count", data)
        self.assertIn("matches", data)
        
        print(f"✅ Process candidate matches successful. Processed {data['matches_processed']} matches")

    def test_get_candidate_matches(self):
        """Test retrieving saved matches for a candidate"""
        # First process some matches
        requests.post(
            f"{API_URL}/candidates/{self.candidate_id}/process-matches",
            params={"max_jobs": 5}
        )
        
        # Then retrieve them
        response = requests.get(
            f"{API_URL}/candidates/{self.candidate_id}/matches",
            params={"limit": 10}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("candidate_id", data)
        self.assertIn("candidate_name", data)
        self.assertIn("total_matches", data)
        self.assertIn("matches", data)
        
        print(f"✅ Get candidate matches successful. Retrieved {data['total_matches']} matches")

    def test_matching_stats(self):
        """Test retrieving matching statistics"""
        response = requests.get(f"{API_URL}/matching/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("stats", data)
        stats = data["stats"]
        self.assertIn("total_matches", stats)
        self.assertIn("high_priority_matches", stats)
        self.assertIn("should_apply_matches", stats)
        self.assertIn("recent_matches_24h", stats)
        
        print(f"✅ Matching stats successful. Total matches: {stats['total_matches']}")

    def test_process_all_candidates(self):
        """Test batch processing all candidates"""
        response = requests.post(f"{API_URL}/matching/process-all")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("results", data)
        results = data["results"]
        self.assertIn("total_candidates", results)
        self.assertIn("successful_matches", results)
        self.assertIn("failed_matches", results)
        self.assertIn("total_matches_found", results)
        self.assertIn("candidates_processed", results)
        
        print(f"✅ Process all candidates successful. Processed {results['total_candidates']} candidates")

    def test_vector_embeddings(self):
        """Test vector embedding generation indirectly through matching"""
        response = requests.post(
            f"{API_URL}/matching/test",
            params={
                "candidate_id": self.candidate_id,
                "job_title": "Machine Learning Engineer",
                "job_description": "We need an ML engineer with Python, TensorFlow, and PyTorch experience."
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        
        # The match score should reflect semantic similarity
        match = data["match"]
        self.assertGreaterEqual(match["match_score"], 0.0)
        
        print(f"✅ Vector embeddings test successful. Match score: {match['match_score']}")

    def test_invalid_candidate_id(self):
        """Test with invalid candidate ID"""
        invalid_id = str(uuid.uuid4())
        response = requests.post(
            f"{API_URL}/candidates/{invalid_id}/process-matches",
            params={"max_jobs": 10}
        )
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("not found", data["detail"].lower())
        
        print("✅ Invalid candidate ID test successful")

    def test_dashboard_integration(self):
        """Test dashboard integration with job matching stats"""
        response = requests.get(f"{API_URL}/dashboard/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("counts", data)
        self.assertIn("matching_stats", data)
        self.assertIn("recent_activity", data)
        
        # Verify job matches count is included
        self.assertIn("job_matches", data["counts"])
        
        print("✅ Dashboard integration test successful")

if __name__ == "__main__":
    unittest.main(verbosity=2)