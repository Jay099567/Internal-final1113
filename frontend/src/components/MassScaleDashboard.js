import React, { useState, useEffect } from 'react';
import { Users, Briefcase, Target, Send, TrendingUp, Clock, AlertCircle, CheckCircle, Activity } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const MassScaleDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');

  // Sample data for charts (in real implementation, this would come from the API)
  const applicationTrendData = [
    { date: '00:00', applications: 0, matches: 0 },
    { date: '04:00', applications: 12, matches: 8 },
    { date: '08:00', applications: 45, matches: 28 },
    { date: '12:00', applications: 78, matches: 45 },
    { date: '16:00', applications: 102, matches: 62 },
    { date: '20:00', applications: 134, matches: 81 },
    { date: '24:00', applications: 156, matches: 94 }
  ];

  const candidateStatusData = [
    { name: 'Active', value: 67, color: '#10B981' },
    { name: 'Processing', value: 23, color: '#F59E0B' },
    { name: 'Paused', value: 8, color: '#EF4444' },
    { name: 'Completed', value: 45, color: '#6B7280' }
  ];

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/analytics/mass-scale-dashboard`);
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data.dashboard);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Refresh data every 2 minutes
    const interval = setInterval(fetchDashboardData, 120000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  // Use default data structure if API data is not available
  const data = dashboardData || {
    candidates: { total: 143, active: 67, inactive: 76 },
    jobs: { total: 2456, scraped_today: 156, scraping_active: true },
    applications: { total: 1234, submitted_today: 45, success_rate: 12.5 },
    matching: { total_matches: 3456, high_priority: 234, match_rate: 85.2 },
    outreach: { total_sent: 567, responses: 89, response_rate: 15.7 },
    automation: { status: 'running', uptime: '4h 23m', last_cycle: '2 min ago', processed_today: 34 }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mass Scale Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Real-time monitoring and analytics for 100+ candidates</p>
        </div>
        
        {/* Time Range Selector */}
        <div className="flex space-x-2">
          {['1h', '24h', '7d', '30d'].map((range) => (
            <button
              key={range}
              onClick={() => setSelectedTimeRange(range)}
              className={`px-3 py-1 text-sm rounded ${
                selectedTimeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        {/* Total Candidates */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Candidates</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(data.candidates?.total)}</p>
              <p className="text-xs text-green-600">↗ {data.candidates?.active} active</p>
            </div>
            <div className="p-2 bg-blue-100 rounded-full">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Jobs Scraped */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Jobs Today</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(data.jobs?.scraped_today)}</p>
              <p className="text-xs text-blue-600">of {formatNumber(data.jobs?.total)} total</p>
            </div>
            <div className="p-2 bg-green-100 rounded-full">
              <Briefcase className="w-5 h-5 text-green-600" />
            </div>
          </div>
        </div>

        {/* Matches Found */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Priority</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(data.matching?.high_priority)}</p>
              <p className="text-xs text-purple-600">{data.matching?.match_rate}% match rate</p>
            </div>
            <div className="p-2 bg-purple-100 rounded-full">
              <Target className="w-5 h-5 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Applications Today */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Apps Today</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(data.applications?.submitted_today)}</p>
              <p className="text-xs text-orange-600">{data.applications?.success_rate}% success</p>
            </div>
            <div className="p-2 bg-orange-100 rounded-full">
              <Send className="w-5 h-5 text-orange-600" />
            </div>
          </div>
        </div>

        {/* Outreach Response Rate */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Response Rate</p>
              <p className="text-2xl font-bold text-gray-900">{data.outreach?.response_rate}%</p>
              <p className="text-xs text-indigo-600">{formatNumber(data.outreach?.responses)} replies</p>
            </div>
            <div className="p-2 bg-indigo-100 rounded-full">
              <TrendingUp className="w-5 h-5 text-indigo-600" />
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Status</p>
              <p className="text-lg font-bold text-green-900 capitalize">{data.automation?.status}</p>
              <p className="text-xs text-gray-600">Uptime: {data.automation?.uptime}</p>
            </div>
            <div className="p-2 bg-green-100 rounded-full">
              <Activity className="w-5 h-5 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Application Trends */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Application Trends (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={applicationTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="applications" stroke="#3B82F6" strokeWidth={2} />
              <Line type="monotone" dataKey="matches" stroke="#10B981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Candidate Status Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Candidate Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={candidateStatusData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {candidateStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">System Health</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                <span className="text-green-800">Job Scraping Service</span>
              </div>
              <span className="text-green-600 text-sm">Operational</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                <span className="text-green-800">AI Matching Engine</span>
              </div>
              <span className="text-green-600 text-sm">Operational</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
                <span className="text-yellow-800">LinkedIn Outreach</span>
              </div>
              <span className="text-yellow-600 text-sm">Rate Limited</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                <span className="text-green-800">Application Submission</span>
              </div>
              <span className="text-green-600 text-sm">Operational</span>
            </div>
          </div>
        </div>

        {/* Recent Activities */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Activities</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 p-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">34 candidates processed in current cycle</p>
                <p className="text-xs text-gray-500">2 minutes ago</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">156 new jobs scraped from Indeed</p>
                <p className="text-xs text-gray-500">15 minutes ago</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">89 high-priority matches identified</p>
                <p className="text-xs text-gray-500">30 minutes ago</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-2">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">45 applications submitted successfully</p>
                <p className="text-xs text-gray-500">1 hour ago</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-2">
              <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">12 LinkedIn outreach messages sent</p>
                <p className="text-xs text-gray-500">2 hours ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Summary */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">24-Hour Performance Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{data.candidates?.active}</div>
            <div className="text-sm text-gray-600">Candidates Processed</div>
            <div className="text-xs text-green-600 mt-1">↗ 12% vs yesterday</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{data.applications?.submitted_today}</div>
            <div className="text-sm text-gray-600">Applications Submitted</div>
            <div className="text-xs text-green-600 mt-1">↗ 8% vs yesterday</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{data.matching?.high_priority}</div>
            <div className="text-sm text-gray-600">High-Quality Matches</div>
            <div className="text-xs text-green-600 mt-1">↗ 15% vs yesterday</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-indigo-600">{data.outreach?.responses}</div>
            <div className="text-sm text-gray-600">Outreach Responses</div>
            <div className="text-xs text-red-600 mt-1">↘ 3% vs yesterday</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MassScaleDashboard;