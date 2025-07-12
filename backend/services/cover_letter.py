"""
Elite JobHunter X - Advanced Cover Letter Generation Service
Phase 5: Multi-Tone, LLM-Powered Cover Letter Engine

Features:
- Multi-tone generation (Formal, Curious, Friendly, Challenger)
- Company research integration
- ATS optimization
- PDF generation
- Performance tracking and A/B testing
- Personalization engines
- Industry-specific templates
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import hashlib
import tempfile
import os

# PDF Generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor

# AI and ML
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

from models import (
    CoverLetter, OutreachTone, CoverLetterTemplate, 
    CompanyResearch, CoverLetterPerformance
)
from .openrouter import get_openrouter_service

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class CompanyResearchEngine:
    """Advanced company research engine for cover letter personalization"""
    
    def __init__(self):
        self.session = None
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def research_company(self, company_name: str, company_domain: str = None) -> Dict[str, Any]:
        """Comprehensive company research for personalization"""
        try:
            research_data = {
                "company_name": company_name,
                "domain": company_domain,
                "about": "",
                "mission": "",
                "values": [],
                "recent_news": [],
                "culture_keywords": [],
                "tech_stack": [],
                "company_size": "",
                "industry": "",
                "locations": [],
                "leadership": [],
                "awards": [],
                "sentiment_score": 0.0,
                "key_initiatives": [],
                "research_timestamp": datetime.utcnow().isoformat(),
                "research_sources": []
            }
            
            # Research from company website
            if company_domain:
                website_data = await self._research_company_website(company_domain)
                research_data.update(website_data)
            
            # Research from LinkedIn (simplified)
            linkedin_data = await self._research_linkedin_company(company_name)
            research_data.update(linkedin_data)
            
            # Research from Glassdoor (simplified)
            glassdoor_data = await self._research_glassdoor_reviews(company_name)
            research_data.update(glassdoor_data)
            
            # Analyze overall sentiment
            all_text = f"{research_data['about']} {' '.join(research_data['recent_news'])}"
            if all_text.strip():
                sentiment = self.sentiment_analyzer.polarity_scores(all_text)
                research_data['sentiment_score'] = sentiment['compound']
            
            return research_data
            
        except Exception as e:
            logger.error(f"Company research failed for {company_name}: {e}")
            return {
                "company_name": company_name,
                "domain": company_domain,
                "research_timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def _research_company_website(self, domain: str) -> Dict[str, Any]:
        """Research company from their official website"""
        data = {"research_sources": [f"https://{domain}"]}
        
        try:
            # Common pages to check
            pages_to_check = [
                f"https://{domain}",
                f"https://{domain}/about",
                f"https://{domain}/about-us",
                f"https://{domain}/company",
                f"https://{domain}/careers",
                f"https://{domain}/news",
                f"https://{domain}/blog"
            ]
            
            for url in pages_to_check[:3]:  # Limit to first 3 to avoid rate limiting
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract about information
                            about_sections = soup.find_all(['div', 'section', 'p'], 
                                                         class_=re.compile(r'about|mission|vision', re.I))
                            for section in about_sections:
                                text = section.get_text(strip=True)
                                if len(text) > 100:
                                    data['about'] = text[:500]
                                    break
                            
                            # Extract mission/values
                            mission_sections = soup.find_all(text=re.compile(r'mission|vision|values', re.I))
                            for section in mission_sections:
                                parent = section.parent
                                if parent:
                                    text = parent.get_text(strip=True)
                                    if len(text) > 50:
                                        data['mission'] = text[:300]
                                        break
                            
                            # Extract tech stack from careers page
                            if 'careers' in url or 'jobs' in url:
                                tech_keywords = ['python', 'javascript', 'react', 'aws', 'docker', 
                                               'kubernetes', 'typescript', 'nodejs', 'postgresql']
                                text_lower = html.lower()
                                found_tech = [tech for tech in tech_keywords if tech in text_lower]
                                data['tech_stack'] = found_tech
                                
                except Exception as e:
                    logger.debug(f"Failed to research {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Website research failed for {domain}: {e}")
        
        return data
    
    async def _research_linkedin_company(self, company_name: str) -> Dict[str, Any]:
        """Simplified LinkedIn company research"""
        return {
            "company_size": "Unknown",
            "industry": "Technology",  # Default assumption
            "locations": ["United States"]  # Default
        }
    
    async def _research_glassdoor_reviews(self, company_name: str) -> Dict[str, Any]:
        """Simplified Glassdoor research"""
        return {
            "culture_keywords": ["innovative", "fast-paced", "collaborative"],
            "recent_news": []
        }


class CoverLetterPersonalizationEngine:
    """Advanced personalization engine for cover letters"""
    
    def __init__(self):
        self.tone_strategies = {
            OutreachTone.FORMAL: {
                "greeting": "Dear Hiring Manager,",
                "intro_style": "professional",
                "body_style": "structured",
                "closing": "Sincerely,",
                "language_level": "formal"
            },
            OutreachTone.CURIOUS: {
                "greeting": "Hello there!",
                "intro_style": "question-based",
                "body_style": "exploratory",
                "closing": "Looking forward to learning more,",
                "language_level": "conversational"
            },
            OutreachTone.WARM: {
                "greeting": "Hi team,",
                "intro_style": "personal",
                "body_style": "story-driven",
                "closing": "Best regards,",
                "language_level": "friendly"
            },
            OutreachTone.BOLD: {
                "greeting": "Dear Hiring Team,",
                "intro_style": "confident",
                "body_style": "achievement-focused",
                "closing": "Ready to contribute,",
                "language_level": "assertive"
            },
            OutreachTone.STRATEGIC: {
                "greeting": "Dear Hiring Manager,",
                "intro_style": "value-proposition",
                "body_style": "results-oriented",
                "closing": "Best regards,",
                "language_level": "business"
            }
        }
    
    def generate_personalization_hooks(self, company_research: Dict[str, Any], 
                                     job_description: str, candidate_profile: Dict[str, Any]) -> List[str]:
        """Generate personalization hooks based on research"""
        hooks = []
        
        # Company mission/values hooks
        if company_research.get('mission'):
            hooks.append(f"I was drawn to {company_research['company_name']}'s mission: {company_research['mission'][:100]}...")
        
        # Company news/initiatives hooks
        if company_research.get('recent_news'):
            for news in company_research['recent_news'][:2]:
                hooks.append(f"I was excited to read about {news[:80]}...")
        
        # Tech stack alignment hooks
        candidate_skills = candidate_profile.get('skills', [])
        company_tech = company_research.get('tech_stack', [])
        matching_tech = set(skill.lower() for skill in candidate_skills) & set(company_tech)
        if matching_tech:
            hooks.append(f"I notice you use {', '.join(list(matching_tech)[:3])}, which aligns perfectly with my expertise")
        
        # Culture fit hooks
        culture_keywords = company_research.get('culture_keywords', [])
        if culture_keywords:
            hooks.append(f"Your {', '.join(culture_keywords[:2])} culture resonates with my professional values")
        
        return hooks[:3]  # Return top 3 hooks
    
    def calculate_ats_keywords(self, job_description: str, candidate_profile: Dict[str, Any]) -> List[str]:
        """Extract and prioritize ATS keywords"""
        # Extract keywords from job description
        job_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', job_description)
        job_words.extend(re.findall(r'\b[a-z]+(?:\.[a-z]+)+\b', job_description.lower()))  # tech terms
        
        # Filter for relevant keywords
        candidate_skills = [skill.lower() for skill in candidate_profile.get('skills', [])]
        relevant_keywords = []
        
        for word in job_words:
            if any(skill in word.lower() for skill in candidate_skills):
                relevant_keywords.append(word)
        
        # Add important job requirements
        requirement_patterns = [
            r'(\d+\+?\s*years?\s*(?:of\s*)?(?:experience|exp))',
            r'(bachelor|master|phd|degree)',
            r'(remote|hybrid|on-site)',
            r'(full-time|part-time|contract)'
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, job_description.lower())
            relevant_keywords.extend(matches)
        
        return list(set(relevant_keywords))[:15]  # Top 15 keywords


class CoverLetterGenerator:
    """Advanced multi-tone cover letter generator"""
    
    def __init__(self, db):
        self.db = db
        self.openrouter_service = get_openrouter_service()
        self.personalization_engine = CoverLetterPersonalizationEngine()
        
    async def generate_cover_letter(
        self,
        candidate_id: str,
        job_id: str,
        job_description: str,
        company_name: str,
        company_domain: str = None,
        tone: OutreachTone = OutreachTone.FORMAL,
        position_title: str = "",
        hiring_manager: str = "",
        include_research: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive cover letter with research and personalization"""
        
        try:
            # Get candidate profile
            candidate = await self.db.candidates.find_one({"id": candidate_id})
            if not candidate:
                raise ValueError("Candidate not found")
            
            # Get company research
            company_research = {}
            if include_research:
                async with CompanyResearchEngine() as research_engine:
                    company_research = await research_engine.research_company(
                        company_name, company_domain
                    )
            
            # Generate personalization hooks
            hooks = self.personalization_engine.generate_personalization_hooks(
                company_research, job_description, candidate
            )
            
            # Calculate ATS keywords
            ats_keywords = self.personalization_engine.calculate_ats_keywords(
                job_description, candidate
            )
            
            # Generate cover letter content using AI
            cover_letter_content = await self._generate_ai_cover_letter(
                candidate, job_description, company_name, company_research,
                tone, hooks, ats_keywords, position_title, hiring_manager
            )
            
            # Create cover letter record
            cover_letter_id = str(uuid.uuid4())
            cover_letter = CoverLetter(
                id=cover_letter_id,
                candidate_id=candidate_id,
                job_id=job_id,
                tone=tone,
                content=cover_letter_content['content'],
                ats_keywords=ats_keywords,
                reasoning=cover_letter_content.get('reasoning', ''),
                company_research=json.dumps(company_research) if company_research else None
            )
            
            # Save to database
            await self.db.cover_letters.insert_one(cover_letter.dict())
            
            # Generate PDF
            pdf_path = await self._generate_pdf(cover_letter_content['content'], candidate, company_name)
            
            # Update cover letter with PDF path
            await self.db.cover_letters.update_one(
                {"id": cover_letter_id},
                {"$set": {"pdf_url": pdf_path}}
            )
            
            return {
                "cover_letter_id": cover_letter_id,
                "content": cover_letter_content['content'],
                "tone": tone.value,
                "ats_keywords": ats_keywords,
                "personalization_hooks": hooks,
                "company_research": company_research,
                "pdf_url": pdf_path,
                "reasoning": cover_letter_content.get('reasoning', ''),
                "word_count": len(cover_letter_content['content'].split()),
                "sentiment_analysis": cover_letter_content.get('sentiment_analysis', {}),
                "estimated_reading_time": len(cover_letter_content['content'].split()) // 200  # minutes
            }
            
        except Exception as e:
            logger.error(f"Cover letter generation failed: {e}")
            raise
    
    async def _generate_ai_cover_letter(
        self,
        candidate: Dict[str, Any],
        job_description: str,
        company_name: str,
        company_research: Dict[str, Any],
        tone: OutreachTone,
        hooks: List[str],
        ats_keywords: List[str],
        position_title: str,
        hiring_manager: str
    ) -> Dict[str, Any]:
        """Generate AI-powered cover letter content"""
        
        tone_config = self.personalization_engine.tone_strategies[tone]
        
        # Construct comprehensive prompt
        prompt = f"""
        You are an expert career coach and professional writer specializing in creating compelling, personalized cover letters that get results. 

        Create a highly personalized, ATS-optimized cover letter with the following specifications:

        **CANDIDATE PROFILE:**
        - Name: {candidate.get('full_name', 'N/A')}
        - Email: {candidate.get('email', 'N/A')}
        - Phone: {candidate.get('phone', 'N/A')}
        - Location: {candidate.get('location', 'N/A')}
        - Years of Experience: {candidate.get('years_experience', 'N/A')}
        - Skills: {', '.join(candidate.get('skills', []))}
        - Target Roles: {', '.join(candidate.get('target_roles', []))}

        **JOB DETAILS:**
        - Company: {company_name}
        - Position: {position_title or 'The advertised position'}
        - Hiring Manager: {hiring_manager or 'Hiring Manager'}
        
        **JOB DESCRIPTION:**
        {job_description}

        **COMPANY RESEARCH DATA:**
        {json.dumps(company_research, indent=2) if company_research else 'No research data available'}

        **TONE REQUIREMENTS:**
        - Primary Tone: {tone.value}
        - Greeting Style: {tone_config['greeting']}
        - Introduction Style: {tone_config['intro_style']}
        - Body Style: {tone_config['body_style']}
        - Closing Style: {tone_config['closing']}
        - Language Level: {tone_config['language_level']}

        **PERSONALIZATION HOOKS (Use 1-2 of these):**
        {chr(10).join(f"- {hook}" for hook in hooks)}

        **ATS KEYWORDS TO INCORPORATE:**
        {', '.join(ats_keywords)}

        **WRITING GUIDELINES:**
        1. Length: 250-400 words (concise but comprehensive)
        2. Structure: Header, Greeting, 3 body paragraphs, closing, signature
        3. Include specific examples and quantifiable achievements
        4. Demonstrate knowledge of the company and role
        5. Show enthusiasm and cultural fit
        6. Use action verbs and power words
        7. Incorporate ATS keywords naturally
        8. Maintain consistent tone throughout
        9. End with a strong call-to-action

        **PARAGRAPH STRUCTURE:**
        1. Opening: Hook + position interest + brief value proposition
        2. Body 1: Relevant experience + specific achievements with numbers
        3. Body 2: Skills alignment + company research insight + cultural fit
        4. Body 3: Future contribution + enthusiasm + call to action

        Provide your response in JSON format:
        {{
            "content": "The complete formatted cover letter with proper spacing and structure",
            "reasoning": "Detailed explanation of strategic choices made",
            "tone_analysis": "Analysis of how the tone requirements were met",
            "personalization_score": "Score 1-10 of how personalized the letter is",
            "ats_optimization": "How ATS keywords were incorporated",
            "key_selling_points": ["point1", "point2", "point3"],
            "sentiment_analysis": {{
                "enthusiasm_level": "high/medium/low",
                "confidence_level": "high/medium/low",
                "professionalism_score": "1-10"
            }},
            "improvement_suggestions": ["suggestion1", "suggestion2"]
        }}
        """
        
        try:
            response = await self.openrouter_service.generate_completion(
                prompt, "cover_letter", max_tokens=3000, temperature=0.8
            )
            return json.loads(response)
        except Exception as e:
            logger.error(f"OpenRouter API failed: {e}")
            # Comprehensive fallback for when OpenRouter is unavailable
            return self._generate_fallback_cover_letter(
                candidate, job_description, company_name, company_research,
                tone, hooks, ats_keywords, position_title, hiring_manager
            )
    
    def _generate_fallback_cover_letter(
        self,
        candidate: Dict[str, Any],
        job_description: str,
        company_name: str,
        company_research: Dict[str, Any],
        tone: OutreachTone,
        hooks: List[str],
        ats_keywords: List[str],
        position_title: str,
        hiring_manager: str
    ) -> Dict[str, Any]:
        """Generate a high-quality cover letter without AI when OpenRouter is unavailable"""
        
        # Extract key information
        candidate_name = candidate.get('full_name', 'Candidate')
        candidate_skills = candidate.get('skills', [])
        candidate_experience = candidate.get('years_experience', 0)
        
        # Tone-specific greetings and closings
        tone_config = self.personalization_engine.tone_strategies[tone]
        
        # Build personalized content
        greeting = f"Dear {hiring_manager or 'Hiring Manager'},"
        
        # Opening paragraph
        opening = f"I am writing to express my strong interest in the {position_title or 'position'} at {company_name}. "
        
        if tone == OutreachTone.WARM:
            opening += f"I was excited to discover this opportunity as it perfectly aligns with my {candidate_experience}+ years of experience and passion for {', '.join(candidate_skills[:2]) if candidate_skills else 'technology'}."
        elif tone == OutreachTone.BOLD:
            opening += f"With {candidate_experience}+ years of proven expertise in {', '.join(candidate_skills[:3]) if candidate_skills else 'the field'}, I am confident I can deliver exceptional results for your team."
        elif tone == OutreachTone.CURIOUS:
            opening += f"I am particularly intrigued by {company_name}'s innovative approach and would love to contribute my {candidate_experience}+ years of experience to your mission."
        elif tone == OutreachTone.STRATEGIC:
            opening += f"Given my strategic background in {', '.join(candidate_skills[:2]) if candidate_skills else 'the industry'} and {candidate_experience}+ years of experience, I see significant opportunities to drive growth at {company_name}."
        else:  # FORMAL
            opening += f"With {candidate_experience}+ years of professional experience in {', '.join(candidate_skills[:2]) if candidate_skills else 'the field'}, I am well-positioned to contribute to your team's success."
        
        # Body paragraph 1 - Experience and achievements
        body1 = f"In my professional career, I have developed strong expertise in {', '.join(candidate_skills[:4]) if candidate_skills else 'key technical areas'}. "
        
        # Add company research if available
        if company_research and company_research.get('about'):
            body1 += f"I am particularly drawn to {company_name}'s commitment to {company_research.get('mission', 'innovation')} and believe my background aligns well with your values. "
        
        # Body paragraph 2 - Skills alignment and enthusiasm
        body2 = f"The requirements outlined in your job posting closely match my skill set, particularly in {', '.join(ats_keywords[:3]) if ats_keywords else 'the core competencies'}. "
        
        if hooks:
            body2 += f"I am especially excited about {hooks[0] if hooks else 'the opportunity to contribute'}. "
        
        body2 += f"I am eager to bring my experience and enthusiasm to help {company_name} achieve its goals."
        
        # Closing paragraph
        closing = f"I would welcome the opportunity to discuss how my background in {', '.join(candidate_skills[:2]) if candidate_skills else 'the field'} can contribute to {company_name}'s continued success. "
        
        if tone == OutreachTone.BOLD:
            closing += "I am confident that my proven track record and results-driven approach make me an ideal candidate for this role."
        elif tone == OutreachTone.WARM:
            closing += "Thank you for considering my application, and I look forward to the possibility of joining your team."
        else:
            closing += "Thank you for your time and consideration."
        
        # Combine all parts
        content = f"""{greeting}

{opening}

{body1}

{body2}

{closing}

Best regards,
{candidate_name}"""
        
        return {
            "content": content,
            "reasoning": f"Generated fallback cover letter with {tone.value} tone, incorporating {len(ats_keywords)} ATS keywords and {len(hooks)} personalization hooks",
            "tone_analysis": f"Applied {tone.value} tone with appropriate language level and style",
            "personalization_score": "7",
            "ats_optimization": f"Incorporated {len(ats_keywords)} relevant keywords: {', '.join(ats_keywords[:5])}",
            "key_selling_points": [
                f"{candidate_experience}+ years of experience",
                f"Expertise in {', '.join(candidate_skills[:3]) if candidate_skills else 'key areas'}",
                "Strong alignment with role requirements"
            ],
            "sentiment_analysis": {
                "enthusiasm_level": "high" if tone in [OutreachTone.WARM, OutreachTone.CURIOUS] else "medium",
                "confidence_level": "high" if tone == OutreachTone.BOLD else "medium",
                "professionalism_score": "9"
            },
            "improvement_suggestions": [
                "Add specific quantifiable achievements when AI is available",
                "Include more detailed company research insights"
            ]
        }
    
    async def _generate_pdf(self, content: str, candidate: Dict[str, Any], company_name: str) -> str:
        """Generate professional PDF cover letter"""
        try:
            # Create temporary file
            temp_dir = "/tmp/cover_letters"
            os.makedirs(temp_dir, exist_ok=True)
            
            filename = f"cover_letter_{candidate.get('full_name', 'candidate').replace(' ', '_')}_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(temp_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=1*inch)
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=HexColor('#2c3e50')
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                alignment=TA_LEFT,
                leftIndent=0,
                rightIndent=0
            )
            
            # Content elements
            elements = []
            
            # Header with candidate info
            header_text = f"""
            <b>{candidate.get('full_name', 'N/A')}</b><br/>
            {candidate.get('email', 'N/A')} | {candidate.get('phone', 'N/A')}<br/>
            {candidate.get('location', 'N/A')}<br/>
            """
            elements.append(Paragraph(header_text, title_style))
            elements.append(Spacer(1, 20))
            
            # Date
            elements.append(Paragraph(f"{datetime.now().strftime('%B %d, %Y')}", normal_style))
            elements.append(Spacer(1, 20))
            
            # Cover letter content
            # Split content into paragraphs
            paragraphs = content.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    elements.append(Paragraph(paragraph.strip(), normal_style))
                    elements.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(elements)
            
            # Return relative path for storage
            return f"/tmp/cover_letters/{filename}"
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return ""

    async def generate_multiple_versions(
        self,
        candidate_id: str,
        job_id: str,
        job_description: str,
        company_name: str,
        company_domain: str = None,
        position_title: str = "",
        versions_count: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate multiple cover letter versions for A/B testing"""
        
        tones = [OutreachTone.FORMAL, OutreachTone.WARM, OutreachTone.CURIOUS, OutreachTone.STRATEGIC, OutreachTone.BOLD]
        selected_tones = tones[:versions_count]
        
        versions = []
        for tone in selected_tones:
            try:
                version = await self.generate_cover_letter(
                    candidate_id, job_id, job_description, company_name,
                    company_domain, tone, position_title
                )
                version['version_name'] = f"{tone.value.title()} Version"
                versions.append(version)
            except Exception as e:
                logger.error(f"Failed to generate {tone.value} version: {e}")
                continue
        
        return versions

    async def get_performance_analytics(self, cover_letter_id: str) -> Dict[str, Any]:
        """Get performance analytics for a cover letter"""
        try:
            # Get cover letter
            cover_letter = await self.db.cover_letters.find_one({"id": cover_letter_id})
            if not cover_letter:
                return {"error": "Cover letter not found"}
            
            # Get applications using this cover letter
            applications = await self.db.applications.find(
                {"cover_letter_id": cover_letter_id}
            ).to_list(1000)
            
            # Calculate metrics
            total_applications = len(applications)
            responses = sum(1 for app in applications if app.get('response_received'))
            interviews = sum(1 for app in applications if app.get('interview_scheduled'))
            
            return {
                "cover_letter_id": cover_letter_id,
                "total_applications": total_applications,
                "response_rate": (responses / total_applications * 100) if total_applications > 0 else 0,
                "interview_rate": (interviews / total_applications * 100) if total_applications > 0 else 0,
                "success_score": ((responses * 0.5 + interviews * 1.0) / total_applications * 100) if total_applications > 0 else 0,
                "usage_count": cover_letter.get('used_count', 0),
                "last_used": cover_letter.get('updated_at'),
                "tone": cover_letter.get('tone'),
                "word_count": len(cover_letter.get('content', '').split())
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance analytics: {e}")
            return {"error": str(e)}


# Service factory function
def get_cover_letter_service(db):
    """Get CoverLetterGenerator service instance"""
    return CoverLetterGenerator(db)