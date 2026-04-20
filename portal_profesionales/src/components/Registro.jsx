import React, { useState } from 'react';
import { UserPlus, ArrowLeft, Upload } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

export default function Registro() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    dni: '',
    nombre: '',
    apellido: '',
    email: '',
    matricula: '',
    profesion_id: '',
    telefono: '',
    direccion: '',
    razon_social: ''
  });
  
  const [archivos, setArchivos] = useState({
    foto_dni_frente: null,
    foto_dni_reverso: null
  });

  const [aceptaTerminos, setAceptaTerminos] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [terminosContent, setTerminosContent] = useState('Cargando términos y condiciones...');
  const [profesiones, setProfesiones] = useState([]);

  const [isLoading, setIsLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});

  React.useEffect(() => {
    // Fetch Términos
    fetch('http://localhost:8000/api/configuracion-portal/')
      .then(res => res.json())
      .then(data => {
        if (data.terminos_y_condiciones) {
          setTerminosContent(data.terminos_y_condiciones);
        } else {
          setTerminosContent('No se han configurado los términos y condiciones.');
        }
      })
      .catch(err => {
        setTerminosContent('Error al cargar los términos y condiciones. Por favor, intente nuevamente más tarde.');
      });

    // Fetch Profesiones
    fetch('http://localhost:8000/api/profesiones/')
      .then(res => res.json())
      .then(data => {
        setProfesiones(data);
      })
      .catch(err => console.error("Error al cargar profesiones", err));
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear error for this field when typing
    if (fieldErrors[e.target.name]) {
      setFieldErrors({
        ...fieldErrors,
        [e.target.name]: null
      });
    }
  };

  const handleFileChange = (e) => {
    setArchivos({
      ...archivos,
      [e.target.name]: e.target.files[0]
    });
    if (fieldErrors[e.target.name]) {
      setFieldErrors({
        ...fieldErrors,
        [e.target.name]: null
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setStatusMsg('');
    setFieldErrors({});
    
    // Al haber archivos, usamos FormData
    const payload = new FormData();
    Object.keys(formData).forEach(key => {
      if (key === 'profesion_id') {
        payload.append('profesion', formData[key]);
      } else {
        payload.append(key, formData[key]);
      }
    });
    
    if (archivos.foto_dni_frente) {
      payload.append('foto_dni_frente', archivos.foto_dni_frente);
    }
    if (archivos.foto_dni_reverso) {
      payload.append('foto_dni_reverso', archivos.foto_dni_reverso);
    }
    
    try {
      const response = await fetch('http://localhost:8000/api/registro-profesional/', {
        method: 'POST',
        body: payload
      });
      
      let data = {};
      try { data = await response.json(); } catch(e) {}
      
      if (response.ok || response.status === 201) {
        setIsSuccess(true);
        setStatusMsg('¡Solicitud enviada exitosamente! Cuando sea aprobada por un operador, recibirás tu contraseña temporal por correo electrónico.');
      } else {
        if (data.detalles) {
          // Flatten DRF error arrays
          const formattedErrors = {};
          Object.keys(data.detalles).forEach(key => {
            formattedErrors[key] = Array.isArray(data.detalles[key]) ? data.detalles[key][0] : data.detalles[key];
          });
          setFieldErrors(formattedErrors);
          setStatusMsg('Por favor, corrige los errores resaltados en el formulario.');
          
          // Hacer scroll suave hacia el primer campo con error
          setTimeout(() => {
            const firstErrorKey = Object.keys(formattedErrors)[0];
            if (firstErrorKey) {
              const el = document.getElementsByName(firstErrorKey)[0];
              if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                el.focus();
              } else {
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }
            }
          }, 100);
        } else {
          setStatusMsg(data.error || 'Ocurrió un error al enviar el registro. Verifica los datos.');
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        setIsSuccess(false);
      }
    } catch (err) {
      setStatusMsg('No se pudo contactar con el servidor. Se necesita crear la API en el backend.');
      setIsSuccess(false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh', padding: '3rem 0' }}>
      <div className="glass-panel animate-fade-in" style={{ padding: '2.5rem', width: '100%', maxWidth: '600px' }}>
        
        <Link to="/login" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', textDecoration: 'none', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
          <ArrowLeft size={16} /> Volver al Login
        </Link>

        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ display: 'inline-flex', padding: '12px', background: 'rgba(16, 185, 129, 0.2)', borderRadius: '16px', marginBottom: '1rem' }}>
            <UserPlus size={32} color="#10b981" />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Registro de Profesional</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Completa el formulario y adjunta la documentación solicitada</p>
        </div>

        {statusMsg && (
          <div style={{ 
            background: isSuccess ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', 
            border: `1px solid ${isSuccess ? '#10b981' : '#ef4444'}`, 
            color: isSuccess ? '#34d399' : '#fca5a5', 
            padding: '12px', 
            borderRadius: '8px', 
            marginBottom: '1.5rem', 
            fontSize: '0.95rem', 
            textAlign: 'center' 
          }}>
            {statusMsg}
          </div>
        )}

        {!isSuccess && (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Nombre *</label>
                <input type="text" name="nombre" className="input-field" style={fieldErrors.nombre ? { borderColor: '#ef4444' } : {}} value={formData.nombre} onChange={handleChange} required />
                {fieldErrors.nombre && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.nombre}</span>}
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Apellido *</label>
                <input type="text" name="apellido" className="input-field" style={fieldErrors.apellido ? { borderColor: '#ef4444' } : {}} value={formData.apellido} onChange={handleChange} required />
                {fieldErrors.apellido && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.apellido}</span>}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>DNI / CI *</label>
                <input type="text" name="dni" className="input-field" style={fieldErrors.dni ? { borderColor: '#ef4444' } : {}} value={formData.dni} onChange={handleChange} placeholder="Sólo números" required />
                {fieldErrors.dni && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.dni}</span>}
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Email *</label>
                <input type="email" name="email" className="input-field" style={fieldErrors.email ? { borderColor: '#ef4444' } : {}} value={formData.email} onChange={handleChange} required />
                {fieldErrors.email && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.email}</span>}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Profesión *</label>
                <select name="profesion_id" className="input-field" style={fieldErrors.profesion ? { borderColor: '#ef4444' } : {}} value={formData.profesion_id} onChange={handleChange} required>
                  <option value="">Seleccione...</option>
                  {profesiones.map(prof => (
                    <option key={prof.id} value={prof.id}>{prof.nombre}</option>
                  ))}
                </select>
                {fieldErrors.profesion && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.profesion}</span>}
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Matrícula *</label>
                <input type="text" name="matricula" className="input-field" style={fieldErrors.matricula ? { borderColor: '#ef4444' } : {}} value={formData.matricula} onChange={handleChange} required />
                {fieldErrors.matricula && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.matricula}</span>}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Teléfono *</label>
                <input type="text" name="telefono" className="input-field" style={fieldErrors.telefono ? { borderColor: '#ef4444' } : {}} value={formData.telefono} onChange={handleChange} required />
                {fieldErrors.telefono && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.telefono}</span>}
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Razón Social (Si es empresa)</label>
                <input type="text" name="razon_social" className="input-field" style={fieldErrors.razon_social ? { borderColor: '#ef4444' } : {}} value={formData.razon_social} onChange={handleChange} />
                {fieldErrors.razon_social && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.razon_social}</span>}
              </div>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Dirección / Domicilio *</label>
              <input type="text" name="direccion" className="input-field" style={fieldErrors.direccion ? { borderColor: '#ef4444' } : {}} value={formData.direccion} onChange={handleChange} required />
              {fieldErrors.direccion && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.direccion}</span>}
            </div>

            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)', marginTop: '0.5rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 500, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Upload size={18} /> Documentación Adjunta
              </h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div style={{ overflow: 'hidden' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>DNI (Frente) *</label>
                  <input 
                    type="file" 
                    name="foto_dni_frente" 
                    onChange={handleFileChange} 
                    accept=".jpg,.jpeg,.pdf" 
                    style={{ fontSize: '0.85rem', maxWidth: '100%', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap', borderColor: fieldErrors.foto_dni_frente ? '#ef4444' : undefined }} 
                    required 
                  />
                  {fieldErrors.foto_dni_frente && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.foto_dni_frente}</span>}
                </div>
                <div style={{ overflow: 'hidden' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>DNI (Reverso) *</label>
                  <input 
                    type="file" 
                    name="foto_dni_reverso" 
                    onChange={handleFileChange} 
                    accept=".jpg,.jpeg,.pdf" 
                    style={{ fontSize: '0.85rem', maxWidth: '100%', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap', borderColor: fieldErrors.foto_dni_reverso ? '#ef4444' : undefined }} 
                    required 
                  />
                  {fieldErrors.foto_dni_reverso && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.foto_dni_reverso}</span>}
                </div>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '1rem' }}>Formatos aceptados: Imagen o PDF.</p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem' }}>
              <input 
                type="checkbox" 
                id="aceptaTerminos" 
                checked={aceptaTerminos} 
                onChange={(e) => setAceptaTerminos(e.target.checked)} 
                required 
              />
              <label htmlFor="aceptaTerminos" style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                Acepto los <span 
                  onClick={() => setIsModalOpen(true)} 
                  style={{ color: '#3b82f6', cursor: 'pointer', textDecoration: 'underline' }}
                >
                  Términos y Condiciones de Uso
                </span>
              </label>
            </div>

            <button 
              type="submit" 
              className="btn-primary" 
              style={{ 
                width: '100%', 
                marginTop: '1rem', 
                padding: '12px', 
                background: (isLoading || !aceptaTerminos) ? '#9ca3af' : '#10b981',
                cursor: (isLoading || !aceptaTerminos) ? 'not-allowed' : 'pointer',
                opacity: (isLoading || !aceptaTerminos) ? 0.7 : 1,
                border: 'none',
                color: 'white',
                fontWeight: 'bold',
                borderRadius: '8px',
                transition: 'all 0.3s ease'
              }}
              disabled={isLoading || !aceptaTerminos}
            >
              {isLoading ? 'Enviando solicitud...' : 'Enviar Solicitud de Registro'}
            </button>
          </form>
        )}
      </div>

      {isModalOpen && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ background: 'var(--glass-bg)', backdropFilter: 'blur(16px)', padding: '2rem', borderRadius: '12px', maxWidth: '800px', width: '90%', maxHeight: '80vh', overflowY: 'auto', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-primary)' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem' }}>Términos y Condiciones</h2>
            <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              {terminosContent}
            </div>
            <button 
              onClick={() => setIsModalOpen(false)} 
              className="btn-primary" 
              style={{ marginTop: '1.5rem', padding: '8px 16px', background: '#3b82f6' }}
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
