import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import mtaLogo from '../assets/mta-logo.png';

function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    // Validate passwords match
    if (password !== confirmPassword) {
      setMessage('❌ Passwords do not match');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage('✅ ' + data.message);
        // Redirect to login page after successful registration
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else {
        setMessage('❌ ' + data.error);
      }
    } catch (err) {
      console.error('Registration request failed:', err);
      setMessage('❌ Network or server error.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-[#232328] text-white">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-3">
            <img src={mtaLogo} alt="MTA Logo" className="w-12 h-12 rounded-full bg-white object-contain p-1" />
            <span className="text-lg font-semibold">MTA Form Processor</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-md mx-auto mt-16">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">MTA Overtime Forms Processor</h1>
          <p className="text-sm text-gray-600">Create your account to access the overtime forms system</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-xs font-medium text-gray-700 mb-2">
                BSC ID
              </label>
              <input
                id="username"
                type="text"
                placeholder="Enter your BSC ID"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                required
                minLength={3}
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-xs font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                required
                minLength={6}
              />
            </div>
            
            <div>
              <label htmlFor="confirmPassword" className="block text-xs font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                required
                minLength={6}
              />
            </div>
            
            <button 
              type="submit" 
              className="w-full bg-blue-600 text-white p-3 rounded-md font-semibold hover:bg-blue-700 disabled:bg-gray-400 transition-colors text-sm"
              disabled={isLoading}
            >
              {isLoading ? 'Creating Account...' : 'Sign Up'}
            </button>
          </form>
          
          {message && (
            <div className={`mt-4 p-3 rounded-md text-center text-sm ${
              message.includes('✅') ? 'bg-green-100 text-green-700 border border-green-200' : 'bg-red-100 text-red-700 border border-red-200'
            }`}>
              {message}
            </div>
          )}
          
          <div className="mt-6 text-center">
            <p className="text-xs text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-800 font-medium">
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register; 