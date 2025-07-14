import React, { useState, useEffect } from 'react';
import { LinkedinIcon, Play, Pause, Users, MessageCircle, TrendingUp, Clock, Target, Send } from 'lucide-react';
import toast from 'react-hot-toast';

const LinkedInAutomation = () => {
  const [candidates, setCandidates] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [campaignStats, setCampaignStats] = useState({
    total_sent: 0,
    responses: 0,
    connections: 0,
    response_rate: 0
  });

  const fetchCandidates = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/candidates`);
      if (response.ok) {
        const data = await response.json();
        setCandidates(data.candidates || []);
      }
    } catch (error) {
      console.error('Error fetching candidates:', error);
    }
  };

  const fetchCampaigns = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/linkedin/campaigns`);
      if (response.ok) {
        const data = await response.json();
        setCampaigns(data.campaigns || []);
      }
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    }
  };

  const fetchStats = async () => {
    // In a real implementation, this would fetch actual LinkedIn outreach stats
    // For now, using mock data
    setCampaignStats({
      total_sent: 156,
      responses: 23,
      connections: 45,
      response_rate: 14.7
    });
  };

  useEffect(() => {
    fetchCandidates();
    fetchCampaigns();
    fetchStats();
  }, []);

  const startOutreachCampaign = async () => {
    if (!selectedCandidate) {
      toast.error('Please select a candidate first');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/linkedin/start-outreach`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          candidate_id: selectedCandidate
        }),
      });

      if (response.ok) {
        toast.success('LinkedIn outreach campaign started successfully!');
        fetchCampaigns(); // Refresh campaigns list
      } else {
        toast.error('Failed to start LinkedIn outreach campaign');
      }
    } catch (error) {
      console.error('Error starting outreach:', error);
      toast.error('Error starting LinkedIn outreach campaign');
    } finally {
      setIsLoading(false);
    }
  };

  const getOutreachStatus = async (candidateId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/linkedin/outreach-status/${candidateId}`);
      if (response.ok) {
        const data = await response.json();
        return data.status;
      }
    } catch (error) {
      console.error('Error fetching outreach status:', error);
    }
    return null;
  };

  const formatNumber = (num) => {
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  const messageTemplates = [
    {
      name: 'Software Engineer Outreach',
      tone: 'Professional',
      preview: 'Hi [Name], I noticed your background in software development...'
    },
    {
      name: 'Warm Introduction',
      tone: 'Friendly',
      preview: 'Hello [Name], I hope this message finds you well...'
    },
    {
      name: 'Direct Opportunity',
      tone: 'Bold',
      preview: 'Hi [Name], I have an exciting opportunity that matches...'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <LinkedinIcon className="w-8 h-8 mr-3 text-blue-600" />
            LinkedIn Automation
          </h1>
          <p className="text-gray-600 mt-2">Automated LinkedIn outreach and recruiter networking for job seekers</p>
        </div>
        
        {/* Status Badge */}
        <div className="px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            <span>Rate Limited - Safe Mode</span>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Messages Sent</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(campaignStats.total_sent)}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Send className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Responses</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(campaignStats.responses)}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <MessageCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Connections</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(campaignStats.connections)}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Response Rate</p>
              <p className="text-2xl font-bold text-gray-900">{campaignStats.response_rate}%</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Campaign Creation */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Start New Outreach Campaign</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Candidate Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Candidate
            </label>
            <select
              value={selectedCandidate}
              onChange={(e) => setSelectedCandidate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Choose a candidate...</option>
              {candidates.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>
                  {candidate.full_name} - {candidate.job_preferences?.desired_role || 'No role specified'}
                </option>
              ))}
            </select>
          </div>

          {/* Campaign Settings */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Campaign Type
            </label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="recruiter_outreach">Recruiter Outreach</option>
              <option value="hiring_manager">Hiring Manager</option>
              <option value="network_expansion">Network Expansion</option>
              <option value="company_employees">Company Employees</option>
            </select>
          </div>
        </div>

        <div className="mt-6 flex space-x-4">
          <button
            onClick={startOutreachCampaign}
            disabled={isLoading || !selectedCandidate}
            className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Play className="w-4 h-4 mr-2" />
            {isLoading ? 'Starting Campaign...' : 'Start Campaign'}
          </button>
          
          <button className="flex items-center px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <Target className="w-4 h-4 mr-2" />
            Preview Messages
          </button>
        </div>
      </div>

      {/* Message Templates */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Message Templates</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {messageTemplates.map((template, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium text-gray-900">{template.name}</h3>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  {template.tone}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{template.preview}</p>
              <button className="text-blue-600 text-sm hover:text-blue-800">
                Edit Template →
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Active Campaigns */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Active Campaigns</h2>
        
        {campaigns.length === 0 ? (
          <div className="text-center py-8">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No active campaigns yet</p>
            <p className="text-sm text-gray-400">Start your first LinkedIn outreach campaign above</p>
          </div>
        ) : (
          <div className="space-y-4">
            {campaigns.map((campaign, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium text-gray-900">{campaign.name || `Campaign ${index + 1}`}</h3>
                    <p className="text-sm text-gray-600">{campaign.description || 'Automated LinkedIn outreach'}</p>
                  </div>
                  <div className="flex space-x-2">
                    <button className="text-blue-600 hover:text-blue-800">
                      <Play className="w-4 h-4" />
                    </button>
                    <button className="text-gray-600 hover:text-gray-800">
                      <Pause className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <div className="mt-4 grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Sent:</span>
                    <span className="ml-1 font-medium">{campaign.sent || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Responses:</span>
                    <span className="ml-1 font-medium">{campaign.responses || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Rate:</span>
                    <span className="ml-1 font-medium">{campaign.response_rate || 0}%</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Status:</span>
                    <span className="ml-1 font-medium text-green-600">Active</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Rate Limiting Information */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-start">
          <Clock className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
          <div>
            <h3 className="text-yellow-800 font-medium">LinkedIn Rate Limiting</h3>
            <p className="text-yellow-700 text-sm mt-1">
              To maintain account safety, outreach is limited to:
            </p>
            <ul className="text-yellow-700 text-sm mt-2 space-y-1">
              <li>• 15 connection requests per day</li>
              <li>• 25 messages per day</li>
              <li>• 50 profile views per day</li>
              <li>• 2-5 minute delays between actions</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LinkedInAutomation;