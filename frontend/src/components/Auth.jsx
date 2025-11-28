import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { Mail, Moon, Sun } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Auth.css';

const Auth = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [darkMode, setDarkMode] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    // Redirect if already logged in
    if (user) {
      navigate('/kanban');
    }
  }, [user, navigate]);

  const handleEmailAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        setMessage('Check your email to confirm your account!');
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
      }
    } catch (error) {
      console.error('Auth error:', error);
      setMessage(error.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`auth-container ${darkMode ? 'dark-mode' : ''}`}>
      <button 
        onClick={() => setDarkMode(!darkMode)} 
        className="dark-mode-toggle"
        aria-label="Toggle dark mode"
      >
        {darkMode ? <Sun size={24} /> : <Moon size={24} />}
      </button>
      <div className="auth-card">
        {!showForm ? (
          <div className="welcome-screen">
            <h1 className="main-headline">Welcome to your organizer.</h1>
            <div className="cta-buttons">
              <button 
                onClick={() => { setShowForm(true); setIsSignUp(true); }} 
                className="btn-cta primary"
              >
                Sign Up
              </button>
              <button 
                onClick={() => { setShowForm(true); setIsSignUp(false); }} 
                className="btn-cta secondary"
              >
                Log In
              </button>
            </div>
          </div>
        ) : (
          <>
          <div className="form-section">
            <div className="auth-header">
              <h1>{isSignUp ? 'Create your account' : 'Welcome back'}</h1>
              <p>{isSignUp ? 'Start organizing your time' : 'Continue your productivity journey'}</p>
            </div>
            
            <form onSubmit={handleEmailAuth} className="auth-form">
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          
          <button type="submit" disabled={loading} className="auth-button primary">
            <Mail size={20} />
            <span>{loading ? 'Loading...' : isSignUp ? 'Sign Up' : 'Sign In'}</span>
          </button>

          {message && <p className="auth-message">{message}</p>}
          
          <p className="toggle-mode">
            {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button type="button" onClick={() => setIsSignUp(!isSignUp)} className="link-button">
              {isSignUp ? 'Sign In' : 'Sign Up'}
            </button>
          </p>
        </form>
          
        <button 
          type="button" 
          onClick={() => setShowForm(false)} 
          className="back-button"
        >
          ← Back
        </button>
      </div>
      </>
        )}
      </div>
    </div>
  );
};

export default Auth;
