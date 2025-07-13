import React, { useState, useEffect } from "react";
import axios from "axios";
import { 
  Users, 
  FileText, 
  Briefcase, 
  TrendingUp,
  Activity,
  CheckCircle,
  Clock,
  AlertCircle,
  Plus,
  BarChart3
} from "lucide-react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StatCard = ({ title, value, icon: Icon, trend, color = "blue" }) => {
  const colorClasses = {
    blue: "bg-blue-500",
    green: "bg-green-500",
    yellow: "bg-yellow-500",
    purple: "bg-purple-500"
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {trend && (
            <p className="text-sm text-green-600 font-medium">
              <TrendingUp className="w-4 h-4 inline mr-1" />
              {trend}
            </p>
          )}
        </div>
        <div className={`${colorClasses[color]} p-3 rounded-lg`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
};

const ActivityItem = ({ type, title, time, status }) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-lg">
      {getStatusIcon()}
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-900">{title}</p>
        <p className="text-xs text-gray-500">{time}</p>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_candidates: 0,
    total_resumes: 0,
    applications: {
      total: 0,
      pending: 0,
      successful: 0
    },
    jobs: 0,
    scraping: {
      total_jobs_scraped: 0,
      jobs_scraped_24h: 0,
      scheduled_jobs: 0,
      success_rate: 0,
      is_running: false
    },
    recent_activity: {
      candidates: [],
      applications: []
    }
  });
  const [loading, setLoading] = useState(true);
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    checkSystemHealth();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch main dashboard stats
      const dashboardResponse = await axios.get(`${API}/dashboard/stats`);
      
      // Fetch scraping stats
      const scrapingResponse = await axios.get(`${API}/scraping/status`);
      
      // Fetch resume tailoring stats
      let tailoringStats = {
        total_resume_versions: 0,
        average_ats_score: 0,
        total_genetic_pools: 0
      };
      
      try {
        const tailoringResponse = await axios.get(`${API}/resume-tailoring/stats`);
        if (tailoringResponse.data.success) {
          tailoringStats = tailoringResponse.data.stats;
        }
      } catch (tailoringError) {
        console.warn("Resume tailoring stats not available:", tailoringError);
      }
      
      // Fetch cover letter stats
      let coverLetterStats = {
        total_cover_letters: 0,
        total_applications: 0,
        avg_success_rate: 0,
        total_usage: 0,
        tone_distribution: []
      };
      
      try {
        const coverLetterResponse = await axios.get(`${API}/cover-letters/stats/overview`);
        if (coverLetterResponse.data.success) {
          coverLetterStats = coverLetterResponse.data.data.overview;
        }
      } catch (coverLetterError) {
        console.warn("Cover letter stats not available:", coverLetterError);
      }
      
      const combinedStats = {
        ...dashboardResponse.data,
        scraping: scrapingResponse.data.success ? scrapingResponse.data.stats : {
          total_jobs_scraped: 0,
          jobs_scraped_24h: 0,
          scheduled_jobs: 0,
          success_rate: 0,
          is_running: false
        },
        tailoring: tailoringStats,
        coverLetters: coverLetterStats
      };
      
      setStats(combinedStats);
    } catch (error) {
      console.error("Failed to fetch dashboard stats:", error);
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const checkSystemHealth = async () => {
    try {
      const response = await axios.get(`${API}/health`);
      setSystemStatus(response.data);
    } catch (error) {
      console.error("System health check failed:", error);
      setSystemStatus({ status: "unhealthy" });
    }
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Elite JobHunter X Dashboard
          </h1>
          <p className="text-gray-600 mt-2">
            Autonomous job application automation platform
          </p>
        </div>
        <Link
          to="/candidates/new"
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center space-x-2 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Add Candidate</span>
        </Link>
      </div>

      {/* System Status */}
      {systemStatus && (
        <div className={`p-4 rounded-lg ${
          systemStatus.status === 'healthy' 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              systemStatus.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="font-medium">
              System Status: {systemStatus.status === 'healthy' ? 'Operational' : 'Issues Detected'}
            </span>
          </div>
          <div className="mt-2 text-sm text-gray-600">
            Database: {systemStatus.database} | AI: {systemStatus.openrouter}
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Candidates"
          value={stats.total_candidates}
          icon={Users}
          trend="+12% this week"
          color="blue"
        />
        <StatCard
          title="Jobs Scraped"
          value={stats.total_jobs}
          icon={Search}
          trend="+156 today"
          color="green"
        />
        <StatCard
          title="Job Matches"
          value={stats.total_matches}
          icon={Target}
          trend="+24 new matches"
          color="purple"
        />
        <StatCard
          title="Applications Submitted"
          value={stats.total_applications || 0}
          icon={Send}
          trend="+8 today"
          color="orange"
        />
      </div>

      {/* Phase 6: Application Submission Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Application Submission Engine</h2>
          <Link
            to="/application-submission"
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            View Details &rarr;
          </Link>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.applications_pending || 0}</div>
            <div className="text-sm text-gray-600">In Queue</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{stats.applications_successful || 0}</div>
            <div className="text-sm text-gray-600">Successful</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{stats.applications_active || 0}</div>
            <div className="text-sm text-gray-600">Active</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{stats.applications_today || 0}</div>
            <div className="text-sm text-gray-600">Today</div>
          </div>
        </div>
      </div>
          trend="+8 new this week"
          color="green"
        />
        <StatCard
          title="Applications Sent"
          value={stats.applications.total}
          icon={Briefcase}
          trend="+0 this week"
          color="purple"
        />
        <StatCard
          title="Job Matches"
          value={stats.counts?.job_matches || 0}
          icon={TrendingUp}
          trend="+New matches found"
          color="yellow"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Candidates */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Recent Candidates</h2>
            <p className="text-sm text-gray-600 mt-1">Newly onboarded candidates</p>
          </div>
          <div className="p-6">
            {stats.recent_activity.candidates.length > 0 ? (
              <div className="space-y-4">
                {stats.recent_activity.candidates.map((candidate) => (
                  <Link
                    key={candidate.id}
                    to={`/candidates/${candidate.id}`}
                    className="flex items-center space-x-4 p-4 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <Users className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{candidate.full_name}</p>
                      <p className="text-sm text-gray-500">{candidate.email}</p>
                      <p className="text-xs text-gray-400">
                        Added {formatTime(candidate.created_at)}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No candidates added yet</p>
                <Link
                  to="/candidates/new"
                  className="text-blue-600 hover:text-blue-700 font-medium mt-2 inline-block"
                >
                  Add your first candidate
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* System Activity */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">System Activity</h2>
            <p className="text-sm text-gray-600 mt-1">Recent system events</p>
          </div>
          <div className="p-6">
            <div className="space-y-2">
              <ActivityItem
                type="system"
                title="AI Services Initialized"
                time="2 minutes ago"
                status="success"
              />
              <ActivityItem
                type="system"
                title="Database Connection Established"
                time="5 minutes ago"
                status="success"
              />
              <ActivityItem
                type="feature"
                title="Gmail OAuth Ready"
                time="10 minutes ago"
                status="success"
              />
              <ActivityItem
                type="feature"
                title="Resume Parser Active"
                time="15 minutes ago"
                status="success"
              />
              <ActivityItem
                type="system"
                title="Phase 1 Implementation Complete"
                time="1 hour ago"
                status="success"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Job Matching Statistics */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">AI Job Matching Status</h2>
              <p className="text-sm text-gray-600 mt-1">Advanced job-candidate matching system</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-sm font-medium text-gray-700">AI System Active</span>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.matching_stats?.total_matches || 0}</div>
              <div className="text-sm text-gray-600">Total Matches</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{stats.matching_stats?.high_priority_matches || 0}</div>
              <div className="text-sm text-gray-600">High Priority</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.matching_stats?.should_apply_matches || 0}</div>
              <div className="text-sm text-gray-600">Should Apply</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{stats.matching_stats?.average_match_score || 0}%</div>
              <div className="text-sm text-gray-600">Avg Match Score</div>
            </div>
          </div>
          <div className="mt-6 flex space-x-4">
            <Link
              to="/matching"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <Activity className="w-4 h-4 mr-2" />
              View Matches
            </Link>
            <Link
              to="/matching"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <Brain className="w-4 h-4 mr-2" />
              Process Matches
            </Link>
          </div>
        </div>
      </div>

      {/* Job Scraping Statistics */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Job Scraping Status</h2>
              <p className="text-sm text-gray-600 mt-1">Automated job discovery and collection</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${stats.scraping.is_running ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm font-medium text-gray-700">
                {stats.scraping.is_running ? 'Running' : 'Stopped'}
              </span>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.scraping.total_jobs_scraped}</div>
              <div className="text-sm text-gray-600">Total Jobs Scraped</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.scraping.jobs_scraped_24h}</div>
              <div className="text-sm text-gray-600">Jobs Today</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{stats.scraping.scheduled_jobs}</div>
              <div className="text-sm text-gray-600">Active Scrapers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{stats.scraping.success_rate.toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Success Rate</div>
            </div>
          </div>
          <div className="mt-6 flex space-x-4">
            <Link
              to="/scraping"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              <Activity className="w-4 h-4 mr-2" />
              Manage Scraping
            </Link>
            <Link
              to="/jobs"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <Briefcase className="w-4 h-4 mr-2" />
              View Jobs
            </Link>
          </div>
        </div>
      </div>

      {/* Resume Tailoring Statistics */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">🧬 Resume Tailoring Engine</h2>
              <p className="text-sm text-gray-600 mt-1">AI-powered resume optimization with genetic algorithms</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-sm font-medium text-gray-700">Advanced AI Active</span>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.tailoring?.total_resume_versions || 0}</div>
              <div className="text-sm text-gray-600">Resume Versions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.tailoring?.average_ats_score || 0}</div>
              <div className="text-sm text-gray-600">Avg ATS Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{stats.tailoring?.total_genetic_pools || 0}</div>
              <div className="text-sm text-gray-600">Genetic Pools</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{stats.tailoring?.total_ats_analyses || 0}</div>
              <div className="text-sm text-gray-600">ATS Analyses</div>
            </div>
          </div>
          <div className="mt-6 flex space-x-4">
            <Link
              to="/resume-tailoring"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <Activity className="w-4 h-4 mr-2" />
              Tailor Resumes
            </Link>
            <Link
              to="/resume-tailoring"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <Brain className="w-4 h-4 mr-2" />
              View Analytics
            </Link>
          </div>
        </div>
      </div>
      {/* Cover Letter Management Statistics */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">📝 Cover Letter Generator</h2>
              <p className="text-sm text-gray-600 mt-1">Multi-tone AI cover letters with company research</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-sm font-medium text-gray-700">Phase 5 Complete</span>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.coverLetters?.total_cover_letters || 0}</div>
              <div className="text-sm text-gray-600">Cover Letters</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.coverLetters?.total_applications || 0}</div>
              <div className="text-sm text-gray-600">Applications</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{stats.coverLetters?.avg_success_rate || 0}%</div>
              <div className="text-sm text-gray-600">Success Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{stats.coverLetters?.total_usage || 0}</div>
              <div className="text-sm text-gray-600">Total Usage</div>
            </div>
          </div>
          <div className="mt-6 flex space-x-4">
            <Link
              to="/cover-letters"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700"
            >
              <FileText className="w-4 h-4 mr-2" />
              Generate Cover Letters
            </Link>
            <Link
              to="/cover-letters"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              View Analytics
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Link
            to="/candidates/new"
            className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <Plus className="w-8 h-8 text-blue-600 mb-2" />
            <h3 className="font-medium text-gray-900">Add Candidate</h3>
            <p className="text-sm text-gray-600">Onboard a new job seeker</p>
          </Link>
          
          <Link
            to="/resume-tailoring"
            className="p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-colors"
          >
            <Activity className="w-8 h-8 text-green-600 mb-2" />
            <h3 className="font-medium text-gray-900">Resume Tailoring</h3>
            <p className="text-sm text-gray-600">AI-powered resume optimization</p>
          </Link>
          
          <Link
            to="/test-ai"
            className="p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-colors"
          >
            <Activity className="w-8 h-8 text-purple-600 mb-2" />
            <h3 className="font-medium text-gray-900">Test AI Features</h3>
            <p className="text-sm text-gray-600">Test job matching and AI tools</p>
          </Link>
          
          <Link
            to="/matching"
            className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <Brain className="w-8 h-8 text-blue-600 mb-2" />
            <h3 className="font-medium text-gray-900">AI Job Matching</h3>
            <p className="text-sm text-gray-600">Smart job-candidate matching</p>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;