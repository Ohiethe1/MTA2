import { NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import mtaLogo from '../assets/mta-logo.png';

const Header = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="bg-[#232328] text-white w-full">
      <div className="flex items-center justify-between py-3 px-10">
        <div className="flex items-center space-x-6">
          <img src={mtaLogo} alt="MTA Logo" className="w-12 h-12 rounded-full bg-white object-contain p-1" />
        </div>
        <nav className="flex items-center space-x-12">
          <NavLink to="/" className={({ isActive }) => `font-bold text-lg transition-colors duration-200 hover:text-yellow-400 ${isActive ? 'underline underline-offset-8 decoration-yellow-400' : ''}`}>Upload Form</NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => `font-bold text-lg transition-colors duration-200 hover:text-yellow-400 ${isActive ? 'underline underline-offset-8 decoration-yellow-400' : ''}`}>Dashboard</NavLink>
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