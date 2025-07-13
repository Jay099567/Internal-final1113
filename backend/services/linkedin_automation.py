"""
LinkedIn Automation Service for Elite JobHunter X
Handles LinkedIn authentication, messaging, connection requests, and profile scraping
"""

import os
import json
import time
import random
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode, parse_qs, urlparse
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential

from models import (
    Recruiter, OutreachMessage, OutreachStatus, OutreachChannel, 
    LinkedInOAuth, RecruiterResearch, OutreachTone
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInAutomation:
    """
    LinkedIn Automation Service with stealth features and rate limiting
    """
    
    def __init__(self, db_client):
        self.db_client = db_client
        self.db = db_client.linkedin_automation
        self.ua = UserAgent()
        self.session = None
        self.rate_limit_delay = 2  # Seconds between requests
        self.daily_limit = 100  # Max actions per day
        self.hourly_limit = 10   # Max actions per hour
        
        # LinkedIn API endpoints
        self.base_url = "https://api.linkedin.com/v2"
        self.oauth_url = "https://www.linkedin.com/oauth/v2"
        
        # Headers for stealth
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=self.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def get_oauth_url(self, candidate_id: str) -> str:
        """
        Generate LinkedIn OAuth URL for candidate authentication
        """
        params = {
            'response_type': 'code',
            'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
            'redirect_uri': f"{os.getenv('FRONTEND_URL')}/auth/linkedin/callback",
            'state': candidate_id,
            'scope': 'r_liteprofile r_emailaddress w_member_social rw_organization_admin'
        }
        
        return f"{self.oauth_url}/authorization?{urlencode(params)}"
    
    async def exchange_code_for_tokens(self, code: str, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Exchange OAuth code for access tokens
        """
        try:
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': f"{os.getenv('FRONTEND_URL')}/auth/linkedin/callback",
                'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
                'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET')
            }
            
            async with self.session.post(
                f"{self.oauth_url}/accessToken",
                data=data
            ) as response:
                if response.status == 200:
                    tokens = await response.json()
                    
                    # Save tokens to database
                    linkedin_oauth = LinkedInOAuth(
                        candidate_id=candidate_id,
                        access_token=tokens['access_token'],
                        refresh_token=tokens.get('refresh_token'),
                        token_expiry=datetime.utcnow() + timedelta(seconds=tokens['expires_in']),
                        scopes=tokens.get('scope', '').split(' '),
                        linkedin_user_id=await self.get_user_id(tokens['access_token'])
                    )
                    
                    await self.db.linkedin_oauth.insert_one(linkedin_oauth.dict())
                    return tokens
                else:
                    logger.error(f"Failed to exchange code: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error exchanging code: {str(e)}")
            return None
    
    async def get_user_id(self, access_token: str) -> Optional[str]:
        """
        Get LinkedIn user ID from access token
        """
        try:
            headers = {**self.headers, 'Authorization': f'Bearer {access_token}'}
            
            async with self.session.get(
                f"{self.base_url}/me",
                headers=headers
            ) as response:
                if response.status == 200:
                    user_data = await response.json()
                    return user_data.get('id')
                return None
        except Exception as e:
            logger.error(f"Error getting user ID: {str(e)}")
            return None
    
    async def get_valid_token(self, candidate_id: str) -> Optional[str]:
        """
        Get valid access token for candidate, refresh if needed
        """
        oauth_data = await self.db.linkedin_oauth.find_one(
            {"candidate_id": candidate_id, "is_active": True}
        )
        
        if not oauth_data:
            logger.warning(f"No LinkedIn OAuth data found for candidate: {candidate_id}")
            return None
        
        # Check if token is expired
        if datetime.utcnow() >= oauth_data['token_expiry']:
            if oauth_data.get('refresh_token'):
                new_token = await self.refresh_token(oauth_data['refresh_token'])
                if new_token:
                    await self.db.linkedin_oauth.update_one(
                        {"_id": oauth_data['_id']},
                        {"$set": {
                            "access_token": new_token['access_token'],
                            "token_expiry": datetime.utcnow() + timedelta(seconds=new_token['expires_in']),
                            "updated_at": datetime.utcnow()
                        }}
                    )
                    return new_token['access_token']
            return None
        
        return oauth_data['access_token']
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh LinkedIn access token
        """
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
                'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET')
            }
            
            async with self.session.post(
                f"{self.oauth_url}/accessToken",
                data=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def send_message(self, candidate_id: str, recruiter_id: str, message_content: str, 
                          subject: Optional[str] = None) -> bool:
        """
        Send direct message to recruiter on LinkedIn
        """
        try:
            access_token = await self.get_valid_token(candidate_id)
            if not access_token:
                logger.error(f"No valid access token for candidate: {candidate_id}")
                return False
            
            # Get recruiter LinkedIn ID
            recruiter = await self.db.recruiters.find_one({"id": recruiter_id})
            if not recruiter or not recruiter.get('linkedin_id'):
                logger.error(f"No LinkedIn ID found for recruiter: {recruiter_id}")
                return False
            
            # Rate limiting
            await self.apply_rate_limit()
            
            # Prepare message payload
            message_data = {
                'recipients': [recruiter['linkedin_id']],
                'message': {
                    'subject': subject or "Professional Connection",
                    'body': message_content
                }
            }
            
            headers = {
                **self.headers,
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=message_data
            ) as response:
                if response.status == 201:
                    logger.info(f"Message sent successfully to recruiter: {recruiter_id}")
                    return True
                else:
                    logger.error(f"Failed to send message: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def send_connection_request(self, candidate_id: str, recruiter_id: str, 
                                    message: Optional[str] = None) -> bool:
        """
        Send connection request to recruiter on LinkedIn
        """
        try:
            access_token = await self.get_valid_token(candidate_id)
            if not access_token:
                logger.error(f"No valid access token for candidate: {candidate_id}")
                return False
            
            # Get recruiter LinkedIn ID
            recruiter = await self.db.recruiters.find_one({"id": recruiter_id})
            if not recruiter or not recruiter.get('linkedin_id'):
                logger.error(f"No LinkedIn ID found for recruiter: {recruiter_id}")
                return False
            
            # Rate limiting
            await self.apply_rate_limit()
            
            # Prepare connection request payload
            connection_data = {
                'invitee': {
                    'id': recruiter['linkedin_id']
                },
                'message': message or "I'd like to connect with you"
            }
            
            headers = {
                **self.headers,
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.post(
                f"{self.base_url}/invitations",
                headers=headers,
                json=connection_data
            ) as response:
                if response.status == 201:
                    logger.info(f"Connection request sent to recruiter: {recruiter_id}")
                    return True
                else:
                    logger.error(f"Failed to send connection request: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending connection request: {str(e)}")
            return False
    
    async def scrape_recruiter_profile(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape recruiter profile data from LinkedIn
        """
        try:
            # Rate limiting
            await self.apply_rate_limit()
            
            # Extract profile ID from URL
            profile_id = self.extract_profile_id(linkedin_url)
            if not profile_id:
                logger.error(f"Could not extract profile ID from URL: {linkedin_url}")
                return None
            
            # Use LinkedIn API to get profile data
            # Note: This requires appropriate API access
            headers = {**self.headers}
            
            async with self.session.get(
                f"{self.base_url}/people/{profile_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    profile_data = await response.json()
                    
                    # Extract relevant information
                    extracted_data = {
                        'name': f"{profile_data.get('firstName', '')} {profile_data.get('lastName', '')}".strip(),
                        'headline': profile_data.get('headline'),
                        'location': profile_data.get('location', {}).get('name'),
                        'industry': profile_data.get('industry'),
                        'connections': profile_data.get('numConnections'),
                        'profile_picture': profile_data.get('profilePicture'),
                        'public_profile_url': profile_data.get('publicProfileUrl'),
                        'scraped_at': datetime.utcnow().isoformat()
                    }
                    
                    return extracted_data
                else:
                    logger.error(f"Failed to scrape profile: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error scraping profile: {str(e)}")
            return None
    
    def extract_profile_id(self, linkedin_url: str) -> Optional[str]:
        """
        Extract LinkedIn profile ID from URL
        """
        try:
            parsed_url = urlparse(linkedin_url)
            path_parts = parsed_url.path.split('/')
            
            if 'in' in path_parts:
                in_index = path_parts.index('in')
                if in_index + 1 < len(path_parts):
                    return path_parts[in_index + 1]
            
            return None
        except Exception:
            return None
    
    async def search_recruiters(self, keywords: List[str], location: Optional[str] = None, 
                             company: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for recruiters on LinkedIn
        """
        try:
            # Rate limiting
            await self.apply_rate_limit()
            
            # Build search parameters
            search_params = {
                'keywords': ' '.join(keywords),
                'facetCurrentCompany': company,
                'facetGeoRegion': location,
                'facetNetwork': 'F',  # First degree connections
                'count': limit
            }
            
            # Remove None values
            search_params = {k: v for k, v in search_params.items() if v is not None}
            
            headers = {**self.headers}
            
            async with self.session.get(
                f"{self.base_url}/peopleSearch",
                headers=headers,
                params=search_params
            ) as response:
                if response.status == 200:
                    search_results = await response.json()
                    
                    recruiters = []
                    for person in search_results.get('people', {}).get('values', []):
                        recruiter_data = {
                            'name': f"{person.get('firstName', '')} {person.get('lastName', '')}".strip(),
                            'headline': person.get('headline'),
                            'location': person.get('location', {}).get('name'),
                            'industry': person.get('industry'),
                            'linkedin_id': person.get('id'),
                            'linkedin_url': person.get('publicProfileUrl'),
                            'profile_picture': person.get('profilePicture'),
                            'found_at': datetime.utcnow().isoformat()
                        }
                        recruiters.append(recruiter_data)
                    
                    return recruiters
                else:
                    logger.error(f"Failed to search recruiters: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching recruiters: {str(e)}")
            return []
    
    async def apply_rate_limit(self):
        """
        Apply rate limiting to prevent API abuse
        """
        # Add random delay between requests
        delay = random.uniform(self.rate_limit_delay, self.rate_limit_delay + 2)
        await asyncio.sleep(delay)
        
        # Check daily and hourly limits
        current_time = datetime.utcnow()
        
        # Check hourly limit
        hourly_count = await self.db.rate_limits.count_documents({
            'timestamp': {'$gte': current_time - timedelta(hours=1)}
        })
        
        if hourly_count >= self.hourly_limit:
            logger.warning("Hourly rate limit reached, waiting...")
            await asyncio.sleep(3600)  # Wait 1 hour
        
        # Check daily limit
        daily_count = await self.db.rate_limits.count_documents({
            'timestamp': {'$gte': current_time - timedelta(days=1)}
        })
        
        if daily_count >= self.daily_limit:
            logger.warning("Daily rate limit reached, waiting...")
            await asyncio.sleep(86400)  # Wait 24 hours
        
        # Record this request
        await self.db.rate_limits.insert_one({
            'timestamp': current_time,
            'action': 'linkedin_api_call'
        })
    
    async def get_profile_insights(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Get comprehensive profile insights for recruiter research
        """
        try:
            profile_data = await self.scrape_recruiter_profile(linkedin_url)
            if not profile_data:
                return {}
            
            # Analyze profile for insights
            insights = {
                'engagement_level': self.analyze_engagement(profile_data),
                'response_likelihood': self.calculate_response_likelihood(profile_data),
                'best_contact_time': self.suggest_contact_time(profile_data),
                'personalization_hooks': self.extract_personalization_hooks(profile_data),
                'communication_style': self.analyze_communication_style(profile_data)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting profile insights: {str(e)}")
            return {}
    
    def analyze_engagement(self, profile_data: Dict[str, Any]) -> str:
        """
        Analyze recruiter engagement level
        """
        connections = profile_data.get('connections', 0)
        
        if connections > 500:
            return "high"
        elif connections > 100:
            return "medium"
        else:
            return "low"
    
    def calculate_response_likelihood(self, profile_data: Dict[str, Any]) -> float:
        """
        Calculate likelihood of response based on profile data
        """
        score = 0.5  # Base score
        
        # Adjust based on various factors
        if profile_data.get('industry') == 'Staffing and Recruiting':
            score += 0.2
        
        headline = profile_data.get('headline', '').lower()
        if any(word in headline for word in ['recruiter', 'talent', 'hiring']):
            score += 0.1
        
        if profile_data.get('connections', 0) > 500:
            score += 0.1
        
        return min(score, 1.0)
    
    def suggest_contact_time(self, profile_data: Dict[str, Any]) -> str:
        """
        Suggest best time to contact based on profile
        """
        # Basic logic - can be enhanced with ML
        location = profile_data.get('location', '')
        
        if 'PST' in location or 'Pacific' in location:
            return "10:00 AM PST"
        elif 'EST' in location or 'Eastern' in location:
            return "10:00 AM EST"
        else:
            return "10:00 AM local time"
    
    def extract_personalization_hooks(self, profile_data: Dict[str, Any]) -> List[str]:
        """
        Extract personalization hooks from profile
        """
        hooks = []
        
        if profile_data.get('industry'):
            hooks.append(f"industry:{profile_data['industry']}")
        
        if profile_data.get('location'):
            hooks.append(f"location:{profile_data['location']}")
        
        headline = profile_data.get('headline', '')
        if headline:
            hooks.append(f"headline:{headline}")
        
        return hooks
    
    def analyze_communication_style(self, profile_data: Dict[str, Any]) -> str:
        """
        Analyze preferred communication style
        """
        headline = profile_data.get('headline', '').lower()
        
        if any(word in headline for word in ['senior', 'director', 'vp', 'head']):
            return "professional"
        elif any(word in headline for word in ['passionate', 'innovative', 'creative']):
            return "casual"
        else:
            return "balanced"


class LinkedInMessageGenerator:
    """
    Generate personalized LinkedIn messages using AI
    """
    
    def __init__(self, openrouter_service):
        self.openrouter = openrouter_service
    
    async def generate_outreach_message(self, recruiter_data: Dict[str, Any], 
                                       candidate_data: Dict[str, Any],
                                       job_data: Optional[Dict[str, Any]] = None,
                                       tone: OutreachTone = OutreachTone.WARM,
                                       template: Optional[str] = None) -> str:
        """
        Generate personalized outreach message
        """
        try:
            # Build context for AI
            context = self.build_message_context(recruiter_data, candidate_data, job_data, tone)
            
            # Use template if provided
            if template:
                message = await self.apply_template(template, context)
            else:
                message = await self.generate_ai_message(context, tone)
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating outreach message: {str(e)}")
            return self.get_fallback_message(recruiter_data, candidate_data, tone)
    
    def build_message_context(self, recruiter_data: Dict[str, Any], 
                            candidate_data: Dict[str, Any],
                            job_data: Optional[Dict[str, Any]] = None,
                            tone: OutreachTone = OutreachTone.WARM) -> Dict[str, Any]:
        """
        Build context for message generation
        """
        context = {
            'recruiter_name': recruiter_data.get('name', 'there'),
            'recruiter_title': recruiter_data.get('title', ''),
            'recruiter_company': recruiter_data.get('company', ''),
            'recruiter_location': recruiter_data.get('location', ''),
            'candidate_name': candidate_data.get('full_name', ''),
            'candidate_title': candidate_data.get('current_title', ''),
            'candidate_skills': candidate_data.get('skills', []),
            'candidate_experience': candidate_data.get('years_experience', 0),
            'target_roles': candidate_data.get('target_roles', []),
            'tone': tone.value,
            'job_title': job_data.get('title', '') if job_data else '',
            'job_company': job_data.get('company', '') if job_data else ''
        }
        
        return context
    
    async def generate_ai_message(self, context: Dict[str, Any], tone: OutreachTone) -> str:
        """
        Generate AI-powered message
        """
        prompt = f"""
        Generate a professional LinkedIn outreach message with the following details:
        
        Recruiter: {context['recruiter_name']} ({context['recruiter_title']} at {context['recruiter_company']})
        Candidate: {context['candidate_name']} ({context['candidate_experience']} years experience)
        Skills: {', '.join(context['candidate_skills'][:5])}
        Target Roles: {', '.join(context['target_roles'][:3])}
        Tone: {context['tone']}
        
        Requirements:
        - Keep it under 300 characters (LinkedIn message limit)
        - Be personal and genuine
        - Mention specific skills or experience
        - Include a clear call to action
        - Match the {tone.value} tone
        
        Message:
        """
        
        try:
            response = await self.openrouter.generate_completion(
                prompt=prompt,
                model="anthropic/claude-3-haiku-20240307",
                max_tokens=150
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI message: {str(e)}")
            return self.get_fallback_message(context, tone)
    
    async def apply_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Apply template with context variables
        """
        try:
            message = template.format(**context)
            return message
        except Exception as e:
            logger.error(f"Error applying template: {str(e)}")
            return template
    
    def get_fallback_message(self, recruiter_data: Dict[str, Any], 
                           candidate_data: Dict[str, Any], 
                           tone: OutreachTone) -> str:
        """
        Get fallback message if AI generation fails
        """
        name = recruiter_data.get('name', 'there')
        
        if tone == OutreachTone.WARM:
            return f"Hi {name}, I'm a {candidate_data.get('current_title', 'professional')} with {candidate_data.get('years_experience', 'several')} years of experience. I'd love to connect and discuss potential opportunities. Thanks!"
        elif tone == OutreachTone.FORMAL:
            return f"Dear {name}, I am reaching out to connect regarding potential opportunities in my field. I have {candidate_data.get('years_experience', 'several')} years of experience and would appreciate the chance to discuss how I might contribute to your organization."
        else:
            return f"Hi {name}, I noticed your role at {recruiter_data.get('company', 'your company')} and would love to connect. I'm actively exploring new opportunities and would appreciate any insights you might have. Looking forward to connecting!"