import React, { useState, useEffect } from "react";
import axios from "axios";
import { 
  Target, 
  Brain, 
  TrendingUp, 
  CheckCircle,
  Clock,
  AlertTriangle,
  Play,
  RefreshCw,
  Users,
  Briefcase,
  Star,
  Filter,
  Search,
  ExternalLink,
  MapPin,
  DollarSign,
  Calendar,
  Award
} from "lucide-react";
import toast from "react-hot-toast";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PriorityBadge = ({ priority }) => {
  const colors = {
    high: "bg-red-100 text-red-800 border-red-200",
    medium: "bg-yellow-100 text-yellow-800 border-yellow-200", 
    low: "bg-gray-100 text-gray-800 border-gray-200"
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colors[priority] || colors.low}`}>
      {priority.toUpperCase()}
    </span>
  );
};

const MatchScoreBar = ({ score }) => {
  const percentage = Math.round(score * 100);
  let colorClass = "bg-red-500";
  
  if (percentage >= 80) colorClass = "bg-green-500";
  else if (percentage >= 60) colorClass = "bg-yellow-500";
  else if (percentage >= 40) colorClass = "bg-orange-500";
  
  return (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div 
        className={`h-2 rounded-full ${colorClass}`}
        style={{ width: `${percentage}%` }}
      ></div>
    </div>
  );
};

const JobCard = ({ match, onViewDetails }) => {
  const job = match.job_data || {};
  const percentage = Math.round(match.match_score * 100);
  
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {job.title || 'Unknown Title'}
          </h3>
          <p className="text-gray-600 flex items-center">
            <Briefcase className="w-4 h-4 mr-1" />
            {job.company || 'Unknown Company'}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <PriorityBadge priority={match.priority} />
          {match.should_apply && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
              <Star className="w-3 h-3 mr-1" />
              Apply
            </span>
          )}
        </div>
      </div>
      
      <div className="space-y-3 mb-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Match Score</span>
          <span className="text-sm font-medium text-gray-900">{percentage}%</span>
        </div>
        <MatchScoreBar score={match.match_score} />
        
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center">
            <MapPin className="w-4 h-4 mr-1 text-gray-400" />
            <span className="text-gray-600">{job.location || 'Unknown'}</span>
          </div>
          <div className="flex items-center">
            <DollarSign className="w-4 h-4 mr-1 text-gray-400" />
            <span className="text-gray-600">{job.salary || 'Not specified'}</span>
          </div>
          <div className="flex items-center">
            <Award className="w-4 h-4 mr-1 text-gray-400" />
            <span className="text-gray-600">{job.experience_level || 'Any level'}</span>
          </div>
          <div className="flex items-center">
            <Calendar className="w-4 h-4 mr-1 text-gray-400" />
            <span className="text-gray-600">
              {job.scraped_at ? new Date(job.scraped_at).toLocaleDateString() : 'Unknown'}
            </span>
          </div>
        </div>
      </div>
      
      {match.explanation && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
          <p className="text-sm text-blue-800">{match.explanation}</p>
        </div>
      )}
      
      {match.keywords_matched && match.keywords_matched.length > 0 && (
        <div className="mb-4">
          <p className="text-xs text-gray-500 mb-2">Matched Skills:</p>
          <div className="flex flex-wrap gap-1">
            {match.keywords_matched.slice(0, 5).map((keyword, index) => (
              <span 
                key={index}
                className="inline-flex items-center px-2 py-1 rounded text-xs bg-blue-100 text-blue-800"
              >
                {keyword}
              </span>
            ))}
            {match.keywords_matched.length > 5 && (
              <span className="text-xs text-gray-500">+{match.keywords_matched.length - 5} more</span>
            )}
          </div>
        </div>
      )}
      
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex space-x-2">
          <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${
            match.salary_match ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            💰 Salary
          </span>
          <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${
            match.location_match ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            📍 Location
          </span>
          <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${
            match.visa_match ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            🛂 Visa
          </span>
        </div>
        
        <button
          onClick={() => onViewDetails(match)}
          className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center"
        >
          View Details
          <ExternalLink className="w-3 h-3 ml-1" />
        </button>
      </div>
    </div>
  );
};

const StatsCard = ({ title, value, icon: Icon, color = "blue", subtitle }) => {
  const colorClasses = {
    blue: "bg-blue-500",
    green: "bg-green-500",
    yellow: "bg-yellow-500",
    purple: "bg-purple-500",
    red: "bg-red-500"
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`${colorClasses[color]} p-3 rounded-lg`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
};

const JobMatching = () => {
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState("");
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [processingMatches, setProcessingMatches] = useState(false);
  const [processingAll, setProcessingAll] = useState(false);
  const [stats, setStats] = useState({});
  const [filter, setFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchCandidates();
    fetchMatchingStats();
  }, []);

  const fetchCandidates = async () => {
    try {
      const response = await axios.get(`${API}/candidates`);
      setCandidates(response.data);
      if (response.data.length > 0 && !selectedCandidate) {
        setSelectedCandidate(response.data[0].id);
      }
    } catch (error) {
      console.error("Failed to fetch candidates:", error);
      toast.error("Failed to load candidates");
    }
  };

  const fetchMatchingStats = async () => {
    try {
      const response = await axios.get(`${API}/matching/stats`);
      setStats(response.data.stats || {});
    } catch (error) {
      console.error("Failed to fetch matching stats:", error);
    }
  };

  const fetchCandidateMatches = async (candidateId) => {
    if (!candidateId) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/candidates/${candidateId}/matches`);
      setMatches(response.data.matches || []);
    } catch (error) {
      console.error("Failed to fetch matches:", error);
      toast.error("Failed to load matches");
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  const processCandidateMatches = async () => {
    if (!selectedCandidate) {
      toast.error("Please select a candidate");
      return;
    }

    setProcessingMatches(true);
    try {
      const response = await axios.post(`${API}/candidates/${selectedCandidate}/process-matches`);
      toast.success(`Found ${response.data.matches_processed} matches!`);
      
      // Refresh matches and stats
      await fetchCandidateMatches(selectedCandidate);
      await fetchMatchingStats();
    } catch (error) {
      console.error("Failed to process matches:", error);
      toast.error("Failed to process matches");
    } finally {
      setProcessingMatches(false);
    }
  };

  const processAllCandidates = async () => {
    setProcessingAll(true);
    try {
      const response = await axios.post(`${API}/matching/process-all`);
      const results = response.data.results;
      toast.success(`Processed ${results.total_candidates} candidates, found ${results.total_matches_found} total matches!`);
      
      // Refresh current candidate matches and stats
      if (selectedCandidate) {
        await fetchCandidateMatches(selectedCandidate);
      }
      await fetchMatchingStats();
    } catch (error) {
      console.error("Failed to process all candidates:", error);
      toast.error("Failed to process all candidates");
    } finally {
      setProcessingAll(false);
    }
  };

  const handleCandidateChange = (candidateId) => {
    setSelectedCandidate(candidateId);
    setMatches([]);
    if (candidateId) {
      fetchCandidateMatches(candidateId);
    }
  };

  const filteredMatches = matches.filter(match => {
    // Filter by priority
    if (filter !== "all" && match.priority !== filter) return false;
    
    // Filter by search term
    if (searchTerm) {
      const job = match.job_data || {};
      const searchLower = searchTerm.toLowerCase();
      return (
        job.title?.toLowerCase().includes(searchLower) ||
        job.company?.toLowerCase().includes(searchLower) ||
        job.location?.toLowerCase().includes(searchLower)
      );
    }
    
    return true;
  });

  const selectedCandidateName = candidates.find(c => c.id === selectedCandidate)?.full_name || "Unknown";

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Job Matching</h1>
          <p className="text-gray-600 mt-2">
            Advanced AI-powered job-candidate matching system
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={processCandidateMatches}
            disabled={processingMatches || !selectedCandidate}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium flex items-center space-x-2 transition-colors"
          >
            {processingMatches ? (
              <RefreshCw className="w-5 h-5 animate-spin" />
            ) : (
              <Target className="w-5 h-5" />
            )}
            <span>{processingMatches ? 'Processing...' : 'Process Matches'}</span>
          </button>
          
          <button
            onClick={processAllCandidates}
            disabled={processingAll}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium flex items-center space-x-2 transition-colors"
          >
            {processingAll ? (
              <RefreshCw className="w-5 h-5 animate-spin" />
            ) : (
              <Users className="w-5 h-5" />
            )}
            <span>{processingAll ? 'Processing All...' : 'Process All Candidates'}</span>
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Matches"
          value={stats.total_matches || 0}
          icon={Target}
          color="blue"
          subtitle="All time"
        />
        <StatsCard
          title="High Priority"
          value={stats.high_priority_matches || 0}
          icon={Star}
          color="red"
          subtitle="Excellent matches"
        />
        <StatsCard
          title="Should Apply"
          value={stats.should_apply_matches || 0}
          icon={CheckCircle}
          color="green"
          subtitle="Recommended"
        />
        <StatsCard
          title="Avg Match Score"
          value={`${stats.average_match_score || 0}%`}
          icon={TrendingUp}
          color="purple"
          subtitle="Quality metric"
        />
      </div>

      {/* Candidate Selection and Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Candidate Selection</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Candidate
            </label>
            <select
              value={selectedCandidate}
              onChange={(e) => handleCandidateChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a candidate...</option>
              {candidates.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>
                  {candidate.full_name} ({candidate.email})
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Priority
            </label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Matches</option>
              <option value="high">High Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="low">Low Priority</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Jobs
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search by title, company, location..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Matches Display */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Job Matches {selectedCandidate && `for ${selectedCandidateName}`}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {filteredMatches.length} of {matches.length} matches shown
              </p>
            </div>
            
            {selectedCandidate && (
              <button
                onClick={() => fetchCandidateMatches(selectedCandidate)}
                disabled={loading}
                className="text-blue-600 hover:text-blue-700 font-medium flex items-center space-x-1"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            )}
          </div>
        </div>
        
        <div className="p-6">
          {loading ? (
            <div className="text-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
              <p className="text-gray-600">Loading matches...</p>
            </div>
          ) : !selectedCandidate ? (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Please select a candidate to view matches</p>
            </div>
          ) : filteredMatches.length === 0 ? (
            <div className="text-center py-12">
              <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">
                {matches.length === 0 
                  ? "No matches found. Click 'Process Matches' to find jobs for this candidate."
                  : "No matches found for current filter."
                }
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredMatches.map((match, index) => (
                <JobCard
                  key={match.id || index}
                  match={match}
                  onViewDetails={(match) => {
                    // TODO: Implement job details modal
                    console.log("View job details:", match);
                  }}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobMatching;