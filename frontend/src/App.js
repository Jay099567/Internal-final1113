import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Dashboard from "./components/Dashboard";
import CandidateOnboarding from "./components/CandidateOnboarding";
import CandidateProfile from "./components/CandidateProfile";
import TestAI from "./components/TestAI";
import JobScraping from "./components/JobScraping";
import JobsList from "./components/JobsList";
import JobMatching from "./components/JobMatching";
import ResumeTailoring from "./components/ResumeTailoring";
import CoverLetterManagement from "./components/CoverLetterManagement";
import Navigation from "./components/Navigation";

function App() {
  return (
    <div className="App min-h-screen bg-gray-50">
      <BrowserRouter>
        <div className="flex">
          <Navigation />
          <main className="flex-1 ml-64 p-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/candidates/new" element={<CandidateOnboarding />} />
              <Route path="/candidates/:id" element={<CandidateProfile />} />
              <Route path="/scraping" element={<JobScraping />} />
              <Route path="/jobs" element={<JobsList />} />
              <Route path="/matching" element={<JobMatching />} />
              <Route path="/resume-tailoring" element={<ResumeTailoring />} />
              <Route path="/test-ai" element={<TestAI />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </div>
  );
}

export default App;
