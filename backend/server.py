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
from services.openrouter import openrouter_service
from services.gmail import gmail_service
from services.resume_parser import resume_service


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
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
