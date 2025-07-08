import React, { useState, useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import { 
  Brain, 
  FileText, 
  Mail, 
  Target, 
  Play, 
  CheckCircle,
  AlertCircle,
  Loader
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TestCard = ({ title, description, icon: Icon, onTest, loading, result, error }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
            <Icon className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{title}</h3>
            <p className="text-sm text-gray-600">{description}</p>
          </div>
        </div>
        <button
          onClick={onTest}
          disabled={loading}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              <span>Testing...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Test</span>
            </>
          )}
        </button>
      </div>
      
      {result && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span className="font-medium text-green-900">Test Successful</span>
          </div>
          <pre className="text-sm text-green-800 whitespace-pre-wrap overflow-auto max-h-64">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
      
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-4 h-4 text-red-600" />
            <span className="font-medium text-red-900">Test Failed</span>
          </div>
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}
    </div>
  );
};

const TestAI = () => {
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [loading, setLoading] = useState({});
  const [results, setResults] = useState({});
  const [errors, setErrors] = useState({});
  const [matchingResult, setMatchingResult] = useState(null);
  const [matchingLoading, setMatchingLoading] = useState(false);

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      const response = await axios.get(`${API}/candidates`);
      setCandidates(response.data);
      if (response.data.length > 0) {
        setSelectedCandidate(response.data[0].id);
      }
    } catch (error) {
      console.error("Failed to fetch candidates:", error);
      toast.error("Failed to load candidates");
    }
  };

  const setTestState = (testName, { loading: isLoading, result, error }) => {
    if (isLoading !== undefined) {
      setLoading(prev => ({ ...prev, [testName]: isLoading }));
    }
    if (result !== undefined) {
      setResults(prev => ({ ...prev, [testName]: result }));
      setErrors(prev => ({ ...prev, [testName]: null }));
    }
    if (error !== undefined) {
      setErrors(prev => ({ ...prev, [testName]: error }));
      setResults(prev => ({ ...prev, [testName]: null }));
    }
  };

  const testJobMatching = async () => {
    if (!selectedCandidate || !jobDescription) {
      toast.error("Please select a candidate and enter a job description");
      return;
    }

    setTestState('jobMatch', { loading: true });

    try {
      const response = await axios.post(`${API}/matching/test`, {
        candidate_id: selectedCandidate,
        job_title: "Software Developer Test",
        job_description: jobDescription
      });

      setTestState('jobMatch', { 
        loading: false, 
        result: response.data.match,
        error: null 
      });
      toast.success("Job matching test completed!");
    } catch (error) {
      console.error("Job matching test failed:", error);
      setTestState('jobMatch', { 
        loading: false, 
        result: null, 
        error: error.response?.data?.detail || error.message 
      });
      toast.error("Job matching test failed");
    }
  };

  const testCoverLetter = async () => {
    if (!selectedCandidate || !jobDescription || !companyName) {
      toast.error("Please fill in all required fields");
      return;
    }

    setTestState('coverLetter', { loading: true });

    try {
      const response = await axios.post(`${API}/ai/test/cover-letter`, {
        candidate_id: selectedCandidate,
        job_description: jobDescription,
        company_name: companyName,
        tone: "professional"
      });

      setTestState('coverLetter', { result: response.data.cover_letter });
      toast.success("Cover letter generation test completed!");
    } catch (error) {
      console.error("Cover letter test failed:", error);
      setTestState('coverLetter', { error: error.response?.data?.detail || "Test failed" });
      toast.error("Cover letter test failed");
    } finally {
      setTestState('coverLetter', { loading: false });
    }
  };

  const checkSystemHealth = async () => {
    setTestState('health', { loading: true });

    try {
      const response = await axios.get(`${API}/health`);
      setTestState('health', { result: response.data });
      toast.success("System health check completed!");
    } catch (error) {
      console.error("Health check failed:", error);
      setTestState('health', { error: error.response?.data?.detail || "Health check failed" });
      toast.error("System health check failed");
    } finally {
      setTestState('health', { loading: false });
    }
  };

  const sampleJobDescription = `We are looking for a Senior Software Engineer to join our team. 

Responsibilities:
- Design and develop scalable web applications
- Work with React, Node.js, and MongoDB
- Collaborate with cross-functional teams
- Mentor junior developers
- Participate in code reviews

Requirements:
- 5+ years of software development experience
- Strong experience with JavaScript, React, and Node.js
- Experience with databases (MongoDB, PostgreSQL)
- Knowledge of cloud platforms (AWS, Azure)
- Bachelor's degree in Computer Science or related field
- Excellent communication skills

Nice to have:
- Experience with Docker and Kubernetes
- Knowledge of microservices architecture
- Previous startup experience

We offer competitive salary, equity, and comprehensive benefits.`;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Features Testing</h1>
        <p className="text-gray-600 mt-2">
          Test the AI-powered features of Elite JobHunter X
        </p>
      </div>

      {/* Test Configuration */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Test Configuration</h2>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Candidate for Testing
            </label>
            <select
              value={selectedCandidate}
              onChange={(e) => setSelectedCandidate(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            >
              <option value="">Select a candidate...</option>
              {candidates.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>
                  {candidate.full_name} ({candidate.email})
                </option>
              ))}
            </select>
            {candidates.length === 0 && (
              <p className="text-sm text-gray-500 mt-2">
                No candidates found. <a href="/candidates/new" className="text-purple-600 hover:text-purple-700">Create one first</a>.
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Description
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={12}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              placeholder="Paste a job description here..."
            />
            <div className="mt-2 flex justify-between items-center">
              <p className="text-sm text-gray-500">
                Enter a job description to test AI matching and cover letter generation
              </p>
              <button
                onClick={() => setJobDescription(sampleJobDescription)}
                className="text-sm text-purple-600 hover:text-purple-700 font-medium"
              >
                Use Sample Job Description
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Company Name
            </label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              placeholder="e.g., TechCorp Inc."
            />
          </div>
        </div>
      </div>

      {/* Test Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TestCard
          title="System Health Check"
          description="Test system connectivity and AI service status"
          icon={Brain}
          onTest={testSystemHealth}
          loading={loading.health}
          result={results.health}
          error={errors.health}
        />

        <TestCard
          title="Job Matching AI"
          description="Test AI-powered job matching algorithm"
          icon={Target}
          onTest={testJobMatching}
          loading={loading.jobMatch}
          result={results.jobMatch}
          error={errors.jobMatch}
        />

        <TestCard
          title="Cover Letter Generation"
          description="Test AI-powered cover letter creation"
          icon={Mail}
          onTest={testCoverLetter}
          loading={loading.coverLetter}
          result={results.coverLetter}
          error={errors.coverLetter}
        />

        <TestCard
          title="Resume Analysis"
          description="Test resume parsing and analysis (upload resume via candidate onboarding)"
          icon={FileText}
          onTest={() => toast.info("Upload a resume via candidate onboarding to test this feature")}
          loading={false}
          result={null}
          error={null}
        />
      </div>

      {/* API Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">API Endpoints Status</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-green-900">Candidate Management</span>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-green-900">Resume Upload</span>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-green-900">AI Job Matching</span>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-green-900">Cover Letter AI</span>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
            <AlertCircle className="w-5 h-5 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-900">Gmail OAuth (Ready)</span>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <AlertCircle className="w-5 h-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-900">Job Scraping (Phase 2)</span>
          </div>
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Next Steps</h3>
        <div className="text-sm text-blue-800 space-y-1">
          <p>• ✅ Phase 1: Core Infrastructure & AI Features (Current)</p>
          <p>• 🚧 Phase 2: Job Scraping & Application Engine</p>
          <p>• 🚧 Phase 3: Gmail Integration & Outreach</p>
          <p>• 🚧 Phase 4: Automation & Analytics</p>
        </div>
      </div>
    </div>
  );
};

export default TestAI;