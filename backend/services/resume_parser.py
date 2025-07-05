import os
import re
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import aiofiles
import PyPDF2
from docx import Document
import docx2txt
import fitz  # PyMuPDF
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class ParsedResume:
    raw_text: str
    contact_info: Dict[str, str]
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    certifications: List[str]
    languages: List[str]
    years_experience: int
    extracted_data: Dict[str, Any]

class ResumeParsingService:
    def __init__(self):
        self.upload_dir = Path("/app/backend/uploads/resumes")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Common skill patterns
        self.skill_patterns = [
            r'\b(?:Python|Java|JavaScript|C\+\+|C#|Go|Rust|Ruby|PHP|Swift|Kotlin|Scala|TypeScript)\b',
            r'\b(?:React|Angular|Vue|Node\.js|Django|Flask|FastAPI|Spring|Express|Laravel)\b',
            r'\b(?:MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|DynamoDB)\b',
            r'\b(?:AWS|Azure|GCP|Google Cloud|Docker|Kubernetes|Jenkins|GitLab|GitHub)\b',
            r'\b(?:TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy|Matplotlib|Seaborn)\b',
            r'\b(?:HTML|CSS|SCSS|Tailwind|Bootstrap|Material-UI|Figma|Adobe)\b',
            r'\b(?:Linux|Ubuntu|Windows|macOS|Apache|Nginx|Git|SVN|Jira|Confluence)\b',
            r'\b(?:Agile|Scrum|DevOps|CI/CD|TDD|BDD|REST|GraphQL|API|Microservices)\b'
        ]
        
        # Experience level patterns
        self.experience_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\s*(?:to|[-–])\s*(\d+)\s*(?:years?|yrs?)',
            r'over\s*(\d+)\s*(?:years?|yrs?)',
            r'more\s*than\s*(\d+)\s*(?:years?|yrs?)'
        ]
    
    async def save_uploaded_file(self, file_content: bytes, filename: str, candidate_id: str) -> str:
        """Save uploaded file to disk"""
        try:
            # Create candidate directory
            candidate_dir = self.upload_dir / candidate_id
            candidate_dir.mkdir(exist_ok=True)
            
            # Save file
            file_path = candidate_dir / filename
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    async def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            
            # Try PyMuPDF first (better text extraction)
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text()
                doc.close()
            except Exception as e:
                logger.warning(f"PyMuPDF failed, trying PyPDF2: {str(e)}")
                
                # Fallback to PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text()
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    async def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            # Try python-docx first
            try:
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text.strip()
            except Exception as e:
                logger.warning(f"python-docx failed, trying docx2txt: {str(e)}")
                
                # Fallback to docx2txt
                text = docx2txt.process(file_path)
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            return ""
    
    async def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from file based on extension"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return await self.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return await self.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume text"""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone pattern
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = f"({phones[0][0]}) {phones[0][1]}-{phones[0][2]}"
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/([A-Za-z0-9-]+)'
        linkedin_matches = re.findall(linkedin_pattern, text)
        if linkedin_matches:
            contact_info['linkedin'] = f"https://linkedin.com/in/{linkedin_matches[0]}"
        
        # GitHub pattern
        github_pattern = r'github\.com/([A-Za-z0-9-]+)'
        github_matches = re.findall(github_pattern, text)
        if github_matches:
            contact_info['github'] = f"https://github.com/{github_matches[0]}"
        
        # Location pattern (simple)
        location_pattern = r'([A-Za-z\s]+,\s*[A-Z]{2}(?:\s*\d{5})?)'
        locations = re.findall(location_pattern, text)
        if locations:
            contact_info['location'] = locations[0]
        
        return contact_info
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        skills = set()
        
        # Use predefined patterns
        for pattern in self.skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(matches)
        
        # Look for skills section
        skills_section_pattern = r'(?:SKILLS|TECHNICAL SKILLS|TECHNOLOGIES|COMPETENCIES)[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)'
        skills_match = re.search(skills_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if skills_match:
            skills_text = skills_match.group(1)
            # Split by common separators
            skill_items = re.split(r'[,•·\n\|]', skills_text)
            for skill in skill_items:
                skill = skill.strip()
                if skill and len(skill) > 1:
                    skills.add(skill)
        
        return list(skills)
    
    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume text"""
        experience = []
        
        # Look for experience section
        experience_patterns = [
            r'(?:EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT)[:\s]*(.*?)(?=\n\n[A-Z]|EDUCATION|SKILLS|$)',
            r'(?:PROFESSIONAL HISTORY|CAREER HISTORY|WORK HISTORY)[:\s]*(.*?)(?=\n\n[A-Z]|EDUCATION|SKILLS|$)'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                experience_text = match.group(1)
                
                # Split by job entries (look for date patterns)
                job_entries = re.split(r'\n(?=\d{4}|\d{1,2}/\d{4}|[A-Z][a-z]+ \d{4})', experience_text)
                
                for entry in job_entries:
                    if entry.strip():
                        job_info = self._parse_job_entry(entry)
                        if job_info:
                            experience.append(job_info)
                break
        
        return experience
    
    def _parse_job_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        """Parse individual job entry"""
        try:
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            if not lines:
                return None
            
            # Try to identify title, company, dates
            job_info = {
                'title': '',
                'company': '',
                'dates': '',
                'description': '',
                'responsibilities': []
            }
            
            # First line usually contains title and/or company
            if lines:
                first_line = lines[0]
                # Look for date patterns in first few lines
                date_pattern = r'(\d{4}[-–]\d{4}|\d{1,2}/\d{4}[-–]\d{1,2}/\d{4}|[A-Z][a-z]+ \d{4}[-–][A-Z][a-z]+ \d{4})'
                
                for i, line in enumerate(lines[:3]):
                    if re.search(date_pattern, line):
                        job_info['dates'] = line
                        # Title is usually before dates
                        if i > 0:
                            job_info['title'] = lines[0]
                            if i > 1:
                                job_info['company'] = lines[1]
                        break
                
                # Description is the remaining lines
                description_lines = lines[3:] if job_info['dates'] else lines[1:]
                job_info['description'] = '\n'.join(description_lines)
                
                # Extract bullet points as responsibilities
                responsibilities = []
                for line in description_lines:
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        responsibilities.append(line[1:].strip())
                
                job_info['responsibilities'] = responsibilities
            
            return job_info if job_info['title'] or job_info['company'] else None
        except Exception as e:
            logger.error(f"Error parsing job entry: {str(e)}")
            return None
    
    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education from resume text"""
        education = []
        
        # Look for education section
        education_pattern = r'(?:EDUCATION|ACADEMIC BACKGROUND|QUALIFICATIONS)[:\s]*(.*?)(?=\n\n[A-Z]|EXPERIENCE|SKILLS|$)'
        match = re.search(education_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            education_text = match.group(1)
            
            # Look for degree patterns
            degree_patterns = [
                r'(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.|MBA|Ph\.D\.)\s*(?:of|in)?\s*([A-Za-z\s]+)',
                r'(Associate|Diploma|Certificate)\s*(?:of|in)?\s*([A-Za-z\s]+)'
            ]
            
            for pattern in degree_patterns:
                matches = re.findall(pattern, education_text, re.IGNORECASE)
                for match in matches:
                    education.append({
                        'degree': match[0],
                        'field': match[1].strip(),
                        'institution': '',
                        'year': ''
                    })
        
        return education
    
    def calculate_years_experience(self, text: str) -> int:
        """Calculate years of experience from resume text"""
        years = 0
        
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Range pattern (e.g., "3-5 years")
                    years = max(years, int(match[1]) if match[1] else int(match[0]))
                else:
                    # Single number pattern
                    years = max(years, int(match))
        
        return years
    
    async def parse_resume(self, file_path: str) -> ParsedResume:
        """Parse resume file and extract all information"""
        try:
            # Extract text
            raw_text = await self.extract_text_from_file(file_path)
            
            if not raw_text:
                raise ValueError("No text could be extracted from the file")
            
            # Extract all components
            contact_info = self.extract_contact_info(raw_text)
            skills = self.extract_skills(raw_text)
            experience = self.extract_experience(raw_text)
            education = self.extract_education(raw_text)
            years_experience = self.calculate_years_experience(raw_text)
            
            # Extract additional data
            extracted_data = {
                'file_path': file_path,
                'extraction_date': datetime.now().isoformat(),
                'text_length': len(raw_text),
                'skills_count': len(skills),
                'experience_count': len(experience),
                'education_count': len(education)
            }
            
            return ParsedResume(
                raw_text=raw_text,
                contact_info=contact_info,
                skills=skills,
                experience=experience,
                education=education,
                certifications=[],  # TODO: Implement certification extraction
                languages=[],  # TODO: Implement language extraction
                years_experience=years_experience,
                extracted_data=extracted_data
            )
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise
    
    async def analyze_resume_quality(self, parsed_resume: ParsedResume) -> Dict[str, Any]:
        """Analyze resume quality and provide improvement suggestions"""
        quality_score = 0
        suggestions = []
        
        # Check contact information
        if parsed_resume.contact_info.get('email'):
            quality_score += 20
        else:
            suggestions.append("Add email address")
        
        if parsed_resume.contact_info.get('phone'):
            quality_score += 10
        else:
            suggestions.append("Add phone number")
        
        # Check skills
        if len(parsed_resume.skills) >= 5:
            quality_score += 25
        else:
            suggestions.append("Add more technical skills")
        
        # Check experience
        if len(parsed_resume.experience) >= 1:
            quality_score += 30
        else:
            suggestions.append("Add work experience")
        
        # Check education
        if len(parsed_resume.education) >= 1:
            quality_score += 15
        else:
            suggestions.append("Add educational background")
        
        return {
            'quality_score': quality_score,
            'suggestions': suggestions,
            'completeness': {
                'contact_info': len(parsed_resume.contact_info),
                'skills': len(parsed_resume.skills),
                'experience': len(parsed_resume.experience),
                'education': len(parsed_resume.education)
            }
        }

# Global instance
resume_service = ResumeParsingService()