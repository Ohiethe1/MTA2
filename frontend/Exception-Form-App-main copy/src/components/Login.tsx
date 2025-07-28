import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import mtaLogo from "../assets/mta-logo.png";

const Login = () => {
  const [bscId, setBscId] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Mock authentication - simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));

    try {
      const response = await fetch('http://localhost:8000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: bscId, password }),
      });
      const data = await response.json();
      if (response.ok) {
        login(data.token, data.user);
        navigate('/');
      } else {
        setError(data.error || 'Login failed.');
      }
    } catch (err) {
      setError('Network or server error.');
    }
    setIsLoading(false);
  };

  // Only allow numbers in BSC ID field
  const handleBscIdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/[^0-9]/g, '');
    setBscId(value);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-[#232328] text-white w-full">
        <div className="flex items-center justify-center py-3 px-10">
          <img src={mtaLogo} alt="MTA Logo" className="w-12 h-12 rounded-full bg-white object-contain p-1 mr-4" />
          <span className="text-xl font-extrabold tracking-normal font-[Montserrat,sans-serif]">MTA Form Processor</span>
        </div>
      </header>
      <div className="flex flex-col justify-center min-h-screen py-12 bg-gray-50 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="text-center">
            <h2 className="mb-2 text-2xl font-bold text-gray-900">
              MTA Overtime Forms Processor
            </h2>
            <p className="text-gray-600">
              Sign in to access the overtime forms system
            </p>
          </div>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="px-4 py-8 bg-white shadow sm:rounded-lg sm:px-10">
            <form className="space-y-6" onSubmit={handleSubmit}>
              <div>
                <label htmlFor="bscId" className="block text-sm font-medium text-gray-700">
                  BSC ID
                </label>
                <div className="mt-1">
                  <input
                    id="bscId"
                    name="bscId"
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    required
                    value={bscId}
                    onChange={handleBscIdChange}
                    className="block w-full px-3 py-2 placeholder-gray-400 border border-gray-300 rounded-md shadow-sm appearance-none focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="Enter your BSC ID"
                    autoComplete="username"
                    maxLength={16}
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <div className="mt-1">
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="block w-full px-3 py-2 placeholder-gray-400 border border-gray-300 rounded-md shadow-sm appearance-none focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="Enter your password"
                  />
                </div>
              </div>

              {error && (
                <div className="p-4 border border-red-200 rounded-md bg-red-50">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="w-5 h-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-red-800">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex justify-center w-full px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <div className="flex items-center">
                      <div className="w-4 h-4 mr-2 border-b-2 border-white rounded-full animate-spin"></div>
                      Signing in...
                    </div>
                  ) : (
                    'Sign in'
                  )}
                </button>
              </div>
            </form>

            {/* Registration link */}
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Don't have an account?{' '}
                <Link to="/register" className="font-medium text-blue-600 hover:text-blue-500">
                  Sign Up Here
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login; 