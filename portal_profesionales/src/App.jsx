import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

import Registro from './components/Registro';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (sessionStorage.getItem('access_token')) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (userData) => {
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route 
            path="/login" 
            element={!isAuthenticated ? <Login onLogin={handleLogin} /> : <Navigate to="/dashboard" />} 
          />
          <Route 
            path="/registro" 
            element={!isAuthenticated ? <Registro /> : <Navigate to="/dashboard" />} 
          />
          <Route 
            path="/dashboard/*" 
            element={isAuthenticated ? <Dashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
          />
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
