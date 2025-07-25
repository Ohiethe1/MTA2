import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const HourlyFormUpload = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [result, setResult] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!files.length) {
      alert('Please select at least one file');
      return;
    }
    setIsProcessing(true);
    setResult('Uploading...');
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    try {
      const response = await fetch('http://localhost:8000/upload/hourly', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setResult(`Upload complete: ${data.success || 0} succeeded, ${data.failed || 0} failed.`);
        setTimeout(() => {
          navigate('/dashboard/hourly');
        }, 1500);
      } else {
        setResult(data.error || 'Upload failed.');
      }
    } catch {
      setResult('Upload failed.');
    }
    setIsProcessing(false);
  };

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-lg mt-10">
      <h2 className="text-3xl font-extrabold text-gray-900 mb-2 text-center">Upload Exception Claim Form (Hourly Employees)</h2>
      <p className="text-gray-500 text-center mb-8">Upload your form file for hourly employees. Our AI will extract all the details automatically.</p>
      <form onSubmit={handleSubmit} className="space-y-6">
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
            multiple
            onChange={e => setFiles(Array.from(e.target.files || []))} 
            accept=".pdf,.jpg,.jpeg,.png"
            className="mt-2" 
          />
          {files.length > 0 && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <span className="text-sm text-blue-700">Selected: {files.map(f => f.name).join(', ')}</span>
            </div>
          )}
        </div>
        <div className="flex justify-center">
          <button
            type="submit"
            disabled={!files.length || isProcessing}
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
        {result && (
          <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
            <p className="text-green-800">{result}</p>
          </div>
        )}
      </form>
    </div>
  );
};

export default HourlyFormUpload; 