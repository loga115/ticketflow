import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import Auth from './components/Auth';
import Layout from './components/Layout';
import PageTransition from './components/PageTransition';
import AdminDashboard from './components/AdminDashboard';
import EmployeeManager from './components/EmployeeManager';
import './App.css';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return user ? children : <Navigate to="/auth" />;
};

const App = () => {
  return (
    <AuthProvider>
      <NotificationProvider>
        <Router>
          <Routes>
            <Route path="/auth" element={<Auth />} />
            <Route
              path="/*"
              element={
                <PrivateRoute>
                  <Layout>
                    <PageTransition>
                      <Routes>
                        <Route path="/" element={<Navigate to="/dashboard" />} />
                        <Route path="/dashboard" element={<AdminDashboard />} />
                        <Route path="/employees" element={<EmployeeManager />} />
                      </Routes>
                    </PageTransition>
                  </Layout>
                </PrivateRoute>
              }
            />
          </Routes>
        </Router>
      </NotificationProvider>
    </AuthProvider>
  );
};

export default App;
