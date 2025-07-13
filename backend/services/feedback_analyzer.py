"""
Elite JobHunter X - Feedback Learning Loop (Phase 8)
Advanced machine learning system for continuous optimization

This service handles:
1. Application outcome tracking and analysis
2. Success rate analysis and pattern recognition
3. AI model fine-tuning based on results
4. Automated strategy adjustments
5. Performance optimization algorithms
6. Predictive analytics for job success
"""

import asyncio
import logging
import numpy as np
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
from collections import defaultdict
import statistics

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.preprocessing import StandardScaler
    import pandas as pd
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available - using simplified analytics")

from .openrouter import get_openrouter_service

class ApplicationOutcome(Enum):
    PENDING = "pending"
    VIEWED = "viewed"
    REJECTED = "rejected"
    PHONE_SCREEN = "phone_screen"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    OFFER_RECEIVED = "offer_received"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"

class OptimizationStrategy(Enum):
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    TIMING_OPTIMIZATION = "timing_optimization"
    RESUME_STRATEGY = "resume_strategy"
    OUTREACH_STRATEGY = "outreach_strategy"
    JOB_TARGETING = "job_targeting"

@dataclass
class PerformanceMetrics:
    total_applications: int
    response_rate: float
    interview_rate: float
    offer_rate: float
    success_score: float
    avg_time_to_response: float
    top_performing_keywords: List[str]
    best_application_times: List[int]  # Hours of day

@dataclass
class OptimizationRecommendation:
    strategy: OptimizationStrategy
    current_performance: float
    predicted_improvement: float
    confidence: float
    action_items: List[str]
    priority: int

class FeedbackAnalyzer:
    """
    ADVANCED FEEDBACK LEARNING SYSTEM
    Continuously learns from application outcomes to optimize strategies
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.logger = self._setup_logging()
        self.openrouter = get_openrouter_service()
        
        # ML Models for prediction and optimization
        self.success_predictor = None
        self.keyword_optimizer = None
        self.timing_optimizer = None
        
        # Performance tracking
        self.baseline_metrics = {}
        self.optimization_history = []
        
    def _setup_logging(self):
        """Setup logging for feedback analysis"""
        logger = logging.getLogger("FeedbackAnalyzer")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def analyze_daily_performance(self):
        """
        Analyze daily performance across all candidates and optimize strategies
        """
        try:
            self.logger.info("📊 Starting daily performance analysis")
            
            # Collect performance data
            performance_data = await self._collect_performance_data()
            
            # Analyze success patterns
            success_patterns = await self._analyze_success_patterns(performance_data)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(success_patterns)
            
            # Apply automated optimizations
            applied_optimizations = await self._apply_automated_optimizations(recommendations)
            
            # Update ML models with new data
            if SKLEARN_AVAILABLE:
                await self._update_ml_models(performance_data)
            
            # Generate performance report
            report = await self._generate_performance_report(
                performance_data, 
                success_patterns, 
                recommendations,
                applied_optimizations
            )
            
            # Save analysis results
            await self._save_analysis_results(report)
            
            self.logger.info("✅ Daily performance analysis completed")
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Performance analysis error: {e}")
            return None
    
    async def _collect_performance_data(self) -> Dict[str, Any]:
        """
        Collect comprehensive performance data from all system components
        """
        try:
            # Time ranges for analysis
            today = datetime.utcnow().replace(hour=0, minute=0, second=0)
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Application outcomes data
            applications_pipeline = [
                {"$match": {"created_at": {"$gte": month_ago}}},
                {"$group": {
                    "_id": {
                        "candidate_id": "$candidate_id",
                        "outcome": "$outcome",
                        "week": {"$week": "$created_at"}
                    },
                    "count": {"$sum": 1},
                    "avg_ats_score": {"$avg": "$ats_score"},
                    "keywords_used": {"$push": "$keywords"}
                }}
            ]
            
            application_stats = await self.db.applications.aggregate(applications_pipeline).to_list(None)
            
            # Job matching performance
            matching_pipeline = [
                {"$match": {"created_at": {"$gte": month_ago}}},
                {"$group": {
                    "_id": "$candidate_id",
                    "total_matches": {"$sum": 1},
                    "avg_match_score": {"$avg": "$match_score"},
                    "applied_ratio": {
                        "$avg": {
                            "$cond": [{"$eq": ["$applied", True]}, 1, 0]
                        }
                    }
                }}
            ]
            
            matching_stats = await self.db.job_matches.aggregate(matching_pipeline).to_list(None)
            
            # Resume tailoring effectiveness
            tailoring_pipeline = [
                {"$match": {"created_at": {"$gte": month_ago}}},
                {"$group": {
                    "_id": "$strategy",
                    "avg_ats_improvement": {"$avg": "$ats_improvement"},
                    "success_rate": {
                        "$avg": {
                            "$cond": [{"$gte": ["$final_ats_score", 80]}, 1, 0]
                        }
                    },
                    "usage_count": {"$sum": 1}
                }}
            ]
            
            tailoring_stats = await self.db.resume_versions.aggregate(tailoring_pipeline).to_list(None)
            
            # Outreach effectiveness
            outreach_pipeline = [
                {"$match": {"created_at": {"$gte": month_ago}}},
                {"$group": {
                    "_id": "$message_type",
                    "total_sent": {"$sum": 1},
                    "response_rate": {
                        "$avg": {
                            "$cond": [{"$eq": ["$status", "replied"]}, 1, 0]
                        }
                    },
                    "connection_rate": {
                        "$avg": {
                            "$cond": [{"$eq": ["$status", "connected"]}, 1, 0]
                        }
                    }
                }}
            ]
            
            outreach_stats = await self.db.outreach_messages.aggregate(outreach_pipeline).to_list(None)
            
            return {
                "applications": application_stats,
                "matching": matching_stats,
                "tailoring": tailoring_stats,
                "outreach": outreach_stats,
                "analysis_period": {
                    "start_date": month_ago,
                    "end_date": datetime.utcnow()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Performance data collection error: {e}")
            return {}
    
    async def _analyze_success_patterns(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze patterns in successful vs unsuccessful applications
        """
        try:
            patterns = {
                "successful_keywords": [],
                "optimal_application_times": [],
                "best_resume_strategies": [],
                "effective_outreach_approaches": [],
                "candidate_success_factors": {}
            }
            
            # Analyze keyword effectiveness
            keyword_success = defaultdict(list)
            
            for app_stat in performance_data.get("applications", []):
                outcome = app_stat["_id"]["outcome"]
                keywords = app_stat.get("keywords_used", [])
                
                success_score = self._calculate_success_score(outcome)
                
                for keyword_list in keywords:
                    for keyword in keyword_list:
                        keyword_success[keyword].append(success_score)
            
            # Find top-performing keywords
            keyword_performance = {}
            for keyword, scores in keyword_success.items():
                if len(scores) >= 3:  # Minimum sample size
                    keyword_performance[keyword] = {
                        "avg_success": statistics.mean(scores),
                        "usage_count": len(scores),
                        "consistency": 1 - statistics.stdev(scores) / statistics.mean(scores) if statistics.mean(scores) > 0 else 0
                    }
            
            # Sort by performance
            top_keywords = sorted(
                keyword_performance.items(),
                key=lambda x: x[1]["avg_success"] * x[1]["consistency"],
                reverse=True
            )[:10]
            
            patterns["successful_keywords"] = [kw[0] for kw in top_keywords]
            
            # Analyze resume strategy effectiveness
            strategy_performance = {}
            for tailoring_stat in performance_data.get("tailoring", []):
                strategy = tailoring_stat["_id"]
                strategy_performance[strategy] = {
                    "avg_improvement": tailoring_stat["avg_ats_improvement"],
                    "success_rate": tailoring_stat["success_rate"],
                    "usage_count": tailoring_stat["usage_count"]
                }
            
            best_strategies = sorted(
                strategy_performance.items(),
                key=lambda x: x[1]["success_rate"] * x[1]["avg_improvement"],
                reverse=True
            )
            
            patterns["best_resume_strategies"] = [s[0] for s in best_strategies[:3]]
            
            # Analyze outreach effectiveness
            outreach_performance = {}
            for outreach_stat in performance_data.get("outreach", []):
                message_type = outreach_stat["_id"]
                outreach_performance[message_type] = {
                    "response_rate": outreach_stat["response_rate"],
                    "connection_rate": outreach_stat["connection_rate"],
                    "total_sent": outreach_stat["total_sent"]
                }
            
            effective_outreach = sorted(
                outreach_performance.items(),
                key=lambda x: x[1]["response_rate"] + x[1]["connection_rate"],
                reverse=True
            )
            
            patterns["effective_outreach_approaches"] = [o[0] for o in effective_outreach]
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Success pattern analysis error: {e}")
            return {}
    
    async def _generate_optimization_recommendations(
        self, 
        success_patterns: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """
        Generate actionable optimization recommendations based on success patterns
        """
        try:
            recommendations = []
            
            # Keyword optimization recommendations
            if success_patterns.get("successful_keywords"):
                top_keywords = success_patterns["successful_keywords"][:5]
                
                keyword_rec = OptimizationRecommendation(
                    strategy=OptimizationStrategy.KEYWORD_OPTIMIZATION,
                    current_performance=await self._get_current_keyword_performance(),
                    predicted_improvement=15.0,  # Estimated 15% improvement
                    confidence=0.8,
                    action_items=[
                        f"Increase usage of high-performing keywords: {', '.join(top_keywords)}",
                        "Update resume templates to include successful keywords",
                        "Modify job matching algorithm to prioritize keyword-rich positions",
                        "Train cover letter generation to emphasize effective keywords"
                    ],
                    priority=1
                )
                recommendations.append(keyword_rec)
            
            # Resume strategy optimization
            if success_patterns.get("best_resume_strategies"):
                best_strategies = success_patterns["best_resume_strategies"][:2]
                
                resume_rec = OptimizationRecommendation(
                    strategy=OptimizationStrategy.RESUME_STRATEGY,
                    current_performance=await self._get_current_resume_performance(),
                    predicted_improvement=12.0,
                    confidence=0.75,
                    action_items=[
                        f"Default to high-performing strategies: {', '.join(best_strategies)}",
                        "Increase genetic algorithm emphasis on successful strategies",
                        "Update strategy selection weights based on performance data",
                        "A/B test strategy combinations for compound improvements"
                    ],
                    priority=2
                )
                recommendations.append(resume_rec)
            
            # Outreach optimization
            if success_patterns.get("effective_outreach_approaches"):
                effective_approaches = success_patterns["effective_outreach_approaches"][:2]
                
                outreach_rec = OptimizationRecommendation(
                    strategy=OptimizationStrategy.OUTREACH_STRATEGY,
                    current_performance=await self._get_current_outreach_performance(),
                    predicted_improvement=20.0,
                    confidence=0.7,
                    action_items=[
                        f"Focus on effective message types: {', '.join(effective_approaches)}",
                        "Adjust outreach timing based on response patterns",
                        "Personalize messages using successful templates",
                        "Increase frequency of high-performing outreach methods"
                    ],
                    priority=3
                )
                recommendations.append(outreach_rec)
            
            # Use AI to generate additional insights
            ai_recommendations = await self._generate_ai_insights(success_patterns)
            recommendations.extend(ai_recommendations)
            
            # Sort by priority and predicted impact
            recommendations.sort(key=lambda x: (x.priority, -x.predicted_improvement))
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation error: {e}")
            return []
    
    async def _apply_automated_optimizations(
        self, 
        recommendations: List[OptimizationRecommendation]
    ) -> List[Dict[str, Any]]:
        """
        Apply automated optimizations based on recommendations
        """
        try:
            applied_optimizations = []
            
            for rec in recommendations[:3]:  # Apply top 3 recommendations
                if rec.confidence >= 0.7:  # Only apply high-confidence recommendations
                    
                    optimization_result = await self._apply_single_optimization(rec)
                    
                    if optimization_result["success"]:
                        applied_optimizations.append({
                            "strategy": rec.strategy.value,
                            "predicted_improvement": rec.predicted_improvement,
                            "confidence": rec.confidence,
                            "action_items": rec.action_items,
                            "applied_at": datetime.utcnow(),
                            "result": optimization_result
                        })
                        
                        self.logger.info(f"✅ Applied optimization: {rec.strategy.value}")
                    else:
                        self.logger.warning(f"⚠️ Failed to apply optimization: {rec.strategy.value}")
            
            return applied_optimizations
            
        except Exception as e:
            self.logger.error(f"Optimization application error: {e}")
            return []
    
    async def _apply_single_optimization(
        self, 
        recommendation: OptimizationRecommendation
    ) -> Dict[str, Any]:
        """
        Apply a single optimization recommendation
        """
        try:
            if recommendation.strategy == OptimizationStrategy.KEYWORD_OPTIMIZATION:
                return await self._apply_keyword_optimization(recommendation)
            
            elif recommendation.strategy == OptimizationStrategy.RESUME_STRATEGY:
                return await self._apply_resume_strategy_optimization(recommendation)
            
            elif recommendation.strategy == OptimizationStrategy.OUTREACH_STRATEGY:
                return await self._apply_outreach_optimization(recommendation)
            
            elif recommendation.strategy == OptimizationStrategy.JOB_TARGETING:
                return await self._apply_job_targeting_optimization(recommendation)
            
            else:
                return {"success": False, "reason": "Unknown optimization strategy"}
                
        except Exception as e:
            return {"success": False, "reason": str(e)}
    
    async def _apply_keyword_optimization(self, rec: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply keyword optimization"""
        try:
            # Update system-wide keyword preferences
            await self.db.system_config.update_one(
                {"_id": "keyword_optimization"},
                {
                    "$set": {
                        "priority_keywords": rec.action_items,
                        "updated_at": datetime.utcnow(),
                        "confidence": rec.confidence
                    }
                },
                upsert=True
            )
            
            return {"success": True, "action": "Updated priority keywords"}
            
        except Exception as e:
            return {"success": False, "reason": str(e)}
    
    async def _apply_resume_strategy_optimization(self, rec: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply resume strategy optimization"""
        try:
            # Update resume strategy weights
            await self.db.system_config.update_one(
                {"_id": "resume_strategy_weights"},
                {
                    "$set": {
                        "optimization_data": rec.action_items,
                        "updated_at": datetime.utcnow(),
                        "predicted_improvement": rec.predicted_improvement
                    }
                },
                upsert=True
            )
            
            return {"success": True, "action": "Updated resume strategy weights"}
            
        except Exception as e:
            return {"success": False, "reason": str(e)}
    
    async def _apply_outreach_optimization(self, rec: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply outreach strategy optimization"""
        try:
            # Update outreach configuration
            await self.db.system_config.update_one(
                {"_id": "outreach_optimization"},
                {
                    "$set": {
                        "preferred_methods": rec.action_items,
                        "updated_at": datetime.utcnow(),
                        "confidence": rec.confidence
                    }
                },
                upsert=True
            )
            
            return {"success": True, "action": "Updated outreach preferences"}
            
        except Exception as e:
            return {"success": False, "reason": str(e)}
    
    async def _apply_job_targeting_optimization(self, rec: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply job targeting optimization"""
        try:
            # Update job matching parameters
            await self.db.system_config.update_one(
                {"_id": "job_targeting"},
                {
                    "$set": {
                        "targeting_parameters": rec.action_items,
                        "updated_at": datetime.utcnow(),
                        "improvement_score": rec.predicted_improvement
                    }
                },
                upsert=True
            )
            
            return {"success": True, "action": "Updated job targeting parameters"}
            
        except Exception as e:
            return {"success": False, "reason": str(e)}
    
    async def _generate_ai_insights(self, success_patterns: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """
        Generate additional insights using AI analysis
        """
        try:
            prompt = f"""
            Analyze the following job application success patterns and generate 2 additional optimization recommendations:
            
            Successful Keywords: {success_patterns.get('successful_keywords', [])}
            Best Resume Strategies: {success_patterns.get('best_resume_strategies', [])}
            Effective Outreach: {success_patterns.get('effective_outreach_approaches', [])}
            
            Based on this data, suggest 2 specific, actionable optimizations that could improve job application success rates.
            
            Format your response as JSON:
            {{
                "recommendations": [
                    {{
                        "strategy": "timing_optimization",
                        "predicted_improvement": 10.0,
                        "confidence": 0.8,
                        "action_items": ["specific action 1", "specific action 2"]
                    }}
                ]
            }}
            """
            
            response = await self.openrouter.get_completion(
                messages=[{"role": "user", "content": prompt}],
                model="google/gemma-2-9b-it:free",  # Free model
                max_tokens=300
            )
            
            ai_recommendations = []
            
            if response and "recommendations" in response:
                for rec_data in response["recommendations"]:
                    strategy_mapping = {
                        "timing_optimization": OptimizationStrategy.TIMING_OPTIMIZATION,
                        "keyword_optimization": OptimizationStrategy.KEYWORD_OPTIMIZATION,
                        "resume_strategy": OptimizationStrategy.RESUME_STRATEGY,
                        "outreach_strategy": OptimizationStrategy.OUTREACH_STRATEGY,
                        "job_targeting": OptimizationStrategy.JOB_TARGETING
                    }
                    
                    strategy = strategy_mapping.get(rec_data.get("strategy"), OptimizationStrategy.JOB_TARGETING)
                    
                    ai_rec = OptimizationRecommendation(
                        strategy=strategy,
                        current_performance=0.0,  # Will be calculated
                        predicted_improvement=rec_data.get("predicted_improvement", 5.0),
                        confidence=rec_data.get("confidence", 0.6),
                        action_items=rec_data.get("action_items", []),
                        priority=4  # Lower priority for AI-generated
                    )
                    ai_recommendations.append(ai_rec)
            
            return ai_recommendations
            
        except Exception as e:
            self.logger.error(f"AI insights generation error: {e}")
            return []
    
    def _calculate_success_score(self, outcome: str) -> float:
        """Calculate success score based on application outcome"""
        outcome_scores = {
            "pending": 0.1,
            "viewed": 0.2,
            "rejected": 0.0,
            "phone_screen": 0.5,
            "interview_scheduled": 0.7,
            "interview_completed": 0.8,
            "offer_received": 1.0,
            "offer_accepted": 1.0,
            "offer_declined": 0.9
        }
        
        return outcome_scores.get(outcome, 0.0)
    
    async def _get_current_keyword_performance(self) -> float:
        """Get current keyword performance baseline"""
        try:
            # Calculate average success rate for current keyword usage
            pipeline = [
                {"$match": {"created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}}},
                {"$group": {
                    "_id": None,
                    "avg_success": {"$avg": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$outcome", "offer_received"]}, "then": 1.0},
                                {"case": {"$eq": ["$outcome", "interview_scheduled"]}, "then": 0.7},
                                {"case": {"$eq": ["$outcome", "phone_screen"]}, "then": 0.5},
                                {"case": {"$eq": ["$outcome", "viewed"]}, "then": 0.2}
                            ],
                            "default": 0.0
                        }
                    }}
                }}
            ]
            
            result = await self.db.applications.aggregate(pipeline).to_list(1)
            return result[0]["avg_success"] * 100 if result else 50.0
            
        except:
            return 50.0  # Default baseline
    
    async def _get_current_resume_performance(self) -> float:
        """Get current resume strategy performance"""
        try:
            pipeline = [
                {"$match": {"created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}}},
                {"$group": {
                    "_id": None,
                    "avg_ats_score": {"$avg": "$final_ats_score"}
                }}
            ]
            
            result = await self.db.resume_versions.aggregate(pipeline).to_list(1)
            return result[0]["avg_ats_score"] if result else 75.0
            
        except:
            return 75.0
    
    async def _get_current_outreach_performance(self) -> float:
        """Get current outreach performance"""
        try:
            pipeline = [
                {"$match": {"created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}}},
                {"$group": {
                    "_id": None,
                    "response_rate": {
                        "$avg": {
                            "$cond": [{"$eq": ["$status", "replied"]}, 1, 0]
                        }
                    }
                }}
            ]
            
            result = await self.db.outreach_messages.aggregate(pipeline).to_list(1)
            return result[0]["response_rate"] * 100 if result else 25.0
            
        except:
            return 25.0
    
    async def _update_ml_models(self, performance_data: Dict[str, Any]):
        """Update machine learning models with new performance data"""
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            self.logger.info("🤖 Updating ML models with new performance data")
            
            # Prepare training data
            training_data = await self._prepare_ml_training_data(performance_data)
            
            if len(training_data) < 10:  # Need minimum data for training
                self.logger.warning("Insufficient data for ML model update")
                return
            
            # Update success prediction model
            await self._update_success_predictor(training_data)
            
            self.logger.info("✅ ML models updated successfully")
            
        except Exception as e:
            self.logger.error(f"ML model update error: {e}")
    
    async def _prepare_ml_training_data(self, performance_data: Dict[str, Any]) -> List[Dict]:
        """Prepare training data for ML models"""
        # This would extract and format training data from performance_data
        # For now, return empty list as placeholder
        return []
    
    async def _update_success_predictor(self, training_data: List[Dict]):
        """Update the success prediction ML model"""
        # Placeholder for ML model training
        pass
    
    async def _generate_performance_report(
        self,
        performance_data: Dict[str, Any],
        success_patterns: Dict[str, Any],
        recommendations: List[OptimizationRecommendation],
        applied_optimizations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        """
        try:
            report = {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.utcnow(),
                "analysis_period": performance_data.get("analysis_period"),
                "performance_summary": {
                    "total_applications": len(performance_data.get("applications", [])),
                    "total_matches": len(performance_data.get("matching", [])),
                    "total_outreach": len(performance_data.get("outreach", [])),
                    "optimization_count": len(applied_optimizations)
                },
                "success_patterns": success_patterns,
                "recommendations": [
                    {
                        "strategy": rec.strategy.value,
                        "predicted_improvement": rec.predicted_improvement,
                        "confidence": rec.confidence,
                        "priority": rec.priority,
                        "action_items": rec.action_items
                    }
                    for rec in recommendations
                ],
                "applied_optimizations": applied_optimizations,
                "key_insights": await self._generate_key_insights(success_patterns, recommendations),
                "next_analysis_date": datetime.utcnow() + timedelta(days=1)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Performance report generation error: {e}")
            return {}
    
    async def _generate_key_insights(
        self, 
        success_patterns: Dict[str, Any], 
        recommendations: List[OptimizationRecommendation]
    ) -> List[str]:
        """Generate key insights from analysis"""
        insights = []
        
        if success_patterns.get("successful_keywords"):
            insights.append(f"Top performing keywords: {', '.join(success_patterns['successful_keywords'][:3])}")
        
        if success_patterns.get("best_resume_strategies"):
            insights.append(f"Most effective resume strategies: {', '.join(success_patterns['best_resume_strategies'][:2])}")
        
        high_impact_recs = [r for r in recommendations if r.predicted_improvement >= 15.0]
        if high_impact_recs:
            insights.append(f"High-impact optimizations available: {len(high_impact_recs)} recommendations with >15% improvement potential")
        
        return insights
    
    async def _save_analysis_results(self, report: Dict[str, Any]):
        """Save analysis results to database"""
        try:
            await self.db.performance_reports.insert_one(report)
            
            # Update system performance metrics
            await self.db.system_metrics.update_one(
                {"_id": "daily_performance"},
                {
                    "$set": {
                        "last_analysis": datetime.utcnow(),
                        "report_id": report["report_id"],
                        "key_insights": report.get("key_insights", []),
                        "optimizations_applied": len(report.get("applied_optimizations", []))
                    }
                },
                upsert=True
            )
            
        except Exception as e:
            self.logger.error(f"Analysis results save error: {e}")
    
    async def get_performance_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get performance trends over specified time period
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get historical performance reports
            cursor = self.db.performance_reports.find({
                "generated_at": {"$gte": start_date}
            }).sort("generated_at", 1)
            
            reports = await cursor.to_list(None)
            
            # Calculate trends
            trends = {
                "application_trend": [],
                "success_rate_trend": [],
                "optimization_trend": [],
                "improvement_trend": []
            }
            
            for report in reports:
                date = report["generated_at"].strftime("%Y-%m-%d")
                
                trends["application_trend"].append({
                    "date": date,
                    "count": report["performance_summary"]["total_applications"]
                })
                
                trends["optimization_trend"].append({
                    "date": date,
                    "count": report["performance_summary"]["optimization_count"]
                })
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Performance trends error: {e}")
            return {}
    
    async def predict_application_success(
        self, 
        candidate_id: str, 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict application success probability for a specific job
        """
        try:
            # Get candidate performance history
            candidate_history = await self.db.applications.find({
                "candidate_id": candidate_id
            }).to_list(None)
            
            if not candidate_history:
                return {"success_probability": 0.5, "confidence": 0.3, "factors": []}
            
            # Calculate success factors
            factors = []
            success_probability = 0.5
            
            # Keyword match factor
            job_keywords = job_data.get("keywords", [])
            candidate_keywords = await self._get_candidate_keywords(candidate_id)
            
            keyword_overlap = len(set(job_keywords) & set(candidate_keywords))
            if keyword_overlap > 0:
                keyword_factor = min(keyword_overlap / len(job_keywords), 1.0)
                success_probability += keyword_factor * 0.2
                factors.append(f"Keyword match: {keyword_overlap}/{len(job_keywords)}")
            
            # ATS score factor
            avg_ats_score = await self._get_candidate_avg_ats_score(candidate_id)
            if avg_ats_score > 80:
                success_probability += 0.15
                factors.append(f"High ATS performance: {avg_ats_score:.1f}")
            
            # Application timing factor
            current_hour = datetime.utcnow().hour
            optimal_hours = [9, 10, 11, 14, 15]  # Business hours
            if current_hour in optimal_hours:
                success_probability += 0.1
                factors.append("Optimal application timing")
            
            # Company size factor
            company_size = job_data.get("company_size", "unknown")
            if company_size in ["startup", "small"]:
                success_probability += 0.05
                factors.append("Higher success rate with smaller companies")
            
            # Cap probability at 0.95
            success_probability = min(success_probability, 0.95)
            
            return {
                "success_probability": success_probability,
                "confidence": 0.7,
                "factors": factors,
                "recommendation": "apply" if success_probability > 0.6 else "consider_alternatives"
            }
            
        except Exception as e:
            self.logger.error(f"Success prediction error: {e}")
            return {"success_probability": 0.5, "confidence": 0.3, "factors": []}
    
    async def _get_candidate_keywords(self, candidate_id: str) -> List[str]:
        """Get candidate's most effective keywords"""
        try:
            candidate = await self.db.candidates.find_one({"_id": candidate_id})
            return candidate.get("skills", []) if candidate else []
        except:
            return []
    
    async def _get_candidate_avg_ats_score(self, candidate_id: str) -> float:
        """Get candidate's average ATS score"""
        try:
            pipeline = [
                {"$match": {"candidate_id": candidate_id}},
                {"$group": {"_id": None, "avg_score": {"$avg": "$final_ats_score"}}}
            ]
            
            result = await self.db.resume_versions.aggregate(pipeline).to_list(1)
            return result[0]["avg_score"] if result else 75.0
        except:
            return 75.0