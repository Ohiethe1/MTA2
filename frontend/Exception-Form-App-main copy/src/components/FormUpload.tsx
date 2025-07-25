import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const FormUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [formType, setFormType] = useState<'hourly' | 'supervisor'>('hourly');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploadError(null);
    setUploadSuccess(null);
    if (!file) {
      alert('Please select a file first');
      return;
    }
    setIsProcessing(true);
    setResult('Uploading file to server...');
    try {
      const formData = new FormData();
      formData.append('file', file);
      // Optionally, add username if you have auth context
      // formData.append('username', user?.id || 'unknown');
      const response = await fetch(`http://localhost:8000/upload/${formType}`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setUploadSuccess(data.message || 'Upload successful!');
        setResult(null);
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } else {
        setUploadError(data.error || 'Upload failed.');
        setResult(null);
      }
    } catch (err: any) {
      setUploadError('Network or server error.');
      setResult(null);
    }
    setIsProcessing(false);
  };

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-lg mt-10">
      <h2 className="text-3xl font-extrabold text-gray-900 mb-2 text-center">Upload Overtime Forms</h2>
      <p className="text-gray-500 text-center mb-8">Upload your form file and our AI will extract all the details automatically.</p>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Form Type Selection */}
        <div className="flex justify-center gap-4 mb-2">
          <label>
            <input
              type="radio"
              name="formType"
              value="hourly"
              checked={formType === 'hourly'}
              onChange={() => setFormType('hourly')}
              className="mr-1"
            />
            Hourly
          </label>
          <label>
            <input
              type="radio"
              name="formType"
              value="supervisor"
              checked={formType === 'supervisor'}
              onChange={() => setFormType('supervisor')}
              className="mr-1"
            />
            Supervisor
          </label>
        </div>
        {/* File Upload Section */}
        <div className="flex flex-col items-center justify-center gap-4 border-2 border-dashed border-gray-300 rounded-lg p-8 bg-gray-50 hover:border-blue-400 transition-colors">
          <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <label className="font-semibold text-gray-700 text-lg">Upload Form File</label>
          <p className="text-sm text-gray-500">Supported formats: PDF, JPG, PNG</p>
          <input 
            type="file" 
            onChange={e => setFile(e.target.files?.[0] || null)} 
            accept=".pdf,.jpg,.jpeg,.png"
            className="mt-2" 
          />
          {file && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <span className="text-sm text-blue-700">Selected: {file.name}</span>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-center">
          <button
            type="submit"
            disabled={!file || isProcessing}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isProcessing ? (
              <div className="flex items-center">
                <div className="w-4 h-4 mr-2 border-b-2 border-white rounded-full animate-spin"></div>
                Processing...
              </div>
            ) : (
              'Upload & Process Form'
            )}
          </button>
        </div>

        {/* Result/Error Message */}
        {result && (
          <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-blue-800">{result}</p>
          </div>
        )}
        {uploadSuccess && (
          <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
            <p className="text-green-800">{uploadSuccess}</p>
          </div>
        )}
        {uploadError && (
          <div className="text-center p-4 bg-red-50 rounded-lg border border-red-200">
            <p className="text-red-800">{uploadError}</p>
          </div>
        )}
      </form>
    </div>
  );
};

export default FormUpload; 