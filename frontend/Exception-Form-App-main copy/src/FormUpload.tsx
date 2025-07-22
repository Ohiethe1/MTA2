import React, { useState } from 'react';
import { useAuth } from './contexts/AuthContext';

const FormUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const { user } = useAuth ? useAuth() : { user: null };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    // Attach username if available
    if (user && user.id) {
      formData.append('username', user.id);
    } else if (localStorage.getItem('user')) {
      try {
        const parsed = JSON.parse(localStorage.getItem('user') || '{}');
        if (parsed.id) formData.append('username', parsed.id);
      } catch {}
    }

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResult(data.message || 'Upload successful!');
      // Automatically reload the page to update dashboard
      window.location.reload();
    } catch (error) {
      console.error('Upload error:', error);
      setResult('Upload failed.');
    }
  };

  return (
    <div className="flex items-start justify-center bg-gray-50 pt-10 pb-10 min-h-[40vh]">
      <div className="bg-white rounded-2xl shadow-2xl p-10 w-full max-w-lg flex flex-col items-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4" />
          </svg>
        </div>
        <h2 className="text-2xl font-extrabold text-gray-900 mb-2 text-center">Upload Exception Claim Form</h2>
        <p className="text-gray-500 text-center mb-6">Select a scanned form image (JPG, PNG, etc.) and submit to extract all details automatically.</p>
        <form onSubmit={handleSubmit} className="space-y-6 w-full flex flex-col items-center">
          <label className="w-full flex flex-col items-center px-4 py-6 bg-gray-100 text-blue-600 rounded-lg shadow-md tracking-wide uppercase border border-blue-200 cursor-pointer hover:bg-blue-50 transition mb-2">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M7 16V4a1 1 0 011-1h8a1 1 0 011 1v12m-4 4h-4a1 1 0 01-1-1v-4h6v4a1 1 0 01-1 1z" />
            </svg>
            <span className="mt-2 text-base leading-normal">Choose a file</span>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="hidden"
            />
            {file && <span className="mt-2 text-sm text-gray-700">Selected: {file.name}</span>}
          </label>
          <button
            type="submit"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors w-full"
          >
            Submit
          </button>
        </form>
        {result && <p className="mt-6 text-green-600 text-center font-medium">{result}</p>}
      </div>
    </div>
  );
};

export default FormUpload;
