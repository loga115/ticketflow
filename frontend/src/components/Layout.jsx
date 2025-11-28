import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LayoutDashboard, LogOut, Moon, Sun, ChevronLeft, ChevronRight, Users, Ticket } from 'lucide-react';
import { useState, useEffect } from 'react';
import NotificationTray from './NotificationTray';
import './Layout.css';

const Layout = ({ children }) => {
  const { user, signOut } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showLanding, setShowLanding] = useState(true);
  const [landingFadeOut, setLandingFadeOut] = useState(false);

  const navigation = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, description: 'Ticket management overview' },
    { name: 'Employees', path: '/employees', icon: Users, description: 'Manage your team' },
  ];

  useEffect(() => {
    // Show landing only on root path or when no specific feature is selected
    setShowLanding(location.pathname === '/' || location.pathname === '/dashboard');
    setLandingFadeOut(false);
  }, [location.pathname]);

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const handleFeatureSelect = (path) => {
    setLandingFadeOut(true);
    setTimeout(() => {
      setShowLanding(false);
      navigate(path);
    }, 500); // Match fadeOut animation duration
  };

  return (
    <div className={`layout ${darkMode ? 'dark-mode' : ''}`}>
      <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <Link to="/dashboard" className="logo-link" onClick={() => setShowLanding(true)}>
            <Ticket size={32} />
            {!sidebarCollapsed && <h1>TicketFlow</h1>}
          </Link>
          <div className="header-actions">
            <NotificationTray />
            <button 
              onClick={() => setDarkMode(!darkMode)} 
              className="dark-mode-toggle-header"
              aria-label="Toggle dark mode"
              title={darkMode ? 'Light mode' : 'Dark mode'}
            >
              {darkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          </div>
        </div>

        <button 
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="sidebar-toggle"
          aria-label="Toggle sidebar"
        >
          {sidebarCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>

        <nav className="sidebar-nav">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
                title={sidebarCollapsed ? item.name : ''}
                onClick={() => setShowLanding(false)}
              >
                <Icon size={20} />
                {!sidebarCollapsed && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">
              {user?.email?.[0]?.toUpperCase() || 'U'}
            </div>
            {!sidebarCollapsed && (
              <div className="user-details">
                <div className="user-name">{user?.email?.split('@')[0]}</div>
                <div className="user-email">{user?.email}</div>
              </div>
            )}
          </div>
          <button onClick={handleSignOut} className="btn-signout" title="Sign out">
            <LogOut size={20} />
          </button>
        </div>
      </aside>

      <main className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        {showLanding && location.pathname === '/kanban' ? (
          <div className={`landing-page ${landingFadeOut ? 'fade-out' : ''}`}>
            <h1 className="landing-title">What would you like to do today?</h1>
            <div className="feature-cards">
              {navigation.map((item, index) => {
                const Icon = item.icon;
                return (
                  <div
                    key={item.path}
                    className="feature-card"
                    onClick={() => handleFeatureSelect(item.path)}
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className="feature-icon">
                      <Icon size={48} />
                    </div>
                    <h2>{item.name}</h2>
                    <p>{item.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="content-wrapper">
            {children}
          </div>
        )}
      </main>
    </div>
  );
};

export default Layout;
