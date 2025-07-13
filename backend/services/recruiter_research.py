"""
Recruiter Research Service for Elite JobHunter X
Finds and researches recruiters for outreach campaigns
"""

import os
import re
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from models import Recruiter, RecruiterType, RecruiterResearch
from services.linkedin_automation import LinkedInAutomation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecruiterResearchService:
    """
    Service for finding and researching recruiters
    """
    
    def __init__(self, db_client):
        self.db_client = db_client
        self.db = db_client.recruiter_research
        self.ua = UserAgent()
        self.session = None
        
        # Common recruiter keywords
        self.recruiter_keywords = [
            'recruiter', 'talent acquisition', 'hiring manager', 'hr manager',
            'talent partner', 'staffing', 'human resources', 'people ops',
            'technical recruiter', 'senior recruiter', 'head of talent',
            'talent scout', 'recruitment consultant', 'hiring lead'
        ]
        
        # Company domains to research
        self.target_domains = [
            'linkedin.com', 'indeed.com', 'glassdoor.com', 'monster.com',
            'dice.com', 'careerbuilder.com', 'ziprecruiter.com'
        ]
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': self.ua.random}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def find_company_recruiters(self, company_name: str, company_domain: Optional[str] = None,
                                    limit: int = 20) -> List[Dict[str, Any]]:
        """
        Find recruiters for a specific company
        """
        try:
            recruiters = []
            
            # Search LinkedIn for company recruiters
            linkedin_recruiters = await self.search_linkedin_recruiters(
                company=company_name, limit=limit//2
            )
            recruiters.extend(linkedin_recruiters)
            
            # Search company website for HR contacts
            if company_domain:
                website_recruiters = await self.scrape_company_website(company_domain)
                recruiters.extend(website_recruiters)
            
            # Search job boards for hiring managers
            job_board_recruiters = await self.find_job_board_recruiters(company_name)
            recruiters.extend(job_board_recruiters)
            
            # Deduplicate and enrich data
            unique_recruiters = await self.deduplicate_recruiters(recruiters)
            enriched_recruiters = await self.enrich_recruiter_data(unique_recruiters)
            
            return enriched_recruiters[:limit]
            
        except Exception as e:
            logger.error(f"Error finding company recruiters: {str(e)}")
            return []
    
    async def search_linkedin_recruiters(self, company: Optional[str] = None,
                                       location: Optional[str] = None,
                                       keywords: Optional[List[str]] = None,
                                       limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search LinkedIn for recruiters
        """
        try:
            search_keywords = keywords or self.recruiter_keywords
            
            # Use LinkedIn automation service
            async with LinkedInAutomation(self.db_client) as linkedin:
                recruiters = await linkedin.search_recruiters(
                    keywords=search_keywords,
                    location=location,
                    company=company,
                    limit=limit
                )
                
                return recruiters
                
        except Exception as e:
            logger.error(f"Error searching LinkedIn recruiters: {str(e)}")
            return []
    
    async def scrape_company_website(self, domain: str) -> List[Dict[str, Any]]:
        """
        Scrape company website for HR contacts
        """
        try:
            recruiters = []
            
            # Common HR/careers pages
            hr_pages = [
                f"https://{domain}/careers",
                f"https://{domain}/jobs",
                f"https://{domain}/about/team",
                f"https://{domain}/team",
                f"https://{domain}/contact",
                f"https://{domain}/about"
            ]
            
            for page_url in hr_pages:
                try:
                    page_recruiters = await self.scrape_website_page(page_url, domain)
                    recruiters.extend(page_recruiters)
                except Exception as e:
                    logger.warning(f"Error scraping {page_url}: {str(e)}")
                    continue
                
                # Add delay to avoid rate limiting
                await asyncio.sleep(2)
            
            return recruiters
            
        except Exception as e:
            logger.error(f"Error scraping company website: {str(e)}")
            return []
    
    async def scrape_website_page(self, url: str, domain: str) -> List[Dict[str, Any]]:
        """
        Scrape a specific website page for recruiter information
        """
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                recruiters = []
                
                # Look for email addresses
                emails = self.extract_emails_from_html(html)
                
                # Look for names and titles
                names_and_titles = self.extract_names_and_titles(soup)
                
                # Combine email and name/title data
                for email in emails:
                    if self.is_hr_email(email):
                        recruiter_data = {
                            'email': email,
                            'company': domain,
                            'company_domain': domain,
                            'recruiter_type': RecruiterType.INTERNAL.value,
                            'found_at': datetime.utcnow().isoformat(),
                            'source': 'company_website'
                        }
                        
                        # Try to match with names
                        for name_title in names_and_titles:
                            if any(keyword in name_title['title'].lower() for keyword in ['hr', 'recruiting', 'talent']):
                                recruiter_data.update({
                                    'name': name_title['name'],
                                    'title': name_title['title']
                                })
                                break
                        
                        recruiters.append(recruiter_data)
                
                return recruiters
                
        except Exception as e:
            logger.error(f"Error scraping website page {url}: {str(e)}")
            return []
    
    def extract_emails_from_html(self, html: str) -> List[str]:
        """
        Extract email addresses from HTML content
        """
        try:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, html)
            
            # Filter out common non-personal emails
            filtered_emails = []
            for email in emails:
                if not any(word in email.lower() for word in ['noreply', 'donotreply', 'admin', 'info', 'support']):
                    filtered_emails.append(email)
            
            return list(set(filtered_emails))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting emails: {str(e)}")
            return []
    
    def extract_names_and_titles(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract names and titles from HTML soup
        """
        try:
            names_and_titles = []
            
            # Look for team member sections
            team_sections = soup.find_all(['div', 'section'], class_=re.compile(r'team|staff|member', re.I))
            
            for section in team_sections:
                # Look for name and title pairs
                names = section.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span'], 
                                       string=re.compile(r'[A-Z][a-z]+ [A-Z][a-z]+'))
                
                for name_elem in names:
                    name = name_elem.get_text().strip()
                    
                    # Look for title near the name
                    title_elem = name_elem.find_next_sibling() or name_elem.find_next()
                    if title_elem:
                        title = title_elem.get_text().strip()
                        
                        if any(keyword in title.lower() for keyword in self.recruiter_keywords):
                            names_and_titles.append({
                                'name': name,
                                'title': title
                            })
            
            return names_and_titles
            
        except Exception as e:
            logger.error(f"Error extracting names and titles: {str(e)}")
            return []
    
    def is_hr_email(self, email: str) -> bool:
        """
        Check if email is likely HR/recruiting related
        """
        hr_keywords = ['hr', 'recruiting', 'talent', 'careers', 'jobs', 'hiring']
        email_lower = email.lower()
        
        return any(keyword in email_lower for keyword in hr_keywords)
    
    async def find_job_board_recruiters(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Find recruiters from job board postings
        """
        try:
            recruiters = []
            
            # Search job boards for company postings
            job_urls = [
                f"https://www.indeed.com/jobs?q={company_name}+hiring+manager",
                f"https://www.glassdoor.com/Jobs/{company_name.replace(' ', '-')}-jobs-SRCH_IL.0,{len(company_name)}_IC1147401.htm"
            ]
            
            for url in job_urls:
                try:
                    job_recruiters = await self.scrape_job_board(url, company_name)
                    recruiters.extend(job_recruiters)
                except Exception as e:
                    logger.warning(f"Error scraping job board {url}: {str(e)}")
                    continue
                
                await asyncio.sleep(3)  # Rate limiting
            
            return recruiters
            
        except Exception as e:
            logger.error(f"Error finding job board recruiters: {str(e)}")
            return []
    
    async def scrape_job_board(self, url: str, company_name: str) -> List[Dict[str, Any]]:
        """
        Scrape job board for recruiter information
        """
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                recruiters = []
                
                # Look for contact information in job postings
                job_cards = soup.find_all(['div', 'article'], class_=re.compile(r'job|posting', re.I))
                
                for job_card in job_cards:
                    # Look for contact details
                    contact_info = job_card.find_all(string=re.compile(r'contact|apply|recruiter', re.I))
                    
                    for contact in contact_info:
                        # Extract email from contact information
                        emails = self.extract_emails_from_html(str(contact))
                        
                        for email in emails:
                            recruiter_data = {
                                'email': email,
                                'company': company_name,
                                'recruiter_type': RecruiterType.INTERNAL.value,
                                'found_at': datetime.utcnow().isoformat(),
                                'source': 'job_board'
                            }
                            recruiters.append(recruiter_data)
                
                return recruiters
                
        except Exception as e:
            logger.error(f"Error scraping job board: {str(e)}")
            return []
    
    async def deduplicate_recruiters(self, recruiters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate recruiters based on email and LinkedIn URL
        """
        try:
            seen_emails = set()
            seen_linkedin_urls = set()
            unique_recruiters = []
            
            for recruiter in recruiters:
                email = recruiter.get('email')
                linkedin_url = recruiter.get('linkedin_url')
                
                is_duplicate = False
                
                if email and email in seen_emails:
                    is_duplicate = True
                elif linkedin_url and linkedin_url in seen_linkedin_urls:
                    is_duplicate = True
                
                if not is_duplicate:
                    if email:
                        seen_emails.add(email)
                    if linkedin_url:
                        seen_linkedin_urls.add(linkedin_url)
                    
                    unique_recruiters.append(recruiter)
            
            return unique_recruiters
            
        except Exception as e:
            logger.error(f"Error deduplicating recruiters: {str(e)}")
            return recruiters
    
    async def enrich_recruiter_data(self, recruiters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich recruiter data with additional information
        """
        try:
            enriched_recruiters = []
            
            for recruiter in recruiters:
                try:
                    # Get LinkedIn profile data if available
                    if recruiter.get('linkedin_url'):
                        async with LinkedInAutomation(self.db_client) as linkedin:
                            profile_data = await linkedin.get_profile_insights(recruiter['linkedin_url'])
                            
                            if profile_data:
                                recruiter.update({
                                    'response_rate': profile_data.get('response_likelihood', 0.5),
                                    'profile_data': profile_data
                                })
                    
                    # Analyze specializations from title
                    title = recruiter.get('title', '')
                    specializations = self.extract_specializations(title)
                    recruiter['specializations'] = specializations
                    
                    # Determine seniority level
                    seniority_level = self.determine_seniority_level(title)
                    recruiter['seniority_levels'] = [seniority_level]
                    
                    # Set default values
                    recruiter.setdefault('name', recruiter.get('email', '').split('@')[0].title())
                    recruiter.setdefault('is_active', True)
                    recruiter.setdefault('total_contacts', 0)
                    recruiter.setdefault('successful_contacts', 0)
                    
                    enriched_recruiters.append(recruiter)
                    
                except Exception as e:
                    logger.warning(f"Error enriching recruiter data: {str(e)}")
                    enriched_recruiters.append(recruiter)
            
            return enriched_recruiters
            
        except Exception as e:
            logger.error(f"Error enriching recruiter data: {str(e)}")
            return recruiters
    
    def extract_specializations(self, title: str) -> List[str]:
        """
        Extract specializations from job title
        """
        try:
            specializations = []
            title_lower = title.lower()
            
            # Technical specializations
            if any(word in title_lower for word in ['technical', 'tech', 'software', 'engineering', 'developer']):
                specializations.append('Technology')
            
            # Sales specializations
            if any(word in title_lower for word in ['sales', 'business development', 'account']):
                specializations.append('Sales')
            
            # Marketing specializations
            if any(word in title_lower for word in ['marketing', 'digital', 'brand', 'content']):
                specializations.append('Marketing')
            
            # Finance specializations
            if any(word in title_lower for word in ['finance', 'accounting', 'financial']):
                specializations.append('Finance')
            
            # Executive specializations
            if any(word in title_lower for word in ['executive', 'c-level', 'director', 'vp', 'president']):
                specializations.append('Executive')
            
            return specializations or ['General']
            
        except Exception as e:
            logger.error(f"Error extracting specializations: {str(e)}")
            return ['General']
    
    def determine_seniority_level(self, title: str) -> str:
        """
        Determine seniority level from job title
        """
        try:
            title_lower = title.lower()
            
            if any(word in title_lower for word in ['senior', 'sr', 'lead', 'principal']):
                return 'Senior'
            elif any(word in title_lower for word in ['director', 'head', 'vp', 'vice president']):
                return 'Executive'
            elif any(word in title_lower for word in ['junior', 'jr', 'associate', 'coordinator']):
                return 'Junior'
            else:
                return 'Mid'
                
        except Exception as e:
            logger.error(f"Error determining seniority level: {str(e)}")
            return 'Mid'
    
    async def save_recruiter(self, recruiter_data: Dict[str, Any]) -> str:
        """
        Save recruiter to database
        """
        try:
            recruiter = Recruiter(**recruiter_data)
            
            # Check if recruiter already exists
            existing_recruiter = await self.db.recruiters.find_one({
                "$or": [
                    {"email": recruiter.email},
                    {"linkedin_url": recruiter.linkedin_url}
                ]
            })
            
            if existing_recruiter:
                # Update existing recruiter
                await self.db.recruiters.update_one(
                    {"id": existing_recruiter['id']},
                    {"$set": recruiter.dict(exclude={'id', 'created_at'})}
                )
                return existing_recruiter['id']
            else:
                # Insert new recruiter
                result = await self.db.recruiters.insert_one(recruiter.dict())
                return recruiter.id
                
        except Exception as e:
            logger.error(f"Error saving recruiter: {str(e)}")
            raise
    
    async def research_recruiter(self, recruiter_id: str) -> Dict[str, Any]:
        """
        Perform comprehensive research on a recruiter
        """
        try:
            recruiter = await self.db.recruiters.find_one({"id": recruiter_id})
            if not recruiter:
                logger.error(f"Recruiter not found: {recruiter_id}")
                return {}
            
            research_data = {}
            
            # LinkedIn profile research
            if recruiter.get('linkedin_url'):
                async with LinkedInAutomation(self.db_client) as linkedin:
                    profile_data = await linkedin.scrape_recruiter_profile(recruiter['linkedin_url'])
                    if profile_data:
                        research_data['linkedin_profile'] = profile_data
            
            # Company research
            if recruiter.get('company_domain'):
                company_data = await self.research_company(recruiter['company_domain'])
                research_data['company_info'] = company_data
            
            # Email validation
            if recruiter.get('email'):
                email_valid = await self.validate_email(recruiter['email'])
                research_data['email_validation'] = email_valid
            
            # Save research data
            research_record = RecruiterResearch(
                recruiter_id=recruiter_id,
                research_type="comprehensive",
                data_source="multiple",
                research_data=research_data,
                confidence_score=self.calculate_confidence_score(research_data)
            )
            
            await self.db.recruiter_research.insert_one(research_record.dict())
            
            return research_data
            
        except Exception as e:
            logger.error(f"Error researching recruiter: {str(e)}")
            return {}
    
    async def research_company(self, domain: str) -> Dict[str, Any]:
        """
        Research company information
        """
        try:
            company_data = {}
            
            # Scrape company website
            company_url = f"https://{domain}"
            
            async with self.session.get(company_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract company information
                    company_data['title'] = soup.find('title').get_text() if soup.find('title') else ''
                    company_data['description'] = soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else ''
                    
                    # Look for company size indicators
                    size_indicators = soup.find_all(string=re.compile(r'\d+\+?\s*(employees|people|team members)', re.I))
                    if size_indicators:
                        company_data['size_indicators'] = [indicator.strip() for indicator in size_indicators]
                    
                    # Look for locations
                    locations = soup.find_all(string=re.compile(r'(headquarters|office|location)', re.I))
                    if locations:
                        company_data['locations'] = [location.strip() for location in locations]
            
            return company_data
            
        except Exception as e:
            logger.error(f"Error researching company: {str(e)}")
            return {}
    
    async def validate_email(self, email: str) -> Dict[str, Any]:
        """
        Validate email address
        """
        try:
            # Basic email format validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            is_valid_format = bool(re.match(email_pattern, email))
            
            # Extract domain
            domain = email.split('@')[1] if '@' in email else ''
            
            return {
                'is_valid_format': is_valid_format,
                'domain': domain,
                'is_business_email': not any(domain.endswith(provider) for provider in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']),
                'validated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating email: {str(e)}")
            return {'is_valid_format': False}
    
    def calculate_confidence_score(self, research_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score for research data
        """
        try:
            score = 0.0
            
            # LinkedIn profile data
            if research_data.get('linkedin_profile'):
                score += 0.4
            
            # Company information
            if research_data.get('company_info'):
                score += 0.3
            
            # Email validation
            if research_data.get('email_validation', {}).get('is_valid_format'):
                score += 0.2
            
            # Business email
            if research_data.get('email_validation', {}).get('is_business_email'):
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 0.5
    
    async def bulk_research_recruiters(self, company_names: List[str], 
                                     limit_per_company: int = 10) -> List[Dict[str, Any]]:
        """
        Perform bulk research for multiple companies
        """
        try:
            all_recruiters = []
            
            for company_name in company_names:
                try:
                    recruiters = await self.find_company_recruiters(
                        company_name=company_name,
                        limit=limit_per_company
                    )
                    
                    # Save recruiters to database
                    for recruiter in recruiters:
                        recruiter_id = await self.save_recruiter(recruiter)
                        recruiter['id'] = recruiter_id
                        all_recruiters.append(recruiter)
                    
                    logger.info(f"Found {len(recruiters)} recruiters for {company_name}")
                    
                except Exception as e:
                    logger.error(f"Error researching {company_name}: {str(e)}")
                    continue
                
                # Rate limiting
                await asyncio.sleep(5)
            
            return all_recruiters
            
        except Exception as e:
            logger.error(f"Error in bulk research: {str(e)}")
            return []
    
    async def get_recruiter_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about recruited recruiters
        """
        try:
            total_recruiters = await self.db.recruiters.count_documents({})
            active_recruiters = await self.db.recruiters.count_documents({"is_active": True})
            
            # Group by recruiter type
            type_stats = {}
            for recruiter_type in RecruiterType:
                count = await self.db.recruiters.count_documents({"recruiter_type": recruiter_type.value})
                type_stats[recruiter_type.value] = count
            
            # Group by specialization
            specialization_stats = {}
            recruiters = await self.db.recruiters.find({}, {"specializations": 1}).to_list(length=None)
            
            for recruiter in recruiters:
                for specialization in recruiter.get('specializations', []):
                    specialization_stats[specialization] = specialization_stats.get(specialization, 0) + 1
            
            return {
                'total_recruiters': total_recruiters,
                'active_recruiters': active_recruiters,
                'type_stats': type_stats,
                'specialization_stats': specialization_stats,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting recruiter statistics: {str(e)}")
            return {}