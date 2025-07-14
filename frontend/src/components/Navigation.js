import React from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  Home, 
  Users, 
  Plus, 
  Brain, 
  Settings, 
  Activity,
  Search,
  Send,
  BarChart3,
  FileText,
  Play,
  Zap,
  Target,
  LinkedinIcon,
  TrendingUp
} from "lucide-react";

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    {
      title: "Dashboard",
      icon: Home,
      path: "/",
      description: "Overview & Analytics"
    },
    {
      title: "Mass Scale Dashboard",
      icon: BarChart3,
      path: "/mass-scale",
      description: "100+ Candidates Analytics",
      badge: "NEW"
    },
    {
      title: "Automation Control",
      icon: Zap,
      path: "/automation",
      description: "Master Orchestrator",
      badge: "AUTONOMOUS"
    },
    {
      title: "Add Candidate",
      icon: Plus,
      path: "/candidates/new",
      description: "Onboard New Candidate"
    },
    {
      title: "Job Scraping",
      icon: Search,
      path: "/scraping",
      description: "Manage Job Scraping",
      badge: "ACTIVE"
    },
    {
      title: "Job Matching",
      icon: Brain,
      path: "/matching",
      description: "AI Job Matching",
      badge: "AI"
    },
    {
      title: "Resume Tailoring",
      icon: Settings,
      path: "/resume-tailoring",
      description: "AI Resume Optimization",
      badge: "GENETIC"
    },
    {
      title: "Cover Letters",
      icon: FileText,
      path: "/cover-letters",
      description: "AI Cover Letter Generation",
      badge: "MULTI-TONE"
    },
    {
      title: "Application Submission",
      icon: Play,
      path: "/application-submission",
      description: "Autonomous Application Engine",
      badge: "STEALTH"
    },
    {
      title: "LinkedIn Outreach",
      icon: LinkedinIcon,
      path: "/linkedin-automation",
      description: "Automated LinkedIn Networking",
      badge: "PHASE 7"
    },
    {
      title: "AI Analytics",
      icon: TrendingUp,
      path: "/feedback-analytics",
      description: "Performance Learning Loop",
      badge: "PHASE 8"
    },
    {
      title: "Jobs List",
      icon: Target,
      path: "/jobs",
      description: "View Scraped Jobs"
    },
    {
      title: "Test AI",
      icon: Brain,
      path: "/test-ai",
      description: "Test AI Features"
    }
  ];

  const isActivePath = (path) => {
    return location.pathname === path;
  };

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-slate-900 text-white flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold">JobHunter X</h1>
            <p className="text-sm text-slate-400">Elite Automation</p>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = isActivePath(item.path);
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200
                  ${isActive 
                    ? 'bg-blue-600 text-white shadow-lg' 
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">{item.title}</span>
                    {item.badge && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        {item.badge}
                      </span>
                    )}
                  </div>
                  <div className="text-xs opacity-70">{item.description}</div>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Feature Sections */}
        <div className="mt-8">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-4 mb-3">
            MASS SCALE SYSTEM
          </div>
          <div className="space-y-2">
            <div className="flex items-center space-x-3 px-4 py-2 text-slate-400 text-sm">
              <Zap className="w-4 h-4" />
              <span>Automation</span>
              <span className="ml-auto bg-green-500 w-2 h-2 rounded-full"></span>
            </div>
            <div className="flex items-center space-x-3 px-4 py-2 text-slate-400 text-sm">
              <Search className="w-4 h-4" />
              <span>Job Scraping</span>
              <span className="ml-auto bg-green-500 w-2 h-2 rounded-full"></span>
            </div>
            <div className="flex items-center space-x-3 px-4 py-2 text-slate-400 text-sm">
              <Brain className="w-4 h-4" />
              <span>AI Matching</span>
              <span className="ml-auto bg-green-500 w-2 h-2 rounded-full"></span>
            </div>
            <div className="flex items-center space-x-3 px-4 py-2 text-slate-400 text-sm">
              <Settings className="w-4 h-4" />
              <span>Resume Tailoring</span>
              <span className="ml-auto bg-green-500 w-2 h-2 rounded-full"></span>
            </div>
            <div className="flex items-center space-x-3 px-4 py-2 text-slate-400 text-sm">
              <Send className="w-4 h-4" />
              <span>Applications</span>
              <span className="ml-auto bg-green-500 w-2 h-2 rounded-full"></span>
            </div>
            <div className="flex items-center space-x-3 px-4 py-2 text-slate-400 text-sm">
              <LinkedinIcon className="w-4 h-4" />
              <span>LinkedIn Outreach</span>
              <span className="ml-auto bg-green-500 w-2 h-2 rounded-full"></span>
            </div>
            <div className="flex items-center space-x-3 px-4 py-2 text-slate-400 text-sm">
              <TrendingUp className="w-4 h-4" />
              <span>AI Learning</span>
              <span className="ml-auto bg-green-500 w-2 h-2 rounded-full"></span>
            </div>
          </div>
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700">
        <div className="text-xs text-slate-400 text-center">
          <div>Elite JobHunter X v2.0.0</div>
          <div className="mt-1">MASS SCALE AUTONOMOUS</div>
        </div>
      </div>
    </div>
  );
};

export default Navigation;