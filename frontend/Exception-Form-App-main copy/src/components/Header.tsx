import { NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import mtaLogo from '../assets/mta-logo.png';
import { useState, useRef } from 'react';

const Header = () => {
  const { user, logout } = useAuth();
  const [uploadDropdownOpen, setUploadDropdownOpen] = useState(false);
  const [dashboardDropdownOpen, setDashboardDropdownOpen] = useState(false);
  const closeUploadTimeout = useRef<number | null>(null);
  const closeDashboardTimeout = useRef<number | null>(null);

  const handleLogout = () => {
    logout();
  };

  // Upload Form Dropdown handlers
  const handleUploadDropdownEnter = () => {
    if (closeUploadTimeout.current) window.clearTimeout(closeUploadTimeout.current);
    setUploadDropdownOpen(true);
  };
  const handleUploadDropdownLeave = () => {
    closeUploadTimeout.current = window.setTimeout(() => setUploadDropdownOpen(false), 200);
  };

  // Dashboard Dropdown handlers
  const handleDashboardDropdownEnter = () => {
    if (closeDashboardTimeout.current) window.clearTimeout(closeDashboardTimeout.current);
    setDashboardDropdownOpen(true);
  };
  const handleDashboardDropdownLeave = () => {
    closeDashboardTimeout.current = window.setTimeout(() => setDashboardDropdownOpen(false), 200);
  };

  return (
    <header className="bg-[#232328] text-white w-full">
      <div className="flex items-center justify-between py-3 px-10">
        <div className="flex items-center space-x-6">
          <img src={mtaLogo} alt="MTA Logo" className="w-12 h-12 rounded-full bg-white object-contain p-1" />
        </div>
        <nav className="flex items-center space-x-12">
          {/* Upload Form Dropdown */}
          <div
            className="relative"
            tabIndex={0}
            onMouseEnter={handleUploadDropdownEnter}
            onMouseLeave={handleUploadDropdownLeave}
            onFocus={handleUploadDropdownEnter}
            onBlur={handleUploadDropdownLeave}
          >
            <div className="flex items-center cursor-pointer font-bold text-lg transition-colors duration-200 hover:text-yellow-400 focus:text-yellow-400">
              <NavLink to="/" className={({ isActive }) => `${isActive ? 'underline underline-offset-8 decoration-yellow-400' : ''}`}>Upload Form</NavLink>
              <svg className={`ml-2 w-4 h-4 text-yellow-400 transition-transform duration-200 ${uploadDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
            </div>
            <div
              className={`absolute left-0 mt-2 w-56 bg-white text-black rounded-xl shadow-xl transition-all z-20 py-2 ${uploadDropdownOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
              style={{ minWidth: '180px' }}
            >
              <NavLink to="/upload/hourly" className={({ isActive }) => `block px-6 py-3 font-medium text-sm transition-colors duration-200 rounded-lg ${isActive ? 'text-yellow-400 underline underline-offset-8 decoration-yellow-400 bg-gray-50' : 'text-[#232328]'} hover:text-yellow-400 hover:underline hover:underline-offset-8 hover:decoration-yellow-400 hover:bg-gray-100`}>Hourly Employees</NavLink>
              <NavLink to="/upload/supervisor" className={({ isActive }) => `block px-6 py-3 font-medium text-sm transition-colors duration-200 rounded-lg ${isActive ? 'text-yellow-400 underline underline-offset-8 decoration-yellow-400 bg-gray-50' : 'text-[#232328]'} hover:text-yellow-400 hover:underline hover:underline-offset-8 hover:decoration-yellow-400 hover:bg-gray-100`}>Supervisors</NavLink>
            </div>
          </div>
          {/* Dashboard Dropdown */}
          <div
            className="relative"
            tabIndex={0}
            onMouseEnter={handleDashboardDropdownEnter}
            onMouseLeave={handleDashboardDropdownLeave}
            onFocus={handleDashboardDropdownEnter}
            onBlur={handleDashboardDropdownLeave}
          >
            <div className="flex items-center cursor-pointer font-bold text-lg transition-colors duration-200 hover:text-yellow-400 focus:text-yellow-400">
              <NavLink to="/dashboard" className={({ isActive }) => `${isActive ? 'underline underline-offset-8 decoration-yellow-400' : ''}`}>Dashboard</NavLink>
              <svg className={`ml-2 w-4 h-4 text-yellow-400 transition-transform duration-200 ${dashboardDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
            </div>
            <div
              className={`absolute left-0 mt-2 w-56 bg-white text-black rounded-xl shadow-xl transition-all z-20 py-2 ${dashboardDropdownOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
              style={{ minWidth: '180px' }}
            >
              <NavLink to="/dashboard/hourly" className={({ isActive }) => `block px-6 py-3 font-medium text-sm transition-colors duration-200 rounded-lg ${isActive ? 'text-yellow-400 underline underline-offset-8 decoration-yellow-400 bg-gray-50' : 'text-[#232328]'} hover:text-yellow-400 hover:underline hover:underline-offset-8 hover:decoration-yellow-400 hover:bg-gray-100`}>Hourly Employees</NavLink>
              <NavLink to="/dashboard/supervisor" className={({ isActive }) => `block px-6 py-3 font-medium text-sm transition-colors duration-200 rounded-lg ${isActive ? 'text-yellow-400 underline underline-offset-8 decoration-yellow-400 bg-gray-50' : 'text-[#232328]'} hover:text-yellow-400 hover:underline hover:underline-offset-8 hover:decoration-yellow-400 hover:bg-gray-100`}>Supervisors</NavLink>
            </div>
          </div>
          <NavLink to="/audit-trail" className={({ isActive }) => `font-bold text-lg transition-colors duration-200 hover:text-yellow-400 ${isActive ? 'underline underline-offset-8 decoration-yellow-400' : ''}`}>Audit Trail</NavLink>
        </nav>
        <div className="flex items-center space-x-6">
          <span className="font-bold text-base">Welcome, MTA Admin</span>
          <button onClick={handleLogout} className="border border-white text-white px-5 py-2 rounded-lg font-bold hover:bg-white hover:text-[#232328] transition">Logout</button>
        </div>
      </div>
    </header>
  );
};

export default Header; 