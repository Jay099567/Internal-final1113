import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import JSONResponse, RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta

# Import our models and services
from models import *
from services.openrouter import get_openrouter_service
from services.gmail import gmail_service
from services.resume_parser import resume_service
from services.scheduler import get_scheduler, create_custom_schedule
from services.job_matching import get_job_matching_service
from services.resume_tailoring import get_resume_tailoring_service
from services.application_submission import ApplicationSubmissionManager, ApplicationSubmissionConfig, ApplicationMethod, ApplicationResult


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Elite JobHunter X", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Elite JobHunter X API v1.0.0", "status": "operational"}

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        await db.command("ping")
        
        # Check OpenRouter API (simplified check)
        try:
            openrouter_service = get_openrouter_service()
            openrouter_status = "operational" if openrouter_service.api_key else "missing_api_key"
        except Exception as e:
            logger.warning(f"OpenRouter service check failed: {e}")
            openrouter_status = "error"
        
        return {
            "status": "healthy",
            "database": "connected",
            "openrouter": openrouter_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# =============================================================================
# CANDIDATE MANAGEMENT ENDPOINTS
# =============================================================================

@api_router.post("/candidates", response_model=Candidate)
async def create_candidate(candidate_data: CandidateCreate):
    """Create a new candidate"""
    try:
        candidate = Candidate(**candidate_data.dict())
        await db.candidates.insert_one(candidate.dict())
        return candidate
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create candidate: {str(e)}")

@api_router.get("/candidates", response_model=List[Candidate])
async def get_candidates(skip: int = 0, limit: int = 100):
    """Get all candidates"""
    try:
        candidates = await db.candidates.find().skip(skip).limit(limit).to_list(length=limit)
        return [Candidate(**candidate) for candidate in candidates]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get candidates: {str(e)}")

@api_router.get("/candidates/{candidate_id}", response_model=Candidate)
async def get_candidate(candidate_id: str):
    """Get candidate by ID"""
    try:
        candidate = await db.candidates.find_one({"id": candidate_id})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return Candidate(**candidate)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get candidate: {str(e)}")

@api_router.put("/candidates/{candidate_id}", response_model=Candidate)
async def update_candidate(candidate_id: str, candidate_data: CandidateUpdate):
    """Update candidate"""
    try:
        # Check if candidate exists
        existing = await db.candidates.find_one({"id": candidate_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Update fields
        update_data = {k: v for k, v in candidate_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await db.candidates.update_one(
            {"id": candidate_id},
            {"$set": update_data}
        )
        
        # Return updated candidate
        updated_candidate = await db.candidates.find_one({"id": candidate_id})
        return Candidate(**updated_candidate)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update candidate: {str(e)}")

# =============================================================================
# RESUME MANAGEMENT ENDPOINTS
# =============================================================================

@api_router.post("/candidates/{candidate_id}/resume/upload")
async def upload_resume(candidate_id: str, file: UploadFile = File(...)):
    """Upload and parse resume for candidate"""
    try:
        # Check if candidate exists
        candidate = await db.candidates.find_one({"id": candidate_id})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Save file
        file_content = await file.read()
        file_path = await resume_service.save_uploaded_file(file_content, file.filename, candidate_id)
        
        # Parse resume
        parsed_resume = await resume_service.parse_resume(file_path)
        
        # Save resume to database
        resume_data = Resume(
            candidate_id=candidate_id,
            version_name="Original",
            file_path=file_path,
            extracted_text=parsed_resume.raw_text,
            skills=parsed_resume.skills,
            experience_years=parsed_resume.years_experience,
            is_primary=True  # Set as primary resume
        )
        
        await db.resumes.insert_one(resume_data.dict())
        
        # Update candidate with extracted info
        candidate_updates = {}
        if parsed_resume.contact_info.get('email') and not candidate.get('email'):
            candidate_updates['email'] = parsed_resume.contact_info['email']
        if parsed_resume.contact_info.get('phone') and not candidate.get('phone'):
            candidate_updates['phone'] = parsed_resume.contact_info['phone']
        if parsed_resume.contact_info.get('location') and not candidate.get('location'):
            candidate_updates['location'] = parsed_resume.contact_info['location']
        if parsed_resume.contact_info.get('linkedin') and not candidate.get('linkedin_url'):
            candidate_updates['linkedin_url'] = parsed_resume.contact_info['linkedin']
        if parsed_resume.contact_info.get('github') and not candidate.get('github_url'):
            candidate_updates['github_url'] = parsed_resume.contact_info['github']
        if parsed_resume.skills and not candidate.get('skills'):
            candidate_updates['skills'] = parsed_resume.skills
        if parsed_resume.years_experience and not candidate.get('years_experience'):
            candidate_updates['years_experience'] = parsed_resume.years_experience
        
        if candidate_updates:
            candidate_updates['updated_at'] = datetime.utcnow()
            await db.candidates.update_one(
                {"id": candidate_id},
                {"$set": candidate_updates}
            )
        
        # Analyze resume quality
        quality_analysis = await resume_service.analyze_resume_quality(parsed_resume)
        
        return {
            "resume_id": resume_data.id,
            "message": "Resume uploaded and parsed successfully",
            "extracted_data": {
                "contact_info": parsed_resume.contact_info,
                "skills": parsed_resume.skills,
                "experience_count": len(parsed_resume.experience),
                "education_count": len(parsed_resume.education),
                "years_experience": parsed_resume.years_experience
            },
            "quality_analysis": quality_analysis,
            "candidate_updated": bool(candidate_updates)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload resume: {str(e)}")

@api_router.get("/candidates/{candidate_id}/resumes")
async def get_candidate_resumes(candidate_id: str):
    """Get all resumes for a candidate"""
    try:
        resumes = await db.resumes.find({"candidate_id": candidate_id}).to_list(length=100)
        return [Resume(**resume) for resume in resumes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resumes: {str(e)}")

# =============================================================================
# GMAIL OAUTH ENDPOINTS
# =============================================================================

@api_router.get("/gmail/auth/url")
async def get_gmail_auth_url(candidate_id: str, redirect_uri: str = None):
    """Get Gmail OAuth authorization URL"""
    try:
        # Check if candidate exists
        candidate = await db.candidates.find_one({"id": candidate_id})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        auth_url = gmail_service.get_authorization_url(redirect_uri)
        
        return {
            "auth_url": auth_url,
            "candidate_id": candidate_id,
            "message": "Visit the auth_url to authorize Gmail access"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@api_router.post("/gmail/auth/callback")
async def gmail_auth_callback(
    code: str,
    candidate_id: str,
    redirect_uri: str = None
):
    """Handle Gmail OAuth callback"""
    try:
        # Exchange code for tokens
        tokens = gmail_service.exchange_code_for_tokens(code, redirect_uri)
        
        # Get user profile
        service = gmail_service.build_service(tokens['access_token'])
        profile = await gmail_service.get_user_profile(service)
        
        # Save OAuth tokens
        oauth_data = GmailOAuth(
            candidate_id=candidate_id,
            gmail_address=profile['email'],
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_expiry=tokens['token_expiry'],
            scopes=tokens['scopes']
        )
        
        await db.gmail_oauth.insert_one(oauth_data.dict())
        
        # Update candidate with Gmail info
        await db.candidates.update_one(
            {"id": candidate_id},
            {"$set": {
                "email": profile['email'],
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {
            "message": "Gmail authentication successful",
            "gmail_address": profile['email'],
            "candidate_id": candidate_id,
            "oauth_id": oauth_data.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gmail authentication failed: {str(e)}")

@api_router.get("/candidates/{candidate_id}/gmail/profile")
async def get_gmail_profile(candidate_id: str):
    """Get Gmail profile for candidate"""
    try:
        # Get OAuth tokens
        oauth_data = await db.gmail_oauth.find_one({"candidate_id": candidate_id, "is_active": True})
        if not oauth_data:
            raise HTTPException(status_code=404, detail="Gmail authentication not found")
        
        # Build service and get profile
        service = gmail_service.build_service(oauth_data['access_token'])
        profile = await gmail_service.get_user_profile(service)
        
        return {
            "gmail_address": profile['email'],
            "messages_total": profile['messages_total'],
            "threads_total": profile['threads_total'],
            "authenticated_at": oauth_data['created_at']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Gmail profile: {str(e)}")

# =============================================================================
# AI TESTING ENDPOINTS
# =============================================================================

@api_router.post("/ai/test/job-match")
async def test_job_match(
    candidate_id: str,
    job_description: str
):
    """Test AI job matching"""
    try:
        # Get candidate
        candidate = await db.candidates.find_one({"id": candidate_id})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Test job matching
        openrouter_service = get_openrouter_service()
        match_analysis = await openrouter_service.analyze_job_match(job_description, candidate)
        
        return {
            "candidate_id": candidate_id,
            "job_description": job_description[:200] + "..." if len(job_description) > 200 else job_description,
            "match_analysis": match_analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI job matching failed: {str(e)}")

@api_router.post("/ai/test/cover-letter")
async def test_cover_letter_generation(
    candidate_id: str,
    job_description: str,
    company_name: str,
    tone: str = "professional"
):
    """Test AI cover letter generation"""
    try:
        # Get candidate
        candidate = await db.candidates.find_one({"id": candidate_id})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Test cover letter generation
        company_info = {"name": company_name}
        openrouter_service = get_openrouter_service()
        cover_letter = await openrouter_service.generate_cover_letter(
            job_description, candidate, company_info, tone
        )
        
        return {
            "candidate_id": candidate_id,
            "company_name": company_name,
            "tone": tone,
            "cover_letter": cover_letter
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")

# =============================================================================
# JOB MATCHING ENDPOINTS (PHASE 3)
# =============================================================================

@api_router.post("/candidates/{candidate_id}/process-matches")
async def process_candidate_matches(candidate_id: str, max_jobs: int = 50):
    """Process job matches for a specific candidate"""
    try:
        # Check if candidate exists
        candidate = await db.candidates.find_one({"id": candidate_id})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Process matches
        matching_service = get_job_matching_service()
        matches = await matching_service.process_candidate_matches(candidate_id, max_jobs)
        
        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate.get('full_name'),
            "matches_processed": len(matches),
            "high_priority_matches": len([m for m in matches if m.priority.value == "high"]),
            "should_apply_count": len([m for m in matches if m.should_apply]),
            "matches": [
                {
                    "job_id": match.job_id,
                    "match_score": round(match.match_score, 3),
                    "priority": match.priority.value,
                    "should_apply": match.should_apply,
                    "explanation": match.explanation,
                    "keywords_matched": match.keywords_matched,
                    "strengths": match.strengths,
                    "missing_requirements": match.missing_requirements
                }
                for match in matches[:10]  # Return top 10 for API response
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process matches: {str(e)}")

@api_router.get("/candidates/{candidate_id}/matches")
async def get_candidate_matches(candidate_id: str, limit: int = 50):
    """Get saved job matches for a candidate"""
    try:
        # Check if candidate exists
        candidate = await db.candidates.find_one({"id": candidate_id})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Get matches
        matching_service = get_job_matching_service()
        matches = matching_service.get_candidate_matches(candidate_id, limit)
        
        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate.get('full_name'),
            "total_matches": len(matches),
            "matches": matches
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get matches: {str(e)}")

@api_router.post("/matching/process-all")
async def process_all_candidate_matches():
    """Process job matches for all active candidates"""
    try:
        matching_service = get_job_matching_service()
        results = await matching_service.process_all_candidates()
        
        return {
            "message": "Batch matching completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch matching failed: {str(e)}")

@api_router.get("/matching/stats")
async def get_matching_statistics():
    """Get job matching statistics"""
    try:
        matching_service = get_job_matching_service()
        stats = matching_service.get_matching_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get matching stats: {str(e)}")

@api_router.post("/matching/test")
async def test_job_matching(
    candidate_id: str,
    job_title: str = "Software Developer",
    job_description: str = "We are looking for a skilled software developer with experience in Python, React, and cloud technologies."
):
    """Test job matching with sample data"""
    try:
        # Check if candidate exists
        candidate = await db.candidates.find_one({"id": candidate_id})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Create sample job
        sample_job = {
            "_id": f"test_{uuid.uuid4().hex[:8]}",
            "title": job_title,
            "company": "Test Company",
            "location": "Remote",
            "description": job_description,
            "experience_level": "mid",
            "skills": ["python", "react", "aws"],
            "remote": True,
            "salary": "$80,000 - $120,000",
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        # Test matching
        matching_service = get_job_matching_service()
        match = await matching_service.match_job_to_candidate(sample_job, candidate)
        
        if match:
            return {
                "success": True,
                "match": {
                    "match_score": round(match.match_score, 3),
                    "priority": match.priority.value,
                    "should_apply": match.should_apply,
                    "explanation": match.explanation,
                    "salary_match": match.salary_match,
                    "location_match": match.location_match,
                    "visa_match": match.visa_match,
                    "skills_match_score": round(match.skills_match_score, 3),
                    "experience_match": match.experience_match,
                    "keywords_matched": match.keywords_matched,
                    "strengths": match.strengths,
                    "missing_requirements": match.missing_requirements,
                    "reasoning": match.reasoning
                },
                "sample_job": sample_job
            }
        else:
            return {
                "success": False,
                "message": "No match generated",
                "sample_job": sample_job
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test matching failed: {str(e)}")

# =============================================================================
# DASHBOARD ENDPOINTS
# =============================================================================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get counts
        candidates_count = await db.candidates.count_documents({})
        resumes_count = await db.resumes.count_documents({})
        applications_count = await db.applications.count_documents({})
        jobs_count = await db.jobs_raw.count_documents({})
        
        # Get job matching stats
        matching_service = get_job_matching_service()
        matching_stats = matching_service.get_matching_stats()
        
        # Get recent activity
        recent_candidates = await db.candidates.find().sort("created_at", -1).limit(5).to_list(length=5)
        recent_applications = await db.applications.find().sort("created_at", -1).limit(5).to_list(length=5)
        
        return {
            "counts": {
                "candidates": candidates_count,
                "resumes": resumes_count,
                "applications": applications_count,
                "jobs": jobs_count,
                "job_matches": matching_stats.get('total_matches', 0)
            },
            "matching_stats": matching_stats,
            "recent_activity": {
                "candidates": [Candidate(**c) for c in recent_candidates],
                "applications": [Application(**a) for a in recent_applications]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

# Original endpoints for backward compatibility
# =============================================================================
# JOB SCRAPING ENDPOINTS
# =============================================================================

class ScrapingRequest(BaseModel):
    """Request model for manual scraping"""
    scraper: str = Field(..., description="Scraper name (e.g., 'indeed')")
    query: str = Field(..., description="Job search query")
    location: str = Field(default="Remote", description="Location to search")
    max_pages: int = Field(default=3, description="Maximum pages to scrape")

class ScheduleRequest(BaseModel):
    """Request model for scheduling scraping"""
    name: str = Field(..., description="Schedule name")
    scraper: str = Field(..., description="Scraper name")
    query: str = Field(..., description="Job search query")
    location: str = Field(default="Remote", description="Location to search")
    interval_hours: int = Field(default=6, description="Interval in hours")
    max_pages: int = Field(default=3, description="Maximum pages to scrape")

@api_router.post("/scraping/start")
async def start_scraping(request: ScrapingRequest):
    """Start manual job scraping"""
    try:
        scheduler = get_scheduler()
        
        # Create search parameters
        search_params = {
            'q': request.query,
            'l': request.location,
            'max_pages': request.max_pages
        }
        
        # Run manual scraping
        results = await scheduler.run_manual_scraping(
            config_name=f"manual_{request.scraper}_{request.query}",
            scraper_name=request.scraper,
            search_params=search_params
        )
        
        return {
            "success": True,
            "message": f"Started scraping {request.query} jobs on {request.scraper}",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Failed to start scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start scraping: {str(e)}")

@api_router.get("/scraping/status")
async def get_scraping_status():
    """Get current scraping status and statistics"""
    try:
        scheduler = get_scheduler()
        
        # Get statistics
        stats = scheduler.get_scraping_stats()
        
        # Get scheduled jobs
        scheduled_jobs = scheduler.get_scheduled_jobs()
        
        # Get recent logs
        recent_logs = scheduler.get_scraping_logs(limit=10)
        
        return {
            "success": True,
            "stats": stats,
            "scheduled_jobs": scheduled_jobs,
            "recent_logs": recent_logs
        }
        
    except Exception as e:
        logger.error(f"Failed to get scraping status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scraping status: {str(e)}")

@api_router.post("/scraping/schedule")
async def create_scraping_schedule(request: ScheduleRequest):
    """Create a new scraping schedule"""
    try:
        scheduler = get_scheduler()
        
        # Create schedule configuration
        config = create_custom_schedule(
            name=request.name,
            scraper=request.scraper,
            query=request.query,
            location=request.location,
            interval_hours=request.interval_hours,
            max_pages=request.max_pages
        )
        
        # Add schedule
        scheduler.add_scraping_schedule(request.name, config)
        
        return {
            "success": True,
            "message": f"Created scraping schedule: {request.name}",
            "schedule": config
        }
        
    except Exception as e:
        logger.error(f"Failed to create schedule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create schedule: {str(e)}")

@api_router.delete("/scraping/schedule/{schedule_name}")
async def delete_scraping_schedule(schedule_name: str):
    """Delete a scraping schedule"""
    try:
        scheduler = get_scheduler()
        scheduler.remove_scraping_schedule(schedule_name)
        
        return {
            "success": True,
            "message": f"Deleted scraping schedule: {schedule_name}"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete schedule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete schedule: {str(e)}")

@api_router.get("/scraping/logs")
async def get_scraping_logs(limit: int = Query(50, ge=1, le=500)):
    """Get scraping logs"""
    try:
        scheduler = get_scheduler()
        logs = scheduler.get_scraping_logs(limit=limit)
        
        return {
            "success": True,
            "logs": logs,
            "total": len(logs)
        }
        
    except Exception as e:
        logger.error(f"Failed to get scraping logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scraping logs: {str(e)}")

# =============================================================================
# SCRAPED JOBS ENDPOINTS
# =============================================================================

@api_router.get("/jobs/raw")
async def get_scraped_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    source: Optional[str] = Query(None, description="Filter by source (e.g., 'indeed')"),
    location: Optional[str] = Query(None, description="Filter by location"),
    title: Optional[str] = Query(None, description="Filter by job title"),
    company: Optional[str] = Query(None, description="Filter by company"),
    remote: Optional[bool] = Query(None, description="Filter by remote jobs")
):
    """Get scraped job listings with filtering"""
    try:
        # Build filter query
        filter_query = {}
        
        if source:
            filter_query['source'] = source
        if location:
            filter_query['location'] = {"$regex": location, "$options": "i"}
        if title:
            filter_query['title'] = {"$regex": title, "$options": "i"}
        if company:
            filter_query['company'] = {"$regex": company, "$options": "i"}
        if remote is not None:
            filter_query['remote'] = remote
        
        # Get jobs with pagination
        jobs = await db.jobs_raw.find(filter_query).skip(skip).limit(limit).sort([('scraped_at', -1)]).to_list(length=limit)
        
        # Get total count
        total_count = await db.jobs_raw.count_documents(filter_query)
        
        return {
            "success": True,
            "jobs": jobs,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to get scraped jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scraped jobs: {str(e)}")

@api_router.get("/jobs/stats")
async def get_jobs_stats():
    """Get job scraping statistics"""
    try:
        # Get total jobs
        total_jobs = await db.jobs_raw.count_documents({})
        
        # Get jobs by source
        source_pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        sources = await db.jobs_raw.aggregate(source_pipeline).to_list(length=None)
        
        # Get recent jobs (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_jobs = await db.jobs_raw.count_documents({
            'scraped_at': {'$gte': seven_days_ago.isoformat()}
        })
        
        # Get jobs by location
        location_pipeline = [
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        locations = await db.jobs_raw.aggregate(location_pipeline).to_list(length=None)
        
        # Get remote vs on-site
        remote_stats = await db.jobs_raw.aggregate([
            {"$group": {"_id": "$remote", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        return {
            "success": True,
            "total_jobs": total_jobs,
            "recent_jobs_7d": recent_jobs,
            "jobs_by_source": sources,
            "jobs_by_location": locations,
            "remote_stats": remote_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get job stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job stats: {str(e)}")

@api_router.get("/jobs/search")
async def search_jobs(
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100)
):
    """Search jobs using text search"""
    try:
        # Create text search
        search_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"company": {"$regex": query, "$options": "i"}},
                {"location": {"$regex": query, "$options": "i"}}
            ]
        }
        
        jobs = await db.jobs_raw.find(search_query).limit(limit).sort([('scraped_at', -1)]).to_list(length=limit)
        
        return {
            "success": True,
            "jobs": jobs,
            "query": query,
            "total": len(jobs)
        }
        
    except Exception as e:
        logger.error(f"Failed to search jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search jobs: {str(e)}")

@api_router.post("/scraping/scheduler/start")
async def start_scheduler():
    """Start the job scraping scheduler"""
    try:
        scheduler = get_scheduler()
        scheduler.start()
        
        return {
            "success": True,
            "message": "Job scraping scheduler started successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")

@api_router.post("/scraping/scheduler/stop")
async def stop_scheduler():
    """Stop the job scraping scheduler"""
    try:
        scheduler = get_scheduler()
        scheduler.stop()
        
        return {
            "success": True,
            "message": "Job scraping scheduler stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")

@api_router.post("/scraping/scheduler/restart")
async def restart_scheduler():
    """Restart the job scraping scheduler"""
    try:
        scheduler = get_scheduler()
        scheduler.restart()
        
        return {
            "success": True,
            "message": "Job scraping scheduler restarted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to restart scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart scheduler: {str(e)}")


# ================================================================================
# RESUME TAILORING ENDPOINTS - Phase 4: Advanced Resume Tailoring
# ================================================================================

class ResumeTailoringRequest(BaseModel):
    candidate_id: str
    resume_id: str
    job_id: str
    job_description: str
    strategy: TailoringStrategy = TailoringStrategy.JOB_SPECIFIC
    optimization_level: ATSOptimization = ATSOptimization.ADVANCED
    use_genetic_algorithm: bool = True

class ResumeVariantsRequest(BaseModel):
    candidate_id: str
    resume_id: str
    count: int = Field(default=5, ge=1, le=10)
    strategies: Optional[List[TailoringStrategy]] = None

@api_router.post("/resumes/{resume_id}/tailor")
async def tailor_resume_for_job(resume_id: str, request: ResumeTailoringRequest):
    """Tailor resume for specific job using advanced AI and genetic algorithms"""
    try:
        tailoring_service = get_resume_tailoring_service(db)
        
        tailored_resume = await tailoring_service.tailor_resume_for_job(
            candidate_id=request.candidate_id,
            resume_id=resume_id,
            job_id=request.job_id,
            job_description=request.job_description,
            strategy=request.strategy,
            optimization_level=request.optimization_level,
            use_genetic_algorithm=request.use_genetic_algorithm
        )
        
        return {
            "success": True,
            "message": "Resume tailored successfully",
            "resume_version": tailored_resume.dict(),
            "ats_score": tailored_resume.ats_score,
            "strategy": request.strategy.value,
            "optimization_level": request.optimization_level.value
        }
        
    except Exception as e:
        logger.error(f"Failed to tailor resume: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to tailor resume: {str(e)}")

@api_router.get("/candidates/{candidate_id}/resume-versions")
async def get_candidate_resume_versions(
    candidate_id: str,
    job_id: Optional[str] = Query(None, description="Filter by job ID")
):
    """Get all resume versions for a candidate"""
    try:
        tailoring_service = get_resume_tailoring_service(db)
        versions = await tailoring_service.get_resume_versions(candidate_id, job_id)
        
        return {
            "success": True,
            "versions": [version.dict() for version in versions],
            "total": len(versions)
        }
        
    except Exception as e:
        logger.error(f"Failed to get resume versions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get resume versions: {str(e)}")

@api_router.post("/resumes/{resume_id}/generate-variants")
async def generate_resume_variants(resume_id: str, request: ResumeVariantsRequest):
    """Generate multiple resume variants for A/B testing"""
    try:
        tailoring_service = get_resume_tailoring_service(db)
        
        variants = await tailoring_service.generate_resume_variants(
            candidate_id=request.candidate_id,
            resume_id=resume_id,
            count=request.count,
            strategies=request.strategies
        )
        
        return {
            "success": True,
            "message": f"Generated {len(variants)} resume variants",
            "variants": [variant.dict() for variant in variants],
            "strategies_used": [variant.tailoring_strategy.value for variant in variants]
        }
        
    except Exception as e:
        logger.error(f"Failed to generate resume variants: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate resume variants: {str(e)}")

@api_router.get("/resume-versions/{version_id}/ats-analysis")
async def get_ats_analysis(version_id: str):
    """Get ATS analysis for a resume version"""
    try:
        tailoring_service = get_resume_tailoring_service(db)
        analysis = await tailoring_service.get_ats_analysis(version_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="ATS analysis not found")
        
        return {
            "success": True,
            "analysis": analysis.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ATS analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ATS analysis: {str(e)}")

@api_router.get("/resume-versions/{version_id}/performance")
async def get_resume_performance(version_id: str):
    """Get performance metrics for a resume version"""
    try:
        tailoring_service = get_resume_tailoring_service(db)
        metrics = await tailoring_service.get_performance_metrics(version_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Performance metrics not found")
        
        return {
            "success": True,
            "metrics": metrics.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@api_router.post("/resume-versions/{version_id}/update-performance")
async def update_resume_performance(
    version_id: str,
    applications_sent: Optional[int] = None,
    responses_received: Optional[int] = None,
    interviews_scheduled: Optional[int] = None,
    offers_received: Optional[int] = None,
    rejections_received: Optional[int] = None
):
    """Update performance metrics for a resume version"""
    try:
        tailoring_service = get_resume_tailoring_service(db)
        
        await tailoring_service.update_performance_metrics(
            resume_version_id=version_id,
            applications_sent=applications_sent,
            responses_received=responses_received,
            interviews_scheduled=interviews_scheduled,
            offers_received=offers_received,
            rejections_received=rejections_received
        )
        
        return {
            "success": True,
            "message": "Performance metrics updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update performance metrics: {str(e)}")

@api_router.get("/candidates/{candidate_id}/resume-performance")
async def analyze_candidate_resume_performance(candidate_id: str):
    """Analyze overall resume performance for a candidate"""
    try:
        tailoring_service = get_resume_tailoring_service(db)
        analysis = await tailoring_service.analyze_resume_performance(candidate_id)
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze resume performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze resume performance: {str(e)}")

@api_router.post("/resumes/test-ats-scoring")
async def test_ats_scoring():
    """Test ATS scoring engine with sample data"""
    try:
        # Create ATS engine directly without full tailoring service
        from services.resume_tailoring import ATSScoreEngine
        ats_engine = ATSScoreEngine()
        
        sample_resume = """
John Doe
Software Engineer
john.doe@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years developing scalable web applications using Python, React, and AWS.

EXPERIENCE
Senior Software Engineer | Tech Company | 2020-2024
• Developed and maintained 15+ microservices handling 1M+ daily requests
• Led team of 4 engineers and improved deployment efficiency by 40%
• Implemented CI/CD pipelines reducing deployment time from 2 hours to 15 minutes

Software Engineer | StartupCorp | 2018-2020
• Built REST APIs serving 100K+ users using Python and Django
• Optimized database queries improving application performance by 60%

EDUCATION
Bachelor of Computer Science | University of Technology | 2018

SKILLS
Python, JavaScript, React, AWS, Docker, Kubernetes, SQL, MongoDB
"""
        
        sample_job = """
We are looking for a Senior Python Developer to join our team.
Requirements: 5+ years Python experience, React, AWS, Docker, Kubernetes
Strong experience with microservices and API development
"""
        
        analysis = ats_engine.calculate_ats_score(sample_resume, sample_job)
        
        return {
            "success": True,
            "message": "ATS scoring test completed",
            "sample_resume_score": analysis.overall_score,
            "breakdown": {
                "keyword_score": analysis.keyword_score,
                "format_score": analysis.format_score,
                "section_score": analysis.section_score,
                "experience_score": analysis.experience_score,
                "education_score": analysis.education_score,
                "skills_score": analysis.skills_score,
                "contact_score": analysis.contact_score
            },
            "recommendations": analysis.recommendations,
            "missing_keywords": analysis.missing_keywords
        }
        
    except Exception as e:
        logger.error(f"Failed to test ATS scoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test ATS scoring: {str(e)}")

@api_router.get("/resume-tailoring/stats")
async def get_resume_tailoring_stats():
    """Get resume tailoring system statistics"""
    try:
        # Get counts from different collections
        total_versions = await db.resume_versions.count_documents({})
        total_genetic_pools = await db.resume_genetic_pools.count_documents({})
        total_ats_analyses = await db.ats_analyses.count_documents({})
        total_performance_metrics = await db.resume_performance_metrics.count_documents({})
        
        # Get recent activity
        recent_versions = await db.resume_versions.find({}).sort([('created_at', -1)]).limit(5).to_list(length=5)
        
        # Calculate average scores
        pipeline = [
            {"$match": {"ats_score": {"$exists": True, "$ne": None}}},
            {"$group": {
                "_id": None,
                "avg_ats_score": {"$avg": "$ats_score"},
                "max_ats_score": {"$max": "$ats_score"},
                "min_ats_score": {"$min": "$ats_score"}
            }}
        ]
        
        score_stats = await db.resume_versions.aggregate(pipeline).to_list(length=1)
        avg_scores = score_stats[0] if score_stats else {
            "avg_ats_score": 0,
            "max_ats_score": 0,
            "min_ats_score": 0
        }
        
        return {
            "success": True,
            "stats": {
                "total_resume_versions": total_versions,
                "total_genetic_pools": total_genetic_pools,
                "total_ats_analyses": total_ats_analyses,
                "total_performance_metrics": total_performance_metrics,
                "average_ats_score": round(avg_scores["avg_ats_score"], 2),
                "max_ats_score": round(avg_scores["max_ats_score"], 2),
                "min_ats_score": round(avg_scores["min_ats_score"], 2)
            },
            "recent_activity": [
                {
                    "version_name": version.get("version_name"),
                    "strategy": version.get("tailoring_strategy"),
                    "ats_score": version.get("ats_score"),
                    "created_at": version.get("created_at")
                }
                for version in recent_versions
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get resume tailoring stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get resume tailoring stats: {str(e)}")


# ================================================================================
# END RESUME TAILORING ENDPOINTS
# ================================================================================


# ================================================================================
# COVER LETTER GENERATION ENDPOINTS (PHASE 5)
# ================================================================================

from services.cover_letter import get_cover_letter_service
from models import OutreachTone, CoverLetterTemplate, CompanyResearch, CoverLetterPerformance

class CoverLetterGenerationRequest(BaseModel):
    candidate_id: str
    job_id: str
    job_description: str
    company_name: str
    company_domain: Optional[str] = None
    position_title: Optional[str] = ""
    hiring_manager: Optional[str] = ""
    tone: OutreachTone = OutreachTone.FORMAL
    include_research: bool = True

class MultipleCoverLetterRequest(BaseModel):
    candidate_id: str
    job_id: str
    job_description: str
    company_name: str
    company_domain: Optional[str] = None
    position_title: Optional[str] = ""
    versions_count: int = 3

@api_router.post("/cover-letters/generate")
async def generate_cover_letter(request: CoverLetterGenerationRequest):
    """Generate a personalized cover letter with company research and AI optimization"""
    try:
        cover_letter_service = get_cover_letter_service(db)
        
        result = await cover_letter_service.generate_cover_letter(
            candidate_id=request.candidate_id,
            job_id=request.job_id,
            job_description=request.job_description,
            company_name=request.company_name,
            company_domain=request.company_domain,
            tone=request.tone,
            position_title=request.position_title,
            hiring_manager=request.hiring_manager,
            include_research=request.include_research
        )
        
        return {
            "success": True,
            "message": "Cover letter generated successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")

@api_router.post("/cover-letters/generate-multiple")
async def generate_multiple_cover_letters(request: MultipleCoverLetterRequest):
    """Generate multiple cover letter versions for A/B testing"""
    try:
        cover_letter_service = get_cover_letter_service(db)
        
        versions = await cover_letter_service.generate_multiple_versions(
            candidate_id=request.candidate_id,
            job_id=request.job_id,
            job_description=request.job_description,
            company_name=request.company_name,
            company_domain=request.company_domain,
            position_title=request.position_title,
            versions_count=request.versions_count
        )
        
        return {
            "success": True,
            "message": f"Generated {len(versions)} cover letter versions",
            "data": {
                "versions": versions,
                "total_count": len(versions)
            }
        }
        
    except Exception as e:
        logger.error(f"Multiple cover letter generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Multiple cover letter generation failed: {str(e)}")

@api_router.get("/candidates/{candidate_id}/cover-letters")
async def get_candidate_cover_letters(candidate_id: str, limit: int = 20, skip: int = 0):
    """Get all cover letters for a specific candidate"""
    try:
        cover_letters = await db.cover_letters.find(
            {"candidate_id": candidate_id}
        ).sort([('created_at', -1)]).skip(skip).limit(limit).to_list(length=limit)
        
        total = await db.cover_letters.count_documents({"candidate_id": candidate_id})
        
        return {
            "success": True,
            "data": {
                "cover_letters": cover_letters,
                "total": total,
                "limit": limit,
                "skip": skip
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get candidate cover letters: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get candidate cover letters: {str(e)}")

@api_router.get("/cover-letters/{cover_letter_id}")
async def get_cover_letter(cover_letter_id: str):
    """Get a specific cover letter by ID"""
    try:
        cover_letter = await db.cover_letters.find_one({"id": cover_letter_id})
        if not cover_letter:
            raise HTTPException(status_code=404, detail="Cover letter not found")
        
        return {
            "success": True,
            "data": cover_letter
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cover letter: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cover letter: {str(e)}")

@api_router.get("/cover-letters/{cover_letter_id}/performance")
async def get_cover_letter_performance(cover_letter_id: str):
    """Get performance analytics for a specific cover letter"""
    try:
        cover_letter_service = get_cover_letter_service(db)
        performance = await cover_letter_service.get_performance_analytics(cover_letter_id)
        
        return {
            "success": True,
            "data": performance
        }
        
    except Exception as e:
        logger.error(f"Failed to get cover letter performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cover letter performance: {str(e)}")

@api_router.delete("/cover-letters/{cover_letter_id}")
async def delete_cover_letter(cover_letter_id: str):
    """Delete a cover letter"""
    try:
        result = await db.cover_letters.delete_one({"id": cover_letter_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Cover letter not found")
        
        return {
            "success": True,
            "message": "Cover letter deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete cover letter: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete cover letter: {str(e)}")

@api_router.get("/cover-letters/{cover_letter_id}/download")
async def download_cover_letter_pdf(cover_letter_id: str):
    """Download cover letter as PDF"""
    try:
        cover_letter = await db.cover_letters.find_one({"id": cover_letter_id})
        if not cover_letter:
            raise HTTPException(status_code=404, detail="Cover letter not found")
        
        pdf_url = cover_letter.get('pdf_url')
        if not pdf_url or not os.path.exists(pdf_url):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        from fastapi.responses import FileResponse
        import os
        return FileResponse(
            path=pdf_url,
            media_type='application/pdf',
            filename=f"cover_letter_{cover_letter_id}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download cover letter PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download cover letter PDF: {str(e)}")

@api_router.post("/cover-letters/{cover_letter_id}/track-usage")
async def track_cover_letter_usage(cover_letter_id: str):
    """Track usage of a cover letter (increment usage count)"""
    try:
        result = await db.cover_letters.update_one(
            {"id": cover_letter_id},
            {
                "$inc": {"used_count": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Cover letter not found")
        
        return {
            "success": True,
            "message": "Cover letter usage tracked"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to track cover letter usage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to track cover letter usage: {str(e)}")

@api_router.get("/cover-letters/stats/overview")
async def get_cover_letter_stats():
    """Get comprehensive cover letter statistics"""
    try:
        # Basic counts
        total_cover_letters = await db.cover_letters.count_documents({})
        total_applications = await db.applications.count_documents({
            "cover_letter_id": {"$exists": True, "$ne": None}
        })
        
        # Tone distribution
        tone_pipeline = [
            {"$group": {"_id": "$tone", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        tone_distribution = await db.cover_letters.aggregate(tone_pipeline).to_list(length=10)
        
        # Performance metrics
        performance_pipeline = [
            {"$match": {"success_rate": {"$exists": True, "$ne": None}}},
            {"$group": {
                "_id": None,
                "avg_success_rate": {"$avg": "$success_rate"},
                "avg_usage_count": {"$avg": "$used_count"},
                "total_usage": {"$sum": "$used_count"}
            }}
        ]
        performance_stats = await db.cover_letters.aggregate(performance_pipeline).to_list(length=1)
        performance = performance_stats[0] if performance_stats else {
            "avg_success_rate": 0,
            "avg_usage_count": 0,
            "total_usage": 0
        }
        
        # Recent activity
        recent_cover_letters = await db.cover_letters.find({}).sort([
            ('created_at', -1)
        ]).limit(5).to_list(length=5)
        
        return {
            "success": True,
            "data": {
                "overview": {
                    "total_cover_letters": total_cover_letters,
                    "total_applications": total_applications,
                    "avg_success_rate": round(performance["avg_success_rate"], 2),
                    "avg_usage_count": round(performance["avg_usage_count"], 2),
                    "total_usage": performance["total_usage"]
                },
                "tone_distribution": [
                    {"tone": item["_id"], "count": item["count"]}
                    for item in tone_distribution
                ],
                "recent_activity": [
                    {
                        "id": letter.get("id"),
                        "candidate_id": letter.get("candidate_id"),
                        "tone": letter.get("tone"),
                        "created_at": letter.get("created_at"),
                        "usage_count": letter.get("used_count", 0)
                    }
                    for letter in recent_cover_letters
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get cover letter stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cover letter stats: {str(e)}")

@api_router.post("/cover-letters/test-generation")
async def test_cover_letter_generation():
    """Test cover letter generation with sample data"""
    try:
        # Create a test candidate if needed
        test_candidate = {
            "id": "test_candidate_cover_letter",
            "full_name": "Alex Johnson",
            "email": "alex.johnson@example.com",
            "phone": "+1-555-0199",
            "location": "Seattle, WA",
            "target_roles": ["Senior Software Engineer", "Full Stack Developer"],
            "skills": ["Python", "JavaScript", "React", "AWS", "Docker", "Kubernetes"],
            "years_experience": 6,
            "created_at": datetime.utcnow()
        }
        
        # Upsert test candidate
        await db.candidates.update_one(
            {"id": test_candidate["id"]},
            {"$set": test_candidate},
            upsert=True
        )
        
        cover_letter_service = get_cover_letter_service(db)
        
        sample_job_description = """
        We are seeking a Senior Python Developer to join our innovative team at TechCorp.
        
        Requirements:
        - 5+ years of experience with Python development
        - Strong experience with React and JavaScript
        - Experience with AWS cloud services
        - Docker and Kubernetes experience preferred
        - Bachelor's degree in Computer Science or related field
        - Excellent communication and teamwork skills
        
        We offer competitive salary, flexible work arrangements, and opportunities for growth.
        """
        
        result = await cover_letter_service.generate_cover_letter(
            candidate_id=test_candidate["id"],
            job_id="test_job_123",
            job_description=sample_job_description,
            company_name="TechCorp",
            company_domain="techcorp.com",
            tone=OutreachTone.WARM,
            position_title="Senior Python Developer",
            hiring_manager="Sarah Martinez"
        )
        
        return {
            "success": True,
            "message": "Cover letter generation test completed successfully",
            "test_data": {
                "candidate": test_candidate,
                "job_description": sample_job_description,
                "result": result
            }
        }
        
    except Exception as e:
        logger.error(f"Cover letter generation test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cover letter generation test failed: {str(e)}")

# ================================================================================
# END COVER LETTER GENERATION ENDPOINTS
# ================================================================================

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Start job scraping scheduler
        scheduler = get_scheduler()
        scheduler.start()
        logger.info("Job scraping scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Cleanup on shutdown"""
    try:
        # Stop scheduler
        scheduler = get_scheduler()
        scheduler.close()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
    
    # Close database connection
    client.close()
    logger.info("Database connection closed")

# Global application submission manager
application_submission_manager = ApplicationSubmissionManager(ApplicationSubmissionConfig())

#====================================================================
# PHASE 6: AUTONOMOUS APPLICATION SUBMISSION API ENDPOINTS
#====================================================================

class ApplicationSubmissionRequest(BaseModel):
    """Request model for application submission"""
    candidate_id: str
    job_id: str
    resume_version_id: Optional[str] = None
    cover_letter_id: Optional[str] = None
    method: ApplicationMethod = ApplicationMethod.DIRECT_FORM
    
class BulkApplicationSubmissionRequest(BaseModel):
    """Request model for bulk application submission"""
    candidate_id: str
    job_ids: List[str]
    resume_version_id: Optional[str] = None
    cover_letter_id: Optional[str] = None
    method: ApplicationMethod = ApplicationMethod.DIRECT_FORM

@api_router.post("/applications/submit")
async def submit_single_application(request: ApplicationSubmissionRequest):
    """Submit a single job application"""
    try:
        # Get candidate
        candidate_doc = await db.candidates.find_one({"id": request.candidate_id})
        if not candidate_doc:
            raise HTTPException(status_code=404, detail="Candidate not found")
        candidate = Candidate(**candidate_doc)
        
        # Get job
        job_doc = await db.jobs_raw.find_one({"id": request.job_id})
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        job = JobRaw(**job_doc)
        
        # Get resume version or use latest
        if request.resume_version_id:
            resume_doc = await db.resume_versions.find_one({"id": request.resume_version_id})
        else:
            resume_doc = await db.resume_versions.find_one(
                {"candidate_id": request.candidate_id}, 
                sort=[("created_at", -1)]
            )
        
        if not resume_doc:
            raise HTTPException(status_code=404, detail="Resume version not found")
        resume_version = ResumeVersion(**resume_doc)
        
        # Get cover letter if specified
        cover_letter = None
        if request.cover_letter_id:
            cover_letter_doc = await db.cover_letters.find_one({"id": request.cover_letter_id})
            if cover_letter_doc:
                cover_letter = CoverLetter(**cover_letter_doc)
        
        # Queue application for submission
        await application_submission_manager.queue_application(
            candidate=candidate,
            job=job,
            resume_version=resume_version,
            cover_letter=cover_letter,
            method=request.method
        )
        
        return {
            "success": True,
            "message": "Application queued for submission",
            "candidate_id": request.candidate_id,
            "job_id": request.job_id,
            "method": request.method.value,
            "queued_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error submitting application: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Application submission failed: {str(e)}")

@api_router.post("/applications/submit-bulk")
async def submit_bulk_applications(request: BulkApplicationSubmissionRequest):
    """Submit multiple job applications for a candidate"""
    try:
        # Get candidate
        candidate_doc = await db.candidates.find_one({"id": request.candidate_id})
        if not candidate_doc:
            raise HTTPException(status_code=404, detail="Candidate not found")
        candidate = Candidate(**candidate_doc)
        
        # Get resume version or use latest
        if request.resume_version_id:
            resume_doc = await db.resume_versions.find_one({"id": request.resume_version_id})
        else:
            resume_doc = await db.resume_versions.find_one(
                {"candidate_id": request.candidate_id}, 
                sort=[("created_at", -1)]
            )
        
        if not resume_doc:
            raise HTTPException(status_code=404, detail="Resume version not found")
        resume_version = ResumeVersion(**resume_doc)
        
        # Get cover letter if specified
        cover_letter = None
        if request.cover_letter_id:
            cover_letter_doc = await db.cover_letters.find_one({"id": request.cover_letter_id})
            if cover_letter_doc:
                cover_letter = CoverLetter(**cover_letter_doc)
        
        # Queue applications for all jobs
        queued_applications = []
        for job_id in request.job_ids:
            job_doc = await db.jobs_raw.find_one({"id": job_id})
            if job_doc:
                job = JobRaw(**job_doc)
                
                await application_submission_manager.queue_application(
                    candidate=candidate,
                    job=job,
                    resume_version=resume_version,
                    cover_letter=cover_letter,
                    method=request.method
                )
                
                queued_applications.append({
                    "job_id": job_id,
                    "company": job.company,
                    "position": job.title,
                    "method": request.method.value
                })
        
        return {
            "success": True,
            "message": f"Queued {len(queued_applications)} applications for submission",
            "candidate_id": request.candidate_id,
            "queued_applications": queued_applications,
            "queued_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error submitting bulk applications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk application submission failed: {str(e)}")

@api_router.get("/applications/status")
async def get_application_status():
    """Get application submission status and statistics"""
    try:
        stats = await application_submission_manager.get_submission_stats()
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting application status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get application status: {str(e)}")

@api_router.get("/applications/{application_id}")
async def get_application_details(application_id: str):
    """Get details of a specific application"""
    try:
        application_doc = await db.applications.find_one({"id": application_id})
        if not application_doc:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return {
            "success": True,
            "application": application_doc,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting application details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get application details: {str(e)}")

@api_router.get("/applications/candidate/{candidate_id}")
async def get_candidate_applications(candidate_id: str, 
                                   status: Optional[str] = None,
                                   limit: int = 50, 
                                   offset: int = 0):
    """Get applications for a specific candidate"""
    try:
        # Build query
        query = {"candidate_id": candidate_id}
        if status:
            query["status"] = status
        
        # Get applications
        applications_cursor = db.applications.find(query).skip(offset).limit(limit).sort("created_at", -1)
        applications = await applications_cursor.to_list(length=limit)
        
        # Get total count
        total_count = await db.applications.count_documents(query)
        
        return {
            "success": True,
            "applications": applications,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting candidate applications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get candidate applications: {str(e)}")

@api_router.post("/applications/auto-submit")
async def auto_submit_applications():
    """Auto-submit applications for all candidates with matched jobs"""
    try:
        # Get all candidates
        candidates_cursor = db.candidates.find({"status": "active"})
        candidates = await candidates_cursor.to_list(length=None)
        
        total_queued = 0
        
        for candidate_doc in candidates:
            candidate = Candidate(**candidate_doc)
            
            # Get matched jobs for this candidate
            matches_cursor = db.job_matches.find({
                "candidate_id": candidate.id,
                "priority": {"$in": ["high", "medium"]},
                "applied": {"$ne": True}
            }).sort("match_score", -1).limit(10)
            
            matches = await matches_cursor.to_list(length=10)
            
            for match in matches:
                # Get job details
                job_doc = await db.jobs_raw.find_one({"id": match["job_id"]})
                if not job_doc:
                    continue
                
                job = JobRaw(**job_doc)
                
                # Get latest resume version
                resume_doc = await db.resume_versions.find_one(
                    {"candidate_id": candidate.id}, 
                    sort=[("created_at", -1)]
                )
                
                if not resume_doc:
                    continue
                
                resume_version = ResumeVersion(**resume_doc)
                
                # Get latest cover letter
                cover_letter = None
                cover_letter_doc = await db.cover_letters.find_one(
                    {"candidate_id": candidate.id}, 
                    sort=[("created_at", -1)]
                )
                
                if cover_letter_doc:
                    cover_letter = CoverLetter(**cover_letter_doc)
                
                # Determine application method based on job board
                method = ApplicationMethod.DIRECT_FORM
                if job.source == "indeed":
                    method = ApplicationMethod.INDEED_QUICK
                elif job.apply_url and job.apply_url.startswith("mailto:"):
                    method = ApplicationMethod.EMAIL_APPLY
                
                # Queue application
                await application_submission_manager.queue_application(
                    candidate=candidate,
                    job=job,
                    resume_version=resume_version,
                    cover_letter=cover_letter,
                    method=method
                )
                
                # Mark as applied in job_matches
                await db.job_matches.update_one(
                    {"id": match["id"]},
                    {"$set": {"applied": True, "applied_at": datetime.utcnow()}}
                )
                
                total_queued += 1
        
        return {
            "success": True,
            "message": f"Auto-queued {total_queued} applications for submission",
            "total_queued": total_queued,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error auto-submitting applications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Auto-submission failed: {str(e)}")

@api_router.get("/applications/analytics")
async def get_application_analytics():
    """Get comprehensive application analytics"""
    try:
        # Get overall statistics
        total_applications = await db.applications.count_documents({})
        successful_applications = await db.applications.count_documents({"status": "applied"})
        pending_applications = await db.applications.count_documents({"status": "pending"})
        failed_applications = await db.applications.count_documents({"status": "failed"})
        
        # Get applications by method
        pipeline_method = [
            {"$group": {"_id": "$job_board", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        applications_by_method = await db.applications.aggregate(pipeline_method).to_list(length=None)
        
        # Get applications by day (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        pipeline_daily = [
            {"$match": {"created_at": {"$gte": thirty_days_ago}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        daily_applications = await db.applications.aggregate(pipeline_daily).to_list(length=None)
        
        # Get response rates
        applications_with_response = await db.applications.count_documents({"response_at": {"$ne": None}})
        response_rate = (applications_with_response / total_applications * 100) if total_applications > 0 else 0
        
        # Get top companies applied to
        pipeline_companies = [
            {"$group": {"_id": "$company", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_companies = await db.applications.aggregate(pipeline_companies).to_list(length=10)
        
        return {
            "success": True,
            "analytics": {
                "overall_stats": {
                    "total_applications": total_applications,
                    "successful_applications": successful_applications,
                    "pending_applications": pending_applications,
                    "failed_applications": failed_applications,
                    "success_rate": (successful_applications / total_applications * 100) if total_applications > 0 else 0,
                    "response_rate": response_rate
                },
                "applications_by_method": applications_by_method,
                "daily_applications": daily_applications,
                "top_companies": top_companies
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting application analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get application analytics: {str(e)}")

@api_router.post("/applications/test-submission")
async def test_application_submission():
    """Test application submission system with mock data"""
    try:
        # Create test candidate
        test_candidate = Candidate(
            id=str(uuid.uuid4()),
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="555-123-4567",
            location="San Francisco, CA",
            status="active"
        )
        
        # Create test job
        test_job = JobRaw(
            id=str(uuid.uuid4()),
            title="Software Engineer",
            company="Tech Corp",
            location="San Francisco, CA",
            description="We are looking for a skilled Software Engineer...",
            requirements="Bachelor's degree in Computer Science...",
            apply_url="https://example.com/apply",
            source="indeed",
            scraped_at=datetime.utcnow()
        )
        
        # Create test resume version
        test_resume_version = ResumeVersion(
            id=str(uuid.uuid4()),
            candidate_id=test_candidate.id,
            resume_id=str(uuid.uuid4()),
            version_name="test_version",
            content=b"Test resume content",
            tailoring_strategy="job_specific",
            ats_score=85.5,
            created_at=datetime.utcnow()
        )
        
        # Create test cover letter
        test_cover_letter = CoverLetter(
            id=str(uuid.uuid4()),
            candidate_id=test_candidate.id,
            job_id=test_job.id,
            tone="professional",
            content="Dear Hiring Manager, I am writing to express my interest...",
            ats_keywords=["python", "javascript", "software", "engineering"],
            created_at=datetime.utcnow()
        )
        
        # Test application submission
        result = await application_submission_manager.engine.submit_application(
            candidate=test_candidate,
            job=test_job,
            resume_version=test_resume_version,
            cover_letter=test_cover_letter,
            method=ApplicationMethod.DIRECT_FORM
        )
        
        return {
            "success": True,
            "message": "Application submission test completed",
            "test_result": {
                "application_id": result.application_id,
                "success": result.success,
                "method": result.method.value,
                "submission_time": result.submission_time.isoformat(),
                "error_message": result.error_message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error testing application submission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Application submission test failed: {str(e)}")

# Start the submission queue processor
import asyncio
asyncio.create_task(application_submission_manager.process_submission_queue())


# ================================================================================
# PHASE 7: RECRUITER OUTREACH ENGINE API ENDPOINTS
# ================================================================================

# Temporarily disabled due to import issues
# from services.outreach_manager import OutreachCampaignManager
# Temporarily disabled due to import issues
# from services.recruiter_research import RecruiterResearchService
# Temporarily disabled due to import issues
# from services.linkedin_automation import LinkedInAutomation

# Initialize outreach services
# Temporarily disabled due to import issues
# outreach_manager = OutreachCampaignManager(client)
# Temporarily disabled due to import issues
# recruiter_research_service = RecruiterResearchService(client)

# Request models for outreach
class RecruiterCreateRequest(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    linkedin_url: Optional[str] = None
    linkedin_id: Optional[str] = None
    company: Optional[str] = None
    company_domain: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    recruiter_type: RecruiterType = RecruiterType.INTERNAL
    specializations: List[str] = []
    seniority_levels: List[str] = []

class CampaignCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    target_roles: List[str] = []
    target_companies: List[str] = []
    target_locations: List[str] = []
    channels: List[OutreachChannel] = [OutreachChannel.LINKEDIN]
    daily_limit: int = 10
    delay_between_messages: int = 300
    follow_up_delay: int = 86400
    max_follow_ups: int = 3
    personalization_level: str = "medium"
    tone: OutreachTone = OutreachTone.WARM
    auto_follow_up: bool = True

class MessageCreateRequest(BaseModel):
    campaign_id: str
    recruiter_id: str
    channel: OutreachChannel
    subject: Optional[str] = None
    content: str
    personalization_data: Dict[str, Any] = {}
    tone: OutreachTone
    scheduled_for: Optional[datetime] = None

# LinkedIn OAuth endpoints
@api_router.get("/outreach/linkedin/auth-url/{candidate_id}")
async def get_linkedin_auth_url(candidate_id: str):
    """Get LinkedIn OAuth URL for candidate authentication"""
    try:
        # Check if candidate exists
        candidate = await db.candidates.find_one({"id": candidate_id})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        async with LinkedInAutomation(client) as linkedin:
            auth_url = linkedin.get_oauth_url(candidate_id)
        
        return {
            "success": True,
            "auth_url": auth_url,
            "candidate_id": candidate_id
        }
        
    except Exception as e:
        logger.error(f"Error getting LinkedIn auth URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get LinkedIn auth URL: {str(e)}")

@api_router.post("/outreach/linkedin/callback")
async def linkedin_oauth_callback(code: str, state: str):
    """Handle LinkedIn OAuth callback"""
    try:
        candidate_id = state
        
        async with LinkedInAutomation(client) as linkedin:
            tokens = await linkedin.exchange_code_for_tokens(code, candidate_id)
        
        if tokens:
            return {
                "success": True,
                "message": "LinkedIn authentication successful",
                "candidate_id": candidate_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to authenticate with LinkedIn")
            
    except Exception as e:
        logger.error(f"Error in LinkedIn OAuth callback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LinkedIn authentication failed: {str(e)}")

# Recruiter management endpoints
@api_router.post("/outreach/recruiters")
async def create_recruiter(request: RecruiterCreateRequest):
    """Create a new recruiter"""
    try:
        async with RecruiterResearchService(client) as research_service:
            recruiter_id = await research_service.save_recruiter(request.dict())
        
        return {
            "success": True,
            "message": "Recruiter created successfully",
            "recruiter_id": recruiter_id
        }
        
    except Exception as e:
        logger.error(f"Error creating recruiter: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create recruiter: {str(e)}")

@api_router.get("/outreach/recruiters")
async def get_recruiters(
    company: Optional[str] = None,
    location: Optional[str] = None,
    specialization: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
):
    """Get recruiters with optional filters"""
    try:
        # Build query
        query = {"is_active": True}
        if company:
            query["company"] = {"$regex": company, "$options": "i"}
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
        if specialization:
            query["specializations"] = {"$in": [specialization]}
        
        # Get recruiters
        recruiters = await db.recruiters.find(query).skip(skip).limit(limit).to_list(length=limit)
        total = await db.recruiters.count_documents(query)
        
        return {
            "success": True,
            "recruiters": recruiters,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"Error getting recruiters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recruiters: {str(e)}")

@api_router.get("/outreach/recruiters/{recruiter_id}")
async def get_recruiter(recruiter_id: str):
    """Get recruiter details"""
    try:
        recruiter = await db.recruiters.find_one({"id": recruiter_id})
        if not recruiter:
            raise HTTPException(status_code=404, detail="Recruiter not found")
        
        return {
            "success": True,
            "recruiter": recruiter
        }
        
    except Exception as e:
        logger.error(f"Error getting recruiter: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recruiter: {str(e)}")

@api_router.post("/outreach/recruiters/{recruiter_id}/research")
async def research_recruiter(recruiter_id: str):
    """Perform comprehensive research on a recruiter"""
    try:
        async with RecruiterResearchService(client) as research_service:
            research_data = await research_service.research_recruiter(recruiter_id)
        
        return {
            "success": True,
            "message": "Recruiter research completed",
            "research_data": research_data
        }
        
    except Exception as e:
        logger.error(f"Error researching recruiter: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to research recruiter: {str(e)}")

@api_router.post("/outreach/recruiters/search")
async def search_recruiters(
    company_names: List[str],
    limit_per_company: int = 10
):
    """Search for recruiters across multiple companies"""
    try:
        async with RecruiterResearchService(client) as research_service:
            recruiters = await research_service.bulk_research_recruiters(
                company_names=company_names,
                limit_per_company=limit_per_company
            )
        
        return {
            "success": True,
            "message": f"Found {len(recruiters)} recruiters",
            "recruiters": recruiters,
            "companies_searched": company_names
        }
        
    except Exception as e:
        logger.error(f"Error searching recruiters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search recruiters: {str(e)}")

# Campaign management endpoints
@api_router.post("/outreach/campaigns")
async def create_campaign(candidate_id: str, request: CampaignCreateRequest):
    """Create a new outreach campaign"""
    try:
        # Check if candidate exists
        candidate = await db.candidates.find_one({"id": candidate_id})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        campaign_id = await outreach_manager.create_campaign(
            candidate_id=candidate_id,
            campaign_data=request.dict()
        )
        
        return {
            "success": True,
            "message": "Campaign created successfully",
            "campaign_id": campaign_id
        }
        
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")

@api_router.get("/outreach/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get campaign details"""
    try:
        campaign = await db.campaigns.find_one({"id": campaign_id})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return {
            "success": True,
            "campaign": campaign
        }
        
    except Exception as e:
        logger.error(f"Error getting campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get campaign: {str(e)}")

@api_router.get("/outreach/candidates/{candidate_id}/campaigns")
async def get_candidate_campaigns(candidate_id: str, limit: int = 20, skip: int = 0):
    """Get campaigns for a candidate"""
    try:
        campaigns = await db.campaigns.find(
            {"candidate_id": candidate_id}
        ).skip(skip).limit(limit).sort("created_at", -1).to_list(length=limit)
        
        total = await db.campaigns.count_documents({"candidate_id": candidate_id})
        
        return {
            "success": True,
            "campaigns": campaigns,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"Error getting candidate campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get candidate campaigns: {str(e)}")

@api_router.post("/outreach/campaigns/{campaign_id}/start")
async def start_campaign(campaign_id: str):
    """Start an outreach campaign"""
    try:
        success = await outreach_manager.start_campaign(campaign_id)
        
        if success:
            return {
                "success": True,
                "message": "Campaign started successfully",
                "campaign_id": campaign_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to start campaign")
            
    except Exception as e:
        logger.error(f"Error starting campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start campaign: {str(e)}")

@api_router.post("/outreach/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """Pause an active campaign"""
    try:
        success = await outreach_manager.pause_campaign(campaign_id)
        
        if success:
            return {
                "success": True,
                "message": "Campaign paused successfully",
                "campaign_id": campaign_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to pause campaign")
            
    except Exception as e:
        logger.error(f"Error pausing campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to pause campaign: {str(e)}")

@api_router.post("/outreach/campaigns/{campaign_id}/resume")
async def resume_campaign(campaign_id: str):
    """Resume a paused campaign"""
    try:
        success = await outreach_manager.resume_campaign(campaign_id)
        
        if success:
            return {
                "success": True,
                "message": "Campaign resumed successfully",
                "campaign_id": campaign_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to resume campaign")
            
    except Exception as e:
        logger.error(f"Error resuming campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resume campaign: {str(e)}")

@api_router.post("/outreach/campaigns/{campaign_id}/stop")
async def stop_campaign(campaign_id: str):
    """Stop a campaign"""
    try:
        success = await outreach_manager.stop_campaign(campaign_id)
        
        if success:
            return {
                "success": True,
                "message": "Campaign stopped successfully",
                "campaign_id": campaign_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to stop campaign")
            
    except Exception as e:
        logger.error(f"Error stopping campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop campaign: {str(e)}")

@api_router.get("/outreach/campaigns/{campaign_id}/analytics")
async def get_campaign_analytics(campaign_id: str):
    """Get campaign analytics"""
    try:
        analytics = await outreach_manager.get_campaign_analytics(campaign_id)
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting campaign analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get campaign analytics: {str(e)}")

# Message management endpoints
@api_router.post("/outreach/messages")
async def create_message(request: MessageCreateRequest):
    """Create a new outreach message"""
    try:
        message = OutreachMessage(**request.dict())
        await db.messages.insert_one(message.dict())
        
        return {
            "success": True,
            "message": "Outreach message created successfully",
            "message_id": message.id
        }
        
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")

@api_router.get("/outreach/campaigns/{campaign_id}/messages")
async def get_campaign_messages(
    campaign_id: str,
    status: Optional[OutreachStatus] = None,
    limit: int = 50,
    skip: int = 0
):
    """Get messages for a campaign"""
    try:
        # Build query
        query = {"campaign_id": campaign_id}
        if status:
            query["status"] = status.value
        
        messages = await db.messages.find(query).skip(skip).limit(limit).sort("created_at", -1).to_list(length=limit)
        total = await db.messages.count_documents(query)
        
        return {
            "success": True,
            "messages": messages,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"Error getting campaign messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get campaign messages: {str(e)}")

@api_router.get("/outreach/messages/{message_id}")
async def get_message(message_id: str):
    """Get message details"""
    try:
        message = await db.messages.find_one({"id": message_id})
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return {
            "success": True,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Error getting message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get message: {str(e)}")

# Processing endpoints
@api_router.post("/outreach/process-scheduled-messages")
async def process_scheduled_messages():
    """Process scheduled outreach messages"""
    try:
        await outreach_manager.process_scheduled_messages()
        
        return {
            "success": True,
            "message": "Scheduled messages processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing scheduled messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process scheduled messages: {str(e)}")

@api_router.post("/outreach/process-follow-ups")
async def process_follow_ups():
    """Process follow-up messages for campaigns"""
    try:
        await outreach_manager.process_follow_ups()
        
        return {
            "success": True,
            "message": "Follow-ups processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing follow-ups: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process follow-ups: {str(e)}")

# Statistics and analytics
@api_router.get("/outreach/stats")
async def get_outreach_stats():
    """Get comprehensive outreach statistics"""
    try:
        # Get recruiter statistics
        async with RecruiterResearchService(client) as research_service:
            recruiter_stats = await research_service.get_recruiter_statistics()
        
        # Get campaign statistics
        total_campaigns = await db.campaigns.count_documents({})
        active_campaigns = await db.campaigns.count_documents({"status": CampaignStatus.ACTIVE.value})
        
        # Get message statistics
        total_messages = await db.messages.count_documents({})
        sent_messages = await db.messages.count_documents({"status": OutreachStatus.SENT.value})
        replied_messages = await db.messages.count_documents({"replied_at": {"$ne": None}})
        
        # Calculate rates
        response_rate = (replied_messages / sent_messages * 100) if sent_messages > 0 else 0
        
        return {
            "success": True,
            "statistics": {
                "recruiters": recruiter_stats,
                "campaigns": {
                    "total_campaigns": total_campaigns,
                    "active_campaigns": active_campaigns
                },
                "messages": {
                    "total_messages": total_messages,
                    "sent_messages": sent_messages,
                    "replied_messages": replied_messages,
                    "response_rate": round(response_rate, 2)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting outreach stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get outreach stats: {str(e)}")

@api_router.post("/outreach/test")
async def test_outreach_system():
    """Test the outreach system with sample data"""
    try:
        # Create test candidate
        test_candidate = {
            "id": "test_candidate_outreach",
            "full_name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "+1-555-0198",
            "location": "New York, NY",
            "target_roles": ["Software Engineer", "Senior Developer"],
            "target_companies": ["TechCorp", "InnovateCo"],
            "skills": ["Python", "React", "AWS", "Machine Learning"],
            "years_experience": 5,
            "created_at": datetime.utcnow()
        }
        
        # Upsert test candidate
        await db.candidates.update_one(
            {"id": test_candidate["id"]},
            {"$set": test_candidate},
            upsert=True
        )
        
        # Create test recruiter
        test_recruiter = {
            "id": "test_recruiter_001",
            "name": "Sarah Johnson",
            "email": "sarah.johnson@techcorp.com",
            "linkedin_url": "https://linkedin.com/in/sarahjohnson",
            "company": "TechCorp",
            "title": "Senior Technical Recruiter",
            "location": "San Francisco, CA",
            "recruiter_type": RecruiterType.INTERNAL.value,
            "specializations": ["Technology"],
            "seniority_levels": ["Mid", "Senior"],
            "response_rate": 0.65,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        # Upsert test recruiter
        await db.recruiters.update_one(
            {"id": test_recruiter["id"]},
            {"$set": test_recruiter},
            upsert=True
        )
        
        # Create test campaign
        campaign_data = {
            "name": "Test Outreach Campaign",
            "description": "Testing the outreach system",
            "target_roles": ["Software Engineer"],
            "target_companies": ["TechCorp"],
            "channels": [OutreachChannel.EMAIL.value],
            "tone": OutreachTone.WARM.value
        }
        
        campaign_id = await outreach_manager.create_campaign(
            candidate_id=test_candidate["id"],
            campaign_data=campaign_data
        )
        
        return {
            "success": True,
            "message": "Outreach system test completed successfully",
            "test_data": {
                "candidate": test_candidate,
                "recruiter": test_recruiter,
                "campaign_id": campaign_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing outreach system: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Outreach system test failed: {str(e)}")

# ================================================================================
# END PHASE 7: RECRUITER OUTREACH ENGINE ENDPOINTS
# ================================================================================
