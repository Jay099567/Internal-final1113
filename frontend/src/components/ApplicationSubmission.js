import React, { useState, useEffect } from 'react';
import { 
  PlayCircleIcon, 
  PauseCircleIcon, 
  DocumentTextIcon, 
  EnvelopeIcon,
  GlobeAltIcon,
  BuildingOfficeIcon,
  UserIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationCircleIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline';

const ApplicationSubmission = () => {
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState({});
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(true);
  const [submissionStatus, setSubmissionStatus] = useState('idle');
  const [selectedCandidates, setSelectedCandidates] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [submissionConfig, setSubmissionConfig] = useState({
    method: 'direct_form',
    batchSize: 10,
    delay: 30,
    enableAutoSubmit: false
  });

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchApplicationStats();
    fetchApplicationAnalytics();
    fetchCandidates();
    fetchJobs();
    fetchRecentApplications();
  }, []);

  const fetchApplicationStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applications/status`);
      const data = await response.json();
      if (data.success) {
        setStats(data.statistics);
      }
    } catch (error) {
      console.error('Error fetching application stats:', error);
    }
  };

  const fetchApplicationAnalytics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applications/analytics`);
      const data = await response.json();
      if (data.success) {
        setAnalytics(data.analytics);
      }
    } catch (error) {
      console.error('Error fetching application analytics:', error);
    }
  };

  const fetchCandidates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/candidates`);
      const data = await response.json();
      if (data.success) {
        setCandidates(data.candidates);
      }
    } catch (error) {
      console.error('Error fetching candidates:', error);
    }
  };

  const fetchJobs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/jobs?limit=100`);
      const data = await response.json();
      if (data.success) {
        setJobs(data.jobs);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const fetchRecentApplications = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applications/candidate/all?limit=50`);
      const data = await response.json();
      if (data.success) {
        setApplications(data.applications);
      }
    } catch (error) {
      console.error('Error fetching recent applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAutoSubmit = async () => {
    setSubmissionStatus('running');
    try {
      const response = await fetch(`${API_BASE_URL}/api/applications/auto-submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      
      if (data.success) {
        alert(`Successfully queued ${data.total_queued} applications for submission`);
        fetchApplicationStats();
        fetchRecentApplications();
      } else {
        alert('Failed to start auto-submission');
      }
    } catch (error) {
      console.error('Error starting auto-submission:', error);
      alert('Error starting auto-submission');
    } finally {
      setSubmissionStatus('idle');
    }
  };

  const handleBulkSubmit = async () => {
    if (selectedCandidates.length === 0) {
      alert('Please select at least one candidate');
      return;
    }

    setSubmissionStatus('running');
    try {
      const jobIds = jobs.slice(0, submissionConfig.batchSize).map(job => job.id);
      
      for (const candidateId of selectedCandidates) {
        const response = await fetch(`${API_BASE_URL}/api/applications/submit-bulk`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            candidate_id: candidateId,
            job_ids: jobIds,
            method: submissionConfig.method
          }),
        });
        const data = await response.json();
        
        if (!data.success) {
          console.error(`Failed to submit applications for candidate ${candidateId}`);
        }
      }
      
      alert('Bulk submission completed');
      fetchApplicationStats();
      fetchRecentApplications();
    } catch (error) {
      console.error('Error with bulk submission:', error);
      alert('Error with bulk submission');
    } finally {
      setSubmissionStatus('idle');
    }
  };

  const handleTestSubmission = async () => {
    setSubmissionStatus('testing');
    try {
      const response = await fetch(`${API_BASE_URL}/api/applications/test-submission`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      
      if (data.success) {
        alert('Test submission completed successfully');
      } else {
        alert('Test submission failed');
      }
    } catch (error) {
      console.error('Error testing submission:', error);
      alert('Error testing submission');
    } finally {
      setSubmissionStatus('idle');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'applied':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ExclamationCircleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getMethodIcon = (method) => {
    switch (method) {
      case 'direct_form':
        return <DocumentTextIcon className="h-5 w-5 text-blue-500" />;
      case 'email_apply':
        return <EnvelopeIcon className="h-5 w-5 text-green-500" />;
      case 'indeed_quick':
        return <GlobeAltIcon className="h-5 w-5 text-purple-500" />;
      case 'linkedin_easy':
        return <UserIcon className="h-5 w-5 text-blue-600" />;
      default:
        return <DocumentTextIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Application Submission Engine</h1>
              <p className="mt-2 text-gray-600">Phase 6: Autonomous job application submission with stealth capabilities</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={handleTestSubmission}
                disabled={submissionStatus !== 'idle'}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                <DocumentTextIcon className="h-5 w-5 mr-2" />
                Test Submission
              </button>
              <button
                onClick={handleAutoSubmit}
                disabled={submissionStatus !== 'idle'}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                {submissionStatus === 'running' ? (
                  <PauseCircleIcon className="h-5 w-5 mr-2" />
                ) : (
                  <PlayCircleIcon className="h-5 w-5 mr-2" />
                )}
                Auto Submit
              </button>
            </div>
          </div>
        </div>

        {/* Stats Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Applications</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.total_applications || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Successful</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.successful_applications || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">In Queue</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.queue_size || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowUpIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Active Submissions</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.active_submissions || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Control Panel */}
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Submission Control Panel</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Application Method</label>
              <select
                value={submissionConfig.method}
                onChange={(e) => setSubmissionConfig({...submissionConfig, method: e.target.value})}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="direct_form">Direct Form</option>
                <option value="email_apply">Email Apply</option>
                <option value="indeed_quick">Indeed Quick Apply</option>
                <option value="linkedin_easy">LinkedIn Easy Apply</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Batch Size</label>
              <input
                type="number"
                value={submissionConfig.batchSize}
                onChange={(e) => setSubmissionConfig({...submissionConfig, batchSize: parseInt(e.target.value)})}
                min="1"
                max="50"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Delay (seconds)</label>
              <input
                type="number"
                value={submissionConfig.delay}
                onChange={(e) => setSubmissionConfig({...submissionConfig, delay: parseInt(e.target.value)})}
                min="10"
                max="300"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={handleBulkSubmit}
                disabled={submissionStatus !== 'idle'}
                className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
              >
                <PlayCircleIcon className="h-5 w-5 mr-2" />
                Bulk Submit
              </button>
            </div>
          </div>

          {/* Candidate Selection */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Select Candidates</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-40 overflow-y-auto">
              {candidates.map(candidate => (
                <label key={candidate.id} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedCandidates.includes(candidate.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedCandidates([...selectedCandidates, candidate.id]);
                      } else {
                        setSelectedCandidates(selectedCandidates.filter(id => id !== candidate.id));
                      }
                    }}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    {candidate.first_name} {candidate.last_name}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Applications */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Applications</h2>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Company
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Position
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Method
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Submitted
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Candidate
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {applications.map((application) => (
                  <tr key={application.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(application.status)}
                        <span className="ml-2 text-sm font-medium text-gray-900 capitalize">
                          {application.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <BuildingOfficeIcon className="h-5 w-5 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-900">{application.company}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{application.position}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getMethodIcon(application.job_board)}
                        <span className="ml-2 text-sm text-gray-900 capitalize">
                          {application.job_board}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {application.applied_at ? new Date(application.applied_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {application.candidate_id}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {applications.length === 0 && (
            <div className="text-center py-8">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No applications yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Start by submitting your first application or running auto-submit.
              </p>
            </div>
          )}
        </div>

        {/* Analytics Section */}
        {analytics.overall_stats && (
          <div className="mt-8 bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Application Analytics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Success Rate</h3>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${analytics.overall_stats.success_rate}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {analytics.overall_stats.success_rate.toFixed(1)}% success rate
                </p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Response Rate</h3>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${analytics.overall_stats.response_rate}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {analytics.overall_stats.response_rate.toFixed(1)}% response rate
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ApplicationSubmission;