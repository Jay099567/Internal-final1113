import React, { useState, useEffect } from 'react';
import { 
  PlayIcon, 
  PauseIcon, 
  CogIcon, 
  ClockIcon,
  ChartBarIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

const JobScraping = () => {
  const [scrapingStatus, setScrapingStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [manualScraping, setManualScraping] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // Manual scraping form
  const [manualForm, setManualForm] = useState({
    scraper: 'indeed',
    query: 'Software Developer',
    location: 'Remote',
    max_pages: 3
  });

  const fetchScrapingStatus = async () => {
    try {
      setRefreshing(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/scraping/status`);
      const data = await response.json();
      if (data.success) {
        setScrapingStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch scraping status:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const startManualScraping = async () => {
    try {
      setManualScraping(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/scraping/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(manualForm)
      });
      
      const data = await response.json();
      if (data.success) {
        alert(`Scraping started successfully! Found ${data.results?.jobs_found || 0} jobs.`);
        fetchScrapingStatus(); // Refresh status
      } else {
        alert('Failed to start scraping');
      }
    } catch (error) {
      console.error('Failed to start manual scraping:', error);
      alert('Failed to start scraping');
    } finally {
      setManualScraping(false);
    }
  };

  const controlScheduler = async (action) => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/scraping/scheduler/${action}`, {
        method: 'POST'
      });
      
      const data = await response.json();
      if (data.success) {
        alert(data.message);
        fetchScrapingStatus(); // Refresh status
      } else {
        alert(`Failed to ${action} scheduler`);
      }
    } catch (error) {
      console.error(`Failed to ${action} scheduler:`, error);
      alert(`Failed to ${action} scheduler`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScrapingStatus();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchScrapingStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = (status) => {
    const badges = {
      'started': 'bg-blue-100 text-blue-800',
      'completed': 'bg-green-100 text-green-800',
      'error': 'bg-red-100 text-red-800',
      'stopped': 'bg-gray-100 text-gray-800'
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  const formatNextRun = (dateString) => {
    if (!dateString) return 'Not scheduled';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date - now;
    const diffMins = Math.round(diffMs / 60000);
    
    if (diffMins < 60) {
      return `${diffMins} minutes`;
    } else if (diffMins < 1440) {
      return `${Math.round(diffMins / 60)} hours`;
    } else {
      return `${Math.round(diffMins / 1440)} days`;
    }
  };

  if (!scrapingStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const { stats, scheduled_jobs, recent_logs } = scrapingStatus;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Job Scraping Control</h1>
            <p className="text-gray-600">Manage automated job scraping and view statistics</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={fetchScrapingStatus}
              disabled={refreshing}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              <ArrowPathIcon className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={() => controlScheduler('restart')}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
            >
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Restart Scheduler
            </button>
          </div>
        </div>
      </div>

      {/* Stats Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CogIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Schedules</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.total_scheduled_jobs}</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                stats.is_running ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {stats.is_running ? 'Running' : 'Stopped'}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Jobs Scraped (24h)</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.jobs_scraped_24h}</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <span className="text-gray-600">Total: {stats.total_jobs_scraped}</span>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Success Rate</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.success_rate.toFixed(1)}%</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <span className="text-green-600">{stats.successful_runs_24h} successful</span>
              <span className="text-gray-400 mx-1">•</span>
              <span className="text-red-600">{stats.failed_runs_24h} failed</span>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-6 w-6 text-purple-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Runs (24h)</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.total_runs_24h}</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <span className="text-gray-600">Session: {stats.session_id.substring(0, 8)}...</span>
            </div>
          </div>
        </div>
      </div>

      {/* Manual Scraping */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Manual Scraping</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Scraper</label>
            <select
              value={manualForm.scraper}
              onChange={(e) => setManualForm({ ...manualForm, scraper: e.target.value })}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            >
              <option value="indeed">Indeed</option>
              <option value="linkedin" disabled>LinkedIn (Coming Soon)</option>
              <option value="glassdoor" disabled>Glassdoor (Coming Soon)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Job Query</label>
            <input
              type="text"
              value={manualForm.query}
              onChange={(e) => setManualForm({ ...manualForm, query: e.target.value })}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., Software Developer"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Location</label>
            <input
              type="text"
              value={manualForm.location}
              onChange={(e) => setManualForm({ ...manualForm, location: e.target.value })}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., Remote, New York"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Max Pages</label>
            <input
              type="number"
              min="1"
              max="10"
              value={manualForm.max_pages}
              onChange={(e) => setManualForm({ ...manualForm, max_pages: parseInt(e.target.value) })}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
        </div>
        <button
          onClick={startManualScraping}
          disabled={manualScraping}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
        >
          <PlayIcon className="h-4 w-4 mr-2" />
          {manualScraping ? 'Scraping...' : 'Start Manual Scraping'}
        </button>
      </div>

      {/* Scheduled Jobs */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Scheduled Jobs</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Job Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Query
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Next Run
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Interval
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {scheduled_jobs.map((job) => (
                <tr key={job.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {job.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {job.args[2]?.q || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {job.args[2]?.l || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatNextRun(job.next_run)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {job.trigger}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Logs */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {recent_logs.slice(0, 10).map((log) => (
            <div key={log._id} className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                {log.status === 'completed' && (
                  <CheckCircleIcon className="h-5 w-5 text-green-400" />
                )}
                {log.status === 'error' && (
                  <ExclamationCircleIcon className="h-5 w-5 text-red-400" />
                )}
                {log.status === 'started' && (
                  <PlayIcon className="h-5 w-5 text-blue-400" />
                )}
                {log.status === 'stopped' && (
                  <PauseIcon className="h-5 w-5 text-gray-400" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900">{log.message}</p>
                <p className="text-xs text-gray-500">
                  {new Date(log.timestamp).toLocaleString()} • Job: {log.job_id}
                </p>
                {log.error_details && (
                  <p className="text-xs text-red-600 mt-1">{log.error_details}</p>
                )}
              </div>
              <div className="flex-shrink-0">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(log.status)}`}>
                  {log.status}
                </span>
              </div>
            </div>
          ))}
          {recent_logs.length === 0 && (
            <p className="text-gray-500 text-sm">No recent activity</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobScraping;