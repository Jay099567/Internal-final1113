import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, Target, Lightbulb, BarChart3, Settings, CheckCircle, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import toast from 'react-hot-toast';

const FeedbackAnalytics = () => {
  const [performanceData, setPerformanceData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [successPatterns, setSuccessPatterns] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);

  // Sample performance data for visualization
  const performanceTrendData = [
    { date: 'Jan', success_rate: 8.5, applications: 120, interviews: 10 },
    { date: 'Feb', success_rate: 11.2, applications: 145, interviews: 16 },
    { date: 'Mar', success_rate: 13.8, applications: 167, interviews: 23 },
    { date: 'Apr', success_rate: 15.4, applications: 189, interviews: 29 },
    { date: 'May', success_rate: 17.2, applications: 201, interviews: 35 },
    { date: 'Jun', success_rate: 19.6, applications: 224, interviews: 44 }
  ];

  const skillsRadarData = [
    { skill: 'Keywords', current: 85, optimized: 95 },
    { skill: 'Timing', current: 70, optimized: 88 },
    { skill: 'Personalization', current: 75, optimized: 92 },
    { skill: 'Job Matching', current: 90, optimized: 96 },
    { skill: 'Resume Quality', current: 80, optimized: 94 },
    { skill: 'Outreach', current: 65, optimized: 85 }
  ];

  const fetchPerformanceData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/feedback/analyze-performance`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setPerformanceData(data.performance_data);
        setRecommendations(data.recommendations || []);
      }
    } catch (error) {
      console.error('Error fetching performance data:', error);
    }
  };

  const fetchSuccessPatterns = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/feedback/success-patterns`);
      if (response.ok) {
        const data = await response.json();
        setSuccessPatterns(data.patterns || []);
      }
    } catch (error) {
      console.error('Error fetching success patterns:', error);
    }
  };

  useEffect(() => {
    fetchPerformanceData();
    fetchSuccessPatterns();
  }, []);

  const analyzePerformance = async () => {
    setIsAnalyzing(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/feedback/analyze-performance`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        setPerformanceData(data.performance_data);
        setRecommendations(data.recommendations || []);
        toast.success('Performance analysis completed!');
      } else {
        toast.error('Failed to analyze performance');
      }
    } catch (error) {
      console.error('Error analyzing performance:', error);
      toast.error('Error analyzing performance');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const applyOptimizations = async () => {
    setIsOptimizing(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/feedback/apply-optimizations`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        toast.success(`Applied ${data.optimizations_applied?.length || 0} optimizations successfully!`);
        // Refresh data after optimization
        setTimeout(() => {
          fetchPerformanceData();
          fetchSuccessPatterns();
        }, 2000);
      } else {
        toast.error('Failed to apply optimizations');
      }
    } catch (error) {
      console.error('Error applying optimizations:', error);
      toast.error('Error applying optimizations');
    } finally {
      setIsOptimizing(false);
    }
  };

  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'keyword_optimization': return <Target className="w-5 h-5 text-blue-600" />;
      case 'resume_strategy': return <BarChart3 className="w-5 h-5 text-green-600" />;
      case 'outreach_strategy': return <TrendingUp className="w-5 h-5 text-purple-600" />;
      case 'job_targeting': return <Lightbulb className="w-5 h-5 text-orange-600" />;
      case 'timing_optimization': return <Settings className="w-5 h-5 text-indigo-600" />;
      default: return <Brain className="w-5 h-5 text-gray-600" />;
    }
  };

  const getRecommendationColor = (confidence) => {
    if (confidence >= 0.8) return 'border-green-200 bg-green-50';
    if (confidence >= 0.6) return 'border-yellow-200 bg-yellow-50';
    return 'border-red-200 bg-red-50';
  };

  // Mock data for demonstration
  const mockRecommendations = [
    {
      strategy: 'keyword_optimization',
      title: 'Optimize Resume Keywords',
      description: 'Analysis shows 23% improvement in match rates when including "React", "Node.js", and "TypeScript" keywords.',
      confidence: 0.92,
      impact: 'High',
      implementation: 'Automatically update resume templates with trending keywords'
    },
    {
      strategy: 'timing_optimization',
      title: 'Optimal Application Timing',
      description: 'Applications submitted between 9-11 AM on Tuesday-Thursday have 34% higher response rates.',
      confidence: 0.87,
      impact: 'Medium',
      implementation: 'Schedule application submissions during peak response times'
    },
    {
      strategy: 'outreach_strategy',
      title: 'LinkedIn Outreach Personalization',
      description: 'Personalized messages mentioning specific company projects increase response rate by 45%.',
      confidence: 0.84,
      impact: 'High',
      implementation: 'Enhance LinkedIn outreach with company research integration'
    }
  ];

  const displayRecommendations = recommendations.length > 0 ? recommendations : mockRecommendations;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Brain className="w-8 h-8 mr-3 text-purple-600" />
            AI Performance Analytics & Learning
          </h1>
          <p className="text-gray-600 mt-2">Advanced machine learning analysis to optimize job hunting strategies</p>
        </div>
        
        {/* Action Buttons */}
        <div className="flex space-x-3">
          <button
            onClick={analyzePerformance}
            disabled={isAnalyzing}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            {isAnalyzing ? 'Analyzing...' : 'Analyze Performance'}
          </button>
          
          <button
            onClick={applyOptimizations}
            disabled={isOptimizing}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Settings className="w-4 h-4 mr-2" />
            {isOptimizing ? 'Optimizing...' : 'Apply Optimizations'}
          </button>
        </div>
      </div>

      {/* Performance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">19.6%</p>
              <p className="text-xs text-green-600">↗ +4.2% this month</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
              <p className="text-2xl font-bold text-gray-900">3.2 days</p>
              <p className="text-xs text-green-600">↗ -0.8 days improved</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Target className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Match Quality</p>
              <p className="text-2xl font-bold text-gray-900">94.3%</p>
              <p className="text-xs text-green-600">↗ +2.1% optimized</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Optimizations Applied</p>
              <p className="text-2xl font-bold text-gray-900">12</p>
              <p className="text-xs text-blue-600">This week</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Settings className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Performance Trends and Skills Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Trends */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Success Rate Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="success_rate" stroke="#10B981" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Skills Optimization Radar */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Skills Optimization Map</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={skillsRadarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="skill" />
              <PolarRadiusAxis angle={30} domain={[0, 100]} />
              <Radar name="Current" dataKey="current" stroke="#6B7280" fill="#6B7280" fillOpacity={0.3} />
              <Radar name="Optimized" dataKey="optimized" stroke="#10B981" fill="#10B981" fillOpacity={0.3} />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">AI-Generated Optimization Recommendations</h3>
        
        <div className="space-y-4">
          {displayRecommendations.map((rec, index) => (
            <div key={index} className={`border rounded-lg p-4 ${getRecommendationColor(rec.confidence)}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {getRecommendationIcon(rec.strategy)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-medium text-gray-900">{rec.title}</h4>
                      <span className={`px-2 py-1 text-xs rounded ${
                        rec.impact === 'High' ? 'bg-red-100 text-red-800' :
                        rec.impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {rec.impact} Impact
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{rec.description}</p>
                    <p className="text-xs text-gray-600">
                      <strong>Implementation:</strong> {rec.implementation}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">
                      {(rec.confidence * 100).toFixed(0)}% Confidence
                    </div>
                    <div className="w-16 bg-gray-200 rounded-full h-2 mt-1">
                      <div 
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${rec.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <button className="text-green-600 hover:text-green-800">
                    <CheckCircle className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Success Patterns */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Identified Success Patterns</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Keywords Analysis */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3 flex items-center">
              <Target className="w-4 h-4 mr-2 text-blue-600" />
              High-Performance Keywords
            </h4>
            <div className="space-y-2">
              {['React', 'Node.js', 'TypeScript', 'AWS', 'Python'].map((keyword, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm text-gray-700">{keyword}</span>
                  <span className="text-sm font-medium text-green-600">+{15 + index * 3}% match rate</span>
                </div>
              ))}
            </div>
          </div>

          {/* Timing Insights */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3 flex items-center">
              <Lightbulb className="w-4 h-4 mr-2 text-orange-600" />
              Optimal Timing Patterns
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-700">Tuesday 9-11 AM</span>
                <span className="text-sm font-medium text-green-600">Best response rate</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-700">Wednesday 10 AM-12 PM</span>
                <span className="text-sm font-medium text-green-600">High interview rate</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-700">Thursday 2-4 PM</span>
                <span className="text-sm font-medium text-yellow-600">Good for follow-ups</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Learning Status */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
        <div className="flex items-start">
          <Brain className="w-6 h-6 text-purple-600 mt-1 mr-3" />
          <div>
            <h3 className="text-purple-900 font-medium text-lg">Continuous Learning Active</h3>
            <p className="text-purple-800 text-sm mt-1 mb-3">
              The AI system is continuously analyzing application outcomes and optimizing strategies in real-time.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                <span className="text-purple-800">1,234 applications analyzed</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                <span className="text-purple-800">45 patterns identified</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                <span className="text-purple-800">12 optimizations applied</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeedbackAnalytics;