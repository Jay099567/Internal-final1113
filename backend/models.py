from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPLIED = "applied"
    REVIEWING = "reviewing"
    INTERVIEWED = "interviewed"
    REJECTED = "rejected"
    OFFERED = "offered"
    ACCEPTED = "accepted"


class JobStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    PAUSED = "paused"


class EmailDirection(str, Enum):
    SENT = "sent"
    RECEIVED = "received"


class OutreachTone(str, Enum):
    WARM = "warm"
    STRATEGIC = "strategic"
    BOLD = "bold"
    CURIOUS = "curious"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    CHALLENGER = "challenger"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Database Models
class Candidate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    target_roles: List[str] = []
    target_companies: List[str] = []
    target_locations: List[str] = []
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    visa_sponsorship_required: bool = False
    work_authorization: Optional[str] = None
    years_experience: Optional[int] = None
    skills: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class Resume(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    version_name: str
    file_path: str
    file_url: Optional[str] = None
    extracted_text: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[int] = None
    is_primary: bool = False
    ats_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ResumeVersion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    resume_id: str
    version_name: str
    tailored_for_job_id: Optional[str] = None
    tailored_content: str
    keywords_injected: List[str] = []
    ats_score: Optional[float] = None
    used_count: int = 0
    success_rate: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StealthSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    base_email: EmailStr
    alias_suffix: str
    full_email: EmailStr
    target_company: Optional[str] = None
    target_job_board: Optional[str] = None
    user_agent: Optional[str] = None
    proxy_config: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class JobRaw(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_board: str
    job_board_id: str
    title: str
    company: str
    location: str
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_range: Optional[str] = None
    description: str
    requirements: List[str] = []
    benefits: List[str] = []
    visa_sponsorship: bool = False
    remote_work: bool = False
    job_url: str
    company_url: Optional[str] = None
    logo_url: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    status: JobStatus = JobStatus.ACTIVE
    raw_data: Dict[str, Any] = {}


class JobFiltered(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_raw_id: str
    candidate_id: str
    match_score: float
    explanation: str
    keywords_matched: List[str] = []
    salary_match: bool = False
    location_match: bool = False
    visa_match: bool = False
    skills_match_score: Optional[float] = None
    experience_match: bool = False
    filtered_at: datetime = Field(default_factory=datetime.utcnow)
    priority: Priority = Priority.MEDIUM
    should_apply: bool = False


class CoverLetter(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    job_id: str
    tone: OutreachTone
    content: str
    pdf_url: Optional[str] = None
    ats_keywords: List[str] = []
    reasoning: Optional[str] = None
    company_research: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_count: int = 0
    success_rate: Optional[float] = None


class Application(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    job_id: str
    job_raw_id: str
    resume_version_id: str
    cover_letter_id: Optional[str] = None
    stealth_settings_id: str
    job_board: str
    company: str
    position: str
    application_url: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.PENDING
    applied_at: Optional[datetime] = None
    response_at: Optional[datetime] = None
    interview_scheduled: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None
    tracking_pixel_id: Optional[str] = None
    utm_params: Optional[Dict[str, str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OutreachLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    job_id: Optional[str] = None
    application_id: Optional[str] = None
    channel: str  # 'linkedin', 'email', 'twitter'
    target_person: str
    target_role: Optional[str] = None
    message_content: str
    tone: OutreachTone
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    response_at: Optional[datetime] = None
    response_content: Optional[str] = None
    follow_up_scheduled: Optional[datetime] = None
    follow_up_count: int = 0
    success: bool = False
    ghosted: bool = False
    stealth_settings_id: str


class EmailLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    direction: EmailDirection
    subject: str
    message_id: str
    alias_used: EmailStr
    job_id: Optional[str] = None
    application_id: Optional[str] = None
    thread_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    snippet: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    raw_payload: Dict[str, Any] = {}
    processed: bool = False
    sentiment: Optional[str] = None
    intent: Optional[str] = None


class LearningData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    data_type: str  # 'resume_performance', 'outreach_response', 'interview_feedback'
    context: Dict[str, Any]
    outcome: str
    success_score: Optional[float] = None
    insights: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    applied_to_model: bool = False


class JobScheduler(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    job_name: str
    job_type: str  # 'scraping', 'application', 'outreach', 'analysis'
    schedule_cron: str
    next_run: datetime
    last_run: Optional[datetime] = None
    is_active: bool = True
    parameters: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GmailOAuth(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    gmail_address: EmailStr
    access_token: str
    refresh_token: str
    token_expiry: datetime
    scopes: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


# Request/Response Models
class CandidateCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    target_roles: List[str] = []
    target_companies: List[str] = []
    target_locations: List[str] = []
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    visa_sponsorship_required: bool = False
    work_authorization: Optional[str] = None
    years_experience: Optional[int] = None
    skills: List[str] = []


class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    target_roles: Optional[List[str]] = None
    target_companies: Optional[List[str]] = None
    target_locations: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    visa_sponsorship_required: Optional[bool] = None
    work_authorization: Optional[str] = None
    years_experience: Optional[int] = None
    skills: Optional[List[str]] = None
    is_active: Optional[bool] = None


class JobSearchRequest(BaseModel):
    candidate_id: str
    job_boards: List[str] = ["indeed", "linkedin", "glassdoor"]
    keywords: List[str] = []
    location: Optional[str] = None
    max_results: int = 50
    date_range: Optional[str] = "7d"  # 1d, 3d, 7d, 14d, 30d