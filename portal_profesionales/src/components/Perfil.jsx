import React, { useState, useEffect } from 'react';
import { User, AlertTriangle, UploadCloud, Save, Info, ArrowLeft } from 'lucide-react';

export default function Perfil({ perfilData, onLogout, onBack, onProfileUpdated }) {
  const [formData, setFormData] = useState({
    nombre: perfilData.nombre || '',
    apellido: perfilData.apellido || '',
    telefono: perfilData.telefono || '',
    direccion: perfilData.direccion || '',
    razon_social: perfilData.razon_social || '',
    email: perfilData.email || '',
    password: ''
  });
  
  const [currentEstado, setCurrentEstado] = useState(perfilData.estado_nombre ? perfilData.estado_nombre.toUpperCase() : '');

  const [files, setFiles] = useState({
    foto_frente: null,
    foto_reverso: null
  });

  const [isLoading, setIsLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  const isObservado = currentEstado === 'OBSERVADO' || currentEstado === 'SUSPENDIDO';
  const isEsperando = currentEstado === 'LEVANTAR OBSERVACION' || currentEstado === 'LEVANTAR SUSPENSION';

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (fieldErrors[e.target.name]) {
      setFieldErrors({ ...fieldErrors, [e.target.name]: null });
    }
  };

  const handleFileChange = (e) => {
    const { name, files: fileList } = e.target;
    if (fileList.length > 0) {
      setFiles({ ...files, [name]: fileList[0] });
    }
    if (fieldErrors[name]) {
      setFieldErrors({ ...fieldErrors, [name]: null });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg('');
    setSuccessMsg('');
    setFieldErrors({});

    const token = sessionStorage.getItem('access_token');
    const submitData = new FormData();
    submitData.append('nombre', formData.nombre);
    submitData.append('apellido', formData.apellido);
    submitData.append('email', formData.email);
    if (formData.password) {
      submitData.append('password', formData.password);
    }
    submitData.append('telefono', formData.telefono);
    submitData.append('direccion', formData.direccion);
    submitData.append('razon_social', formData.razon_social);
    
    if (files.foto_frente) submitData.append('foto_dni_frente', files.foto_frente);
    if (files.foto_reverso) submitData.append('foto_dni_reverso', files.foto_reverso);

    try {
      const response = await fetch('/api/perfil/', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: submitData
      });

      if (response.ok) {
        const data = await response.json();
        setSuccessMsg('Perfil actualizado correctamente. Si tenías observaciones, se ha notificado al operador para su revisión.');
        setCurrentEstado(data.estado_nombre ? data.estado_nombre.toUpperCase() : currentEstado);
        setFormData({ ...formData, password: '' }); // Limpiar campo de password tras éxito
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (onProfileUpdated) {
          onProfileUpdated(data);
        }
      } else {
        const data = await response.json();
        const formattedErrors = {};
        Object.keys(data).forEach(key => {
          formattedErrors[key] = Array.isArray(data[key]) ? data[key][0] : data[key];
        });
        setFieldErrors(formattedErrors);
        setErrorMsg('Por favor, corrige los errores resaltados en el formulario.');
        
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
      }
    } catch (err) {
      setErrorMsg('Error de conexión al guardar el perfil.');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <header className="header" style={{ marginBottom: '2rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {onBack && (
              <button onClick={onBack} style={{ background: 'transparent', border: 'none', color: '#60a5fa', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                <ArrowLeft size={24} />
              </button>
            )}
            <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Mi Perfil Profesional</h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            Estado actual: <span style={{ color: 'white', fontWeight: 'bold' }}>{currentEstado}</span>
          </p>
        </div>
        <button className="btn-primary" style={{ background: 'var(--glass-bg)', border: '1px solid var(--glass-border)' }} onClick={onLogout}>
          Salir
        </button>
      </header>

      {(isObservado || isEsperando) && (
        <div style={{ 
          background: isObservado ? 'rgba(234, 179, 8, 0.1)' : 'rgba(59, 130, 246, 0.1)', 
          border: `1px solid ${isObservado ? '#eab308' : '#3b82f6'}`, 
          color: isObservado ? '#fde047' : '#93c5fd', 
          padding: '1.5rem', 
          borderRadius: '12px', 
          marginBottom: '2rem' 
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '1rem' }}>
            {isObservado ? <AlertTriangle size={24} /> : <Info size={24} />}
            <h2 style={{ fontSize: '1.2rem', margin: 0 }}>
              {isObservado ? 'Tu cuenta requiere atención' : 'En revisión por el operador'}
            </h2>
          </div>
          <p style={{ marginBottom: '1rem', lineHeight: '1.6' }}>
            {perfilData.observaciones_estado || 'No hay detalles adicionales proporcionados.'}
          </p>
          {isObservado && (
            <p style={{ fontSize: '0.9rem', opacity: 0.9 }}>
              Por favor, corrige los datos necesarios en el formulario a continuación o sube la documentación correcta y haz clic en "Enviar Corrección".
            </p>
          )}
        </div>
      )}

      {successMsg && (
        <div style={{ background: 'rgba(34, 197, 94, 0.1)', border: '1px solid #22c55e', color: '#bbf7d0', padding: '15px', borderRadius: '8px', marginBottom: '1rem' }}>
          {successMsg}
        </div>
      )}

      {errorMsg && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#fca5a5', padding: '15px', borderRadius: '8px', marginBottom: '1rem' }}>
          {errorMsg}
        </div>
      )}

      <form className="glass-panel" style={{ padding: '2rem' }} onSubmit={handleSubmit}>
        <h3 style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem', marginBottom: '1.5rem' }}>Datos Personales y de Contacto</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Nombre</label>
            <input type="text" className="input-field" name="nombre" value={formData.nombre} onChange={handleChange} required disabled={isEsperando} style={fieldErrors.nombre ? { borderColor: '#ef4444' } : {}} />
            {fieldErrors.nombre && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.nombre}</span>}
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Apellido</label>
            <input type="text" className="input-field" name="apellido" value={formData.apellido} onChange={handleChange} required disabled={isEsperando} style={fieldErrors.apellido ? { borderColor: '#ef4444' } : {}} />
            {fieldErrors.apellido && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.apellido}</span>}
          </div>
          <div style={{ gridColumn: '1 / -1' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Email</label>
            <input type="email" className="input-field" name="email" value={formData.email} onChange={handleChange} required disabled={isEsperando} style={fieldErrors.email ? { borderColor: '#ef4444' } : {}} />
            {fieldErrors.email && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.email}</span>}
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Teléfono</label>
            <input type="text" className="input-field" name="telefono" value={formData.telefono} onChange={handleChange} required disabled={isEsperando} style={fieldErrors.telefono ? { borderColor: '#ef4444' } : {}} />
            {fieldErrors.telefono && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.telefono}</span>}
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Dirección</label>
            <input type="text" className="input-field" name="direccion" value={formData.direccion} onChange={handleChange} disabled={isEsperando} style={fieldErrors.direccion ? { borderColor: '#ef4444' } : {}} />
            {fieldErrors.direccion && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.direccion}</span>}
          </div>
          <div style={{ gridColumn: '1 / -1' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Razón Social (Opcional)</label>
            <input type="text" className="input-field" name="razon_social" value={formData.razon_social} onChange={handleChange} disabled={isEsperando} style={fieldErrors.razon_social ? { borderColor: '#ef4444' } : {}} />
            {fieldErrors.razon_social && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.razon_social}</span>}
          </div>
        </div>

        <h3 style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem', marginBottom: '1.5rem' }}>Seguridad</h3>
        <div style={{ marginBottom: '2rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Cambiar Contraseña (dejar en blanco para no modificar)</label>
          <input type="password" className="input-field" name="password" placeholder="Nueva contraseña..." value={formData.password} onChange={handleChange} disabled={isEsperando} style={fieldErrors.password ? { borderColor: '#ef4444' } : {}} />
          {fieldErrors.password && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.password}</span>}
        </div>

        <h3 style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem', marginBottom: '1.5rem' }}>Datos Fijos (Solo Lectura)</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem', opacity: 0.7 }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>DNI/CI</label>
            <input type="text" className="input-field" value={perfilData.documento_identidad} disabled />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Matrícula</label>
            <input type="text" className="input-field" value={perfilData.matricula} disabled />
          </div>
        </div>

        <h3 style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem', marginBottom: '1.5rem' }}>Actualizar Documentación</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Nuevo DNI/CI Frente</label>
            <input type="file" name="foto_frente" accept=".jpg,.jpeg,.pdf" className="input-field" style={{ padding: '8px', borderColor: fieldErrors.foto_dni_frente ? '#ef4444' : undefined }} onChange={handleFileChange} disabled={isEsperando} />
            {fieldErrors.foto_dni_frente && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.foto_dni_frente}</span>}
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Nuevo DNI/CI Reverso</label>
            <input type="file" name="foto_reverso" accept=".jpg,.jpeg,.pdf" className="input-field" style={{ padding: '8px', borderColor: fieldErrors.foto_dni_reverso ? '#ef4444' : undefined }} onChange={handleFileChange} disabled={isEsperando} />
            {fieldErrors.foto_dni_reverso && <span style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>{fieldErrors.foto_dni_reverso}</span>}
          </div>
        </div>

        {!isEsperando && (
          <button type="submit" className="btn-primary" style={{ width: '100%', padding: '14px', fontSize: '1.1rem' }} disabled={isLoading}>
            {isLoading ? 'Guardando...' : (isObservado ? 'Enviar Corrección a Revisión' : 'Guardar Perfil')} <Save size={18} style={{ marginLeft: '8px', verticalAlign: 'middle' }} />
          </button>
        )}
      </form>
    </div>
  );
}
