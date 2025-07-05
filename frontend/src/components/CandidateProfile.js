import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Linkedin, 
  Github, 
  Globe,
  FileText,
  Settings,
  Activity,
  Briefcase
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CandidateProfile = () => {
  const { id } = useParams();
  const [candidate, setCandidate] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCandidateData();
  }, [id]);

  const fetchCandidateData = async () => {
    try {
      const [candidateResponse, resumesResponse] = await Promise.all([
        axios.get(`${API}/candidates/${id}`),
        axios.get(`${API}/candidates/${id}/resumes`)
      ]);
      
      setCandidate(candidateResponse.data);
      setResumes(resumesResponse.data);
    } catch (error) {
      console.error("Failed to fetch candidate data:", error);
      setError("Failed to load candidate profile");
      toast.error("Failed to load candidate profile");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error || !candidate) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Candidate Not Found</h2>
          <p className="text-gray-600">{error || "The candidate profile could not be loaded."}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{candidate.full_name}</h1>
              <p className="text-gray-600">{candidate.email}</p>
              <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                {candidate.location && (
                  <div className="flex items-center space-x-1">
                    <MapPin className="w-4 h-4" />
                    <span>{candidate.location}</span>
                  </div>
                )}
                {candidate.years_experience && (
                  <div className="flex items-center space-x-1">
                    <Briefcase className="w-4 h-4" />
                    <span>{candidate.years_experience} years experience</span>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              candidate.is_active 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {candidate.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Contact Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Information</h2>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-gray-400" />
                <span>{candidate.email}</span>
              </div>
              {candidate.phone && (
                <div className="flex items-center space-x-3">
                  <Phone className="w-5 h-5 text-gray-400" />
                  <span>{candidate.phone}</span>
                </div>
              )}
              {candidate.linkedin_url && (
                <div className="flex items-center space-x-3">
                  <Linkedin className="w-5 h-5 text-gray-400" />
                  <a 
                    href={candidate.linkedin_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-700"
                  >
                    LinkedIn Profile
                  </a>
                </div>
              )}
              {candidate.github_url && (
                <div className="flex items-center space-x-3">
                  <Github className="w-5 h-5 text-gray-400" />
                  <a 
                    href={candidate.github_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-700"
                  >
                    GitHub Profile
                  </a>
                </div>
              )}
              {candidate.portfolio_url && (
                <div className="flex items-center space-x-3">
                  <Globe className="w-5 h-5 text-gray-400" />
                  <a 
                    href={candidate.portfolio_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-700"
                  >
                    Portfolio
                  </a>
                </div>
              )}
            </div>
          </div>

          {/* Job Preferences */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Preferences</h2>
            <div className="space-y-4">
              {candidate.target_roles.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Target Roles</h3>
                  <div className="flex flex-wrap gap-2">
                    {candidate.target_roles.map((role, index) => (
                      <span 
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {role}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {candidate.target_companies.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Target Companies</h3>
                  <div className="flex flex-wrap gap-2">
                    {candidate.target_companies.map((company, index) => (
                      <span 
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                      >
                        {company}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {candidate.target_locations.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Target Locations</h3>
                  <div className="flex flex-wrap gap-2">
                    {candidate.target_locations.map((location, index) => (
                      <span 
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                      >
                        {location}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {(candidate.salary_min || candidate.salary_max) && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Salary Range</h3>
                  <p className="text-gray-600">
                    ${candidate.salary_min?.toLocaleString() || '?'} - ${candidate.salary_max?.toLocaleString() || '?'}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Skills */}
          {candidate.skills.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Skills</h2>
              <div className="flex flex-wrap gap-2">
                {candidate.skills.map((skill, index) => (
                  <span 
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Resumes */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Resumes</h2>
            {resumes.length > 0 ? (
              <div className="space-y-3">
                {resumes.map((resume) => (
                  <div key={resume.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    <FileText className="w-5 h-5 text-gray-400" />
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{resume.version_name}</p>
                      <p className="text-sm text-gray-500">
                        {resume.skills.length} skills extracted
                      </p>
                      {resume.is_primary && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 mt-1">
                          Primary
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4">
                <FileText className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">No resumes uploaded</p>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <button className="w-full flex items-center space-x-3 px-4 py-3 text-left text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                <Settings className="w-5 h-5" />
                <span>Edit Profile</span>
              </button>
              <button className="w-full flex items-center space-x-3 px-4 py-3 text-left text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                <FileText className="w-5 h-5" />
                <span>Upload Resume</span>
              </button>
              <button className="w-full flex items-center space-x-3 px-4 py-3 text-left text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                <Activity className="w-5 h-5" />
                <span>View Applications</span>
              </button>
            </div>
          </div>

          {/* Account Status */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Account Status</h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Created:</span>
                <span className="text-gray-900">
                  {new Date(candidate.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Last Updated:</span>
                <span className="text-gray-900">
                  {new Date(candidate.updated_at).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Visa Sponsorship:</span>
                <span className="text-gray-900">
                  {candidate.visa_sponsorship_required ? 'Required' : 'Not Required'}
                </span>
              </div>
              {candidate.work_authorization && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Work Auth:</span>
                  <span className="text-gray-900">{candidate.work_authorization}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateProfile;