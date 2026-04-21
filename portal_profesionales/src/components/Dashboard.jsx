import React, { useEffect, useState } from 'react';
import { LogOut, Plus, FileText, CheckCircle, Clock, XCircle, AlertCircle } from 'lucide-react';
import Perfil from './Perfil';
import NuevaSolicitud from './NuevaSolicitud';
import ErrorBoundary from './ErrorBoundary';

export default function Dashboard({ user, onLogout }) {
  const [perfilData, setPerfilData] = useState(null);
  const [solicitudes, setSolicitudes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showPerfil, setShowPerfil] = useState(false);
  const [showNuevaSolicitud, setShowNuevaSolicitud] = useState(false);

  useEffect(() => {
    const fetchInitialData = async () => {
      const token = sessionStorage.getItem('access_token');
      if (!token) {
        onLogout();
        return;
      }
      
      try {
        // Fetch Profile
        const perfilRes = await fetch('/api/perfil/', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (perfilRes.ok) {
          const pData = await perfilRes.json();
          setPerfilData(pData);
          
          // If the profile is HABILITADO, we can also try to fetch solicitudes
          if (pData.estado_nombre && pData.estado_nombre.toUpperCase() === 'HABILITADO') {
            try {
              const solRes = await fetch('/api/mis_solicitudes/', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              if (solRes.ok) {
                const solData = await solRes.json();
                setSolicitudes(solData.solicitudes || []);
              }
            } catch (e) {
              console.error("Error fetching solicitudes", e);
            }
          }
        } else if (perfilRes.status === 401) {
          sessionStorage.removeItem('access_token');
          onLogout();
        } else {
          setError('Error al obtener los datos del perfil.');
        }
      } catch (err) {
        setError('Error de conexión con el servidor.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchInitialData();
  }, [onLogout]);

  const getStatusBadge = (estado) => {
    switch (estado.toLowerCase()) {
      case 'enviada': return <span className="status-badge status-enviada"><Clock size={12} style={{display:'inline', marginRight:'4px'}}/> Enviada</span>;
      case 'aprobada': return <span className="status-badge status-aprobada"><CheckCircle size={12} style={{display:'inline', marginRight:'4px'}}/> Aprobada</span>;
      case 'rechazada': return <span className="status-badge status-rechazada"><XCircle size={12} style={{display:'inline', marginRight:'4px'}}/> Rechazada</span>;
      default: return <span className="status-badge">{estado}</span>;
    }
  };

  if (isLoading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'white' }}>Cargando datos del portal...</div>;
  }

  // If not HABILITADO, lock them to the Perfil component
  const isHabilitado = perfilData && perfilData.estado_nombre && perfilData.estado_nombre.toUpperCase() === 'HABILITADO';
  if (!isHabilitado || showPerfil) {
    return (
      <Perfil 
        perfilData={perfilData} 
        onLogout={onLogout} 
        onBack={isHabilitado ? () => setShowPerfil(false) : null} 
        onProfileUpdated={(updatedData) => setPerfilData(updatedData)} 
      />
    );
  }

  if (showNuevaSolicitud) {
    return (
      <ErrorBoundary onBack={() => setShowNuevaSolicitud(false)}>
        <NuevaSolicitud 
          token={sessionStorage.getItem('access_token')} 
          onBack={() => setShowNuevaSolicitud(false)} 
        />
      </ErrorBoundary>
    );
  }

  return (
    <div className="animate-fade-in">
      <header className="header">
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Mis Solicitudes</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>
            Bienvenido, <a href="#" onClick={(e) => { e.preventDefault(); setShowPerfil(true); }} style={{color: '#60a5fa', textDecoration: 'none', fontWeight: 500, borderBottom: '1px dashed #60a5fa'}} title="Hacer clic para editar perfil y contraseña">{perfilData?.nombre} {perfilData?.apellido}</a> ({perfilData?.profesion_nombre || 'Profesional'})
          </p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn-primary" style={{ background: 'var(--glass-bg)', border: '1px solid var(--glass-border)' }} onClick={() => {
            sessionStorage.removeItem('access_token');
            onLogout();
          }}>
            Salir <LogOut size={18} />
          </button>
          <button className="btn-primary" onClick={() => setShowNuevaSolicitud(true)}>
            Nueva Solicitud <Plus size={18} />
          </button>
        </div>
      </header>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#fca5a5', padding: '15px', borderRadius: '8px', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <AlertCircle size={20} /> {error}
        </div>
      )}

      <div className="glass-panel" style={{ padding: '2rem' }}>
        {solicitudes.length === 0 && !error ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
            <FileText size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
            <p>No tienes solicitudes registradas en el sistema aún.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
            {solicitudes.map(sol => (
              <div key={sol.id} style={{ 
                background: 'rgba(15, 23, 42, 0.4)', 
                border: '1px solid var(--glass-border)', 
                borderRadius: '12px', 
                padding: '1.5rem',
                transition: 'transform 0.2s',
                cursor: 'pointer'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText size={20} color="var(--accent-primary)" />
                    <span style={{ fontWeight: 600 }}>{sol.numero_expediente ? `EXP: ${sol.numero_expediente}` : `Solicitud #${sol.id}`}</span>
                  </div>
                  {getStatusBadge(sol.estado)}
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Padrón:</span>
                    <span style={{ fontWeight: 500, color: 'white' }}>Nº {sol.padron}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Trámite:</span>
                    <span style={{ textAlign: 'right' }}>{sol.tramite}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Fecha:</span>
                    <span style={{ fontSize: '0.8rem' }}>{sol.fecha}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
