import React, { useState, useEffect } from 'react';
import { FileText, Download, Eye, Trash2, Plus, BarChart3, Users, Target, TrendingUp, 
         Zap, MessageCircle, Award, Clock, CheckCircle, AlertCircle, 
         Settings, Filter, Search, RefreshCw } from 'lucide-react';

const CoverLetterManagement = () => {
  const [candidates, setCandidates] = useState([]);
  const [coverLetters, setCoverLetters] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState('');
  const [selectedJob, setSelectedJob] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('generate');
  const [jobs, setJobs] = useState([]);
  const [filterTone, setFilterTone] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Generation Form State
  const [formData, setFormData] = useState({
    candidate_id: '',
    job_id: '',
    job_description: '',
    company_name: '',
    company_domain: '',
    position_title: '',
    hiring_manager: '',
    tone: 'formal',
    include_research: true
  });

  // Available tones
  const tones = [
    { value: 'formal', label: 'Formal', description: 'Professional and structured' },
    { value: 'warm', label: 'Warm', description: 'Friendly and personal' },
    { value: 'curious', label: 'Curious', description: 'Question-based and exploratory' },
    { value: 'bold', label: 'Bold', description: 'Confident and achievement-focused' },
    { value: 'strategic', label: 'Strategic', description: 'Business-oriented and results-driven' }
  ];

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchCandidates();
    fetchCoverLetterStats();
    fetchRecentJobs();
  }, []);

  useEffect(() => {
    if (selectedCandidate) {
      fetchCandidateCoverLetters();
    }
  }, [selectedCandidate]);

  const fetchCandidates = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/candidates`);
      const data = await response.json();
      if (data.success) {
        setCandidates(data.data);
      }
    } catch (error) {
      console.error('Error fetching candidates:', error);
    }
  };

  const fetchRecentJobs = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/jobs/filtered?limit=50`);
      const data = await response.json();
      if (data.success) {
        setJobs(data.data.jobs || []);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const fetchCandidateCoverLetters = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/candidates/${selectedCandidate}/cover-letters`);
      const data = await response.json();
      if (data.success) {
        setCoverLetters(data.data.cover_letters || []);
      }
    } catch (error) {
      console.error('Error fetching cover letters:', error);
    }
  };

  const fetchCoverLetterStats = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/cover-letters/stats/overview`);
      const data = await response.json();
      if (data.success) {
        setStats(data.data);
      }
    } catch (error) {
      console.error('Error fetching cover letter stats:', error);
    }
  };

  const generateCoverLetter = async () => {
    if (!formData.candidate_id || !formData.job_description || !formData.company_name) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/cover-letters/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (data.success) {
        alert('Cover letter generated successfully!');
        setFormData({
          candidate_id: '',
          job_id: '',
          job_description: '',
          company_name: '',
          company_domain: '',
          position_title: '',
          hiring_manager: '',
          tone: 'formal',
          include_research: true
        });
        fetchCandidateCoverLetters();
        fetchCoverLetterStats();
      } else {
        alert('Failed to generate cover letter: ' + data.detail);
      }
    } catch (error) {
      console.error('Error generating cover letter:', error);
      alert('Error generating cover letter');
    } finally {
      setLoading(false);
    }
  };

  const generateMultipleVersions = async () => {
    if (!formData.candidate_id || !formData.job_description || !formData.company_name) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/cover-letters/generate-multiple`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          versions_count: 3
        }),
      });

      const data = await response.json();
      if (data.success) {
        alert(`Generated ${data.data.total_count} cover letter versions successfully!`);
        fetchCandidateCoverLetters();
        fetchCoverLetterStats();
      } else {
        alert('Failed to generate multiple versions: ' + data.detail);
      }
    } catch (error) {
      console.error('Error generating multiple versions:', error);
      alert('Error generating multiple versions');
    } finally {
      setLoading(false);
    }
  };

  const deleteCoverLetter = async (coverLetterId) => {
    if (!confirm('Are you sure you want to delete this cover letter?')) return;

    try {
      const response = await fetch(`${backendUrl}/api/cover-letters/${coverLetterId}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      if (data.success) {
        alert('Cover letter deleted successfully!');
        fetchCandidateCoverLetters();
        fetchCoverLetterStats();
      } else {
        alert('Failed to delete cover letter');
      }
    } catch (error) {
      console.error('Error deleting cover letter:', error);
      alert('Error deleting cover letter');
    }
  };

  const downloadPDF = async (coverLetterId) => {
    try {
      const response = await fetch(`${backendUrl}/api/cover-letters/${coverLetterId}/download`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `cover_letter_${coverLetterId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        alert('Failed to download PDF');
      }
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Error downloading PDF');
    }
  };

  const testCoverLetterGeneration = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/cover-letters/test-generation`, {
        method: 'POST',
      });

      const data = await response.json();
      if (data.success) {
        alert('Cover letter generation test completed successfully!');
        fetchCoverLetterStats();
      } else {
        alert('Cover letter generation test failed: ' + data.detail);
      }
    } catch (error) {
      console.error('Error testing cover letter generation:', error);
      alert('Error testing cover letter generation');
    } finally {
      setLoading(false);
    }
  };

  const filteredCoverLetters = coverLetters.filter(letter => {
    const matchesTone = filterTone === 'all' || letter.tone === filterTone;
    const matchesSearch = searchTerm === '' || 
      letter.content?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (candidates.find(c => c.id === letter.candidate_id)?.full_name || '').toLowerCase().includes(searchTerm.toLowerCase());
    return matchesTone && matchesSearch;
  });

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getToneColor = (tone) => {
    const colors = {
      formal: 'bg-blue-100 text-blue-800',
      warm: 'bg-orange-100 text-orange-800',
      curious: 'bg-purple-100 text-purple-800',
      bold: 'bg-red-100 text-red-800',
      strategic: 'bg-green-100 text-green-800'
    };
    return colors[tone] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
          <FileText className="w-8 h-8 text-blue-600" />
          <span>Cover Letter Management</span>
          <span className="bg-blue-100 text-blue-600 text-sm px-3 py-1 rounded-full font-medium">
            Phase 5
          </span>
        </h1>
        <p className="text-gray-600 mt-2">
          Generate AI-powered, multi-tone cover letters with company research and personalization
        </p>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Cover Letters</p>
                <p className="text-2xl font-bold text-gray-900">{stats.overview?.total_cover_letters || 0}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Applications Sent</p>
                <p className="text-2xl font-bold text-gray-900">{stats.overview?.total_applications || 0}</p>
              </div>
              <Target className="w-8 h-8 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-gray-900">{stats.overview?.avg_success_rate || 0}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-600" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Usage</p>
                <p className="text-2xl font-bold text-gray-900">{stats.overview?.total_usage || 0}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('generate')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'generate'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Generate Cover Letters
            </button>
            <button
              onClick={() => setActiveTab('manage')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'manage'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Manage & Analytics
            </button>
            <button
              onClick={() => setActiveTab('test')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'test'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Testing & AI Demo
            </button>
          </nav>
        </div>
      </div>

      {/* Generate Tab */}
      {activeTab === 'generate' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Generation Form */}
          <div className="bg-white p-6 rounded-lg shadow border">
            <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
              <Plus className="w-5 h-5 mr-2 text-blue-600" />
              Generate New Cover Letter
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Candidate *
                </label>
                <select
                  value={formData.candidate_id}
                  onChange={(e) => setFormData({...formData, candidate_id: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Choose a candidate...</option>
                  {candidates.map(candidate => (
                    <option key={candidate.id} value={candidate.id}>
                      {candidate.full_name} ({candidate.email})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Job (Optional)
                </label>
                <select
                  value={formData.job_id}
                  onChange={(e) => {
                    const job = jobs.find(j => j.id === e.target.value);
                    setFormData({
                      ...formData, 
                      job_id: e.target.value,
                      job_description: job?.description || formData.job_description,
                      company_name: job?.company || formData.company_name,
                      position_title: job?.title || formData.position_title
                    });
                  }}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Choose a job or enter manually...</option>
                  {jobs.slice(0, 20).map(job => (
                    <option key={job.id} value={job.id}>
                      {job.title} at {job.company}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Name *
                </label>
                <input
                  type="text"
                  value={formData.company_name}
                  onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter company name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Domain (Optional)
                </label>
                <input
                  type="text"
                  value={formData.company_domain}
                  onChange={(e) => setFormData({...formData, company_domain: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="company.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Position Title
                </label>
                <input
                  type="text"
                  value={formData.position_title}
                  onChange={(e) => setFormData({...formData, position_title: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Senior Software Engineer"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hiring Manager
                </label>
                <input
                  type="text"
                  value={formData.hiring_manager}
                  onChange={(e) => setFormData({...formData, hiring_manager: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="John Smith"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cover Letter Tone
                </label>
                <select
                  value={formData.tone}
                  onChange={(e) => setFormData({...formData, tone: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {tones.map(tone => (
                    <option key={tone.value} value={tone.value}>
                      {tone.label} - {tone.description}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description *
                </label>
                <textarea
                  value={formData.job_description}
                  onChange={(e) => setFormData({...formData, job_description: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows="6"
                  placeholder="Paste the job description here..."
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="include_research"
                  checked={formData.include_research}
                  onChange={(e) => setFormData({...formData, include_research: e.target.checked})}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="include_research" className="ml-2 block text-sm text-gray-700">
                  Include company research and personalization
                </label>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={generateCoverLetter}
                  disabled={loading}
                  className="flex-1 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
                >
                  {loading ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
                  Generate Single Version
                </button>
                
                <button
                  onClick={generateMultipleVersions}
                  disabled={loading}
                  className="flex-1 bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center"
                >
                  {loading ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Zap className="w-4 h-4 mr-2" />}
                  Generate A/B Versions
                </button>
              </div>
            </div>
          </div>

          {/* Tone Guide */}
          <div className="bg-white p-6 rounded-lg shadow border">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              Cover Letter Tone Guide
            </h2>
            
            <div className="space-y-4">
              {tones.map(tone => (
                <div key={tone.value} className="p-4 border rounded-lg">
                  <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium mb-2 ${getToneColor(tone.value)}`}>
                    {tone.label}
                  </div>
                  <p className="text-gray-600 text-sm">{tone.description}</p>
                  <div className="mt-2 text-xs text-gray-500">
                    {tone.value === 'formal' && 'Best for: Corporate roles, traditional companies'}
                    {tone.value === 'warm' && 'Best for: Startups, creative roles, team-focused positions'}
                    {tone.value === 'curious' && 'Best for: Research roles, innovative companies'}
                    {tone.value === 'bold' && 'Best for: Sales roles, leadership positions'}
                    {tone.value === 'strategic' && 'Best for: Consulting, business roles, executive positions'}
                  </div>
                </div>
              ))}
            </div>

            {/* Features List */}
            <div className="mt-6 pt-6 border-t">
              <h3 className="font-semibold text-gray-900 mb-3">Advanced Features</h3>
              <div className="space-y-2">
                <div className="flex items-center text-sm text-gray-600">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                  AI-powered company research & personalization
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                  ATS keyword optimization
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                  Multi-tone generation for A/B testing
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                  Professional PDF generation
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                  Performance tracking & analytics
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Manage Tab */}
      {activeTab === 'manage' && (
        <div className="space-y-6">
          {/* Filters */}
          <div className="bg-white p-4 rounded-lg shadow border">
            <div className="flex flex-wrap gap-4 items-center">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Candidate</label>
                <select
                  value={selectedCandidate}
                  onChange={(e) => setSelectedCandidate(e.target.value)}
                  className="p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Candidates</option>
                  {candidates.map(candidate => (
                    <option key={candidate.id} value={candidate.id}>
                      {candidate.full_name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Tone</label>
                <select
                  value={filterTone}
                  onChange={(e) => setFilterTone(e.target.value)}
                  className="p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Tones</option>
                  {tones.map(tone => (
                    <option key={tone.value} value={tone.value}>
                      {tone.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                    placeholder="Search cover letters..."
                  />
                </div>
              </div>
              
              <button
                onClick={fetchCandidateCoverLetters}
                className="mt-6 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Cover Letters List */}
          <div className="bg-white rounded-lg shadow border">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Cover Letters ({filteredCoverLetters.length})
              </h2>
              
              {filteredCoverLetters.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No cover letters found. Generate your first one!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredCoverLetters.map(letter => (
                    <div key={letter.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getToneColor(letter.tone)}`}>
                              {letter.tone}
                            </span>
                            <span className="text-sm text-gray-500">
                              {candidates.find(c => c.id === letter.candidate_id)?.full_name || 'Unknown Candidate'}
                            </span>
                            <span className="text-sm text-gray-400">
                              <Clock className="w-4 h-4 inline mr-1" />
                              {formatDate(letter.created_at)}
                            </span>
                          </div>
                          
                          <p className="text-gray-700 mb-2 line-clamp-3">
                            {letter.content?.substring(0, 200)}...
                          </p>
                          
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span>Usage: {letter.used_count || 0}</span>
                            <span>Words: {letter.word_count || letter.content?.split(' ').length || 0}</span>
                            {letter.ats_keywords?.length > 0 && (
                              <span>Keywords: {letter.ats_keywords.length}</span>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2 ml-4">
                          <button
                            onClick={() => downloadPDF(letter.id)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                            title="Download PDF"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          
                          <button
                            onClick={() => deleteCoverLetter(letter.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Test Tab */}
      {activeTab === 'test' && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            AI Cover Letter Testing
          </h2>
          
          <div className="space-y-6">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-medium text-blue-900 mb-2">System Test</h3>
              <p className="text-blue-700 text-sm mb-4">
                Test the complete cover letter generation pipeline with sample data
              </p>
              <button
                onClick={testCoverLetterGeneration}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Zap className="w-4 h-4 mr-2" />}
                Run Complete Test
              </button>
            </div>

            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 border rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-3">Tone Distribution</h3>
                  <div className="space-y-2">
                    {stats.tone_distribution?.map(item => (
                      <div key={item.tone} className="flex items-center justify-between">
                        <span className={`px-2 py-1 rounded text-sm ${getToneColor(item.tone)}`}>
                          {item.tone}
                        </span>
                        <span className="text-gray-600">{item.count}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-3">Recent Activity</h3>
                  <div className="space-y-2">
                    {stats.recent_activity?.slice(0, 5).map(activity => (
                      <div key={activity.id} className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">
                          {activity.tone} letter
                        </span>
                        <span className="text-gray-400">
                          {formatDate(activity.created_at)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CoverLetterManagement;