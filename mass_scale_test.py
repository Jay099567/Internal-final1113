#!/usr/bin/env python3
"""
Elite JobHunter X - MASS SCALE AUTONOMOUS SYSTEM Testing
Testing the 12 specific endpoints for Phases 7-9
"""

import unittest
import sys
import os
import json
import requests
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://c0608967-bbec-4527-b994-5ff4fea0c6fd.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class TestMassScaleEndpoints(unittest.TestCase):
    """Test suite for the 12 MASS SCALE AUTONOMOUS SYSTEM endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        cls.test_candidate_id = None
        cls._create_test_candidate()
    
    @classmethod
    def _create_test_candidate(cls):
        """Create test candidate for MASS SCALE testing"""
        try:
            candidate_data = {
                "full_name": "Emma Rodriguez",
                "email": "emma.rodriguez@example.com",
                "phone": "+1-555-0166",
                "location": "Austin, TX",
                "linkedin_url": "https://linkedin.com/in/emmarodriguez",
                "target_roles": ["Senior Software Engineer", "Tech Lead"],
                "target_locations": ["Austin", "Remote"],
                "salary_min": 140000,
                "salary_max": 200000,
                "years_experience": 7,
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

    # ========================================================================
    # MASTER AUTOMATION ORCHESTRATOR ENDPOINTS (4 endpoints)
    # ========================================================================
    
    def test_01_automation_start_endpoint(self):
        """Test POST /api/automation/start - Start autonomous system ✅ PRIORITY"""
        try:
            response = requests.post(f"{API_BASE}/automation/start", timeout=30)
            
            if response.status_code == 500:
                # Check if it's a service initialization error
                error_detail = response.json().get("detail", "")
                if "master_orchestrator" in error_detail.lower():
                    print("❌ Master Automation Orchestrator service not properly initialized")
                    self.fail(f"Service initialization error: {error_detail}")
                else:
                    self.fail(f"Unexpected 500 error: {error_detail}")
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("message", data)
            self.assertIn("status", data)
            self.assertEqual(data["status"], "initializing")
            
            print("✅ POST /api/automation/start - Working")
            
        except Exception as e:
            self.fail(f"Automation start endpoint test failed: {e}")
    
    def test_02_automation_stop_endpoint(self):
        """Test POST /api/automation/stop - Stop autonomous system ✅ PRIORITY"""
        try:
            response = requests.post(f"{API_BASE}/automation/stop", timeout=30)
            
            if response.status_code == 500:
                error_detail = response.json().get("detail", "")
                if "master_orchestrator" in error_detail.lower():
                    print("❌ Master Automation Orchestrator service not properly initialized")
                    self.fail(f"Service initialization error: {error_detail}")
                else:
                    self.fail(f"Unexpected 500 error: {error_detail}")
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("message", data)
            
            print("✅ POST /api/automation/stop - Working")
            
        except Exception as e:
            self.fail(f"Automation stop endpoint test failed: {e}")
    
    def test_03_automation_status_endpoint(self):
        """Test GET /api/automation/status - Get system status ✅ WORKING"""
        try:
            response = requests.get(f"{API_BASE}/automation/status", timeout=30)
            
            if response.status_code == 500:
                error_detail = response.json().get("detail", "")
                if "master_orchestrator" in error_detail.lower():
                    print("❌ Master Automation Orchestrator service not properly initialized")
                    self.fail(f"Service initialization error: {error_detail}")
                else:
                    self.fail(f"Unexpected 500 error: {error_detail}")
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("status", data)
            
            print("✅ GET /api/automation/status - Working")
            
        except Exception as e:
            self.fail(f"Automation status endpoint test failed: {e}")
    
    def test_04_automation_stats_endpoint(self):
        """Test GET /api/automation/stats - Get automation statistics (has minor issue with stats object)"""
        try:
            response = requests.get(f"{API_BASE}/automation/stats", timeout=30)
            
            if response.status_code == 500:
                error_detail = response.json().get("detail", "")
                if "master_orchestrator" in error_detail.lower() or "stats" in error_detail.lower():
                    print("❌ Master Automation Orchestrator stats object issue detected")
                    self.fail(f"Stats object error: {error_detail}")
                else:
                    self.fail(f"Unexpected 500 error: {error_detail}")
            
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
            
            print("✅ GET /api/automation/stats - Working")
            
        except Exception as e:
            self.fail(f"Automation stats endpoint test failed: {e}")

    # ========================================================================
    # LINKEDIN AUTOMATION SERVICE ENDPOINTS (3 endpoints)
    # ========================================================================
    
    def test_05_linkedin_start_outreach_endpoint(self):
        """Test POST /api/linkedin/start-outreach - Start LinkedIn outreach ✅ PRIORITY"""
        try:
            if not self.test_candidate_id:
                self.skipTest("No test candidate available")
            
            response = requests.post(
                f"{API_BASE}/linkedin/start-outreach",
                params={"candidate_id": self.test_candidate_id},
                timeout=30
            )
            
            if response.status_code == 500:
                error_detail = response.json().get("detail", "")
                if "linkedin_automation" in error_detail.lower():
                    print("❌ LinkedIn Automation service not properly initialized")
                    self.fail(f"LinkedIn service initialization error: {error_detail}")
                else:
                    self.fail(f"Unexpected 500 error: {error_detail}")
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("message", data)
            self.assertIn("candidate_id", data)
            self.assertEqual(data["candidate_id"], self.test_candidate_id)
            
            print("✅ POST /api/linkedin/start-outreach - Working")
            
        except Exception as e:
            self.fail(f"LinkedIn start outreach endpoint test failed: {e}")
    
    def test_06_linkedin_outreach_status_endpoint(self):
        """Test GET /api/linkedin/outreach-status/{candidate_id} - Get outreach status"""
        try:
            if not self.test_candidate_id:
                self.skipTest("No test candidate available")
            
            response = requests.get(
                f"{API_BASE}/linkedin/outreach-status/{self.test_candidate_id}",
                timeout=30
            )
            
            if response.status_code == 500:
                error_detail = response.json().get("detail", "")
                if "linkedin_automation" in error_detail.lower():
                    print("❌ LinkedIn Automation service method issue detected")
                    self.fail(f"LinkedIn service method error: {error_detail}")
                else:
                    self.fail(f"Unexpected 500 error: {error_detail}")
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("status", data)
            
            print("✅ GET /api/linkedin/outreach-status/{candidate_id} - Working")
            
        except Exception as e:
            self.fail(f"LinkedIn outreach status endpoint test failed: {e}")
    
    def test_07_linkedin_campaigns_endpoint(self):
        """Test GET /api/linkedin/campaigns - Get outreach campaigns (has method naming issue)"""
        try:
            response = requests.get(f"{API_BASE}/linkedin/campaigns", timeout=30)
            
            if response.status_code == 500:
                error_detail = response.json().get("detail", "")
                if "get_active_campaigns" in error_detail.lower() or "linkedin_automation" in error_detail.lower():
                    print("❌ LinkedIn campaigns method naming issue detected - 'get_active_campaigns' method missing")
                    self.fail(f"Method naming issue: {error_detail}")
                else:
                    self.fail(f"Unexpected 500 error: {error_detail}")
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("campaigns", data)
            
            print("✅ GET /api/linkedin/campaigns - Working")
            
        except Exception as e:
            self.fail(f"LinkedIn campaigns endpoint test failed: {e}")

    # ========================================================================
    # FEEDBACK ANALYTICS SERVICE ENDPOINTS (3 endpoints)
    # ========================================================================
    
    def test_08_feedback_analyze_performance_endpoint(self):
        """Test POST /api/feedback/analyze-performance - Analyze performance ✅ PRIORITY"""
        try:
            response = requests.post(f"{API_BASE}/feedback/analyze-performance", timeout=30)
            
            if response.status_code == 500:
                error_detail = response.json().get("detail", "")
                if "feedback_analyzer" in error_detail.lower():
                    print("❌ Feedback Analyzer service not properly initialized")
                    self.fail(f"Feedback service initialization error: {error_detail}")
                else:
                    self.fail(f"Unexpected 500 error: {error_detail}")
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("performance_data", data)
            self.assertIn("recommendations", data)
            
            print("✅ POST /api/feedback/analyze-performance - Working")
            
        except Exception as e:
            self.fail(f"Feedback analyze performance endpoint test failed: {e}")
    
    def test_09_feedback_apply_optimizations_endpoint(self):
        """Test POST /api/feedback/apply-optimizations - Apply optimizations"""
        try:
            response = requests.post(f"{API_BASE}/feedback/apply-optimizations", timeout=30)
            
            if response.status_code == 500:
                error_detail = response.json().get("detail", "")
                if "feedback_analyzer" in error_detail.lower():
                    print("❌ Feedback Analyzer service method issue detected")
                    self.fail(f"Feedback service method error: {error_detail}")
                else:
                    self.fail(f"Unexpected 500 error: {error_detail}")
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("optimizations_applied", data)
            
            print("✅ POST /api/feedback/apply-optimizations - Working")
            
        except Exception as e:
            self.fail(f"Feedback apply optimizations endpoint test failed: {e}")
    
    def test_10_feedback_success_patterns_endpoint(self):
        """Test GET /api/feedback/success-patterns - Get success patterns"""
        try:
            response = requests.get(f"{API_BASE}/feedback/success-patterns", timeout=30)
            
            if response.status_code == 500:
                error_detail = response.json().get("detail", "")
                if "feedback_analyzer" in error_detail.lower():
                    print("❌ Feedback Analyzer service method issue detected")
                    self.fail(f"Feedback service method error: {error_detail}")
                else:
                    self.fail(f"Unexpected 500 error: {error_detail}")
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("patterns", data)
            
            print("✅ GET /api/feedback/success-patterns - Working")
            
        except Exception as e:
            self.fail(f"Feedback success patterns endpoint test failed: {e}")

    # ========================================================================
    # MASS SCALE ANALYTICS DASHBOARD ENDPOINTS (2 endpoints)
    # ========================================================================
    
    def test_11_analytics_mass_scale_dashboard_endpoint(self):
        """Test GET /api/analytics/mass-scale-dashboard - Get comprehensive dashboard ✅ WORKING"""
        try:
            response = requests.get(f"{API_BASE}/analytics/mass-scale-dashboard", timeout=30)
            
            if response.status_code == 500:
                error_detail = response.json().get("detail", "")
                if "master_orchestrator" in error_detail.lower():
                    print("❌ Mass Scale Dashboard has dependency on master_orchestrator")
                    self.fail(f"Dashboard dependency error: {error_detail}")
                else:
                    self.fail(f"Unexpected 500 error: {error_detail}")
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("dashboard", data)
            
            # Check dashboard structure
            dashboard = data["dashboard"]
            required_sections = ["candidates", "jobs", "applications", "matching", "outreach", "automation"]
            
            for section in required_sections:
                self.assertIn(section, dashboard)
            
            print("✅ GET /api/analytics/mass-scale-dashboard - Working")
            
        except Exception as e:
            self.fail(f"Analytics mass scale dashboard endpoint test failed: {e}")
    
    def test_12_analytics_candidate_performance_endpoint(self):
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
            required_metrics = ["applications", "matching", "outreach"]
            
            for metric in required_metrics:
                self.assertIn(metric, performance)
            
            print("✅ GET /api/analytics/candidate-performance/{candidate_id} - Working")
            
        except Exception as e:
            self.fail(f"Analytics candidate performance endpoint test failed: {e}")


def run_mass_scale_tests():
    """Run the MASS SCALE endpoint tests"""
    print("=" * 80)
    print("TESTING MASS SCALE AUTONOMOUS SYSTEM - 12 ENDPOINTS")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMassScaleEndpoints)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 80)
    print("MASS SCALE ENDPOINTS TEST SUMMARY:")
    print("=" * 80)
    
    # Count results
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    successes = total_tests - failures - errors
    
    print(f"✅ WORKING ENDPOINTS: {successes}/{total_tests}")
    print(f"❌ FAILED ENDPOINTS: {failures}/{total_tests}")
    print(f"🔥 ERROR ENDPOINTS: {errors}/{total_tests}")
    
    if failures > 0:
        print("\nFAILED ENDPOINTS:")
        for test, traceback in result.failures:
            endpoint_name = test._testMethodName.replace('test_', '').replace('_endpoint', '')
            print(f"  ❌ {endpoint_name}")
    
    if errors > 0:
        print("\nERROR ENDPOINTS:")
        for test, traceback in result.errors:
            endpoint_name = test._testMethodName.replace('test_', '').replace('_endpoint', '')
            print(f"  🔥 {endpoint_name}")
    
    print("=" * 80)
    
    return result


if __name__ == "__main__":
    run_mass_scale_tests()