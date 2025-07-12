"""
Elite JobHunter X - Advanced Resume Tailoring Service
=====================================

Advanced AI-powered resume tailoring with genetic algorithms, ATS optimization,
stealth features, and performance tracking.

Features:
- Genetic Algorithm optimization
- Advanced ATS scoring engine
- Multi-strategy tailoring
- Stealth fingerprinting
- A/B testing framework
- Performance analytics
"""

import asyncio
import re
import random
import hashlib
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid

# Text processing
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter, defaultdict

# Machine learning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Document processing
from docx import Document
from docx.shared import Inches
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from ..models import (
    ResumeVersion, ATSAnalysis, ResumeGeneticPool, 
    ResumePerformanceMetrics, KeywordOptimization,
    TailoringStrategy, ATSOptimization, ResumeFormat
)
from .openrouter import OpenRouterService


class ResumeGeneticOptimizer:
    """Genetic Algorithm for resume optimization"""
    
    def __init__(self, population_size: int = 10, mutation_rate: float = 0.1, crossover_rate: float = 0.7):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generation = 0
        self.best_fitness = 0.0
        self.convergence_threshold = 0.01
        self.max_generations = 20
    
    def initialize_population(self, base_resume: str, job_description: str, target_keywords: List[str]) -> List[Dict[str, Any]]:
        """Generate initial population of resume variants"""
        population = []
        
        for i in range(self.population_size):
            variant = {
                'id': str(uuid.uuid4()),
                'content': base_resume,
                'keywords': target_keywords.copy(),
                'fitness': 0.0,
                'generation': 0,
                'parent_ids': [],
                'mutations': []
            }
            
            # Apply random mutations to create diversity
            variant = self._mutate(variant, job_description, aggressive=True)
            population.append(variant)
        
        return population
    
    def _mutate(self, individual: Dict[str, Any], job_description: str, aggressive: bool = False) -> Dict[str, Any]:
        """Apply mutations to an individual resume"""
        mutations = []
        content = individual['content']
        
        # Mutation strategies
        strategies = [
            'keyword_injection',
            'section_reordering',
            'bullet_optimization',
            'skill_enhancement',
            'experience_emphasis',
            'format_adjustment'
        ]
        
        mutation_count = random.randint(1, 3) if not aggressive else random.randint(2, 5)
        selected_strategies = random.sample(strategies, min(mutation_count, len(strategies)))
        
        for strategy in selected_strategies:
            if strategy == 'keyword_injection':
                content, mutation_desc = self._inject_keywords_strategically(content, individual['keywords'])
                mutations.append(f"keyword_injection: {mutation_desc}")
            
            elif strategy == 'section_reordering':
                content, mutation_desc = self._reorder_sections(content)
                mutations.append(f"section_reordering: {mutation_desc}")
            
            elif strategy == 'bullet_optimization':
                content, mutation_desc = self._optimize_bullet_points(content, job_description)
                mutations.append(f"bullet_optimization: {mutation_desc}")
            
            elif strategy == 'skill_enhancement':
                content, mutation_desc = self._enhance_skills_section(content, individual['keywords'])
                mutations.append(f"skill_enhancement: {mutation_desc}")
            
            elif strategy == 'experience_emphasis':
                content, mutation_desc = self._emphasize_relevant_experience(content, job_description)
                mutations.append(f"experience_emphasis: {mutation_desc}")
            
            elif strategy == 'format_adjustment':
                content, mutation_desc = self._adjust_formatting(content)
                mutations.append(f"format_adjustment: {mutation_desc}")
        
        individual['content'] = content
        individual['mutations'].extend(mutations)
        return individual
    
    def _inject_keywords_strategically(self, content: str, keywords: List[str]) -> Tuple[str, str]:
        """Inject keywords naturally into resume content"""
        sections = self._parse_resume_sections(content)
        injected_keywords = []
        
        for keyword in keywords:
            if keyword.lower() not in content.lower():
                # Find best section for keyword
                best_section = self._find_best_section_for_keyword(keyword, sections)
                if best_section:
                    sections[best_section] = self._inject_keyword_naturally(sections[best_section], keyword)
                    injected_keywords.append(keyword)
        
        new_content = self._reconstruct_resume(sections)
        return new_content, f"injected {len(injected_keywords)} keywords"
    
    def _parse_resume_sections(self, content: str) -> Dict[str, str]:
        """Parse resume into sections"""
        sections = {
            'summary': '',
            'experience': '',
            'skills': '',
            'education': '',
            'projects': '',
            'other': ''
        }
        
        # Simple section detection based on common headers
        section_patterns = {
            'summary': r'(summary|profile|objective).*?(?=\n[A-Z]|\n\n|\Z)',
            'experience': r'(experience|work|employment).*?(?=\n[A-Z]|\n\n|\Z)',
            'skills': r'(skills|technical|competencies).*?(?=\n[A-Z]|\n\n|\Z)',
            'education': r'(education|academic|qualifications).*?(?=\n[A-Z]|\n\n|\Z)',
            'projects': r'(projects|portfolio).*?(?=\n[A-Z]|\n\n|\Z)'
        }
        
        for section, pattern in section_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section] = match.group()
        
        return sections
    
    def _find_best_section_for_keyword(self, keyword: str, sections: Dict[str, str]) -> Optional[str]:
        """Find the most appropriate section for a keyword"""
        keyword_categories = {
            'technical': ['skills', 'projects', 'experience'],
            'soft': ['summary', 'experience'],
            'tool': ['skills', 'experience'],
            'language': ['skills'],
            'methodology': ['experience', 'projects']
        }
        
        # Simple keyword categorization
        if any(tech in keyword.lower() for tech in ['python', 'java', 'react', 'sql', 'aws']):
            category = 'technical'
        elif any(soft in keyword.lower() for soft in ['leadership', 'communication', 'teamwork']):
            category = 'soft'
        else:
            category = 'technical'  # default
        
        for section in keyword_categories.get(category, ['skills']):
            if sections.get(section):
                return section
        
        return 'skills'  # fallback
    
    def _inject_keyword_naturally(self, section_content: str, keyword: str) -> str:
        """Inject keyword naturally into section"""
        # Find appropriate insertion points
        sentences = sent_tokenize(section_content)
        if not sentences:
            return section_content + f" {keyword}"
        
        # Insert in middle sentence for naturalness
        insert_idx = len(sentences) // 2
        if insert_idx < len(sentences):
            sentences[insert_idx] = f"{sentences[insert_idx].rstrip('.')}. Experienced with {keyword}."
        
        return ' '.join(sentences)
    
    def _reorder_sections(self, content: str) -> Tuple[str, str]:
        """Reorder resume sections for better impact"""
        # This is a simplified version - in practice, you'd want more sophisticated logic
        return content, "sections reordered for impact"
    
    def _optimize_bullet_points(self, content: str, job_description: str) -> Tuple[str, str]:
        """Optimize bullet points based on job requirements"""
        # Extract bullet points and enhance them
        bullet_pattern = r'•\s*([^\n]+)'
        bullets = re.findall(bullet_pattern, content)
        
        optimized_count = 0
        for i, bullet in enumerate(bullets):
            if len(bullet) < 50:  # Short bullets can be enhanced
                enhanced_bullet = f"• Successfully {bullet.lower()}, contributing to team efficiency and project delivery"
                content = content.replace(f"• {bullet}", enhanced_bullet, 1)
                optimized_count += 1
        
        return content, f"optimized {optimized_count} bullet points"
    
    def _enhance_skills_section(self, content: str, keywords: List[str]) -> Tuple[str, str]:
        """Enhance skills section with relevant keywords"""
        skills_added = 0
        for keyword in keywords[:3]:  # Add top 3 keywords to skills
            if keyword not in content and 'skills' in content.lower():
                # Find skills section and add keyword
                skills_pattern = r'(skills.*?)(\n\n|\Z)'
                match = re.search(skills_pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    skills_content = match.group(1)
                    enhanced_skills = f"{skills_content}, {keyword}"
                    content = content.replace(skills_content, enhanced_skills)
                    skills_added += 1
        
        return content, f"added {skills_added} skills"
    
    def _emphasize_relevant_experience(self, content: str, job_description: str) -> Tuple[str, str]:
        """Emphasize experience relevant to job"""
        return content, "emphasized relevant experience"
    
    def _adjust_formatting(self, content: str) -> Tuple[str, str]:
        """Adjust resume formatting"""
        return content, "adjusted formatting"
    
    def _reconstruct_resume(self, sections: Dict[str, str]) -> str:
        """Reconstruct resume from sections"""
        return '\n\n'.join([section for section in sections.values() if section])
    
    def crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Dict[str, Any]:
        """Create offspring through crossover"""
        offspring = {
            'id': str(uuid.uuid4()),
            'content': parent1['content'],
            'keywords': parent1['keywords'],
            'fitness': 0.0,
            'generation': self.generation + 1,
            'parent_ids': [parent1['id'], parent2['id']],
            'mutations': []
        }
        
        # Simple crossover: mix sections from both parents
        sections1 = self._parse_resume_sections(parent1['content'])
        sections2 = self._parse_resume_sections(parent2['content'])
        
        mixed_sections = {}
        for section in sections1.keys():
            if random.random() < 0.5:
                mixed_sections[section] = sections1[section]
            else:
                mixed_sections[section] = sections2[section]
        
        offspring['content'] = self._reconstruct_resume(mixed_sections)
        return offspring
    
    def selection(self, population: List[Dict[str, Any]], num_parents: int) -> List[Dict[str, Any]]:
        """Select parents for next generation using tournament selection"""
        parents = []
        for _ in range(num_parents):
            tournament_size = min(3, len(population))
            tournament = random.sample(population, tournament_size)
            winner = max(tournament, key=lambda x: x['fitness'])
            parents.append(winner)
        return parents


class ATSScoreEngine:
    """Advanced ATS scoring engine"""
    
    def __init__(self):
        self.section_weights = {
            'contact_info': 0.10,
            'summary': 0.15,
            'experience': 0.30,
            'education': 0.15,
            'skills': 0.20,
            'format': 0.10
        }
        
        self.keyword_weights = {
            'exact_match': 1.0,
            'partial_match': 0.7,
            'synonym_match': 0.5,
            'context_match': 0.8
        }
    
    def calculate_ats_score(self, resume_content: str, job_description: str = None) -> ATSAnalysis:
        """Calculate comprehensive ATS score"""
        analysis = ATSAnalysis(
            resume_version_id="",  # Will be set by calling function
            overall_score=0.0,
            keyword_score=0.0,
            format_score=0.0,
            length_score=0.0,
            section_score=0.0,
            experience_score=0.0,
            education_score=0.0,
            skills_score=0.0,
            contact_score=0.0
        )
        
        # Contact Information Score
        analysis.contact_score = self._score_contact_info(resume_content)
        
        # Format Score
        analysis.format_score = self._score_format(resume_content)
        
        # Length Score
        analysis.length_score = self._score_length(resume_content)
        
        # Section Score
        analysis.section_score = self._score_sections(resume_content)
        
        # Experience Score
        analysis.experience_score = self._score_experience(resume_content)
        
        # Education Score
        analysis.education_score = self._score_education(resume_content)
        
        # Skills Score
        analysis.skills_score = self._score_skills(resume_content)
        
        # Keyword Score (if job description provided)
        if job_description:
            analysis.keyword_score, analysis.missing_keywords, analysis.keyword_frequency = self._score_keywords(resume_content, job_description)
        else:
            analysis.keyword_score = 70.0  # Default score without job description
        
        # Calculate overall score
        analysis.overall_score = (
            analysis.contact_score * self.section_weights['contact_info'] +
            analysis.format_score * self.section_weights['format'] +
            analysis.section_score * self.section_weights['summary'] +
            analysis.experience_score * self.section_weights['experience'] +
            analysis.education_score * self.section_weights['education'] +
            analysis.skills_score * self.section_weights['skills'] +
            analysis.keyword_score * 0.3  # Keyword score has high weight
        )
        
        # Generate recommendations
        analysis.recommendations = self._generate_recommendations(analysis)
        analysis.improvement_suggestions = self._generate_improvement_suggestions(analysis)
        
        return analysis
    
    def _score_contact_info(self, content: str) -> float:
        """Score contact information completeness"""
        score = 0.0
        max_score = 100.0
        
        # Check for email
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
            score += 30.0
        
        # Check for phone
        if re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', content):
            score += 25.0
        
        # Check for LinkedIn
        if re.search(r'linkedin\.com|linkedin\.in', content, re.IGNORECASE):
            score += 20.0
        
        # Check for location
        if re.search(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b', content):
            score += 25.0
        
        return min(score, max_score)
    
    def _score_format(self, content: str) -> float:
        """Score resume formatting"""
        score = 70.0  # Base score for text format
        
        # Check for consistent formatting patterns
        bullet_points = len(re.findall(r'[•\-\*]\s', content))
        if bullet_points > 5:
            score += 10.0
        
        # Check for section headers
        headers = len(re.findall(r'^[A-Z\s]+$', content, re.MULTILINE))
        if headers > 3:
            score += 10.0
        
        # Penalty for excessive length
        if len(content) > 5000:
            score -= 10.0
        
        return min(score, 100.0)
    
    def _score_length(self, content: str) -> float:
        """Score resume length appropriateness"""
        word_count = len(content.split())
        
        if 300 <= word_count <= 800:
            return 100.0
        elif 250 <= word_count < 300 or 800 < word_count <= 1000:
            return 80.0
        elif 200 <= word_count < 250 or 1000 < word_count <= 1200:
            return 60.0
        else:
            return 40.0
    
    def _score_sections(self, content: str) -> float:
        """Score presence and quality of resume sections"""
        required_sections = {
            'summary': [r'summary|profile|objective'],
            'experience': [r'experience|work|employment'],
            'education': [r'education|academic'],
            'skills': [r'skills|technical|competencies']
        }
        
        score = 0.0
        for section, patterns in required_sections.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    score += 25.0
                    break
        
        return min(score, 100.0)
    
    def _score_experience(self, content: str) -> float:
        """Score experience section quality"""
        score = 0.0
        
        # Check for dates
        date_patterns = [
            r'\d{4}\s*-\s*\d{4}',
            r'\d{1,2}/\d{4}\s*-\s*\d{1,2}/\d{4}',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, content):
                score += 20.0
                break
        
        # Check for job titles
        if re.search(r'(engineer|developer|manager|analyst|specialist|coordinator)', content, re.IGNORECASE):
            score += 20.0
        
        # Check for quantified achievements
        if re.search(r'\d+%|\$\d+|\d+\s+(users|customers|projects|team)', content):
            score += 30.0
        
        # Check for action verbs
        action_verbs = ['developed', 'managed', 'led', 'created', 'implemented', 'designed', 'optimized']
        for verb in action_verbs:
            if verb in content.lower():
                score += 5.0
        
        return min(score, 100.0)
    
    def _score_education(self, content: str) -> float:
        """Score education section"""
        score = 0.0
        
        # Check for degree
        degrees = ['bachelor', 'master', 'phd', 'b.s.', 'm.s.', 'b.a.', 'm.a.']
        for degree in degrees:
            if degree in content.lower():
                score += 40.0
                break
        
        # Check for institution
        if re.search(r'university|college|institute', content, re.IGNORECASE):
            score += 30.0
        
        # Check for graduation year
        if re.search(r'(19|20)\d{2}', content):
            score += 30.0
        
        return min(score, 100.0)
    
    def _score_skills(self, content: str) -> float:
        """Score skills section"""
        score = 0.0
        
        # Count distinct skills mentioned
        common_skills = [
            'python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'agile', 'scrum', 'machine learning', 'ai'
        ]
        
        skills_found = 0
        for skill in common_skills:
            if skill in content.lower():
                skills_found += 1
        
        score = min(skills_found * 10, 100.0)
        return score
    
    def _score_keywords(self, resume_content: str, job_description: str) -> Tuple[float, List[str], Dict[str, int]]:
        """Score keyword matching against job description"""
        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description)
        resume_keywords = self._extract_keywords(resume_content)
        
        matched_keywords = 0
        total_keywords = len(job_keywords)
        missing_keywords = []
        keyword_frequency = {}
        
        for keyword in job_keywords:
            freq = resume_content.lower().count(keyword.lower())
            keyword_frequency[keyword] = freq
            
            if freq > 0:
                matched_keywords += 1
            else:
                missing_keywords.append(keyword)
        
        if total_keywords == 0:
            return 70.0, missing_keywords, keyword_frequency
        
        keyword_score = (matched_keywords / total_keywords) * 100
        return keyword_score, missing_keywords, keyword_frequency
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        # Tokenize and filter
        words = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        
        # Filter out stop words and short words
        keywords = [word for word in words if word.isalpha() and len(word) > 2 and word not in stop_words]
        
        # Get most common keywords
        word_freq = Counter(keywords)
        return [word for word, freq in word_freq.most_common(30)]
    
    def _generate_recommendations(self, analysis: ATSAnalysis) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if analysis.contact_score < 80:
            recommendations.append("Add complete contact information including email, phone, and LinkedIn profile")
        
        if analysis.keyword_score < 70:
            recommendations.append("Include more relevant keywords from the job description")
        
        if analysis.experience_score < 80:
            recommendations.append("Add more quantified achievements and use stronger action verbs")
        
        if analysis.skills_score < 70:
            recommendations.append("Expand the skills section with more relevant technical skills")
        
        if analysis.format_score < 80:
            recommendations.append("Improve formatting with consistent bullet points and clear section headers")
        
        return recommendations
    
    def _generate_improvement_suggestions(self, analysis: ATSAnalysis) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        if analysis.missing_keywords:
            suggestions.append(f"Consider adding these missing keywords: {', '.join(analysis.missing_keywords[:5])}")
        
        if analysis.overall_score < 80:
            suggestions.append("Overall ATS score can be improved by focusing on keyword optimization and formatting")
        
        return suggestions


class ResumeTailoringService:
    """Advanced Resume Tailoring Service with Genetic Algorithm and ATS Optimization"""
    
    def __init__(self, db, openrouter_service: Optional[OpenRouterService] = None):
        self.db = db
        self.openrouter_service = openrouter_service or OpenRouterService()
        self.genetic_optimizer = ResumeGeneticOptimizer()
        self.ats_engine = ATSScoreEngine()
        
        # Ensure collection exists
        self.collection = self.db['resume_versions']
        self.genetic_collection = self.db['resume_genetic_pools']
        self.ats_collection = self.db['ats_analyses']
        self.performance_collection = self.db['resume_performance_metrics']
        self.optimization_collection = self.db['keyword_optimizations']
    
    async def tailor_resume_for_job(
        self, 
        candidate_id: str, 
        resume_id: str, 
        job_id: str, 
        job_description: str,
        strategy: TailoringStrategy = TailoringStrategy.JOB_SPECIFIC,
        optimization_level: ATSOptimization = ATSOptimization.ADVANCED,
        use_genetic_algorithm: bool = True
    ) -> ResumeVersion:
        """Tailor resume for specific job using advanced AI and genetic algorithms"""
        
        # Get original resume
        original_resume = await self._get_original_resume(resume_id)
        if not original_resume:
            raise ValueError(f"Resume {resume_id} not found")
        
        # Extract target keywords from job description
        target_keywords = self._extract_job_keywords(job_description)
        
        if use_genetic_algorithm:
            # Use genetic algorithm for optimization
            best_version = await self._optimize_with_genetic_algorithm(
                candidate_id, resume_id, job_id, original_resume['extracted_text'],
                job_description, target_keywords, strategy, optimization_level
            )
        else:
            # Use direct AI tailoring
            best_version = await self._tailor_with_ai(
                candidate_id, resume_id, job_id, original_resume['extracted_text'],
                job_description, target_keywords, strategy, optimization_level
            )
        
        # Perform ATS analysis
        ats_analysis = self.ats_engine.calculate_ats_score(best_version.tailored_content, job_description)
        ats_analysis.resume_version_id = best_version.id
        
        # Save ATS analysis
        await self.ats_collection.insert_one(ats_analysis.dict())
        
        # Update resume version with ATS scores
        best_version.ats_score = ats_analysis.overall_score
        best_version.ats_breakdown = {
            'keyword_score': ats_analysis.keyword_score,
            'format_score': ats_analysis.format_score,
            'section_score': ats_analysis.section_score,
            'experience_score': ats_analysis.experience_score,
            'education_score': ats_analysis.education_score,
            'skills_score': ats_analysis.skills_score,
            'contact_score': ats_analysis.contact_score
        }
        
        # Generate stealth fingerprint
        best_version.stealth_fingerprint = self._generate_stealth_fingerprint(best_version.tailored_content)
        
        # Save resume version
        await self.collection.insert_one(best_version.dict())
        
        # Initialize performance metrics
        metrics = ResumePerformanceMetrics(
            resume_version_id=best_version.id,
            job_id=job_id
        )
        await self.performance_collection.insert_one(metrics.dict())
        
        return best_version
    
    async def _optimize_with_genetic_algorithm(
        self, 
        candidate_id: str, 
        resume_id: str, 
        job_id: str,
        original_content: str,
        job_description: str,
        target_keywords: List[str],
        strategy: TailoringStrategy,
        optimization_level: ATSOptimization
    ) -> ResumeVersion:
        """Optimize resume using genetic algorithm"""
        
        # Initialize genetic pool
        population = self.genetic_optimizer.initialize_population(original_content, job_description, target_keywords)
        
        # Calculate initial fitness scores
        for individual in population:
            individual['fitness'] = await self._calculate_fitness(individual['content'], job_description)
        
        # Store genetic pool
        genetic_pool = ResumeGeneticPool(
            candidate_id=candidate_id,
            job_id=job_id,
            generation=0,
            population_size=len(population),
            fitness_scores=[ind['fitness'] for ind in population],
            version_ids=[ind['id'] for ind in population]
        )
        
        best_individual = max(population, key=lambda x: x['fitness'])
        genetic_pool.best_version_id = best_individual['id']
        
        await self.genetic_collection.insert_one(genetic_pool.dict())
        
        # Evolution loop
        for generation in range(self.genetic_optimizer.max_generations):
            self.genetic_optimizer.generation = generation
            
            # Selection
            parents = self.genetic_optimizer.selection(population, self.genetic_optimizer.population_size // 2)
            
            # Create new generation
            new_population = []
            
            # Elitism: keep best individuals
            population_sorted = sorted(population, key=lambda x: x['fitness'], reverse=True)
            elite_count = max(1, self.genetic_optimizer.population_size // 5)
            new_population.extend(population_sorted[:elite_count])
            
            # Crossover and mutation
            while len(new_population) < self.genetic_optimizer.population_size:
                if random.random() < self.genetic_optimizer.crossover_rate:
                    parent1, parent2 = random.sample(parents, 2)
                    offspring = self.genetic_optimizer.crossover(parent1, parent2)
                    offspring = self.genetic_optimizer._mutate(offspring, job_description)
                else:
                    parent = random.choice(parents)
                    offspring = self.genetic_optimizer._mutate(parent.copy(), job_description)
                
                # Calculate fitness for offspring
                offspring['fitness'] = await self._calculate_fitness(offspring['content'], job_description)
                new_population.append(offspring)
            
            population = new_population[:self.genetic_optimizer.population_size]
            
            # Check for convergence
            current_best = max(population, key=lambda x: x['fitness'])
            if abs(current_best['fitness'] - self.genetic_optimizer.best_fitness) < self.genetic_optimizer.convergence_threshold:
                break
            
            self.genetic_optimizer.best_fitness = current_best['fitness']
        
        # Get best individual
        best_individual = max(population, key=lambda x: x['fitness'])
        
        # Create final resume version
        version_name = f"GA_Optimized_{strategy.value}_{optimization_level.value}"
        resume_version = ResumeVersion(
            candidate_id=candidate_id,
            resume_id=resume_id,
            version_name=version_name,
            tailored_for_job_id=job_id,
            tailoring_strategy=strategy,
            ats_optimization_level=optimization_level,
            tailored_content=best_individual['content'],
            original_content=original_content,
            keywords_injected=target_keywords,
            generation_params={
                'generation': generation + 1,
                'fitness_score': best_individual['fitness'],
                'mutations': best_individual['mutations'],
                'parent_ids': best_individual['parent_ids']
            }
        )
        
        return resume_version
    
    async def _tailor_with_ai(
        self,
        candidate_id: str,
        resume_id: str, 
        job_id: str,
        original_content: str,
        job_description: str,
        target_keywords: List[str],
        strategy: TailoringStrategy,
        optimization_level: ATSOptimization
    ) -> ResumeVersion:
        """Tailor resume using AI without genetic algorithm"""
        
        # Create tailoring prompt
        prompt = self._create_tailoring_prompt(original_content, job_description, target_keywords, strategy, optimization_level)
        
        # Use OpenRouter for tailoring
        tailored_content = await self.openrouter_service.generate_completion(
            prompt=prompt,
            model_type="resume_tailoring",
            max_tokens=2000
        )
        
        version_name = f"AI_Tailored_{strategy.value}_{optimization_level.value}"
        resume_version = ResumeVersion(
            candidate_id=candidate_id,
            resume_id=resume_id,
            version_name=version_name,
            tailored_for_job_id=job_id,
            tailoring_strategy=strategy,
            ats_optimization_level=optimization_level,
            tailored_content=tailored_content,
            original_content=original_content,
            keywords_injected=target_keywords,
            generation_params={
                'method': 'ai_direct',
                'strategy': strategy.value,
                'optimization_level': optimization_level.value
            }
        )
        
        return resume_version
    
    def _create_tailoring_prompt(
        self, 
        original_content: str, 
        job_description: str, 
        keywords: List[str],
        strategy: TailoringStrategy,
        optimization_level: ATSOptimization
    ) -> str:
        """Create AI prompt for resume tailoring"""
        
        optimization_instructions = {
            ATSOptimization.BASIC: "Apply basic keyword optimization and formatting improvements.",
            ATSOptimization.ADVANCED: "Apply advanced ATS optimization including strategic keyword placement, section enhancement, and content restructuring.",
            ATSOptimization.AGGRESSIVE: "Apply aggressive optimization with maximum keyword density and comprehensive content modification.",
            ATSOptimization.STEALTH: "Apply stealth optimization that appears natural while maximizing ATS scores."
        }
        
        strategy_instructions = {
            TailoringStrategy.JOB_SPECIFIC: "Focus on matching the specific job requirements and responsibilities.",
            TailoringStrategy.COMPANY_SPECIFIC: "Emphasize alignment with company culture and values.",
            TailoringStrategy.ROLE_SPECIFIC: "Highlight experience and skills relevant to the role level.",
            TailoringStrategy.INDUSTRY_SPECIFIC: "Emphasize industry-relevant experience and knowledge.",
            TailoringStrategy.SKILL_FOCUSED: "Prioritize technical skills and competencies.",
            TailoringStrategy.EXPERIENCE_FOCUSED: "Emphasize relevant work experience and achievements."
        }
        
        prompt = f"""
You are an expert resume writer and ATS optimization specialist. Your task is to tailor the following resume for a specific job opportunity.

ORIGINAL RESUME:
{original_content}

JOB DESCRIPTION:
{job_description}

TARGET KEYWORDS TO INCLUDE:
{', '.join(keywords)}

TAILORING STRATEGY: {strategy_instructions[strategy]}

OPTIMIZATION LEVEL: {optimization_instructions[optimization_level]}

INSTRUCTIONS:
1. Tailor the resume to match the job requirements while maintaining authenticity
2. Strategically incorporate the target keywords naturally throughout the content
3. Optimize for ATS scanning while keeping the content human-readable
4. Enhance relevant experience and skills that match the job requirements
5. Maintain the overall structure and flow of the original resume
6. Ensure all claims remain truthful and verifiable

Please provide the optimized resume content:
"""
        return prompt
    
    async def _calculate_fitness(self, content: str, job_description: str) -> float:
        """Calculate fitness score for genetic algorithm"""
        # Use ATS engine for fitness calculation
        ats_analysis = self.ats_engine.calculate_ats_score(content, job_description)
        
        # Fitness is based on overall ATS score with some weights
        fitness = (
            ats_analysis.overall_score * 0.4 +
            ats_analysis.keyword_score * 0.3 +
            ats_analysis.experience_score * 0.2 +
            ats_analysis.skills_score * 0.1
        ) / 100.0  # Normalize to 0-1 range
        
        return fitness
    
    def _extract_job_keywords(self, job_description: str) -> List[str]:
        """Extract important keywords from job description"""
        return self.ats_engine._extract_keywords(job_description)
    
    def _generate_stealth_fingerprint(self, content: str) -> str:
        """Generate unique stealth fingerprint for resume"""
        # Create a unique hash based on content and timestamp
        timestamp = str(datetime.utcnow().timestamp())
        combined = f"{content}{timestamp}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    async def _get_original_resume(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """Get original resume content"""
        resumes_collection = self.db['resumes']
        return await resumes_collection.find_one({"id": resume_id})
    
    async def get_resume_versions(self, candidate_id: str, job_id: str = None) -> List[ResumeVersion]:
        """Get all resume versions for a candidate, optionally filtered by job"""
        query = {"candidate_id": candidate_id}
        if job_id:
            query["tailored_for_job_id"] = job_id
        
        cursor = self.collection.find(query).sort("created_at", -1)
        versions = []
        async for doc in cursor:
            versions.append(ResumeVersion(**doc))
        return versions
    
    async def get_performance_metrics(self, resume_version_id: str) -> Optional[ResumePerformanceMetrics]:
        """Get performance metrics for a resume version"""
        doc = await self.performance_collection.find_one({"resume_version_id": resume_version_id})
        return ResumePerformanceMetrics(**doc) if doc else None
    
    async def update_performance_metrics(
        self, 
        resume_version_id: str, 
        applications_sent: int = None,
        responses_received: int = None,
        interviews_scheduled: int = None,
        offers_received: int = None,
        rejections_received: int = None
    ):
        """Update performance metrics for a resume version"""
        update_data = {"last_updated": datetime.utcnow()}
        
        if applications_sent is not None:
            update_data["applications_sent"] = applications_sent
        if responses_received is not None:
            update_data["responses_received"] = responses_received
            update_data["response_rate"] = responses_received / max(applications_sent or 1, 1)
        if interviews_scheduled is not None:
            update_data["interviews_scheduled"] = interviews_scheduled
            update_data["interview_rate"] = interviews_scheduled / max(applications_sent or 1, 1)
        if offers_received is not None:
            update_data["offers_received"] = offers_received
            update_data["offer_rate"] = offers_received / max(applications_sent or 1, 1)
        if rejections_received is not None:
            update_data["rejections_received"] = rejections_received
        
        await self.performance_collection.update_one(
            {"resume_version_id": resume_version_id},
            {"$set": update_data}
        )
    
    async def generate_resume_variants(
        self, 
        candidate_id: str, 
        resume_id: str, 
        count: int = 5,
        strategies: List[TailoringStrategy] = None
    ) -> List[ResumeVersion]:
        """Generate multiple resume variants for A/B testing"""
        if not strategies:
            strategies = [
                TailoringStrategy.JOB_SPECIFIC,
                TailoringStrategy.SKILL_FOCUSED,
                TailoringStrategy.EXPERIENCE_FOCUSED
            ]
        
        original_resume = await self._get_original_resume(resume_id)
        if not original_resume:
            raise ValueError(f"Resume {resume_id} not found")
        
        variants = []
        for i in range(count):
            strategy = strategies[i % len(strategies)]
            optimization_level = ATSOptimization.ADVANCED
            
            # Create generic version without specific job
            prompt = f"""
Create a professionally optimized version of this resume using {strategy.value} strategy:

{original_resume['extracted_text']}

Focus on:
- {strategy.value.replace('_', ' ').title()} optimization
- ATS-friendly formatting
- Strong action verbs and quantified achievements
- Professional presentation

Provide the optimized resume:
"""
            
            tailored_content = await self.openrouter_service.generate_completion(
                prompt=prompt,
                model_type="resume_tailoring",
                max_tokens=2000
            )
            
            version_name = f"Variant_{i+1}_{strategy.value}"
            version = ResumeVersion(
                candidate_id=candidate_id,
                resume_id=resume_id,
                version_name=version_name,
                tailoring_strategy=strategy,
                ats_optimization_level=optimization_level,
                tailored_content=tailored_content,
                original_content=original_resume['extracted_text'],
                stealth_fingerprint=self._generate_stealth_fingerprint(tailored_content),
                generation_params={
                    'method': 'variant_generation',
                    'strategy': strategy.value,
                    'variant_number': i + 1
                }
            )
            
            # Calculate ATS score
            ats_analysis = self.ats_engine.calculate_ats_score(tailored_content)
            version.ats_score = ats_analysis.overall_score
            
            variants.append(version)
        
        # Save all variants
        for variant in variants:
            await self.collection.insert_one(variant.dict())
            
            # Initialize performance metrics
            metrics = ResumePerformanceMetrics(resume_version_id=variant.id)
            await self.performance_collection.insert_one(metrics.dict())
        
        return variants
    
    async def get_ats_analysis(self, resume_version_id: str) -> Optional[ATSAnalysis]:
        """Get ATS analysis for a resume version"""
        doc = await self.ats_collection.find_one({"resume_version_id": resume_version_id})
        return ATSAnalysis(**doc) if doc else None
    
    async def analyze_resume_performance(self, candidate_id: str) -> Dict[str, Any]:
        """Analyze overall resume performance for a candidate"""
        # Get all resume versions
        versions = await self.get_resume_versions(candidate_id)
        
        if not versions:
            return {"error": "No resume versions found"}
        
        # Get performance metrics for each version
        performance_data = []
        for version in versions:
            metrics = await self.get_performance_metrics(version.id)
            if metrics:
                performance_data.append({
                    "version": version,
                    "metrics": metrics
                })
        
        # Calculate aggregate statistics
        total_applications = sum(data["metrics"].applications_sent for data in performance_data)
        total_responses = sum(data["metrics"].responses_received for data in performance_data)
        total_interviews = sum(data["metrics"].interviews_scheduled for data in performance_data)
        total_offers = sum(data["metrics"].offers_received for data in performance_data)
        
        best_performer = max(performance_data, key=lambda x: x["metrics"].response_rate) if performance_data else None
        
        return {
            "summary": {
                "total_versions": len(versions),
                "total_applications": total_applications,
                "total_responses": total_responses,
                "total_interviews": total_interviews,
                "total_offers": total_offers,
                "overall_response_rate": total_responses / max(total_applications, 1),
                "overall_interview_rate": total_interviews / max(total_applications, 1),
                "overall_offer_rate": total_offers / max(total_applications, 1)
            },
            "best_performer": {
                "version_name": best_performer["version"].version_name if best_performer else None,
                "response_rate": best_performer["metrics"].response_rate if best_performer else 0
            },
            "versions": performance_data
        }


# Singleton instance
_resume_tailoring_service = None

def get_resume_tailoring_service(db=None) -> ResumeTailoringService:
    """Get singleton instance of ResumeTailoringService"""
    global _resume_tailoring_service
    if _resume_tailoring_service is None:
        _resume_tailoring_service = ResumeTailoringService(db)
    return _resume_tailoring_service