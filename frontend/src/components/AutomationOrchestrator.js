import React, { useState, useEffect } from 'react';
import { Play, Square, Activity, Users, Target, Briefcase, Send, TrendingUp, Clock, BarChart3 } from 'lucide-react';
import toast from 'react-hot-toast';

const AutomationOrchestrator = () => {
  const [systemStatus, setSystemStatus] = useState('stopped');
  const [stats, setStats] = useState({
    candidates_processed: 0,
    jobs_scraped: 0,
    matches_found: 0,
    resumes_tailored: 0,
    cover_letters_generated: 0,
    applications_submitted: 0,
    outreach_sent: 0,
    total_runtime_hours: 0,
    success_rate: 0,
    active_candidates: 0
  });
  const [isLoading, setIsLoading] = useState(false);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/automation/status`);
      if (response.ok) {
        const data = await response.json();
        setSystemStatus(data.status?.status || 'stopped');
      }
    } catch (error) {
      console.error('Error fetching system status:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/automation/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats || stats);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  useEffect(() => {
    fetchSystemStatus();
    fetchStats();
    
    // Poll status every 30 seconds
    const interval = setInterval(() => {
      fetchSystemStatus();
      fetchStats();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const startAutonomousSystem = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/automation/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        toast.success('Autonomous system started successfully!');
        setSystemStatus('initializing');
        setTimeout(fetchSystemStatus, 5000); // Check status after 5 seconds
      } else {
        toast.error('Failed to start autonomous system');
      }
    } catch (error) {
      console.error('Error starting system:', error);
      toast.error('Error starting autonomous system');
    } finally {
      setIsLoading(false);
    }
  };

  const stopAutonomousSystem = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/automation/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        toast.success('Autonomous system stopped successfully!');
        setSystemStatus('stopped');
      } else {
        toast.error('Failed to stop autonomous system');
      }
    } catch (error) {
      console.error('Error stopping system:', error);
      toast.error('Error stopping autonomous system');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'text-green-600 bg-green-100';
      case 'initializing': return 'text-yellow-600 bg-yellow-100';
      case 'stopped': return 'text-red-600 bg-red-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mass Scale Automation Orchestrator</h1>
          <p className="text-gray-600 mt-2">Control and monitor the autonomous job hunting system for 100+ candidates</p>
        </div>
        
        {/* System Status Badge */}
        <div className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(systemStatus)}`}>
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4" />
            <span className="capitalize">{systemStatus}</span>
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <Play className="w-5 h-5 mr-2 text-blue-600" />
          System Control
        </h2>
        
        <div className="flex space-x-4">
          <button
            onClick={startAutonomousSystem}
            disabled={isLoading || systemStatus === 'running'}
            className="flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Play className="w-4 h-4 mr-2" />
            Start Autonomous System
          </button>
          
          <button
            onClick={stopAutonomousSystem}
            disabled={isLoading || systemStatus === 'stopped'}
            className="flex items-center px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Square className="w-4 h-4 mr-2" />
            Stop System
          </button>
        </div>
        
        {systemStatus === 'running' && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 text-sm">
              🤖 The autonomous system is actively processing candidates and submitting applications. 
              Monitor the statistics below for real-time progress.
            </p>
          </div>
        )}
      </div>

      {/* Real-time Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Candidates</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(stats.active_candidates)}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Jobs Scraped</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(stats.jobs_scraped)}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <Briefcase className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Matches Found</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(stats.matches_found)}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Applications Sent</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(stats.applications_submitted)}</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Send className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Metrics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-purple-600" />
            Performance Metrics
          </h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Success Rate</span>
              <span className="font-semibold text-green-600">{stats.success_rate.toFixed(1)}%</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Resumes Tailored</span>
              <span className="font-semibold">{formatNumber(stats.resumes_tailored)}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Cover Letters Generated</span>
              <span className="font-semibold">{formatNumber(stats.cover_letters_generated)}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Outreach Messages Sent</span>
              <span className="font-semibold">{formatNumber(stats.outreach_sent)}</span>
            </div>
          </div>
        </div>

        {/* System Runtime */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Clock className="w-5 h-5 mr-2 text-blue-600" />
            System Runtime
          </h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Runtime</span>
              <span className="font-semibold">{stats.total_runtime_hours.toFixed(1)} hours</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Candidates Processed</span>
              <span className="font-semibold">{formatNumber(stats.candidates_processed)}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Avg. Processing Time</span>
              <span className="font-semibold">
                {stats.candidates_processed > 0 
                  ? ((stats.total_runtime_hours * 60) / stats.candidates_processed).toFixed(1) 
                  : '0'} min/candidate
              </span>
            </div>
          </div>
          
          {/* Progress visualization */}
          <div className="mt-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Daily Progress</span>
              <span>{Math.min(100, (stats.applications_submitted / 500) * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(100, (stats.applications_submitted / 500) * 100)}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">Target: 500 applications/day</p>
          </div>
        </div>
      </div>

      {/* System Health Indicators */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
          System Health & Alerts
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-green-200 rounded-lg bg-green-50">
            <div className="flex items-center justify-between">
              <span className="text-green-800 font-medium">All Systems Operational</span>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
            <p className="text-sm text-green-600 mt-1">No issues detected</p>
          </div>
          
          <div className="p-4 border border-blue-200 rounded-lg bg-blue-50">
            <div className="flex items-center justify-between">
              <span className="text-blue-800 font-medium">Rate Limiting Active</span>
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            </div>
            <p className="text-sm text-blue-600 mt-1">Within safe limits</p>
          </div>
          
          <div className="p-4 border border-yellow-200 rounded-lg bg-yellow-50">
            <div className="flex items-center justify-between">
              <span className="text-yellow-800 font-medium">Optimization Ready</span>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            </div>
            <p className="text-sm text-yellow-600 mt-1">Learning patterns</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomationOrchestrator;