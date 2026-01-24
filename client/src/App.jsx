import React, { useState } from 'react';
import { Upload, FileText, Briefcase, Sparkles,  Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const App = () => {
  const [jobDescription, setJobDescription] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const [enhancedMarkdown, setEnhancedMarkdown] = useState('');
  const [activeTab, setActiveTab] = useState('resume');

  const server_url = import.meta.env.VITE_SERVER_URL;
  // const server_url = 'http://127.0.0.1:8000';

  const handleSubmit = async () => {
    if (!resumeFile || !jobDescription) {
      alert("Please provide both a resume and a job description.");
      return;
    }

    setLoading(true);
    const formdata = new FormData();
    formdata.append('resume', resumeFile);
    formdata.append('job_description', jobDescription);
  
    try {
      const res = await axios.post(`${server_url}/upload`, formdata,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }

      );
      if(res.data.response == 'None' || !res.data.response){
        alert("Failed to enhance resume. Please try again ....");
        setLoading(false);
        return;
      }
      
      setEnhancedMarkdown(res.data.response); 
      setActiveTab('resume');
    } catch (err) {
      console.error("Analysis failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      {/* --- Header --- */}
      <nav className="flex items-center justify-between px-8 py-4 bg-white border-b border-slate-200 sticky top-0 z-20">
        <div className="flex items-center space-x-2">
          <div className="bg-blue-600 p-2 rounded-lg text-white"><Sparkles size={20} /></div>
          <span className="text-xl font-bold text-slate-800">ResuMatch AI</span>
        </div>
      </nav>

      <main className="max-w-[1600px] mx-auto p-6 grid lg:grid-cols-12 gap-8">
        
        {/* --- Left Side: Inputs --- */}
        <div className="lg:col-span-5 space-y-6">
          <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold">
              <Briefcase size={18} className="text-blue-500" /> Job Description
            </div>
            <textarea 
              className="w-full h-64 p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition text-sm leading-relaxed"
              placeholder="Paste the target JD here..."
              onChange={(e) => setJobDescription(e.target.value)}
            />
          </section>

          <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 text-center">
            <div className="border-2 border-dashed border-slate-200 rounded-xl p-8 bg-slate-50 hover:bg-blue-50/50 transition relative">
              <Upload className="mx-auto text-blue-500 mb-3" size={32} />
              <p className="text-sm font-medium">{resumeFile ? resumeFile.name : "Upload current resume"}</p>
              <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={(e) => setResumeFile(e.target.files[0])} />
            </div>
            <button 
              onClick={handleSubmit}
              disabled={loading}
              className="w-full mt-6 py-4 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 disabled:bg-slate-300 transition shadow-lg shadow-blue-200 flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Sparkles size={18} />}
              {loading ? "Analyzing..." : "Enhance My Resume"}
            </button>
          </section>
        </div>

        {/* --- Right Side: Results Box --- */}
<div className="lg:col-span-7 space-y-6">
  {enhancedMarkdown && (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
      <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
        <FileText size={20} className="text-blue-600" /> Enhanced Resume
      </h2>
      <div className="prose prose-slate max-w-none">
        <ReactMarkdown>{enhancedMarkdown}</ReactMarkdown>
      </div>
    </div>
  )}

  
</div>
      </main>
    </div>
  );
};

export default App;