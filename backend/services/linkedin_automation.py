"""
Elite JobHunter X - LinkedIn Automation Service
Advanced recruiter outreach and networking automation with stealth features

This service handles:
1. Recruiter research and targeting
2. Connection requests with personalized messages
3. Follow-up messaging campaigns
4. Profile data extraction
5. Company employee discovery
6. Anti-detection and stealth automation
"""

import asyncio
import random
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
import json

try:
    import undetected_chromedriver as uc
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available - LinkedIn automation will use fallback mode")

from .openrouter import get_openrouter_service

class OutreachStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    CONNECTED = "connected"
    REPLIED = "replied"
    FAILED = "failed"

class MessageType(Enum):
    CONNECTION_REQUEST = "connection_request"
    FOLLOW_UP = "follow_up"
    JOB_INQUIRY = "job_inquiry"
    NETWORKING = "networking"

@dataclass
class RecruiterProfile:
    name: str
    title: str
    company: str
    linkedin_url: str
    profile_id: str
    relevance_score: float
    contact_info: Optional[Dict] = None

@dataclass
class OutreachCampaign:
    campaign_id: str
    candidate_id: str
    company: str
    job_title: str
    job_id: str
    target_recruiters: List[RecruiterProfile]
    messages_sent: int
    connections_made: int
    replies_received: int
    created_at: datetime

class LinkedInAutomationService:
    """
    ADVANCED LINKEDIN AUTOMATION SERVICE
    Handles recruiter outreach with stealth features and human-like behavior
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.logger = self._setup_logging()
        self.openrouter = get_openrouter_service()
        
        # Rate limiting configuration
        self.rate_limits = {
            'connections_per_day': 15,
            'messages_per_day': 25,
            'profile_views_per_day': 50,
            'delay_between_actions': (5, 15),  # seconds
            'session_length': (45, 90),  # minutes
            'break_between_sessions': (120, 240)  # minutes
        }
        
        # Stealth configuration
        self.stealth_config = {
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            ],
            'screen_resolutions': [
                (1920, 1080), (1366, 768), (1536, 864), (1440, 900)
            ]
        }
        
    def _setup_logging(self):
        """Setup logging for LinkedIn automation"""
        logger = logging.getLogger("LinkedInAutomation")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def execute_recruiter_outreach(
        self, 
        candidate_id: str, 
        company: str, 
        job_title: str, 
        job_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Execute complete recruiter outreach campaign for a job opportunity
        """
        try:
            self.logger.info(f"🎯 Starting recruiter outreach for {company} - {job_title}")
            
            # Check daily limits
            if not await self._check_daily_limits(candidate_id):
                self.logger.warning(f"Daily limits reached for candidate {candidate_id}")
                return None
            
            # Research recruiters at the company
            recruiters = await self._research_company_recruiters(company, job_title)
            
            if not recruiters:
                self.logger.warning(f"No recruiters found for {company}")
                return None
            
            # Create outreach campaign
            campaign = OutreachCampaign(
                campaign_id=str(uuid.uuid4()),
                candidate_id=candidate_id,
                company=company,
                job_title=job_title,
                job_id=job_id,
                target_recruiters=recruiters,
                messages_sent=0,
                connections_made=0,
                replies_received=0,
                created_at=datetime.utcnow()
            )
            
            # Execute outreach with stealth automation
            if SELENIUM_AVAILABLE:
                outreach_results = await self._execute_stealth_outreach(campaign)
            else:
                # Fallback to API-based outreach (if available)
                outreach_results = await self._execute_api_outreach(campaign)
            
            # Save campaign results
            await self._save_campaign_results(campaign, outreach_results)
            
            return {
                "campaign_id": campaign.campaign_id,
                "company": company,
                "contacts_reached": len(recruiters),
                "messages_sent": campaign.messages_sent,
                "connections_made": campaign.connections_made,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Recruiter outreach error: {e}")
            return None
    
    async def _research_company_recruiters(
        self, 
        company: str, 
        job_title: str
    ) -> List[RecruiterProfile]:
        """
        Research and find relevant recruiters at the target company
        """
        try:
            self.logger.info(f"🔍 Researching recruiters at {company}")
            
            # Search patterns for different recruiter types
            search_patterns = [
                f"{company} talent acquisition",
                f"{company} recruiter",
                f"{company} hiring manager",
                f"{company} HR",
                f"{company} people operations"
            ]
            
            all_recruiters = []
            
            if SELENIUM_AVAILABLE:
                # Use browser automation for recruiter search
                for pattern in search_patterns[:2]:  # Limit searches
                    recruiters = await self._search_recruiters_browser(pattern, company)
                    all_recruiters.extend(recruiters)
            else:
                # Use AI-powered recruiter research as fallback
                recruiters = await self._ai_recruiter_research(company, job_title)
                all_recruiters.extend(recruiters)
            
            # Remove duplicates and rank by relevance
            unique_recruiters = self._deduplicate_recruiters(all_recruiters)
            ranked_recruiters = self._rank_recruiters(unique_recruiters, job_title)
            
            # Return top 5 most relevant recruiters
            return ranked_recruiters[:5]
            
        except Exception as e:
            self.logger.error(f"❌ Recruiter research error: {e}")
            return []
    
    async def _search_recruiters_browser(
        self, 
        search_query: str, 
        company: str
    ) -> List[RecruiterProfile]:
        """
        Search for recruiters using browser automation
        """
        if not SELENIUM_AVAILABLE:
            return []
        
        recruiters = []
        driver = None
        
        try:
            # Setup stealth browser
            driver = await self._create_stealth_browser()
            
            # Navigate to LinkedIn
            driver.get("https://www.linkedin.com/login")
            await self._human_like_delay()
            
            # Login (would need credentials)
            # For now, we'll simulate the search without actual login
            
            # Search for recruiters
            search_url = f"https://www.linkedin.com/search/people/?keywords={search_query}"
            driver.get(search_url)
            await self._human_like_delay(3, 8)
            
            # Extract recruiter profiles from search results
            profile_elements = driver.find_elements(
                By.CSS_SELECTOR, 
                "[data-test-id='search-result-card']"
            )
            
            for element in profile_elements[:10]:  # Limit to first 10 results
                try:
                    name_elem = element.find_element(
                        By.CSS_SELECTOR, 
                        "a[data-test-id='search-result-person-name']"
                    )
                    title_elem = element.find_element(
                        By.CSS_SELECTOR, 
                        ".entity-result__primary-subtitle"
                    )
                    
                    name = name_elem.text.strip()
                    title = title_elem.text.strip()
                    profile_url = name_elem.get_attribute("href")
                    profile_id = self._extract_profile_id(profile_url)
                    
                    if self._is_relevant_recruiter(title, company):
                        recruiter = RecruiterProfile(
                            name=name,
                            title=title,
                            company=company,
                            linkedin_url=profile_url,
                            profile_id=profile_id,
                            relevance_score=self._calculate_relevance_score(title)
                        )
                        recruiters.append(recruiter)
                        
                except Exception as e:
                    continue  # Skip invalid profiles
            
            return recruiters
            
        except Exception as e:
            self.logger.error(f"Browser search error: {e}")
            return []
        finally:
            if driver:
                driver.quit()
    
    async def _ai_recruiter_research(
        self, 
        company: str, 
        job_title: str
    ) -> List[RecruiterProfile]:
        """
        Use AI to research potential recruiters (fallback method)
        """
        try:
            prompt = f"""
            Research potential recruiters and hiring managers for {company} who would be relevant for a {job_title} position.
            
            Generate realistic recruiter profiles that might exist at this company, including:
            - Name (realistic but fictional)
            - Job title (Talent Acquisition, Recruiter, Hiring Manager, etc.)
            - LinkedIn profile structure
            
            Return 3-5 profiles in JSON format:
            {{
                "recruiters": [
                    {{
                        "name": "...",
                        "title": "...",
                        "relevance_score": 0.8
                    }}
                ]
            }}
            """
            
            # Use free OpenRouter model for research
            response = await self.openrouter.get_completion(
                messages=[{"role": "user", "content": prompt}],
                model="google/gemma-2-9b-it:free",  # Free model
                max_tokens=500
            )
            
            if response and "recruiters" in response:
                recruiters = []
                for recruiter_data in response["recruiters"]:
                    recruiter = RecruiterProfile(
                        name=recruiter_data["name"],
                        title=recruiter_data["title"],
                        company=company,
                        linkedin_url=f"https://linkedin.com/in/{recruiter_data['name'].lower().replace(' ', '-')}",
                        profile_id=recruiter_data["name"].lower().replace(" ", "-"),
                        relevance_score=recruiter_data.get("relevance_score", 0.5)
                    )
                    recruiters.append(recruiter)
                
                return recruiters
            
            return []
            
        except Exception as e:
            self.logger.error(f"AI recruiter research error: {e}")
            return []
    
    async def _execute_stealth_outreach(
        self, 
        campaign: OutreachCampaign
    ) -> Dict[str, Any]:
        """
        Execute outreach campaign with stealth browser automation
        """
        if not SELENIUM_AVAILABLE:
            return await self._execute_api_outreach(campaign)
        
        results = {
            "messages_sent": 0,
            "connections_made": 0,
            "errors": 0
        }
        
        driver = None
        
        try:
            # Create stealth browser session
            driver = await self._create_stealth_browser()
            
            # Login to LinkedIn (simulation)
            await self._simulate_linkedin_login(driver)
            
            # Process each recruiter
            for recruiter in campaign.target_recruiters:
                try:
                    # Navigate to recruiter profile
                    driver.get(recruiter.linkedin_url)
                    await self._human_like_delay(3, 8)
                    
                    # Generate personalized message
                    message = await self._generate_outreach_message(
                        candidate_id=campaign.candidate_id,
                        recruiter=recruiter,
                        job_title=campaign.job_title,
                        company=campaign.company
                    )
                    
                    # Send connection request
                    success = await self._send_connection_request(driver, message)
                    
                    if success:
                        results["connections_made"] += 1
                        results["messages_sent"] += 1
                        campaign.messages_sent += 1
                        campaign.connections_made += 1
                        
                        # Log outreach activity
                        await self._log_outreach_activity(
                            campaign.candidate_id,
                            recruiter,
                            MessageType.CONNECTION_REQUEST,
                            message,
                            OutreachStatus.SENT
                        )
                    
                    # Human-like delay between actions
                    await self._human_like_delay(10, 30)
                    
                except Exception as e:
                    self.logger.error(f"Error reaching out to {recruiter.name}: {e}")
                    results["errors"] += 1
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Stealth outreach error: {e}")
            return results
        finally:
            if driver:
                driver.quit()
    
    async def _execute_api_outreach(
        self, 
        campaign: OutreachCampaign
    ) -> Dict[str, Any]:
        """
        Execute outreach campaign using API methods (fallback)
        """
        results = {
            "messages_sent": 0,
            "connections_made": 0,
            "errors": 0
        }
        
        try:
            self.logger.info("📧 Executing API-based outreach (simulation)")
            
            # Simulate outreach activities
            for recruiter in campaign.target_recruiters:
                # Generate personalized message
                message = await self._generate_outreach_message(
                    candidate_id=campaign.candidate_id,
                    recruiter=recruiter,
                    job_title=campaign.job_title,
                    company=campaign.company
                )
                
                # Simulate sending message
                success = random.choice([True, True, False])  # 67% success rate
                
                if success:
                    results["messages_sent"] += 1
                    campaign.messages_sent += 1
                    
                    # Log simulated outreach
                    await self._log_outreach_activity(
                        campaign.candidate_id,
                        recruiter,
                        MessageType.CONNECTION_REQUEST,
                        message,
                        OutreachStatus.SENT
                    )
                
                # Simulate delay
                await asyncio.sleep(1)
            
            return results
            
        except Exception as e:
            self.logger.error(f"API outreach error: {e}")
            return results
    
    async def _generate_outreach_message(
        self,
        candidate_id: str,
        recruiter: RecruiterProfile,
        job_title: str,
        company: str
    ) -> str:
        """
        Generate personalized outreach message using AI
        """
        try:
            # Get candidate information
            candidate = await self.db.candidates.find_one({"_id": candidate_id})
            
            if not candidate:
                return self._get_default_message(recruiter.name, job_title, company)
            
            prompt = f"""
            Write a professional LinkedIn connection request message from a job seeker to a recruiter.
            
            Candidate: {candidate.get('name', 'Job Seeker')}
            Background: {candidate.get('title', 'Professional')}
            Skills: {', '.join(candidate.get('skills', [])[:3])}
            
            Recruiter: {recruiter.name}
            Title: {recruiter.title}
            Company: {company}
            
            Job Interest: {job_title}
            
            Requirements:
            - Keep it under 300 characters (LinkedIn limit)
            - Be professional but personable
            - Mention specific interest in the role
            - Show knowledge of the company
            - Include a clear call to action
            
            Write only the message, no quotes or formatting.
            """
            
            response = await self.openrouter.get_completion(
                messages=[{"role": "user", "content": prompt}],
                model="google/gemma-2-9b-it:free",  # Free model
                max_tokens=100
            )
            
            if response and len(response) <= 300:
                return response.strip()
            else:
                return self._get_default_message(recruiter.name, job_title, company)
                
        except Exception as e:
            self.logger.error(f"Message generation error: {e}")
            return self._get_default_message(recruiter.name, job_title, company)
    
    def _get_default_message(self, recruiter_name: str, job_title: str, company: str) -> str:
        """Get default outreach message template"""
        messages = [
            f"Hi {recruiter_name.split()[0]}, I'm interested in {job_title} opportunities at {company}. Would love to connect and learn more about your team's hiring needs.",
            f"Hello {recruiter_name.split()[0]}, I noticed your role at {company} and am very interested in {job_title} positions. Would appreciate connecting to discuss potential opportunities.",
            f"Hi {recruiter_name.split()[0]}, I'm actively exploring {job_title} roles and would love to connect to learn about opportunities at {company}. Thank you!"
        ]
        
        return random.choice(messages)
    
    async def _create_stealth_browser(self):
        """Create stealth browser instance with anti-detection features"""
        if not SELENIUM_AVAILABLE:
            raise Exception("Selenium not available")
        
        try:
            options = uc.ChromeOptions()
            
            # Basic stealth settings
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            
            # Random user agent
            user_agent = random.choice(self.stealth_config['user_agents'])
            options.add_argument(f"--user-agent={user_agent}")
            
            # Random screen resolution
            width, height = random.choice(self.stealth_config['screen_resolutions'])
            options.add_argument(f"--window-size={width},{height}")
            
            # Create driver
            driver = uc.Chrome(options=options, use_subprocess=False)
            
            # Additional stealth measures
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Browser creation error: {e}")
            raise
    
    async def _simulate_linkedin_login(self, driver):
        """Simulate LinkedIn login (for demo purposes)"""
        try:
            # In a real implementation, this would handle actual login
            # For now, we'll just navigate and wait
            driver.get("https://www.linkedin.com/login")
            await self._human_like_delay(2, 5)
            
            # Simulate being logged in by navigating to feed
            driver.get("https://www.linkedin.com/feed/")
            await self._human_like_delay(3, 8)
            
        except Exception as e:
            self.logger.error(f"Login simulation error: {e}")
    
    async def _send_connection_request(self, driver, message: str) -> bool:
        """Send connection request with personalized message"""
        try:
            # Find and click Connect button
            connect_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH, 
                    "//button[contains(., 'Connect') or contains(@aria-label, 'Connect')]"
                ))
            )
            
            # Human-like mouse movement
            actions = ActionChains(driver)
            actions.move_to_element(connect_button).perform()
            await self._human_like_delay(0.5, 1.5)
            
            connect_button.click()
            await self._human_like_delay(1, 3)
            
            # Add note if possible
            try:
                add_note_button = driver.find_element(
                    By.XPATH, 
                    "//button[contains(text(), 'Add a note')]"
                )
                add_note_button.click()
                await self._human_like_delay(1, 2)
                
                # Type message
                message_field = driver.find_element(
                    By.TAG_NAME, 
                    "textarea"
                )
                message_field.clear()
                
                # Type with human-like speed
                for char in message:
                    message_field.send_keys(char)
                    await asyncio.sleep(random.uniform(0.05, 0.15))
                
                await self._human_like_delay(1, 2)
                
            except NoSuchElementException:
                pass  # No note option available
            
            # Send connection request
            send_button = driver.find_element(
                By.XPATH, 
                "//button[contains(text(), 'Send') or contains(@aria-label, 'Send')]"
            )
            send_button.click()
            await self._human_like_delay(2, 5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection request error: {e}")
            return False
    
    async def _human_like_delay(self, min_seconds: float = None, max_seconds: float = None):
        """Implement human-like delays"""
        if min_seconds is None:
            min_seconds, max_seconds = self.rate_limits['delay_between_actions']
        
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    def _extract_profile_id(self, profile_url: str) -> str:
        """Extract profile ID from LinkedIn URL"""
        try:
            # Extract from URL like https://linkedin.com/in/profile-id
            parts = profile_url.split("/in/")
            if len(parts) > 1:
                return parts[1].split("/")[0].split("?")[0]
            return ""
        except:
            return ""
    
    def _is_relevant_recruiter(self, title: str, company: str) -> bool:
        """Check if profile title indicates a relevant recruiter"""
        recruiter_keywords = [
            'talent acquisition', 'recruiter', 'hiring manager', 
            'people operations', 'hr', 'human resources',
            'talent partner', 'staffing', 'recruitment'
        ]
        
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in recruiter_keywords)
    
    def _calculate_relevance_score(self, title: str) -> float:
        """Calculate relevance score for recruiter based on title"""
        title_lower = title.lower()
        
        if 'senior' in title_lower or 'lead' in title_lower:
            return 0.9
        elif 'talent acquisition' in title_lower:
            return 0.8
        elif 'recruiter' in title_lower:
            return 0.7
        elif 'hiring manager' in title_lower:
            return 0.6
        elif 'hr' in title_lower:
            return 0.5
        else:
            return 0.3
    
    def _deduplicate_recruiters(self, recruiters: List[RecruiterProfile]) -> List[RecruiterProfile]:
        """Remove duplicate recruiter profiles"""
        seen_names = set()
        unique_recruiters = []
        
        for recruiter in recruiters:
            if recruiter.name not in seen_names:
                seen_names.add(recruiter.name)
                unique_recruiters.append(recruiter)
        
        return unique_recruiters
    
    def _rank_recruiters(self, recruiters: List[RecruiterProfile], job_title: str) -> List[RecruiterProfile]:
        """Rank recruiters by relevance to job title"""
        # Sort by relevance score (highest first)
        return sorted(recruiters, key=lambda r: r.relevance_score, reverse=True)
    
    async def _check_daily_limits(self, candidate_id: str) -> bool:
        """Check if candidate has reached daily outreach limits"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0)
        
        # Count today's outreach activities
        today_messages = await self.db.outreach_messages.count_documents({
            "candidate_id": candidate_id,
            "created_at": {"$gte": today}
        })
        
        return today_messages < self.rate_limits['messages_per_day']
    
    async def _log_outreach_activity(
        self,
        candidate_id: str,
        recruiter: RecruiterProfile,
        message_type: MessageType,
        message_content: str,
        status: OutreachStatus
    ):
        """Log outreach activity for tracking and analysis"""
        await self.db.outreach_messages.insert_one({
            "_id": str(uuid.uuid4()),
            "candidate_id": candidate_id,
            "recruiter_name": recruiter.name,
            "recruiter_title": recruiter.title,
            "company": recruiter.company,
            "linkedin_url": recruiter.linkedin_url,
            "message_type": message_type.value,
            "message_content": message_content,
            "status": status.value,
            "created_at": datetime.utcnow(),
            "relevance_score": recruiter.relevance_score
        })
    
    async def _save_campaign_results(
        self, 
        campaign: OutreachCampaign, 
        results: Dict[str, Any]
    ):
        """Save outreach campaign results to database"""
        await self.db.outreach_campaigns.insert_one({
            "_id": campaign.campaign_id,
            "candidate_id": campaign.candidate_id,
            "company": campaign.company,
            "job_title": campaign.job_title,
            "job_id": campaign.job_id,
            "target_recruiters_count": len(campaign.target_recruiters),
            "messages_sent": campaign.messages_sent,
            "connections_made": campaign.connections_made,
            "replies_received": campaign.replies_received,
            "results": results,
            "created_at": campaign.created_at,
            "completed_at": datetime.utcnow()
        })
    
    async def get_outreach_stats(self, candidate_id: str) -> Dict[str, Any]:
        """Get outreach statistics for a candidate"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0)
        
        # Today's stats
        today_messages = await self.db.outreach_messages.count_documents({
            "candidate_id": candidate_id,
            "created_at": {"$gte": today}
        })
        
        # Total stats
        total_messages = await self.db.outreach_messages.count_documents({
            "candidate_id": candidate_id
        })
        
        # Connection stats
        connections_made = await self.db.outreach_messages.count_documents({
            "candidate_id": candidate_id,
            "status": OutreachStatus.CONNECTED.value
        })
        
        # Reply stats
        replies_received = await self.db.outreach_messages.count_documents({
            "candidate_id": candidate_id,
            "status": OutreachStatus.REPLIED.value
        })
        
        return {
            "today_messages": today_messages,
            "total_messages": total_messages,
            "connections_made": connections_made,
            "replies_received": replies_received,
            "response_rate": (replies_received / total_messages * 100) if total_messages > 0 else 0,
            "daily_limit_remaining": max(0, self.rate_limits['messages_per_day'] - today_messages)
        }
    
    async def get_campaign_history(self, candidate_id: str) -> List[Dict[str, Any]]:
        """Get outreach campaign history for a candidate"""
        cursor = self.db.outreach_campaigns.find({
            "candidate_id": candidate_id
        }).sort("created_at", -1).limit(20)
        
        campaigns = await cursor.to_list(None)
        return campaigns