import React, { useState } from 'react';
import { LogIn, FileWarning } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg('');
    
    try {
      const response = await fetch('/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Guardamos los tokens seguros en sessionStorage (se borran al cerrar pestaña)
        sessionStorage.setItem('access_token', data.access);
        sessionStorage.setItem('refresh_token', data.refresh);
        onLogin();
      } else {
        let msg = data.detail || 'Credenciales inválidas. Verifica tus datos.';
        // Reemplazamos el mensaje genérico en inglés de DRF
        if (msg === 'No active account found with the given credentials') {
          msg = 'Credenciales inválidas. Verifica tus datos.';
        }
        setErrorMsg(msg);
      }
    } catch (err) {
      setErrorMsg('No se pudo contactar con el servidor. Verifica que el backend esté encendido.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
      <div className="glass-panel animate-fade-in" style={{ padding: '3rem', width: '100%', maxWidth: '420px' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ display: 'inline-flex', padding: '12px', background: 'rgba(59, 130, 246, 0.2)', borderRadius: '16px', marginBottom: '1rem' }}>
            <FileWarning size={32} color="#3b82f6" />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Portal de Profesionales</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Ingreso al sistema de expedientes</p>
        </div>

        {errorMsg && (
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#fca5a5', padding: '10px', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.9rem', textAlign: 'center' }}>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              DNI/CI
            </label>
            <input 
              type="text" 
              className="input-field" 
              placeholder="Ej: 12345678" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Contraseña
            </label>
            <input 
              type="password" 
              className="input-field" 
              placeholder="••••••••" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button 
            type="submit" 
            className="btn-primary" 
            style={{ width: '100%', marginTop: '0.5rem', padding: '12px' }}
            disabled={isLoading}
          >
            {isLoading ? 'Autenticando...' : (
              <>
                Ingresar al Portal <LogIn size={18} />
              </>
            )}
          </button>
        </form>

        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            ¿No tienes cuenta? <Link to="/registro" style={{ color: '#3b82f6', textDecoration: 'none', fontWeight: 500 }}>Regístrate aquí como Profesional</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
