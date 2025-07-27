import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import FormUpload from './FormUpload';
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import AuditTrail from './components/AuditTrail';
import HourlyFormUpload from './components/HourlyFormUpload';
import SupervisorFormUpload from './components/SupervisorFormUpload';
import HourlyDashboard from './components/HourlyDashboard';
import SupervisorDashboard from './components/SupervisorDashboard';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex flex-col items-center justify-center">
                <Header />
                <main className="flex flex-1 items-start justify-center w-full min-h-[80vh]">
                  <div className="bg-white rounded-3xl shadow-2xl px-10 py-14 flex flex-col items-center max-w-xl w-full mt-20">
                    <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                      <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 16v-8m0 8l-4-4m4 4l4-4" /></svg>
                    </div>
                    <h1 className="text-4xl font-extrabold mb-2 text-center text-gray-900">Upload Overtime Forms</h1>
                    <p className="text-lg text-gray-500 mb-10 text-center">Select the type of form you want to upload.</p>
                    {/* Black + Gray (Modern Neutral) */}
                    <div className="flex flex-col md:flex-row gap-8 w-full justify-center items-center mb-8">
                      <Link to="/upload/hourly" className="flex-1 bg-black text-white px-6 py-4 rounded-lg font-semibold text-base shadow border border-black hover:bg-gray-900 active:bg-gray-800 transition-colors text-center focus:outline-none focus:ring-2 focus:ring-gray-400">Upload Hourly Employee Form</Link>
                      <div className="mx-0 md:mx-4 flex flex-col items-center justify-center">
                        <span className="text-gray-400 font-semibold text-lg md:text-xl">or</span>
                      </div>
                      <Link to="/upload/supervisor" className="flex-1 bg-gray-200 text-gray-900 px-6 py-4 rounded-lg font-semibold text-base shadow border border-gray-300 hover:bg-gray-300 active:bg-gray-400 transition-colors text-center focus:outline-none focus:ring-2 focus:ring-gray-300">Upload Supervisor Form</Link>
                    </div>
                    {/* Blue + Gray (Neutral, App-like) */}
                    {/*
                    <div className="flex flex-col md:flex-row gap-8 w-full justify-center">
                      <Link to="/upload/hourly" className="flex-1 bg-blue-600 text-white px-6 py-4 rounded-lg font-semibold text-lg shadow border border-blue-700 hover:bg-blue-700 active:bg-blue-800 transition-colors text-center focus:outline-none focus:ring-2 focus:ring-blue-200">Upload Hourly Employee Form</Link>
                      <Link to="/upload/supervisor" className="flex-1 bg-gray-200 text-gray-900 px-6 py-4 rounded-lg font-semibold text-lg shadow border border-gray-300 hover:bg-gray-300 active:bg-gray-400 transition-colors text-center focus:outline-none focus:ring-2 focus:ring-gray-300">Upload Supervisor Form</Link>
                    </div>
                    */}
                  </div>
                </main>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gray-50">
                <Header />
                <main className="container mx-auto px-4 py-8">
                  <Dashboard heading="General Dashboard (BETA)" />
                </main>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/dashboard/hourly" element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gray-50">
                <Header />
                <main className="container mx-auto px-4 py-8">
                  <HourlyDashboard />
                </main>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/dashboard/supervisor" element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gray-50">
                <Header />
                <main className="container mx-auto px-4 py-8">
                  <SupervisorDashboard />
                </main>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/audit-trail" element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gray-50">
                <Header />
                <main className="container mx-auto px-4 py-8">
                  <AuditTrail />
                </main>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/upload/hourly" element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gray-50">
                <Header />
                <main className="container mx-auto px-4 py-8">
                  <HourlyFormUpload />
                </main>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/upload/supervisor" element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gray-50">
                <Header />
                <main className="container mx-auto px-4 py-8">
                  <SupervisorFormUpload />
                </main>
              </div>
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

