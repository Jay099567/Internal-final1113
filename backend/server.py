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
from datetime import datetime

# Import our models and services
from models import *
from services.openrouter import get_openrouter_service
from services.gmail import gmail_service
from services.resume_parser import resume_service
from services.scheduler import get_scheduler, create_custom_schedule


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
        
        # Check OpenRouter API
        openrouter_service = get_openrouter_service()
        openrouter_status = "operational" if openrouter_service.api_key else "missing_api_key"
        
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
        
        # Get recent activity
        recent_candidates = await db.candidates.find().sort("created_at", -1).limit(5).to_list(length=5)
        recent_applications = await db.applications.find().sort("created_at", -1).limit(5).to_list(length=5)
        
        return {
            "counts": {
                "candidates": candidates_count,
                "resumes": resumes_count,
                "applications": applications_count,
                "jobs": jobs_count
            },
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
