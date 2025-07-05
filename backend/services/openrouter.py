import os
import openai
from typing import List, Dict, Any, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import json

logger = logging.getLogger(__name__)

class OpenRouterService:
    def __init__(self):
        self.api_key = os.environ.get('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        # Configure OpenAI client for OpenRouter
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        
        # Model configurations for different tasks
        self.models = {
            "job_matching": "anthropic/claude-3-sonnet",
            "resume_tailoring": "anthropic/claude-3-sonnet", 
            "cover_letter": "anthropic/claude-3-sonnet",
            "outreach": "anthropic/claude-3-sonnet",
            "content_extraction": "anthropic/claude-3-haiku",
            "classification": "anthropic/claude-3-haiku",
            "embeddings": "text-embedding-3-small"
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_completion(self, prompt: str, model_type: str = "job_matching", 
                                max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """Generate text completion using OpenRouter"""
        try:
            model = self.models.get(model_type, self.models["job_matching"])
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenRouter completion error: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text using OpenRouter"""
        try:
            response = self.client.embeddings.create(
                model=self.models["embeddings"],
                input=texts
            )
            
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"OpenRouter embeddings error: {str(e)}")
            raise
    
    async def analyze_job_match(self, job_description: str, candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze job match using AI"""
        prompt = f"""
        Analyze the job match between this candidate and job posting. Provide a detailed analysis.
        
        CANDIDATE PROFILE:
        - Name: {candidate_profile.get('full_name', 'N/A')}
        - Experience: {candidate_profile.get('years_experience', 'N/A')} years
        - Skills: {', '.join(candidate_profile.get('skills', []))}
        - Target Roles: {', '.join(candidate_profile.get('target_roles', []))}
        - Location: {candidate_profile.get('location', 'N/A')}
        - Salary Range: ${candidate_profile.get('salary_min', 'N/A')}-${candidate_profile.get('salary_max', 'N/A')}
        - Visa Sponsorship Required: {candidate_profile.get('visa_sponsorship_required', False)}
        
        JOB DESCRIPTION:
        {job_description}
        
        Please provide a JSON response with:
        {{
            "match_score": 0-100,
            "explanation": "detailed explanation of the match",
            "keywords_matched": ["keyword1", "keyword2"],
            "salary_match": true/false,
            "location_match": true/false,
            "visa_match": true/false,
            "skills_match_score": 0-100,
            "experience_match": true/false,
            "should_apply": true/false,
            "priority": "high/medium/low",
            "missing_requirements": ["requirement1", "requirement2"],
            "strengths": ["strength1", "strength2"]
        }}
        """
        
        try:
            response = await self.generate_completion(prompt, "job_matching", max_tokens=1000, temperature=0.3)
            # Parse JSON response
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError:
            logger.error(f"Failed to parse job match analysis response: {response}")
            return {
                "match_score": 0,
                "explanation": "Failed to analyze job match",
                "should_apply": False,
                "priority": "low"
            }
    
    async def tailor_resume(self, original_resume: str, job_description: str, 
                          candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Tailor resume for specific job using AI"""
        prompt = f"""
        You are an expert resume optimizer. Tailor this resume for the specific job posting.
        
        ORIGINAL RESUME:
        {original_resume}
        
        JOB DESCRIPTION:
        {job_description}
        
        CANDIDATE PROFILE:
        {json.dumps(candidate_profile, indent=2)}
        
        Instructions:
        1. Optimize the resume for ATS (Applicant Tracking Systems)
        2. Include relevant keywords from the job posting
        3. Highlight matching skills and experience
        4. Maintain truthfulness - don't add false information
        5. Improve formatting and structure
        
        Please provide a JSON response with:
        {{
            "tailored_resume": "the optimized resume content",
            "keywords_injected": ["keyword1", "keyword2"],
            "ats_score": 0-100,
            "changes_made": ["change1", "change2"],
            "optimization_notes": "notes about optimizations"
        }}
        """
        
        try:
            response = await self.generate_completion(prompt, "resume_tailoring", max_tokens=3000, temperature=0.5)
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError:
            logger.error(f"Failed to parse resume tailoring response: {response}")
            return {
                "tailored_resume": original_resume,
                "keywords_injected": [],
                "ats_score": 50,
                "changes_made": [],
                "optimization_notes": "Failed to tailor resume"
            }
    
    async def generate_cover_letter(self, job_description: str, candidate_profile: Dict[str, Any], 
                                  company_info: Dict[str, Any], tone: str = "professional") -> Dict[str, Any]:
        """Generate cover letter using AI"""
        prompt = f"""
        Write a compelling cover letter for this job application.
        
        JOB DESCRIPTION:
        {job_description}
        
        CANDIDATE PROFILE:
        {json.dumps(candidate_profile, indent=2)}
        
        COMPANY INFO:
        {json.dumps(company_info, indent=2)}
        
        TONE: {tone}
        
        Instructions:
        1. Make it specific to the role and company
        2. Highlight relevant achievements and skills
        3. Show enthusiasm and cultural fit
        4. Keep it concise (3-4 paragraphs)
        5. Include a strong opening and closing
        
        Please provide a JSON response with:
        {{
            "cover_letter": "the complete cover letter content",
            "tone_analysis": "analysis of the tone used",
            "key_points": ["point1", "point2"],
            "ats_keywords": ["keyword1", "keyword2"],
            "personalization_elements": ["element1", "element2"]
        }}
        """
        
        try:
            response = await self.generate_completion(prompt, "cover_letter", max_tokens=2000, temperature=0.7)
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError:
            logger.error(f"Failed to parse cover letter response: {response}")
            return {
                "cover_letter": "Failed to generate cover letter",
                "tone_analysis": "Error",
                "key_points": [],
                "ats_keywords": [],
                "personalization_elements": []
            }
    
    async def generate_outreach_message(self, target_person: str, target_role: str, 
                                      job_info: Dict[str, Any], candidate_profile: Dict[str, Any], 
                                      channel: str = "linkedin", tone: str = "warm") -> Dict[str, Any]:
        """Generate outreach message for recruiter/hiring manager"""
        prompt = f"""
        Write a personalized outreach message for job application.
        
        TARGET: {target_person} ({target_role})
        CHANNEL: {channel}
        TONE: {tone}
        
        JOB INFO:
        {json.dumps(job_info, indent=2)}
        
        CANDIDATE PROFILE:
        {json.dumps(candidate_profile, indent=2)}
        
        Instructions:
        1. Personalize based on target person and company
        2. Keep it concise and professional
        3. Include a clear call-to-action
        4. Match the specified tone
        5. Adapt length for the channel (LinkedIn = shorter, Email = longer)
        
        Please provide a JSON response with:
        {{
            "message": "the outreach message content",
            "subject": "subject line (for email)",
            "tone_analysis": "analysis of tone used",
            "personalization_score": 0-100,
            "cta": "the call-to-action used",
            "follow_up_strategy": "suggested follow-up approach"
        }}
        """
        
        try:
            response = await self.generate_completion(prompt, "outreach", max_tokens=1500, temperature=0.8)
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError:
            logger.error(f"Failed to parse outreach message response: {response}")
            return {
                "message": "Failed to generate outreach message",
                "subject": "Job Application Inquiry",
                "tone_analysis": "Error",
                "personalization_score": 0,
                "cta": "Please consider my application",
                "follow_up_strategy": "No follow-up strategy available"
            }
    
    async def analyze_email_response(self, email_content: str, original_message: str) -> Dict[str, Any]:
        """Analyze email response for sentiment and next actions"""
        prompt = f"""
        Analyze this email response to determine sentiment, intent, and next actions.
        
        ORIGINAL MESSAGE:
        {original_message}
        
        EMAIL RESPONSE:
        {email_content}
        
        Please provide a JSON response with:
        {{
            "sentiment": "positive/neutral/negative",
            "intent": "interested/not_interested/request_more_info/schedule_interview/rejection",
            "confidence": 0-100,
            "next_action": "suggested next step",
            "key_points": ["point1", "point2"],
            "requires_follow_up": true/false,
            "follow_up_delay": "suggested delay (e.g., '3 days')"
        }}
        """
        
        try:
            response = await self.generate_completion(prompt, "classification", max_tokens=800, temperature=0.3)
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError:
            logger.error(f"Failed to parse email analysis response: {response}")
            return {
                "sentiment": "neutral",
                "intent": "unknown",
                "confidence": 0,
                "next_action": "manual_review",
                "key_points": [],
                "requires_follow_up": False,
                "follow_up_delay": "1 week"
            }

# Global instance
openrouter_service = OpenRouterService()