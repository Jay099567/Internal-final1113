"""
Elite JobHunter X - AI Job Matching Service
Advanced job-candidate matching with vector embeddings and AI analysis
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
import uuid
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
import os

from .openrouter import get_openrouter_service
from models import JobFiltered, Priority

logger = logging.getLogger(__name__)

@dataclass
class JobMatch:
    """Structured job match result"""
    job_id: str
    candidate_id: str
    match_score: float
    explanation: str
    keywords_matched: List[str]
    salary_match: bool
    location_match: bool
    visa_match: bool
    skills_match_score: float
    experience_match: bool
    priority: Priority
    should_apply: bool
    missing_requirements: List[str]
    strengths: List[str]
    reasoning: str

class JobMatchingService:
    """Advanced AI-powered job matching service"""
    
    def __init__(self):
        self.db_client = MongoClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
        self.db = self.db_client[os.environ.get('DB_NAME', 'jobhunter_x_db')]
        
        # Collections
        self.candidates_collection = self.db['candidates']
        self.jobs_raw_collection = self.db['jobs_raw']
        self.jobs_filtered_collection = self.db['jobs_filtered']
        
        # Initialize sentence transformer for embeddings
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer: {e}")
            self.embedding_model = None
        
        # OpenRouter service
        self.openrouter_service = get_openrouter_service()
        
        # Matching configuration
        self.config = {
            'min_match_score': 0.60,  # Minimum score to consider a match
            'high_priority_threshold': 0.85,
            'medium_priority_threshold': 0.70,
            'salary_tolerance': 0.2,  # 20% tolerance for salary matching
            'location_keywords': ['remote', 'work from home', 'hybrid', 'flexible'],
            'max_matches_per_candidate': 50,
            'embedding_weight': 0.4,  # Weight for semantic similarity
            'ai_analysis_weight': 0.6  # Weight for AI analysis
        }
        
        logger.info("Job matching service initialized")
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for embedding"""
        if not text:
            return ""
        
        # Basic text cleaning
        text = text.lower().strip()
        text = ' '.join(text.split())  # Remove extra whitespace
        
        # Remove HTML tags if any
        import re
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        
        return text[:2000]  # Limit length for embeddings
    
    def generate_job_embedding(self, job: Dict[str, Any]) -> Optional[np.ndarray]:
        """Generate vector embedding for a job"""
        if not self.embedding_model:
            return None
        
        try:
            # Combine job fields for embedding
            job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('company', '')}"
            job_text = self.preprocess_text(job_text)
            
            if not job_text:
                return None
            
            embedding = self.embedding_model.encode([job_text])
            return embedding[0]
            
        except Exception as e:
            logger.error(f"Failed to generate job embedding: {e}")
            return None
    
    def generate_candidate_embedding(self, candidate: Dict[str, Any]) -> Optional[np.ndarray]:
        """Generate vector embedding for a candidate"""
        if not self.embedding_model:
            return None
        
        try:
            # Combine candidate fields for embedding
            candidate_text = f"{' '.join(candidate.get('target_roles', []))} {' '.join(candidate.get('skills', []))}"
            candidate_text = self.preprocess_text(candidate_text)
            
            if not candidate_text:
                return None
            
            embedding = self.embedding_model.encode([candidate_text])
            return embedding[0]
            
        except Exception as e:
            logger.error(f"Failed to generate candidate embedding: {e}")
            return None
    
    def calculate_semantic_similarity(self, job_embedding: np.ndarray, candidate_embedding: np.ndarray) -> float:
        """Calculate semantic similarity between job and candidate"""
        try:
            similarity = cosine_similarity([job_embedding], [candidate_embedding])[0][0]
            return max(0.0, min(1.0, similarity))  # Clamp between 0 and 1
        except Exception as e:
            logger.error(f"Failed to calculate semantic similarity: {e}")
            return 0.0
    
    def check_salary_match(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if job salary matches candidate expectations"""
        try:
            job_salary = job.get('salary')
            candidate_min = candidate.get('salary_min')
            candidate_max = candidate.get('salary_max')
            
            if not job_salary or not candidate_min:
                return False, "Salary information incomplete"
            
            # Extract numbers from salary string
            import re
            salary_numbers = re.findall(r'\d+', str(job_salary))
            
            if salary_numbers:
                # Take the first number as base salary (could be hourly/yearly)
                job_salary_num = int(salary_numbers[0])
                
                # If hourly, convert to yearly estimate
                if 'hour' in str(job_salary).lower():
                    job_salary_num *= 2080  # 40 hours * 52 weeks
                
                # Check if within range with tolerance
                tolerance = self.config['salary_tolerance']
                lower_bound = candidate_min * (1 - tolerance)
                upper_bound = candidate_max * (1 + tolerance) if candidate_max else float('inf')
                
                if lower_bound <= job_salary_num <= upper_bound:
                    return True, f"Salary {job_salary} matches expectations"
                else:
                    return False, f"Salary {job_salary} outside range ${candidate_min}-${candidate_max}"
            
            return False, "Could not parse salary information"
            
        except Exception as e:
            logger.error(f"Error checking salary match: {e}")
            return False, "Error processing salary"
    
    def check_location_match(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if job location matches candidate preferences"""
        try:
            job_location = str(job.get('location', '')).lower()
            job_remote = job.get('remote', False)
            candidate_locations = [loc.lower() for loc in candidate.get('target_locations', [])]
            
            # Check for remote work
            if job_remote or any(keyword in job_location for keyword in self.config['location_keywords']):
                return True, "Remote work available"
            
            # Check if job location matches candidate preferences
            for candidate_loc in candidate_locations:
                if candidate_loc in job_location or job_location in candidate_loc:
                    return True, f"Location match: {job_location}"
            
            # If candidate has no location preferences, accept any location
            if not candidate_locations:
                return True, "No location restrictions"
            
            return False, f"Location {job_location} not in preferences"
            
        except Exception as e:
            logger.error(f"Error checking location match: {e}")
            return False, "Error processing location"
    
    def check_visa_sponsorship(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> Tuple[bool, str]:
        """Check visa sponsorship requirements"""
        try:
            visa_required = candidate.get('visa_sponsorship_required', False)
            
            if not visa_required:
                return True, "No visa sponsorship required"
            
            # Check job description for visa sponsorship mentions
            description = str(job.get('description', '')).lower()
            visa_keywords = ['visa', 'sponsorship', 'h1b', 'work authorization', 'eligible to work']
            
            if any(keyword in description for keyword in visa_keywords):
                return True, "Visa sponsorship mentioned"
            else:
                return False, "Visa sponsorship required but not mentioned"
            
        except Exception as e:
            logger.error(f"Error checking visa sponsorship: {e}")
            return False, "Error processing visa requirements"
    
    def calculate_skills_match(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate skills match score and return matched skills"""
        try:
            job_skills = [skill.lower() for skill in job.get('skills', [])]
            candidate_skills = [skill.lower() for skill in candidate.get('skills', [])]
            
            if not job_skills or not candidate_skills:
                return 0.0, []
            
            # Find matching skills
            matched_skills = list(set(job_skills) & set(candidate_skills))
            
            # Calculate match percentage
            skills_match_score = len(matched_skills) / len(job_skills) if job_skills else 0.0
            
            return skills_match_score, matched_skills
            
        except Exception as e:
            logger.error(f"Error calculating skills match: {e}")
            return 0.0, []
    
    def check_experience_match(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if candidate experience matches job requirements"""
        try:
            candidate_experience = candidate.get('years_experience', 0)
            job_experience_level = job.get('experience_level', 'mid').lower()
            
            # Map experience levels to years
            experience_mapping = {
                'entry': (0, 2),
                'junior': (0, 2),
                'mid': (2, 5),
                'senior': (5, 10),
                'principal': (10, 20),
                'staff': (10, 20),
                'lead': (5, 15)
            }
            
            required_range = experience_mapping.get(job_experience_level, (2, 5))
            
            if required_range[0] <= candidate_experience <= required_range[1]:
                return True, f"Experience {candidate_experience} years matches {job_experience_level} level"
            elif candidate_experience > required_range[1]:
                return True, f"Overqualified: {candidate_experience} years for {job_experience_level} level"
            else:
                return False, f"Underqualified: {candidate_experience} years for {job_experience_level} level"
            
        except Exception as e:
            logger.error(f"Error checking experience match: {e}")
            return False, "Error processing experience"
    
    async def ai_analyze_match(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze job-candidate match"""
        try:
            # Create analysis prompt
            prompt = f"""
            Analyze this job-candidate match and provide detailed assessment:
            
            JOB:
            Title: {job.get('title', 'N/A')}
            Company: {job.get('company', 'N/A')}
            Location: {job.get('location', 'N/A')}
            Experience Level: {job.get('experience_level', 'N/A')}
            Skills: {', '.join(job.get('skills', []))}
            Description: {job.get('description', '')[:1000]}...
            
            CANDIDATE:
            Name: {candidate.get('full_name', 'N/A')}
            Experience: {candidate.get('years_experience', 'N/A')} years
            Skills: {', '.join(candidate.get('skills', []))}
            Target Roles: {', '.join(candidate.get('target_roles', []))}
            Target Locations: {', '.join(candidate.get('target_locations', []))}
            Salary Range: ${candidate.get('salary_min', 'N/A')}-${candidate.get('salary_max', 'N/A')}
            Visa Required: {candidate.get('visa_sponsorship_required', False)}
            
            Provide a JSON response with:
            {{
                "match_score": 0-100,
                "should_apply": true/false,
                "priority": "high/medium/low",
                "explanation": "detailed explanation",
                "strengths": ["strength1", "strength2"],
                "missing_requirements": ["req1", "req2"],
                "keywords_matched": ["keyword1", "keyword2"],
                "reasoning": "detailed reasoning for decision"
            }}
            """
            
            response = await self.openrouter_service.generate_completion(
                prompt, "job_matching", max_tokens=1000, temperature=0.3
            )
            
            # Parse JSON response
            try:
                analysis = json.loads(response)
                return analysis
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI analysis response: {response}")
                return {
                    "match_score": 50,
                    "should_apply": False,
                    "priority": "low",
                    "explanation": "Failed to analyze match",
                    "strengths": [],
                    "missing_requirements": [],
                    "keywords_matched": [],
                    "reasoning": "AI analysis failed"
                }
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {
                "match_score": 0,
                "should_apply": False,
                "priority": "low",
                "explanation": "AI analysis error",
                "strengths": [],
                "missing_requirements": [],
                "keywords_matched": [],
                "reasoning": f"Error: {str(e)}"
            }
    
    async def match_job_to_candidate(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> Optional[JobMatch]:
        """Perform comprehensive job-candidate matching"""
        try:
            logger.info(f"Matching job {job.get('title')} to candidate {candidate.get('full_name')}")
            
            # Generate embeddings
            job_embedding = self.generate_job_embedding(job)
            candidate_embedding = self.generate_candidate_embedding(candidate)
            
            # Calculate semantic similarity
            semantic_score = 0.0
            if job_embedding is not None and candidate_embedding is not None:
                semantic_score = self.calculate_semantic_similarity(job_embedding, candidate_embedding)
            
            # Perform individual checks
            salary_match, salary_reason = self.check_salary_match(job, candidate)
            location_match, location_reason = self.check_location_match(job, candidate)
            visa_match, visa_reason = self.check_visa_sponsorship(job, candidate)
            skills_match_score, matched_skills = self.calculate_skills_match(job, candidate)
            experience_match, experience_reason = self.check_experience_match(job, candidate)
            
            # Get AI analysis
            ai_analysis = await self.ai_analyze_match(job, candidate)
            
            # Combine scores
            ai_score = ai_analysis.get('match_score', 0) / 100.0
            final_score = (
                semantic_score * self.config['embedding_weight'] +
                ai_score * self.config['ai_analysis_weight']
            )
            
            # Adjust score based on hard requirements
            if not visa_match:
                final_score *= 0.3  # Heavily penalize visa mismatch
            if not location_match:
                final_score *= 0.7  # Penalize location mismatch
            
            # Determine priority
            if final_score >= self.config['high_priority_threshold']:
                priority = Priority.HIGH
            elif final_score >= self.config['medium_priority_threshold']:
                priority = Priority.MEDIUM
            else:
                priority = Priority.LOW
            
            # Decide if should apply
            should_apply = (
                final_score >= self.config['min_match_score'] and
                visa_match and
                ai_analysis.get('should_apply', False)
            )
            
            # Create match object
            job_match = JobMatch(
                job_id=job.get('_id') or job.get('id'),
                candidate_id=candidate.get('id'),
                match_score=final_score,
                explanation=ai_analysis.get('explanation', ''),
                keywords_matched=ai_analysis.get('keywords_matched', matched_skills),
                salary_match=salary_match,
                location_match=location_match,
                visa_match=visa_match,
                skills_match_score=skills_match_score,
                experience_match=experience_match,
                priority=priority,
                should_apply=should_apply,
                missing_requirements=ai_analysis.get('missing_requirements', []),
                strengths=ai_analysis.get('strengths', []),
                reasoning=ai_analysis.get('reasoning', '')
            )
            
            logger.info(f"Match score: {final_score:.2f}, Should apply: {should_apply}")
            return job_match
            
        except Exception as e:
            logger.error(f"Error matching job to candidate: {e}")
            return None
    
    async def process_candidate_matches(self, candidate_id: str, max_jobs: int = None) -> List[JobMatch]:
        """Process matches for a specific candidate"""
        try:
            # Get candidate
            candidate = self.candidates_collection.find_one({'id': candidate_id})
            if not candidate:
                logger.error(f"Candidate {candidate_id} not found")
                return []
            
            # Get recent jobs (last 7 days)
            since_date = datetime.now() - timedelta(days=7)
            
            # Get jobs that haven't been matched to this candidate yet
            already_matched = set()
            existing_matches = self.jobs_filtered_collection.find({'candidate_id': candidate_id})
            for match in existing_matches:
                already_matched.add(match['job_raw_id'])
            
            # Find new jobs to match
            job_query = {
                'scraped_at': {'$gte': since_date.isoformat()},
                '_id': {'$nin': list(already_matched)}
            }
            
            jobs = list(self.jobs_raw_collection.find(job_query).limit(max_jobs or 100))
            
            logger.info(f"Processing {len(jobs)} jobs for candidate {candidate.get('full_name')}")
            
            matches = []
            for job in jobs:
                try:
                    match = await self.match_job_to_candidate(job, candidate)
                    if match and match.match_score >= self.config['min_match_score']:
                        matches.append(match)
                        
                        # Save match to database
                        await self.save_job_match(match, job)
                    
                    # Small delay to prevent overwhelming the AI service
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error processing job {job.get('_id')}: {e}")
                    continue
            
            # Sort by match score
            matches.sort(key=lambda x: x.match_score, reverse=True)
            
            logger.info(f"Found {len(matches)} matches for candidate {candidate.get('full_name')}")
            return matches[:self.config['max_matches_per_candidate']]
            
        except Exception as e:
            logger.error(f"Error processing candidate matches: {e}")
            return []
    
    async def save_job_match(self, match: JobMatch, job: Dict[str, Any]):
        """Save job match to database"""
        try:
            job_filtered = JobFiltered(
                job_raw_id=match.job_id,
                candidate_id=match.candidate_id,
                match_score=match.match_score,
                explanation=match.explanation,
                keywords_matched=match.keywords_matched,
                salary_match=match.salary_match,
                location_match=match.location_match,
                visa_match=match.visa_match,
                skills_match_score=match.skills_match_score,
                experience_match=match.experience_match,
                priority=match.priority,
                should_apply=match.should_apply
            )
            
            self.jobs_filtered_collection.insert_one(job_filtered.dict())
            logger.info(f"Saved job match: {match.job_id} -> {match.candidate_id}")
            
        except Exception as e:
            logger.error(f"Failed to save job match: {e}")
    
    async def process_all_candidates(self) -> Dict[str, Any]:
        """Process matches for all active candidates"""
        try:
            logger.info("Starting batch job matching for all candidates")
            
            # Get all active candidates
            candidates = list(self.candidates_collection.find({'is_active': True}))
            
            results = {
                'total_candidates': len(candidates),
                'successful_matches': 0,
                'failed_matches': 0,
                'total_matches_found': 0,
                'high_priority_matches': 0,
                'candidates_processed': []
            }
            
            for candidate in candidates:
                try:
                    candidate_id = candidate['id']
                    matches = await self.process_candidate_matches(candidate_id)
                    
                    candidate_result = {
                        'candidate_id': candidate_id,
                        'candidate_name': candidate.get('full_name'),
                        'matches_found': len(matches),
                        'high_priority_matches': len([m for m in matches if m.priority == Priority.HIGH]),
                        'should_apply_count': len([m for m in matches if m.should_apply])
                    }
                    
                    results['candidates_processed'].append(candidate_result)
                    results['successful_matches'] += 1
                    results['total_matches_found'] += len(matches)
                    results['high_priority_matches'] += candidate_result['high_priority_matches']
                    
                    logger.info(f"Processed candidate {candidate.get('full_name')}: {len(matches)} matches")
                    
                except Exception as e:
                    logger.error(f"Failed to process candidate {candidate.get('id')}: {e}")
                    results['failed_matches'] += 1
            
            logger.info(f"Batch matching completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Batch matching failed: {e}")
            return {'error': str(e)}
    
    def get_candidate_matches(self, candidate_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get saved matches for a candidate"""
        try:
            # Get matches from database
            matches = list(
                self.jobs_filtered_collection
                .find({'candidate_id': candidate_id})
                .sort([('match_score', -1)])
                .limit(limit)
            )
            
            # Enrich with job data
            enriched_matches = []
            for match in matches:
                job_data = self.jobs_raw_collection.find_one({'_id': match['job_raw_id']})
                if job_data:
                    enriched_match = {
                        **match,
                        'job_data': job_data
                    }
                    enriched_matches.append(enriched_match)
            
            return enriched_matches
            
        except Exception as e:
            logger.error(f"Error getting candidate matches: {e}")
            return []
    
    def get_matching_stats(self) -> Dict[str, Any]:
        """Get job matching statistics"""
        try:
            total_matches = self.jobs_filtered_collection.count_documents({})
            high_priority = self.jobs_filtered_collection.count_documents({'priority': 'high'})
            should_apply = self.jobs_filtered_collection.count_documents({'should_apply': True})
            
            # Get recent matches (last 24 hours)
            since_time = datetime.now() - timedelta(hours=24)
            recent_matches = self.jobs_filtered_collection.count_documents({
                'filtered_at': {'$gte': since_time.isoformat()}
            })
            
            return {
                'total_matches': total_matches,
                'high_priority_matches': high_priority,
                'should_apply_matches': should_apply,
                'recent_matches_24h': recent_matches,
                'average_match_score': self.get_average_match_score()
            }
            
        except Exception as e:
            logger.error(f"Error getting matching stats: {e}")
            return {}
    
    def get_average_match_score(self) -> float:
        """Calculate average match score"""
        try:
            pipeline = [
                {'$group': {'_id': None, 'avg_score': {'$avg': '$match_score'}}}
            ]
            result = list(self.jobs_filtered_collection.aggregate(pipeline))
            return round(result[0]['avg_score'], 2) if result else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating average match score: {e}")
            return 0.0
    
    def close(self):
        """Close database connection"""
        if self.db_client:
            self.db_client.close()

# Global instance
job_matching_service = None

def get_job_matching_service():
    """Get or create the global job matching service instance"""
    global job_matching_service
    if job_matching_service is None:
        job_matching_service = JobMatchingService()
    return job_matching_service