import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

const ResumeTailoring = () => {
  const [candidates, setCandidates] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState('');
  const [selectedResume, setSelectedResume] = useState('');
  const [selectedJob, setSelectedJob] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [strategy, setStrategy] = useState('job_specific');
  const [optimizationLevel, setOptimizationLevel] = useState('advanced');
  const [useGeneticAlgorithm, setUseGeneticAlgorithm] = useState(true);
  const [resumeVersions, setResumeVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [atsAnalysis, setATSAnalysis] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [tailoringStats, setTailoringStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('tailor');

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchCandidates();
    fetchJobs();
    fetchTailoringStats();
  }, []);

  useEffect(() => {
    if (selectedCandidate) {
      fetchResumeVersions();
    }
  }, [selectedCandidate]);

  const fetchCandidates = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/candidates`);
      const data = await response.json();
      if (data.success) {
        setCandidates(data.candidates);
      }
    } catch (error) {
      console.error('Error fetching candidates:', error);
      toast.error('Failed to fetch candidates');
    }
  };

  const fetchJobs = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/jobs?limit=50`);
      const data = await response.json();
      if (data.success) {
        setJobs(data.jobs);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
      toast.error('Failed to fetch jobs');
    }
  };

  const fetchResumeVersions = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/candidates/${selectedCandidate}/resume-versions`);
      const data = await response.json();
      if (data.success) {
        setResumeVersions(data.versions);
      }
    } catch (error) {
      console.error('Error fetching resume versions:', error);
      toast.error('Failed to fetch resume versions');
    }
  };

  const fetchTailoringStats = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/resume-tailoring/stats`);
      const data = await response.json();
      if (data.success) {
        setTailoringStats(data.stats);
      }
    } catch (error) {
      console.error('Error fetching tailoring stats:', error);
    }
  };

  const fetchATSAnalysis = async (versionId) => {
    try {
      const response = await fetch(`${backendUrl}/api/resume-versions/${versionId}/ats-analysis`);
      const data = await response.json();
      if (data.success) {
        setATSAnalysis(data.analysis);
      }
    } catch (error) {
      console.error('Error fetching ATS analysis:', error);
      toast.error('ATS analysis not available');
    }
  };

  const fetchPerformanceMetrics = async (versionId) => {
    try {
      const response = await fetch(`${backendUrl}/api/resume-versions/${versionId}/performance`);
      const data = await response.json();
      if (data.success) {
        setPerformanceMetrics(data.metrics);
      }
    } catch (error) {
      console.error('Error fetching performance metrics:', error);
      toast.error('Performance metrics not available');
    }
  };

  const handleTailorResume = async () => {
    if (!selectedCandidate || !selectedResume || !selectedJob || !jobDescription.trim()) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/resumes/${selectedResume}/tailor`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          candidate_id: selectedCandidate,
          resume_id: selectedResume,
          job_id: selectedJob,
          job_description: jobDescription,
          strategy,
          optimization_level: optimizationLevel,
          use_genetic_algorithm: useGeneticAlgorithm
        }),
      });

      const data = await response.json();
      if (data.success) {
        toast.success(`Resume tailored successfully! ATS Score: ${data.ats_score?.toFixed(1) || 'N/A'}`);
        fetchResumeVersions();
        fetchTailoringStats();
        setActiveTab('versions');
      } else {
        toast.error(data.detail || 'Failed to tailor resume');
      }
    } catch (error) {
      console.error('Error tailoring resume:', error);
      toast.error('Failed to tailor resume');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateVariants = async () => {
    if (!selectedCandidate || !selectedResume) {
      toast.error('Please select a candidate and resume');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/resumes/${selectedResume}/generate-variants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          candidate_id: selectedCandidate,
          resume_id: selectedResume,
          count: 5,
          strategies: ['job_specific', 'skill_focused', 'experience_focused']
        }),
      });

      const data = await response.json();
      if (data.success) {
        toast.success(`Generated ${data.variants.length} resume variants for A/B testing`);
        fetchResumeVersions();
        fetchTailoringStats();
        setActiveTab('versions');
      } else {
        toast.error(data.detail || 'Failed to generate variants');
      }
    } catch (error) {
      console.error('Error generating variants:', error);
      toast.error('Failed to generate variants');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestATSScoring = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/resumes/test-ats-scoring`, {
        method: 'POST',
      });

      const data = await response.json();
      if (data.success) {
        toast.success(`ATS Test Score: ${data.sample_resume_score.toFixed(1)}`);
        setATSAnalysis({
          overall_score: data.sample_resume_score,
          keyword_score: data.breakdown.keyword_score,
          format_score: data.breakdown.format_score,
          section_score: data.breakdown.section_score,
          experience_score: data.breakdown.experience_score,
          education_score: data.breakdown.education_score,
          skills_score: data.breakdown.skills_score,
          contact_score: data.breakdown.contact_score,
          recommendations: data.recommendations,
          missing_keywords: data.missing_keywords
        });
      } else {
        toast.error(data.detail || 'Failed to test ATS scoring');
      }
    } catch (error) {
      console.error('Error testing ATS scoring:', error);
      toast.error('Failed to test ATS scoring');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVersionSelect = (version) => {
    setSelectedVersion(version);
    fetchATSAnalysis(version.id);
    fetchPerformanceMetrics(version.id);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const strategyOptions = [
    { value: 'job_specific', label: 'Job-Specific Tailoring' },
    { value: 'company_specific', label: 'Company-Specific' },
    { value: 'role_specific', label: 'Role-Specific' },
    { value: 'industry_specific', label: 'Industry-Specific' },
    { value: 'skill_focused', label: 'Skills-Focused' },
    { value: 'experience_focused', label: 'Experience-Focused' }
  ];

  const optimizationOptions = [
    { value: 'basic', label: 'Basic Optimization' },
    { value: 'advanced', label: 'Advanced Optimization' },
    { value: 'aggressive', label: 'Aggressive Optimization' },
    { value: 'stealth', label: 'Stealth Optimization' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🧬 Advanced Resume Tailoring</h1>
          <p className="text-gray-600">AI-powered resume optimization with genetic algorithms and ATS scoring</p>
        </div>

        {/* Statistics Overview */}
        {tailoringStats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-blue-600">{tailoringStats.total_resume_versions}</div>
              <div className="text-sm text-gray-500">Resume Versions</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-green-600">{tailoringStats.total_genetic_pools}</div>
              <div className="text-sm text-gray-500">Genetic Pools</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-purple-600">{tailoringStats.total_ats_analyses}</div>
              <div className="text-sm text-gray-500">ATS Analyses</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-orange-600">{tailoringStats.average_ats_score}</div>
              <div className="text-sm text-gray-500">Avg ATS Score</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-indigo-600">{tailoringStats.max_ats_score}</div>
              <div className="text-sm text-gray-500">Max ATS Score</div>
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="flex space-x-1 mb-6">
          {['tailor', 'versions', 'analytics'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              {tab === 'tailor' && '🎯 Resume Tailoring'}
              {tab === 'versions' && '📄 Resume Versions'}
              {tab === 'analytics' && '📊 Analytics'}
            </button>
          ))}
        </div>

        {/* Resume Tailoring Tab */}
        {activeTab === 'tailor' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Tailoring Form */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-6">🎯 Tailor Resume for Job</h2>
              
              {/* Candidate Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Candidate</label>
                <select
                  value={selectedCandidate}
                  onChange={(e) => setSelectedCandidate(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Choose candidate...</option>
                  {candidates.map((candidate) => (
                    <option key={candidate.id} value={candidate.id}>
                      {candidate.full_name} ({candidate.email})
                    </option>
                  ))}
                </select>
              </div>

              {/* Resume Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Resume</label>
                <select
                  value={selectedResume}
                  onChange={(e) => setSelectedResume(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={!selectedCandidate}
                >
                  <option value="">Choose resume...</option>
                  {/* This would be populated based on candidate's resumes */}
                  <option value="sample-resume-id">Primary Resume</option>
                </select>
              </div>

              {/* Job Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Job</label>
                <select
                  value={selectedJob}
                  onChange={(e) => {
                    setSelectedJob(e.target.value);
                    const job = jobs.find(j => j.id === e.target.value);
                    if (job) {
                      setJobDescription(job.description);
                    }
                  }}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Choose job...</option>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.title} at {job.company} - {job.location}
                    </option>
                  ))}
                </select>
              </div>

              {/* Job Description */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Job Description</label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here..."
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 h-32 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Strategy Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Tailoring Strategy</label>
                <select
                  value={strategy}
                  onChange={(e) => setStrategy(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {strategyOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Optimization Level */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Optimization Level</label>
                <select
                  value={optimizationLevel}
                  onChange={(e) => setOptimizationLevel(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {optimizationOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Genetic Algorithm Toggle */}
              <div className="mb-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={useGeneticAlgorithm}
                    onChange={(e) => setUseGeneticAlgorithm(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Use Genetic Algorithm (Recommended)</span>
                </label>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  onClick={handleTailorResume}
                  disabled={isLoading}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {isLoading ? '🧬 Tailoring Resume...' : '🎯 Tailor Resume'}
                </button>
                
                <button
                  onClick={handleGenerateVariants}
                  disabled={isLoading}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
                >
                  {isLoading ? '🔄 Generating...' : '🔄 Generate A/B Test Variants'}
                </button>
                
                <button
                  onClick={handleTestATSScoring}
                  disabled={isLoading}
                  className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
                >
                  {isLoading ? '🧪 Testing...' : '🧪 Test ATS Scoring Engine'}
                </button>
              </div>
            </div>

            {/* ATS Analysis Panel */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-6">📊 ATS Analysis</h2>
              
              {atsAnalysis ? (
                <div className="space-y-4">
                  {/* Overall Score */}
                  <div className={`p-4 rounded-lg ${getScoreBg(atsAnalysis.overall_score)}`}>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Overall ATS Score</span>
                      <span className={`text-2xl font-bold ${getScoreColor(atsAnalysis.overall_score)}`}>
                        {atsAnalysis.overall_score?.toFixed(1) || 'N/A'}
                      </span>
                    </div>
                  </div>

                  {/* Score Breakdown */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-gray-50 rounded">
                      <div className="text-sm text-gray-600">Keywords</div>
                      <div className={`font-semibold ${getScoreColor(atsAnalysis.keyword_score)}`}>
                        {atsAnalysis.keyword_score?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded">
                      <div className="text-sm text-gray-600">Format</div>
                      <div className={`font-semibold ${getScoreColor(atsAnalysis.format_score)}`}>
                        {atsAnalysis.format_score?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded">
                      <div className="text-sm text-gray-600">Experience</div>
                      <div className={`font-semibold ${getScoreColor(atsAnalysis.experience_score)}`}>
                        {atsAnalysis.experience_score?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded">
                      <div className="text-sm text-gray-600">Skills</div>
                      <div className={`font-semibold ${getScoreColor(atsAnalysis.skills_score)}`}>
                        {atsAnalysis.skills_score?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                  </div>

                  {/* Recommendations */}
                  {atsAnalysis.recommendations && atsAnalysis.recommendations.length > 0 && (
                    <div>
                      <h3 className="font-medium mb-2">💡 Recommendations</h3>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {atsAnalysis.recommendations.map((rec, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-blue-500 mr-1">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Missing Keywords */}
                  {atsAnalysis.missing_keywords && atsAnalysis.missing_keywords.length > 0 && (
                    <div>
                      <h3 className="font-medium mb-2">🔍 Missing Keywords</h3>
                      <div className="flex flex-wrap gap-2">
                        {atsAnalysis.missing_keywords.slice(0, 10).map((keyword, index) => (
                          <span key={index} className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded">
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">📊</div>
                  <p>Run ATS analysis to see detailed scoring</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Resume Versions Tab */}
        {activeTab === 'versions' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Versions List */}
            <div className="lg:col-span-2 bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-6">📄 Resume Versions</h2>
              
              {resumeVersions.length > 0 ? (
                <div className="space-y-4">
                  {resumeVersions.map((version) => (
                    <div
                      key={version.id}
                      onClick={() => handleVersionSelect(version)}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedVersion?.id === version.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium">{version.version_name}</h3>
                        {version.ats_score && (
                          <span className={`px-2 py-1 rounded text-sm font-medium ${getScoreBg(version.ats_score)} ${getScoreColor(version.ats_score)}`}>
                            ATS: {version.ats_score.toFixed(1)}
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>Strategy: <span className="capitalize">{version.tailoring_strategy?.replace('_', ' ')}</span></p>
                        <p>Optimization: <span className="capitalize">{version.ats_optimization_level}</span></p>
                        <p>Created: {new Date(version.created_at).toLocaleDateString()}</p>
                        {version.used_count > 0 && (
                          <p>Used: {version.used_count} times</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">📄</div>
                  <p>No resume versions found</p>
                  <p className="text-sm">Select a candidate to view their resume versions</p>
                </div>
              )}
            </div>

            {/* Version Details */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-6">🔍 Version Details</h2>
              
              {selectedVersion ? (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium mb-2">📊 Performance Metrics</h3>
                    {performanceMetrics ? (
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Applications:</span>
                          <span className="font-medium">{performanceMetrics.applications_sent}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Responses:</span>
                          <span className="font-medium">{performanceMetrics.responses_received}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Response Rate:</span>
                          <span className="font-medium">{(performanceMetrics.response_rate * 100).toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Interviews:</span>
                          <span className="font-medium">{performanceMetrics.interviews_scheduled}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Offers:</span>
                          <span className="font-medium">{performanceMetrics.offers_received}</span>
                        </div>
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">No performance data available</p>
                    )}
                  </div>

                  <div>
                    <h3 className="font-medium mb-2">🎯 Injected Keywords</h3>
                    {selectedVersion.keywords_injected && selectedVersion.keywords_injected.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {selectedVersion.keywords_injected.map((keyword, index) => (
                          <span key={index} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                            {keyword}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">No keywords injected</p>
                    )}
                  </div>

                  <div>
                    <h3 className="font-medium mb-2">🔬 Generation Info</h3>
                    <div className="text-sm text-gray-600 space-y-1">
                      {selectedVersion.generation_params?.method && (
                        <p>Method: {selectedVersion.generation_params.method}</p>
                      )}
                      {selectedVersion.generation_params?.generation && (
                        <p>Generation: {selectedVersion.generation_params.generation}</p>
                      )}
                      {selectedVersion.generation_params?.fitness_score && (
                        <p>Fitness: {selectedVersion.generation_params.fitness_score.toFixed(3)}</p>
                      )}
                      {selectedVersion.stealth_fingerprint && (
                        <p>Fingerprint: {selectedVersion.stealth_fingerprint.slice(0, 8)}...</p>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">🔍</div>
                  <p>Select a version to view details</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-6">📊 Resume Tailoring Analytics</h2>
            
            <div className="text-center py-12 text-gray-500">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-medium mb-2">Advanced Analytics Coming Soon</h3>
              <p>Performance tracking, A/B testing results, and optimization insights will be available here.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeTailoring;