import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const FormUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file first');
      return;
    }
    
    setIsProcessing(true);
    setResult('Processing form with AI...');
    
    // Simulate AI processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Generate random job data for testing
    const jobPositions = ['Bus Operator', 'Train Conductor', 'Station Agent', 'Maintenance Worker', 'Supervisor'];
    const randomJobPosition = jobPositions[Math.floor(Math.random() * jobPositions.length)];
    const randomJobNumber = `TA-2024-${String(Math.floor(Math.random() * 999) + 1).padStart(3, '0')}`;
    
    // Simulate extracted form data with all Exception Claim Form fields
    const extractedData = {
      passNumber: String(Math.floor(Math.random() * 99999999) + 10000000),
      title: randomJobPosition,
      employeeName: `Employee ${Math.floor(Math.random() * 100) + 1}`,
      rdos: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][Math.floor(Math.random() * 5)],
      actualOTDate: '2024-01-15',
      div: `D${String(Math.floor(Math.random() * 99) + 1).padStart(2, '0')}`,
      exceptionCode: `EXC-${String(Math.floor(Math.random() * 999) + 1).padStart(3, '0')}`,
      location: ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'][Math.floor(Math.random() * 5)],
      runNo: `R${String(Math.floor(Math.random() * 99) + 1).padStart(3, '0')}`,
      exceptionTimeFromHH: String(Math.floor(Math.random() * 12) + 8),
      exceptionTimeFromMM: String(Math.floor(Math.random() * 60)),
      exceptionTimeToHH: String(Math.floor(Math.random() * 12) + 16),
      exceptionTimeToMM: String(Math.floor(Math.random() * 60)),
      overtimeHH: String(Math.floor(Math.random() * 4) + 1),
      overtimeMM: String(Math.floor(Math.random() * 60)),
      bonusHH: String(Math.floor(Math.random() * 2)),
      bonusMM: String(Math.floor(Math.random() * 60)),
      niteDiffHH: String(Math.floor(Math.random() * 2)),
      niteDiffMM: String(Math.floor(Math.random() * 60)),
      taJobNo: randomJobNumber,
      oto: Math.random() > 0.5 ? 'Yes' : 'No',
      otoAmountSaved: `$${Math.floor(Math.random() * 200) + 50}.00`,
      enteredInUTS: Math.random() > 0.3 ? 'Yes' : 'No',
      comments: 'Emergency overtime due to weather conditions. Route was extended due to road closures.',
      supervisorName: `Supervisor ${Math.floor(Math.random() * 100) + 1}`,
      supervisorPassNo: String(Math.floor(Math.random() * 99999999) + 10000000)
    };
    
    // Save complete form data to localStorage
    const formData = {
      id: Date.now().toString(),
      fileName: file.name,
      uploadDate: new Date().toISOString(),
      status: 'processed',
      ...extractedData
    };
    
    const existingData = JSON.parse(localStorage.getItem('mtaForms') || '[]');
    existingData.push(formData);
    localStorage.setItem('mtaForms', JSON.stringify(existingData));
    
    setResult('Form processed successfully! All details extracted.');
    setIsProcessing(false);
    
    setTimeout(() => {
      navigate('/dashboard');
    }, 1500);
  };

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-lg mt-10">
      <h2 className="text-3xl font-extrabold text-gray-900 mb-2 text-center">Upload Exception Claim Form</h2>
      <p className="text-gray-500 text-center mb-8">Upload your form file and our AI will extract all the details automatically.</p>
      
      <form onSubmit={handleSubmit} className="space-y-6">
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

        {/* Result Message */}
        {result && (
          <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
            <p className="text-green-800">{result}</p>
          </div>
        )}
      </form>
    </div>
  );
};

export default FormUpload; 