"""
Elite JobHunter X - Indeed Job Scraper
Advanced stealth scraping for Indeed job listings
"""

import asyncio
import re
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urljoin, quote_plus
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page
import uuid

from .job_scraper import BaseJobScraper, JobListing, StealthScrapingConfig

logger = logging.getLogger(__name__)

class IndeedScraper(BaseJobScraper):
    """Advanced Indeed job scraper with stealth capabilities"""
    
    def __init__(self, config: StealthScrapingConfig):
        super().__init__(config)
        self.base_url = "https://www.indeed.com"
        self.search_url = "https://www.indeed.com/jobs"
        self.source_name = "indeed"
        
        # Indeed-specific selectors
        self.selectors = {
            'job_cards': '[data-jk]',
            'job_title': '[data-testid="job-title"]',
            'company_name': '[data-testid="company-name"]',
            'location': '[data-testid="job-location"]',
            'salary': '[data-testid="salary-snippet"]',
            'job_snippet': '[data-testid="job-snippet"]',
            'post_date': '[data-testid="job-posted-date"]',
            'job_type': '[data-testid="job-type-text"]',
            'apply_button': '[data-testid="apply-button"]',
            'next_page': '[data-testid="pagination-page-next"]',
            'job_description': '#jobDescriptionText',
            'company_rating': '[data-testid="rating"]',
            'remote_tag': '[data-testid="remote-tag"]',
            'benefits': '[data-testid="benefits"]'
        }
        
        # Common search parameters
        self.default_params = {
            'q': 'software developer',
            'l': 'Remote',
            'sort': 'date',
            'radius': '25',
            'fromage': '7'  # Last 7 days
        }
    
    def build_search_url(self, params: Dict[str, Any]) -> str:
        """Build Indeed search URL with parameters"""
        search_params = {**self.default_params, **params}
        
        # URL encode parameters
        query_parts = []
        for key, value in search_params.items():
            if value:
                query_parts.append(f"{key}={quote_plus(str(value))}")
        
        query_string = "&".join(query_parts)
        return f"{self.search_url}?{query_string}"
    
    def parse_posted_date(self, date_str: str) -> datetime:
        """Parse Indeed's posted date format"""
        if not date_str:
            return datetime.now()
        
        date_str = date_str.lower().strip()
        now = datetime.now()
        
        # Handle different date formats
        if 'just posted' in date_str or 'today' in date_str:
            return now
        elif 'yesterday' in date_str:
            return now - timedelta(days=1)
        elif 'days ago' in date_str:
            days_match = re.search(r'(\d+)', date_str)
            if days_match:
                days = int(days_match.group(1))
                return now - timedelta(days=days)
        elif 'hours ago' in date_str:
            hours_match = re.search(r'(\d+)', date_str)
            if hours_match:
                hours = int(hours_match.group(1))
                return now - timedelta(hours=hours)
        
        return now
    
    def extract_salary_info(self, salary_element) -> Optional[str]:
        """Extract and normalize salary information"""
        if not salary_element:
            return None
        
        salary_text = salary_element.get_text(strip=True)
        
        # Clean up salary text
        salary_text = re.sub(r'\s+', ' ', salary_text)
        salary_text = re.sub(r'[^\d.,\-\$k per hour year month]', ' ', salary_text)
        
        return salary_text if salary_text else None
    
    def extract_job_type(self, job_element) -> str:
        """Extract job type (full-time, part-time, etc.)"""
        job_type_element = job_element.select_one(self.selectors['job_type'])
        if job_type_element:
            return job_type_element.get_text(strip=True).lower()
        
        # Try to infer from description
        description = job_element.get_text().lower()
        if 'full-time' in description or 'full time' in description:
            return 'full-time'
        elif 'part-time' in description or 'part time' in description:
            return 'part-time'
        elif 'contract' in description:
            return 'contract'
        elif 'internship' in description:
            return 'internship'
        
        return 'full-time'  # Default
    
    def extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description"""
        skills = []
        
        # Common tech skills to look for
        tech_skills = [
            'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'go', 'rust',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'html', 'css', 'sass', 'less', 'webpack', 'babel', 'typescript',
            'linux', 'unix', 'agile', 'scrum', 'ci/cd', 'devops', 'machine learning',
            'ai', 'data science', 'tensorflow', 'pytorch', 'pandas', 'numpy'
        ]
        
        description_lower = description.lower()
        
        for skill in tech_skills:
            if skill in description_lower:
                skills.append(skill)
        
        return list(set(skills))  # Remove duplicates
    
    def extract_experience_level(self, description: str) -> str:
        """Extract experience level from job description"""
        description_lower = description.lower()
        
        if any(term in description_lower for term in ['entry level', 'junior', 'associate', '0-2 years']):
            return 'entry'
        elif any(term in description_lower for term in ['senior', 'sr.', 'lead', '5+ years', 'expert']):
            return 'senior'
        elif any(term in description_lower for term in ['mid level', 'mid-level', '2-5 years', 'intermediate']):
            return 'mid'
        elif any(term in description_lower for term in ['principal', 'staff', 'architect', '10+ years']):
            return 'principal'
        
        return 'mid'  # Default
    
    def extract_benefits(self, description: str) -> List[str]:
        """Extract benefits from job description"""
        benefits = []
        
        benefit_keywords = [
            'health insurance', 'dental insurance', 'vision insurance',
            '401k', 'retirement plan', 'pension', 'pto', 'vacation',
            'sick leave', 'flexible schedule', 'remote work', 'work from home',
            'gym membership', 'wellness program', 'stock options',
            'equity', 'bonus', 'commission', 'life insurance',
            'disability insurance', 'tuition reimbursement', 'professional development'
        ]
        
        description_lower = description.lower()
        
        for benefit in benefit_keywords:
            if benefit in description_lower:
                benefits.append(benefit)
        
        return list(set(benefits))
    
    async def get_job_urls(self, page: Page) -> List[str]:
        """Extract job URLs from Indeed search results"""
        try:
            # Wait for job cards to load
            await page.wait_for_selector(self.selectors['job_cards'], timeout=10000)
            
            # Get all job cards
            job_cards = await page.locator(self.selectors['job_cards']).all()
            job_urls = []
            
            for card in job_cards:
                try:
                    # Get job ID from data-jk attribute
                    job_id = await card.get_attribute('data-jk')
                    if job_id:
                        job_url = f"{self.base_url}/viewjob?jk={job_id}"
                        job_urls.append(job_url)
                except Exception as e:
                    logger.warning(f"Failed to extract job URL from card: {e}")
                    continue
            
            logger.info(f"Found {len(job_urls)} job URLs on page")
            return job_urls
            
        except Exception as e:
            logger.error(f"Failed to extract job URLs: {e}")
            return []
    
    async def scrape_job_listing(self, page: Page, job_url: str) -> Optional[JobListing]:
        """Scrape a single job listing from Indeed"""
        try:
            # Navigate to job page
            await self.safe_page_load(page, job_url, self.selectors['job_description'])
            
            # Check for CAPTCHA
            if await self.detect_captcha(page):
                logger.warning(f"CAPTCHA detected on job page: {job_url}")
                return None
            
            # Extract job data
            page_content = await page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Basic job information
            title_elem = soup.select_one(self.selectors['job_title'])
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
            
            company_elem = soup.select_one(self.selectors['company_name'])
            company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
            
            location_elem = soup.select_one(self.selectors['location'])
            location = location_elem.get_text(strip=True) if location_elem else "Unknown Location"
            
            # Job description
            desc_elem = soup.select_one(self.selectors['job_description'])
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Salary information
            salary_elem = soup.select_one(self.selectors['salary'])
            salary = self.extract_salary_info(salary_elem)
            
            # Posted date
            date_elem = soup.select_one(self.selectors['post_date'])
            posted_date = self.parse_posted_date(date_elem.get_text(strip=True) if date_elem else "")
            
            # Job type
            job_type = self.extract_job_type(soup)
            
            # Remote work
            remote_elem = soup.select_one(self.selectors['remote_tag'])
            remote = remote_elem is not None or 'remote' in description.lower()
            
            # Extract additional data
            skills = self.extract_skills(description)
            experience_level = self.extract_experience_level(description)
            benefits = self.extract_benefits(description)
            
            # Build requirements from description
            requirements = description[:1000] + "..." if len(description) > 1000 else description
            
            # Create job listing object
            job_listing = JobListing(
                id=str(uuid.uuid4()),
                title=title,
                company=company,
                location=location,
                description=description,
                requirements=requirements,
                salary=salary,
                job_type=job_type,
                remote=remote,
                posted_date=posted_date,
                apply_url=job_url,
                source=self.source_name,
                experience_level=experience_level,
                skills=skills,
                benefits=benefits,
                raw_html=page_content,
                scraped_at=datetime.now()
            )
            
            logger.info(f"Scraped job: {title} at {company}")
            return job_listing
            
        except Exception as e:
            logger.error(f"Failed to scrape job {job_url}: {e}")
            return None
    
    async def scrape_jobs(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to scrape Indeed jobs"""
        results = {
            'jobs_found': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'pages_scraped': 0,
            'search_params': search_params
        }
        
        max_pages = search_params.get('max_pages', 5)
        max_jobs_per_page = search_params.get('max_jobs_per_page', 15)
        
        async with async_playwright() as playwright:
            context = await self.create_stealth_context(playwright)
            
            try:
                for page_num in range(max_pages):
                    page = await self.setup_stealth_page(context)
                    
                    try:
                        # Build search URL for current page
                        search_url = self.build_search_url(search_params)
                        if page_num > 0:
                            search_url += f"&start={page_num * 10}"
                        
                        logger.info(f"Scraping Indeed page {page_num + 1}: {search_url}")
                        
                        # Load search results page
                        await self.safe_page_load(page, search_url, self.selectors['job_cards'])
                        
                        # Check for rate limiting or blocking
                        if await self.detect_captcha(page):
                            logger.warning("CAPTCHA detected, stopping scraping")
                            break
                        
                        # Get job URLs from current page
                        job_urls = await self.get_job_urls(page)
                        
                        if not job_urls:
                            logger.warning(f"No job URLs found on page {page_num + 1}")
                            break
                        
                        results['jobs_found'] += len(job_urls)
                        
                        # Scrape each job (limit to max_jobs_per_page)
                        for i, job_url in enumerate(job_urls[:max_jobs_per_page]):
                            try:
                                # Human-like delay between jobs
                                await self.human_like_delay(3, 8)
                                
                                # Scrape individual job
                                job_listing = await self.scrape_job_listing(page, job_url)
                                
                                if job_listing:
                                    # Save to database
                                    if await self.save_job_to_db(job_listing):
                                        results['successful_scrapes'] += 1
                                    else:
                                        results['failed_scrapes'] += 1
                                else:
                                    results['failed_scrapes'] += 1
                                
                                # Progress logging
                                if (i + 1) % 5 == 0:
                                    logger.info(f"Processed {i + 1}/{len(job_urls)} jobs on page {page_num + 1}")
                                
                            except Exception as e:
                                logger.error(f"Error processing job {job_url}: {e}")
                                results['failed_scrapes'] += 1
                                continue
                        
                        results['pages_scraped'] += 1
                        
                        # Longer delay between pages
                        await self.human_like_delay(10, 20)
                        
                    except Exception as e:
                        logger.error(f"Error on page {page_num + 1}: {e}")
                        continue
                    
                    finally:
                        await page.close()
                
            except Exception as e:
                logger.error(f"Critical error during scraping: {e}")
                results['error'] = str(e)
            
            finally:
                await context.close()
        
        logger.info(f"Indeed scraping completed: {results}")
        return results

class IndeedJobTypes:
    """Indeed job type constants"""
    FULL_TIME = "fulltime"
    PART_TIME = "parttime"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"

class IndeedLocations:
    """Common location searches for Indeed"""
    REMOTE = "Remote"
    NEW_YORK = "New York, NY"
    SAN_FRANCISCO = "San Francisco, CA"
    SEATTLE = "Seattle, WA"
    CHICAGO = "Chicago, IL"
    BOSTON = "Boston, MA"
    AUSTIN = "Austin, TX"
    LOS_ANGELES = "Los Angeles, CA"

class IndeedSearchBuilder:
    """Helper class to build Indeed search parameters"""
    
    def __init__(self):
        self.params = {}
    
    def query(self, q: str):
        """Set search query"""
        self.params['q'] = q
        return self
    
    def location(self, location: str):
        """Set location"""
        self.params['l'] = location
        return self
    
    def job_type(self, job_type: str):
        """Set job type"""
        self.params['jt'] = job_type
        return self
    
    def salary(self, min_salary: int):
        """Set minimum salary"""
        self.params['salary'] = min_salary
        return self
    
    def experience_level(self, level: str):
        """Set experience level"""
        self.params['explvl'] = level
        return self
    
    def date_posted(self, days: int):
        """Set date posted (last N days)"""
        self.params['fromage'] = days
        return self
    
    def radius(self, miles: int):
        """Set search radius"""
        self.params['radius'] = miles
        return self
    
    def sort_by(self, sort_type: str = "date"):
        """Set sort order (date, relevance)"""
        self.params['sort'] = sort_type
        return self
    
    def remote_only(self):
        """Filter for remote jobs only"""
        self.params['remotejob'] = 1
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the search parameters"""
        return self.params.copy()

# Helper function to create common search configurations
def create_tech_job_search(
    title: str = "Software Developer",
    location: str = "Remote",
    experience: str = "entry_level",
    max_pages: int = 3
) -> Dict[str, Any]:
    """Create a common tech job search configuration"""
    
    builder = IndeedSearchBuilder()
    search_params = (builder
                    .query(title)
                    .location(location)
                    .date_posted(7)  # Last 7 days
                    .sort_by("date")
                    .radius(25)
                    .build())
    
    search_params['max_pages'] = max_pages
    search_params['max_jobs_per_page'] = 15
    
    return search_params