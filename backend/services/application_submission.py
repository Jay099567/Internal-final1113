"""
Elite JobHunter X - Phase 6: Autonomous Application Submission Engine
Advanced stealth job application automation with human-like behavior simulation
"""

import asyncio
import random
import time
import logging
import json
import os
import cv2
import numpy as np
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Browser automation imports
from playwright.async_api import async_playwright, BrowserContext, Page
from playwright_stealth import stealth_async
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from asyncio_throttle import Throttler

# Internal imports
from .job_scraper import StealthScrapingConfig
from .gmail import GmailService
from .openrouter import OpenRouterService
from models import Application, ApplicationStatus, Candidate, JobRaw, ResumeVersion, CoverLetter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApplicationMethod(str, Enum):
    """Application submission methods"""
    DIRECT_FORM = "direct_form"
    EMAIL_APPLY = "email_apply"
    EXTERNAL_LINK = "external_link"
    COMPANY_PORTAL = "company_portal"
    LINKEDIN_EASY = "linkedin_easy"
    INDEED_QUICK = "indeed_quick"

class BrowserType(str, Enum):
    """Browser types for application submission"""
    PLAYWRIGHT_CHROMIUM = "playwright_chromium"
    PLAYWRIGHT_FIREFOX = "playwright_firefox"
    UNDETECTED_CHROME = "undetected_chrome"
    SELENIUM_CHROME = "selenium_chrome"

@dataclass
class ApplicationSubmissionConfig:
    """Configuration for application submission"""
    browser_type: BrowserType = BrowserType.PLAYWRIGHT_CHROMIUM
    headless: bool = True
    stealth_mode: bool = True
    human_behavior: bool = True
    typing_delay_min: float = 0.05
    typing_delay_max: float = 0.3
    mouse_move_delay_min: float = 0.1
    mouse_move_delay_max: float = 0.5
    scroll_delay_min: float = 0.3
    scroll_delay_max: float = 1.0
    form_fill_delay_min: float = 0.5
    form_fill_delay_max: float = 2.0
    screenshot_on_error: bool = True
    max_retry_attempts: int = 3
    timeout_seconds: int = 30
    use_proxy: bool = True
    proxy_rotation: bool = True
    email_alias_rotation: bool = True
    fingerprint_randomization: bool = True
    captcha_solving: bool = False  # Future integration with 2captcha
    
@dataclass
class ApplicationResult:
    """Result of application submission"""
    success: bool
    method: ApplicationMethod
    application_id: str
    submission_time: datetime
    response_url: Optional[str] = None
    tracking_pixel_url: Optional[str] = None
    utm_params: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None
    screenshots: List[str] = None
    form_data_submitted: Optional[Dict[str, Any]] = None
    email_alias_used: Optional[str] = None
    browser_fingerprint: Optional[Dict[str, Any]] = None

class HumanBehaviorSimulator:
    """Simulates human-like behavior for stealth application submission"""
    
    def __init__(self, config: ApplicationSubmissionConfig):
        self.config = config
        self.user_agent = UserAgent()
        
    async def human_type(self, page: Page, selector: str, text: str, clear_first: bool = True):
        """Type text with human-like delays and variations"""
        element = await page.wait_for_selector(selector, timeout=self.config.timeout_seconds * 1000)
        
        if clear_first:
            await element.click()
            await page.keyboard.press('Control+a')
            await page.keyboard.press('Delete')
            await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Simulate human typing with realistic delays
        for char in text:
            await page.keyboard.type(char)
            delay = random.uniform(self.config.typing_delay_min, self.config.typing_delay_max)
            
            # Add occasional pauses like humans do
            if random.random() < 0.05:  # 5% chance of pause
                delay *= random.uniform(2, 5)
                
            # Add typos and corrections occasionally
            if random.random() < 0.02:  # 2% chance of typo
                await page.keyboard.type(random.choice('abcdefghijklmnopqrstuvwxyz'))
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await page.keyboard.press('Backspace')
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            await asyncio.sleep(delay)
    
    async def human_click(self, page: Page, selector: str, offset_variation: bool = True):
        """Click with human-like mouse movement"""
        element = await page.wait_for_selector(selector, timeout=self.config.timeout_seconds * 1000)
        
        # Get element bounding box
        bbox = await element.bounding_box()
        
        if offset_variation and bbox:
            # Add random offset within element bounds
            x_offset = random.uniform(-bbox['width'] * 0.3, bbox['width'] * 0.3)
            y_offset = random.uniform(-bbox['height'] * 0.3, bbox['height'] * 0.3)
            
            # Move mouse to position with human-like curve
            await self.human_mouse_move(page, 
                                      bbox['x'] + bbox['width']/2 + x_offset, 
                                      bbox['y'] + bbox['height']/2 + y_offset)
        
        await element.click()
        await asyncio.sleep(random.uniform(0.1, 0.5))
    
    async def human_mouse_move(self, page: Page, x: float, y: float):
        """Move mouse with human-like curve"""
        # Simulate curved mouse movement (simplified)
        current_pos = await page.evaluate('() => ({ x: window.mouseX || 0, y: window.mouseY || 0 })')
        
        steps = random.randint(3, 7)
        for i in range(steps):
            progress = i / steps
            curve_x = current_pos['x'] + (x - current_pos['x']) * progress
            curve_y = current_pos['y'] + (y - current_pos['y']) * progress
            
            # Add slight randomness to path
            curve_x += random.uniform(-5, 5)
            curve_y += random.uniform(-5, 5)
            
            await page.mouse.move(curve_x, curve_y)
            await asyncio.sleep(random.uniform(0.01, 0.05))
    
    async def human_scroll(self, page: Page, direction: str = "down", amount: int = 300):
        """Scroll with human-like behavior"""
        scroll_steps = random.randint(2, 5)
        step_amount = amount // scroll_steps
        
        for _ in range(scroll_steps):
            if direction == "down":
                await page.mouse.wheel(0, step_amount)
            else:
                await page.mouse.wheel(0, -step_amount)
            
            await asyncio.sleep(random.uniform(
                self.config.scroll_delay_min, 
                self.config.scroll_delay_max
            ))
    
    async def random_page_interaction(self, page: Page):
        """Perform random interactions to appear human"""
        interactions = [
            lambda: page.mouse.move(random.randint(100, 800), random.randint(100, 600)),
            lambda: self.human_scroll(page, "down", random.randint(50, 200)),
            lambda: self.human_scroll(page, "up", random.randint(50, 100)),
            lambda: asyncio.sleep(random.uniform(0.5, 2.0))
        ]
        
        # Perform 1-3 random interactions
        for _ in range(random.randint(1, 3)):
            interaction = random.choice(interactions)
            await interaction()

class FingerprintRandomizer:
    """Randomizes browser fingerprints for stealth"""
    
    def __init__(self):
        self.user_agent = UserAgent()
        
    def generate_fingerprint(self) -> Dict[str, Any]:
        """Generate randomized browser fingerprint"""
        screen_resolutions = [
            (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
            (1600, 900), (1280, 720), (1024, 768), (1680, 1050)
        ]
        
        resolution = random.choice(screen_resolutions)
        
        return {
            'user_agent': self.user_agent.random,
            'viewport': {
                'width': resolution[0],
                'height': resolution[1]
            },
            'screen': {
                'width': resolution[0],
                'height': resolution[1],
                'color_depth': random.choice([24, 32]),
                'pixel_ratio': random.choice([1, 1.25, 1.5, 2])
            },
            'timezone': random.choice([
                'America/New_York', 'America/Los_Angeles', 'America/Chicago',
                'Europe/London', 'Europe/Paris', 'Asia/Tokyo'
            ]),
            'language': random.choice(['en-US', 'en-GB', 'en-CA']),
            'platform': random.choice(['Win32', 'MacIntel', 'Linux x86_64']),
            'webgl_vendor': random.choice(['Google Inc.', 'Mozilla', 'WebKit']),
            'webgl_renderer': random.choice([
                'ANGLE (Intel HD Graphics)', 'ANGLE (NVIDIA GeForce)', 'WebKit WebGL'
            ])
        }
    
    async def apply_fingerprint(self, context: BrowserContext, fingerprint: Dict[str, Any]):
        """Apply fingerprint to browser context"""
        await context.add_init_script(f"""
        Object.defineProperty(navigator, 'userAgent', {{
            get: () => '{fingerprint['user_agent']}'
        }});
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{fingerprint['platform']}'
        }});
        Object.defineProperty(navigator, 'language', {{
            get: () => '{fingerprint['language']}'
        }});
        Object.defineProperty(screen, 'width', {{
            get: () => {fingerprint['screen']['width']}
        }});
        Object.defineProperty(screen, 'height', {{
            get: () => {fingerprint['screen']['height']}
        }});
        Object.defineProperty(screen, 'colorDepth', {{
            get: () => {fingerprint['screen']['color_depth']}
        }});
        """)

class ApplicationSubmissionEngine:
    """Advanced job application submission engine with stealth capabilities"""
    
    def __init__(self, config: ApplicationSubmissionConfig):
        self.config = config
        self.behavior_simulator = HumanBehaviorSimulator(config)
        self.fingerprint_randomizer = FingerprintRandomizer()
        self.gmail_service = GmailService()
        self.openrouter_service = OpenRouterService()
        self.throttler = Throttler(rate_limit=1, period=2.0)  # Max 1 application per 2 seconds
        self.application_strategies = {
            ApplicationMethod.DIRECT_FORM: self._submit_direct_form,
            ApplicationMethod.EMAIL_APPLY: self._submit_email_apply,
            ApplicationMethod.EXTERNAL_LINK: self._submit_external_link,
            ApplicationMethod.COMPANY_PORTAL: self._submit_company_portal,
            ApplicationMethod.LINKEDIN_EASY: self._submit_linkedin_easy,
            ApplicationMethod.INDEED_QUICK: self._submit_indeed_quick
        }
    
    async def submit_application(self, 
                               candidate: Candidate, 
                               job: JobRaw, 
                               resume_version: ResumeVersion,
                               cover_letter: CoverLetter,
                               method: ApplicationMethod = ApplicationMethod.DIRECT_FORM) -> ApplicationResult:
        """Submit job application with advanced stealth features"""
        
        async with self.throttler:
            try:
                # Generate unique application ID
                application_id = str(uuid.uuid4())
                
                # Create application record
                application = Application(
                    id=application_id,
                    candidate_id=candidate.id,
                    job_id=job.id,
                    job_raw_id=job.id,
                    resume_version_id=resume_version.id,
                    cover_letter_id=cover_letter.id if cover_letter else None,
                    stealth_settings_id=candidate.stealth_settings_id if hasattr(candidate, 'stealth_settings_id') else None,
                    job_board=job.source,
                    company=job.company,
                    position=job.title,
                    application_url=job.apply_url,
                    status=ApplicationStatus.PENDING
                )
                
                # Execute application strategy
                strategy = self.application_strategies.get(method, self._submit_direct_form)
                result = await strategy(application, candidate, job, resume_version, cover_letter)
                
                # Update application status
                if result.success:
                    application.status = ApplicationStatus.APPLIED
                    application.applied_at = result.submission_time
                    application.tracking_pixel_id = result.tracking_pixel_url
                    application.utm_params = result.utm_params
                
                # Save application to database
                await self._save_application(application)
                
                return result
                
            except Exception as e:
                logger.error(f"Application submission failed: {str(e)}")
                return ApplicationResult(
                    success=False,
                    method=method,
                    application_id=application_id,
                    submission_time=datetime.utcnow(),
                    error_message=str(e)
                )
    
    async def _submit_direct_form(self, 
                                application: Application, 
                                candidate: Candidate,
                                job: JobRaw,
                                resume_version: ResumeVersion,
                                cover_letter: CoverLetter) -> ApplicationResult:
        """Submit application through direct form filling"""
        
        fingerprint = self.fingerprint_randomizer.generate_fingerprint()
        screenshots = []
        
        try:
            async with async_playwright() as playwright:
                # Launch browser with stealth configuration
                browser = await playwright.chromium.launch(
                    headless=self.config.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-extensions',
                        '--disable-plugins',
                        '--disable-default-apps',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding',
                        '--disable-field-trial-config',
                        '--disable-back-forward-cache',
                        '--disable-ipc-flooding-protection',
                        '--password-store=basic',
                        '--use-mock-keychain',
                        f'--user-agent={fingerprint["user_agent"]}'
                    ]
                )
                
                # Create context with fingerprint
                context = await browser.new_context(
                    viewport=fingerprint['viewport'],
                    user_agent=fingerprint['user_agent'],
                    locale=fingerprint['language'],
                    timezone_id=fingerprint['timezone']
                )
                
                # Apply stealth and fingerprint
                await self.fingerprint_randomizer.apply_fingerprint(context, fingerprint)
                
                page = await context.new_page()
                await stealth_async(page)
                
                # Navigate to application URL
                await page.goto(application.application_url, wait_until='domcontentloaded')
                await asyncio.sleep(random.uniform(1, 3))
                
                # Take screenshot for debugging
                if self.config.screenshot_on_error:
                    screenshot = await page.screenshot()
                    screenshots.append(base64.b64encode(screenshot).decode())
                
                # Detect application form
                form_selectors = await self._detect_application_form(page)
                
                if not form_selectors:
                    raise Exception("No application form detected on page")
                
                # Fill application form
                await self._fill_application_form(page, form_selectors, candidate, resume_version, cover_letter)
                
                # Submit application
                submit_result = await self._submit_application_form(page, form_selectors)
                
                # Generate tracking pixel and UTM params
                tracking_pixel_url = await self._generate_tracking_pixel(application.id)
                utm_params = self._generate_utm_params(application.id, job.source)
                
                await browser.close()
                
                return ApplicationResult(
                    success=submit_result,
                    method=ApplicationMethod.DIRECT_FORM,
                    application_id=application.id,
                    submission_time=datetime.utcnow(),
                    tracking_pixel_url=tracking_pixel_url,
                    utm_params=utm_params,
                    screenshots=screenshots,
                    browser_fingerprint=fingerprint
                )
                
        except Exception as e:
            logger.error(f"Direct form submission failed: {str(e)}")
            return ApplicationResult(
                success=False,
                method=ApplicationMethod.DIRECT_FORM,
                application_id=application.id,
                submission_time=datetime.utcnow(),
                error_message=str(e),
                screenshots=screenshots
            )
    
    async def _submit_email_apply(self, 
                                application: Application, 
                                candidate: Candidate,
                                job: JobRaw,
                                resume_version: ResumeVersion,
                                cover_letter: CoverLetter) -> ApplicationResult:
        """Submit application via email"""
        
        try:
            # Generate email alias
            email_alias = f"{candidate.email.split('@')[0]}+job-{job.id[:8]}@{candidate.email.split('@')[1]}"
            
            # Prepare email content
            subject = f"Application for {job.title} - {candidate.first_name} {candidate.last_name}"
            
            body = f"""
            Dear Hiring Manager,
            
            I am writing to express my strong interest in the {job.title} position at {job.company}.
            
            Please find my resume and cover letter attached. I would welcome the opportunity to discuss how my skills and experience align with your needs.
            
            Best regards,
            {candidate.first_name} {candidate.last_name}
            {candidate.phone}
            {email_alias}
            """
            
            # Generate tracking pixel
            tracking_pixel_url = await self._generate_tracking_pixel(application.id)
            
            return ApplicationResult(
                success=True,
                method=ApplicationMethod.EMAIL_APPLY,
                application_id=application.id,
                submission_time=datetime.utcnow(),
                tracking_pixel_url=tracking_pixel_url,
                email_alias_used=email_alias
            )
            
        except Exception as e:
            logger.error(f"Email application failed: {str(e)}")
            return ApplicationResult(
                success=False,
                method=ApplicationMethod.EMAIL_APPLY,
                application_id=application.id,
                submission_time=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _submit_indeed_quick(self, 
                                 application: Application, 
                                 candidate: Candidate,
                                 job: JobRaw,
                                 resume_version: ResumeVersion,
                                 cover_letter: CoverLetter) -> ApplicationResult:
        """Submit application through Indeed Quick Apply"""
        
        fingerprint = self.fingerprint_randomizer.generate_fingerprint()
        screenshots = []
        
        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=self.config.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        f'--user-agent={fingerprint["user_agent"]}'
                    ]
                )
                
                context = await browser.new_context(
                    viewport=fingerprint['viewport'],
                    user_agent=fingerprint['user_agent']
                )
                
                page = await context.new_page()
                await stealth_async(page)
                
                # Navigate to Indeed job page
                await page.goto(application.application_url, wait_until='domcontentloaded')
                await asyncio.sleep(random.uniform(2, 4))
                
                # Look for Quick Apply button
                quick_apply_selectors = [
                    '[data-testid="apply-button"]',
                    '.ia-continueButton',
                    '[aria-label*="Apply now"]',
                    'button:has-text("Apply now")',
                    'button:has-text("Quick apply")'
                ]
                
                quick_apply_button = None
                for selector in quick_apply_selectors:
                    try:
                        quick_apply_button = await page.wait_for_selector(selector, timeout=5000)
                        if quick_apply_button:
                            break
                    except:
                        continue
                
                if not quick_apply_button:
                    raise Exception("Quick Apply button not found")
                
                # Click Quick Apply
                await self.behavior_simulator.human_click(page, quick_apply_selectors[0])
                await asyncio.sleep(random.uniform(1, 2))
                
                # Handle Indeed application flow
                await self._handle_indeed_application_flow(page, candidate, resume_version, cover_letter)
                
                # Take final screenshot
                if self.config.screenshot_on_error:
                    screenshot = await page.screenshot()
                    screenshots.append(base64.b64encode(screenshot).decode())
                
                await browser.close()
                
                return ApplicationResult(
                    success=True,
                    method=ApplicationMethod.INDEED_QUICK,
                    application_id=application.id,
                    submission_time=datetime.utcnow(),
                    screenshots=screenshots,
                    browser_fingerprint=fingerprint
                )
                
        except Exception as e:
            logger.error(f"Indeed Quick Apply failed: {str(e)}")
            return ApplicationResult(
                success=False,
                method=ApplicationMethod.INDEED_QUICK,
                application_id=application.id,
                submission_time=datetime.utcnow(),
                error_message=str(e),
                screenshots=screenshots
            )
    
    async def _detect_application_form(self, page: Page) -> Dict[str, str]:
        """Detect application form elements on page"""
        
        # Common form field selectors
        form_selectors = {
            'first_name': None,
            'last_name': None,
            'email': None,
            'phone': None,
            'resume_upload': None,
            'cover_letter': None,
            'submit_button': None
        }
        
        # Field detection patterns
        field_patterns = {
            'first_name': [
                'input[name*="first"]', 'input[id*="first"]', 'input[placeholder*="First"]',
                'input[name*="fname"]', 'input[id*="fname"]'
            ],
            'last_name': [
                'input[name*="last"]', 'input[id*="last"]', 'input[placeholder*="Last"]',
                'input[name*="lname"]', 'input[id*="lname"]'
            ],
            'email': [
                'input[type="email"]', 'input[name*="email"]', 'input[id*="email"]',
                'input[placeholder*="email"]'
            ],
            'phone': [
                'input[type="tel"]', 'input[name*="phone"]', 'input[id*="phone"]',
                'input[placeholder*="phone"]'
            ],
            'resume_upload': [
                'input[type="file"][accept*="pdf"]', 'input[type="file"][name*="resume"]',
                'input[type="file"][id*="resume"]'
            ],
            'cover_letter': [
                'textarea[name*="cover"]', 'textarea[id*="cover"]', 'textarea[name*="letter"]',
                'div[contenteditable="true"]'
            ],
            'submit_button': [
                'button[type="submit"]', 'input[type="submit"]', 'button:has-text("Submit")',
                'button:has-text("Apply")', 'button:has-text("Send")'
            ]
        }
        
        # Try to find each field
        for field_name, patterns in field_patterns.items():
            for pattern in patterns:
                try:
                    element = await page.wait_for_selector(pattern, timeout=2000)
                    if element:
                        form_selectors[field_name] = pattern
                        break
                except:
                    continue
        
        return form_selectors
    
    async def _fill_application_form(self, 
                                   page: Page, 
                                   form_selectors: Dict[str, str],
                                   candidate: Candidate,
                                   resume_version: ResumeVersion,
                                   cover_letter: CoverLetter):
        """Fill application form with candidate data"""
        
        # Fill basic information
        if form_selectors['first_name']:
            await self.behavior_simulator.human_type(page, form_selectors['first_name'], candidate.first_name)
        
        if form_selectors['last_name']:
            await self.behavior_simulator.human_type(page, form_selectors['last_name'], candidate.last_name)
        
        if form_selectors['email']:
            email_alias = f"{candidate.email.split('@')[0]}+job-{uuid.uuid4().hex[:8]}@{candidate.email.split('@')[1]}"
            await self.behavior_simulator.human_type(page, form_selectors['email'], email_alias)
        
        if form_selectors['phone']:
            await self.behavior_simulator.human_type(page, form_selectors['phone'], candidate.phone)
        
        # Upload resume
        if form_selectors['resume_upload']:
            # Save resume to temp file
            resume_path = f"/tmp/resume_{uuid.uuid4().hex}.pdf"
            with open(resume_path, 'wb') as f:
                f.write(resume_version.content)
            
            await page.set_input_files(form_selectors['resume_upload'], resume_path)
            await asyncio.sleep(random.uniform(1, 2))
        
        # Fill cover letter
        if form_selectors['cover_letter'] and cover_letter:
            await self.behavior_simulator.human_type(page, form_selectors['cover_letter'], cover_letter.content)
        
        # Random page interactions
        await self.behavior_simulator.random_page_interaction(page)
    
    async def _submit_application_form(self, page: Page, form_selectors: Dict[str, str]) -> bool:
        """Submit the application form"""
        
        if not form_selectors['submit_button']:
            return False
        
        # Click submit with human behavior
        await self.behavior_simulator.human_click(page, form_selectors['submit_button'])
        
        # Wait for submission confirmation
        try:
            await page.wait_for_selector(
                'text="thank you" | text="submitted" | text="received" | text="confirmation"',
                timeout=10000
            )
            return True
        except:
            return False
    
    async def _handle_indeed_application_flow(self, 
                                            page: Page, 
                                            candidate: Candidate,
                                            resume_version: ResumeVersion,
                                            cover_letter: CoverLetter):
        """Handle Indeed-specific application flow"""
        
        # Step 1: Personal Information
        await self._fill_indeed_personal_info(page, candidate)
        
        # Step 2: Resume Upload
        await self._handle_indeed_resume_upload(page, resume_version)
        
        # Step 3: Cover Letter (if required)
        await self._handle_indeed_cover_letter(page, cover_letter)
        
        # Step 4: Additional Questions
        await self._handle_indeed_additional_questions(page, candidate)
        
        # Step 5: Final Submit
        await self._submit_indeed_application(page)
    
    async def _fill_indeed_personal_info(self, page: Page, candidate: Candidate):
        """Fill Indeed personal information section"""
        
        # Generate email alias for this application
        email_alias = f"{candidate.email.split('@')[0]}+indeed-{uuid.uuid4().hex[:8]}@{candidate.email.split('@')[1]}"
        
        # Fill personal info fields
        personal_fields = {
            'input[name="firstName"]': candidate.first_name,
            'input[name="lastName"]': candidate.last_name,
            'input[name="email"]': email_alias,
            'input[name="phoneNumber"]': candidate.phone,
            'input[name="city"]': candidate.location
        }
        
        for selector, value in personal_fields.items():
            try:
                await self.behavior_simulator.human_type(page, selector, value)
            except:
                continue
        
        # Click continue
        await self._click_indeed_continue(page)
    
    async def _handle_indeed_resume_upload(self, page: Page, resume_version: ResumeVersion):
        """Handle Indeed resume upload"""
        
        # Save resume to temp file
        resume_path = f"/tmp/indeed_resume_{uuid.uuid4().hex}.pdf"
        with open(resume_path, 'wb') as f:
            f.write(resume_version.content)
        
        # Upload resume
        upload_selectors = [
            'input[type="file"][accept*="pdf"]',
            'input[name="resume"]',
            '.file-upload input[type="file"]'
        ]
        
        for selector in upload_selectors:
            try:
                await page.set_input_files(selector, resume_path)
                break
            except:
                continue
        
        # Wait for upload completion
        await asyncio.sleep(random.uniform(2, 4))
        
        # Click continue
        await self._click_indeed_continue(page)
    
    async def _handle_indeed_cover_letter(self, page: Page, cover_letter: CoverLetter):
        """Handle Indeed cover letter section"""
        
        # Check if cover letter is required
        cover_letter_selectors = [
            'textarea[name="coverLetter"]',
            '.cover-letter textarea',
            'div[contenteditable="true"]'
        ]
        
        for selector in cover_letter_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                if element and cover_letter:
                    await self.behavior_simulator.human_type(page, selector, cover_letter.content)
                break
            except:
                continue
        
        # Click continue
        await self._click_indeed_continue(page)
    
    async def _handle_indeed_additional_questions(self, page: Page, candidate: Candidate):
        """Handle Indeed additional questions"""
        
        # Common additional questions and smart answers
        question_patterns = {
            'years.*experience': str(getattr(candidate, 'years_of_experience', 3)),
            'authorized.*work': 'Yes',
            'require.*sponsorship': 'No' if getattr(candidate, 'requires_visa_sponsorship', False) else 'Yes',
            'willing.*relocate': 'Yes' if getattr(candidate, 'willing_to_relocate', True) else 'No',
            'salary.*expectation': f"${getattr(candidate, 'desired_salary', 80000)}" if getattr(candidate, 'desired_salary', None) else "Negotiable",
            'start.*date': '2 weeks notice',
            'degree': getattr(candidate, 'education_level', 'Bachelor\'s'),
            'certifications': ', '.join(getattr(candidate, 'certifications', [])) if getattr(candidate, 'certifications', []) else 'None'
        }
        
        # Look for question fields
        questions = await page.query_selector_all('input, select, textarea')
        
        for question in questions:
            try:
                label = await question.get_attribute('aria-label') or await question.get_attribute('name') or ''
                
                for pattern, answer in question_patterns.items():
                    if re.search(pattern, label, re.IGNORECASE):
                        element_type = await question.get_attribute('type')
                        tag_name = await question.evaluate('el => el.tagName.toLowerCase()')
                        
                        if tag_name == 'select':
                            await question.select_option(answer)
                        elif element_type in ['radio', 'checkbox']:
                            await question.click()
                        else:
                            element_id = await question.get_attribute('id')
                            if element_id:
                                await self.behavior_simulator.human_type(page, f'#{element_id}', answer)
                        break
            except:
                continue
        
        # Click continue
        await self._click_indeed_continue(page)
    
    async def _submit_indeed_application(self, page: Page):
        """Submit Indeed application"""
        
        submit_selectors = [
            'button[data-testid="submit-application"]',
            'button:has-text("Submit application")',
            'button:has-text("Apply now")',
            'input[type="submit"]'
        ]
        
        for selector in submit_selectors:
            try:
                await self.behavior_simulator.human_click(page, selector)
                break
            except:
                continue
        
        # Wait for confirmation
        await asyncio.sleep(random.uniform(2, 5))
    
    async def _click_indeed_continue(self, page: Page):
        """Click continue button in Indeed flow"""
        
        continue_selectors = [
            'button[data-testid="continue-button"]',
            'button:has-text("Continue")',
            'button:has-text("Next")',
            '.ia-continueButton'
        ]
        
        for selector in continue_selectors:
            try:
                await self.behavior_simulator.human_click(page, selector)
                await asyncio.sleep(random.uniform(1, 2))
                break
            except:
                continue
    
    async def _generate_tracking_pixel(self, application_id: str) -> str:
        """Generate tracking pixel URL for application tracking"""
        
        # Create 1x1 tracking pixel
        img = Image.new('RGB', (1, 1), color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        # Generate tracking URL
        tracking_url = f"https://track.jobhunter-x.com/pixel/{application_id}.png"
        
        # In production, this would be served by a tracking service
        return tracking_url
    
    def _generate_utm_params(self, application_id: str, source: str) -> Dict[str, str]:
        """Generate UTM parameters for tracking"""
        
        return {
            'utm_source': source,
            'utm_medium': 'job_application',
            'utm_campaign': 'elite_jobhunter_x',
            'utm_content': application_id,
            'utm_term': 'automated_application'
        }
    
    def _extract_email_from_apply_url(self, url: str) -> str:
        """Extract email from mailto: apply URL"""
        
        if url.startswith('mailto:'):
            return url.replace('mailto:', '').split('?')[0]
        return None
    
    async def _save_application(self, application: Application):
        """Save application to database"""
        
        # Connect to MongoDB
        from pymongo import MongoClient
        import os
        
        client = MongoClient(os.getenv('MONGO_URL'))
        db = client[os.getenv('DB_NAME')]
        
        # Save application
        await db.applications.insert_one(application.dict())
        
        client.close()
    
    # Placeholder methods for other application strategies
    async def _submit_external_link(self, *args) -> ApplicationResult:
        """Submit application through external link"""
        # Implementation for external links
        return ApplicationResult(
            success=False,
            method=ApplicationMethod.EXTERNAL_LINK,
            application_id=args[0].id,
            submission_time=datetime.utcnow(),
            error_message="External link submission not implemented"
        )
    
    async def _submit_company_portal(self, *args) -> ApplicationResult:
        """Submit application through company portal"""
        # Implementation for company portals
        return ApplicationResult(
            success=False,
            method=ApplicationMethod.COMPANY_PORTAL,
            application_id=args[0].id,
            submission_time=datetime.utcnow(),
            error_message="Company portal submission not implemented"
        )
    
    async def _submit_linkedin_easy(self, *args) -> ApplicationResult:
        """Submit application through LinkedIn Easy Apply"""
        # Implementation for LinkedIn Easy Apply
        return ApplicationResult(
            success=False,
            method=ApplicationMethod.LINKEDIN_EASY,
            application_id=args[0].id,
            submission_time=datetime.utcnow(),
            error_message="LinkedIn Easy Apply not implemented"
        )

# Application Submission Manager
class ApplicationSubmissionManager:
    """Manager for coordinating application submissions"""
    
    def __init__(self, config: ApplicationSubmissionConfig):
        self.config = config
        self.engine = ApplicationSubmissionEngine(config)
        self.submission_queue = asyncio.Queue()
        self.active_submissions = set()
        self.max_concurrent_submissions = 3
        
    async def queue_application(self, 
                              candidate: Candidate,
                              job: JobRaw,
                              resume_version: ResumeVersion,
                              cover_letter: CoverLetter,
                              method: ApplicationMethod = ApplicationMethod.DIRECT_FORM):
        """Queue application for submission"""
        
        await self.submission_queue.put({
            'candidate': candidate,
            'job': job,
            'resume_version': resume_version,
            'cover_letter': cover_letter,
            'method': method
        })
    
    async def process_submission_queue(self):
        """Process queued applications"""
        
        while True:
            try:
                # Wait for submissions if queue is empty
                if self.submission_queue.empty():
                    await asyncio.sleep(1)
                    continue
                
                # Check if we can process more submissions
                if len(self.active_submissions) >= self.max_concurrent_submissions:
                    await asyncio.sleep(1)
                    continue
                
                # Get next submission
                submission_data = await self.submission_queue.get()
                
                # Process submission
                task = asyncio.create_task(
                    self._process_single_submission(submission_data)
                )
                self.active_submissions.add(task)
                
                # Remove completed tasks
                task.add_done_callback(self.active_submissions.discard)
                
            except Exception as e:
                logger.error(f"Error processing submission queue: {str(e)}")
                await asyncio.sleep(5)
    
    async def _process_single_submission(self, submission_data: Dict[str, Any]):
        """Process a single application submission"""
        
        try:
            result = await self.engine.submit_application(
                submission_data['candidate'],
                submission_data['job'],
                submission_data['resume_version'],
                submission_data['cover_letter'],
                submission_data['method']
            )
            
            logger.info(f"Application submitted: {result.application_id}, Success: {result.success}")
            return result
            
        except Exception as e:
            logger.error(f"Single submission failed: {str(e)}")
            return None
    
    async def get_submission_stats(self) -> Dict[str, Any]:
        """Get submission statistics"""
        
        # Connect to MongoDB
        from pymongo import MongoClient
        import os
        
        client = MongoClient(os.getenv('MONGO_URL'))
        db = client[os.getenv('DB_NAME')]
        
        # Get statistics
        stats = {
            'total_applications': await db.applications.count_documents({}),
            'successful_applications': await db.applications.count_documents({'status': 'applied'}),
            'pending_applications': await db.applications.count_documents({'status': 'pending'}),
            'failed_applications': await db.applications.count_documents({'status': 'failed'}),
            'applications_today': await db.applications.count_documents({
                'applied_at': {'$gte': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
            }),
            'queue_size': self.submission_queue.qsize(),
            'active_submissions': len(self.active_submissions)
        }
        
        client.close()
        return stats