"""
Elite JobHunter X - Base Job Scraping Service
Advanced stealth web scraping with Playwright and proxy rotation
"""

import asyncio
import random
import time
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import json
import os
from dataclasses import dataclass, asdict
from playwright.async_api import async_playwright, BrowserContext, Page
from playwright_stealth import stealth
from fake_useragent import UserAgent
from pymongo import MongoClient
from bson import ObjectId
import uuid
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    """Structured job listing data"""
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: str
    salary: Optional[str]
    job_type: str  # full-time, part-time, contract, etc.
    remote: bool
    posted_date: datetime
    apply_url: str
    source: str  # linkedin, indeed, glassdoor, etc.
    experience_level: str
    skills: List[str]
    benefits: List[str]
    raw_html: str
    scraped_at: datetime
    
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        # Convert datetime objects to ISO format
        data['posted_date'] = self.posted_date.isoformat() if self.posted_date else None
        data['scraped_at'] = self.scraped_at.isoformat()
        return data

class StealthScrapingConfig:
    """Configuration for stealth scraping"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        self.viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1440, 'height': 900},
            {'width': 1536, 'height': 864}
        ]
        
        self.proxy_list = [
            os.environ.get('PROXY_HTTP', 'http://104.27.45.90:80'),
            # Add more proxies as needed
        ]
        
        self.delay_range = (
            int(os.environ.get('SCRAPING_DELAY_MIN', '2')),
            int(os.environ.get('SCRAPING_DELAY_MAX', '5'))
        )
        
        self.max_concurrent = int(os.environ.get('MAX_CONCURRENT_JOBS', '3'))

class BaseJobScraper:
    """Base class for job scrapers with advanced stealth features"""
    
    def __init__(self, config: StealthScrapingConfig):
        self.config = config
        self.session_id = str(uuid.uuid4())
        self.db_client = MongoClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
        self.db = self.db_client[os.environ.get('DB_NAME', 'jobhunter_x_db')]
        self.jobs_collection = self.db['jobs_raw']
        self.ua = UserAgent()
        
        # Create indexes for efficient querying
        self.jobs_collection.create_index([('apply_url', 1)], unique=True)
        self.jobs_collection.create_index([('source', 1), ('posted_date', -1)])
        self.jobs_collection.create_index([('scraped_at', -1)])
        
        logger.info(f"Initialized scraper with session ID: {self.session_id}")
    
    async def create_stealth_context(self, playwright) -> BrowserContext:
        """Create a stealth browser context with randomized settings"""
        
        # Randomize settings
        user_agent = random.choice(self.config.user_agents)
        viewport = random.choice(self.config.viewports)
        proxy = random.choice(self.config.proxy_list) if self.config.proxy_list else None
        
        # Browser launch args for stealth
        browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--single-process',
            '--disable-gpu',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-default-apps',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
        ]
        
        # Proxy configuration
        proxy_config = None
        if proxy:
            parsed_proxy = urlparse(proxy)
            proxy_config = {
                'server': proxy,
                'username': parsed_proxy.username,
                'password': parsed_proxy.password
            }
        
        # Launch browser
        browser = await playwright.chromium.launch(
            headless=True,
            args=browser_args,
            proxy=proxy_config
        )
        
        # Create context with stealth settings
        context = await browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # New York
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        return context
    
    async def setup_stealth_page(self, context: BrowserContext) -> Page:
        """Setup a stealth page with additional anti-detection measures"""
        
        page = await context.new_page()
        
        # Apply stealth plugin
        await stealth(page)
        
        # Override webdriver property
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        # Override chrome property
        await page.add_init_script("""
            window.chrome = {
                runtime: {},
                app: { isInstalled: false },
                csi: function() {},
                loadTimes: function() {},
            };
        """)
        
        # Override plugins
        await page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)
        
        # Override languages
        await page.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
        
        # Set random screen resolution
        await page.add_init_script("""
            Object.defineProperty(screen, 'width', {
                get: () => Math.floor(Math.random() * 400) + 1200,
            });
            Object.defineProperty(screen, 'height', {
                get: () => Math.floor(Math.random() * 400) + 800,
            });
        """)
        
        return page
    
    async def human_like_delay(self, min_delay: Optional[int] = None, max_delay: Optional[int] = None):
        """Add human-like delays between actions"""
        min_delay = min_delay or self.config.delay_range[0]
        max_delay = max_delay or self.config.delay_range[1]
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    async def random_mouse_movement(self, page: Page):
        """Add random mouse movements to simulate human behavior"""
        viewport = page.viewport_size
        if viewport:
            x = random.randint(0, viewport['width'])
            y = random.randint(0, viewport['height'])
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def smart_scroll(self, page: Page, target_element: Optional[str] = None):
        """Perform human-like scrolling to load dynamic content"""
        if target_element:
            try:
                await page.locator(target_element).scroll_into_view_if_needed()
            except Exception as e:
                logger.warning(f"Could not scroll to element {target_element}: {e}")
        
        # Random scroll pattern
        scroll_patterns = [
            lambda: page.mouse.wheel(0, random.randint(200, 800)),
            lambda: page.keyboard.press('PageDown'),
            lambda: page.keyboard.press('End'),
        ]
        
        for _ in range(random.randint(2, 5)):
            pattern = random.choice(scroll_patterns)
            await pattern()
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def safe_page_load(self, page: Page, url: str, wait_for: Optional[str] = None):
        """Safely load a page with retry logic and error handling"""
        try:
            # Navigate to URL
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for specific element if provided
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=15000)
            
            # Add human-like delay
            await self.human_like_delay()
            
            # Random mouse movement
            await self.random_mouse_movement(page)
            
            logger.info(f"Successfully loaded page: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load page {url}: {e}")
            raise
    
    async def extract_job_data(self, page: Page, job_element) -> Optional[JobListing]:
        """Extract job data from a page element - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement extract_job_data method")
    
    async def get_job_urls(self, page: Page) -> List[str]:
        """Extract job URLs from a listing page - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement get_job_urls method")
    
    async def scrape_job_listing(self, page: Page, job_url: str) -> Optional[JobListing]:
        """Scrape a single job listing - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement scrape_job_listing method")
    
    async def save_job_to_db(self, job: JobListing) -> bool:
        """Save job listing to database"""
        try:
            # Check if job already exists
            existing = self.jobs_collection.find_one({'apply_url': job.apply_url})
            if existing:
                logger.info(f"Job already exists: {job.title} at {job.company}")
                return False
            
            # Insert new job
            job_dict = job.to_dict()
            job_dict['_id'] = str(uuid.uuid4())
            job_dict['session_id'] = self.session_id
            
            self.jobs_collection.insert_one(job_dict)
            logger.info(f"Saved job: {job.title} at {job.company}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save job to database: {e}")
            return False
    
    async def get_scraped_jobs_count(self, source: str, since_hours: int = 24) -> int:
        """Get count of jobs scraped from a source in the last N hours"""
        since_time = datetime.now() - timedelta(hours=since_hours)
        count = self.jobs_collection.count_documents({
            'source': source,
            'scraped_at': {'$gte': since_time.isoformat()}
        })
        return count
    
    async def cleanup_old_jobs(self, days_old: int = 30):
        """Remove old job listings from database"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        result = self.jobs_collection.delete_many({
            'scraped_at': {'$lt': cutoff_date.isoformat()}
        })
        logger.info(f"Cleaned up {result.deleted_count} old job listings")
    
    async def detect_captcha(self, page: Page) -> bool:
        """Detect if a CAPTCHA is present on the page"""
        captcha_indicators = [
            'captcha',
            'recaptcha',
            'hcaptcha',
            'I am not a robot',
            'verify you are human',
            'security check',
            'unusual traffic'
        ]
        
        page_content = await page.content()
        page_text = page_content.lower()
        
        for indicator in captcha_indicators:
            if indicator in page_text:
                logger.warning(f"CAPTCHA detected: {indicator}")
                return True
        
        return False
    
    async def handle_rate_limit(self, page: Page, delay_multiplier: float = 2.0):
        """Handle rate limiting by increasing delays"""
        current_delay = self.config.delay_range[1] * delay_multiplier
        logger.warning(f"Rate limit detected, increasing delay to {current_delay} seconds")
        await asyncio.sleep(current_delay)
    
    def close(self):
        """Close database connection"""
        if self.db_client:
            self.db_client.close()
            logger.info("Database connection closed")

class JobScrapingManager:
    """Manager for coordinating multiple job scrapers"""
    
    def __init__(self):
        self.config = StealthScrapingConfig()
        self.scrapers = {}
        self.running_tasks = []
        self.results = {
            'total_jobs': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'captcha_encounters': 0,
            'rate_limits': 0,
            'sources': {}
        }
    
    def register_scraper(self, name: str, scraper_class):
        """Register a scraper class"""
        self.scrapers[name] = scraper_class
        logger.info(f"Registered scraper: {name}")
    
    async def run_scraper(self, scraper_name: str, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific scraper with given parameters"""
        if scraper_name not in self.scrapers:
            raise ValueError(f"Scraper {scraper_name} not registered")
        
        scraper_class = self.scrapers[scraper_name]
        scraper = scraper_class(self.config)
        
        try:
            results = await scraper.scrape_jobs(search_params)
            self.results['sources'][scraper_name] = results
            self.results['total_jobs'] += results.get('jobs_found', 0)
            self.results['successful_scrapes'] += results.get('successful_scrapes', 0)
            self.results['failed_scrapes'] += results.get('failed_scrapes', 0)
            
            logger.info(f"Scraper {scraper_name} completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Scraper {scraper_name} failed: {e}")
            self.results['failed_scrapes'] += 1
            return {'error': str(e)}
        finally:
            scraper.close()
    
    async def run_all_scrapers(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Run all registered scrapers concurrently"""
        tasks = []
        
        for scraper_name in self.scrapers:
            task = asyncio.create_task(
                self.run_scraper(scraper_name, search_params)
            )
            tasks.append(task)
        
        # Wait for all scrapers to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"All scrapers completed. Total results: {self.results}")
        return self.results
    
    def get_scraping_stats(self) -> Dict[str, Any]:
        """Get current scraping statistics"""
        return self.results.copy()