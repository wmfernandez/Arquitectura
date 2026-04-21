import React, { useState, useEffect, useRef } from 'react';
import { ArrowLeft, Map, FileText, Upload, CheckCircle, File } from 'lucide-react';

export default function NuevaSolicitud({ onBack, token }) {
  const [step, setStep] = useState(1);
  const [padronSeleccionado, setPadronSeleccionado] = useState(null);
  const [padronDetalles, setPadronDetalles] = useState(null);
  const [tipoTramite, setTipoTramite] = useState('');
  const [archivoTecnico, setArchivoTecnico] = useState([]); // Ahora es un array de archivos
  const [fileError, setFileError] = useState('');
  const fileInputRef = useRef(null);
  
  // Form options state
  const [opciones, setOpciones] = useState({
    tiposPadron: [],
    localidades: [],
    tiposTramite: [],
    configuracion: {
      extensiones_permitidas: '.pdf,.zip,.rar',
      tamano_maximo_archivo_mb: 10,
      tamano_maximo_total_mb: 50
    }
  });
  
  // Search form state
  const [searchParams, setSearchParams] = useState({
    tipo_id: '',
    localidad: '',
    numero: ''
  });
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState('');

  // Determine if selected type is 'Urbano' to show locality
  const isUrbano = opciones?.tiposPadron?.find(t => String(t?.id) === String(searchParams?.tipo_id))?.nombre?.toLowerCase()?.includes('urbano');

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const response = await fetch('/api/form_options/');
        if (response.ok) {
          const data = await response.json();
          setOpciones(prev => ({
            tiposPadron: data.tipos_padron || prev.tiposPadron || [],
            localidades: data.localidades || prev.localidades || [],
            tiposTramite: data.tipos_tramite || prev.tiposTramite || [],
            configuracion: data.configuracion || prev.configuracion
          }));
        }
      } catch (err) {
        console.error("Error fetching options:", err);
      }
    };
    fetchOptions();
  }, []);

  const handleSearchChange = (e) => {
    setSearchParams({ ...searchParams, [e.target.name]: e.target.value });
    setSearchError('');
    setPadronDetalles(null);
  };

  const buscarPadron = async () => {
    if (!searchParams.numero) {
      setSearchError('El número de padrón es obligatorio');
      return;
    }
    
    setIsSearching(true);
    setSearchError('');
    setPadronDetalles(null);

    try {
      // Build query string
      const params = new URLSearchParams({ numero: searchParams.numero });
      if (searchParams.tipo_id) params.append('tipo_id', searchParams.tipo_id);
      if (isUrbano && searchParams.localidad) params.append('localidad', searchParams.localidad);

      const response = await fetch(`/api/padron/buscar/?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.padrones && data.padrones.length > 0) {
          // Tomar el primero que coincida
          setPadronDetalles(data.padrones[0]);
        } else {
          setSearchError('No se encontraron padrones con estos datos.');
        }
      } else {
        const errData = await response.json();
        setSearchError(errData.error || 'Error al buscar el padrón.');
      }
    } catch (err) {
      setSearchError('Error de conexión con el servidor.');
    } finally {
      setIsSearching(false);
    }
  };
  
  // En un paso futuro, aquí integraremos el mapa GIS real
  const renderPaso1 = () => (
    <div className="animate-fade-in">
      <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', color: 'var(--text-primary)' }}>Paso 1: Identificación del Padrón</h2>
      <div style={{ background: 'rgba(255,255,255,0.05)', padding: '2rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)' }}>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Tipo de Padrón *</label>
            <select className="input-field" name="tipo_id" value={searchParams.tipo_id} onChange={handleSearchChange}>
              <option value="">Seleccione Tipo...</option>
              {opciones.tiposPadron.map(t => (
                <option key={t.id} value={t.id}>{t.nombre}</option>
              ))}
            </select>
          </div>

          {isUrbano && (
            <div className="animate-fade-in">
              <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Localidad *</label>
              <select className="input-field" name="localidad" value={searchParams.localidad} onChange={handleSearchChange}>
                <option value="">Seleccione Localidad...</option>
                {opciones.localidades.map(loc => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Número de Padrón *</label>
            <input 
              type="text" 
              className="input-field" 
              name="numero" 
              value={searchParams.numero} 
              onChange={handleSearchChange}
              placeholder="Ej: 12345" 
            />
          </div>
        </div>

        <button 
          className="btn-primary" 
          onClick={buscarPadron}
          disabled={isSearching || !searchParams.numero || !searchParams.tipo_id || (isUrbano && !searchParams.localidad)}
          style={{ width: '100%', justifyContent: 'center', marginBottom: '1.5rem', opacity: (!searchParams.numero || !searchParams.tipo_id || (isUrbano && !searchParams.localidad)) ? 0.5 : 1 }}
        >
          {isSearching ? 'Buscando...' : 'Buscar Padrón'}
        </button>

        {searchError && (
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#fca5a5', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
            {searchError}
          </div>
        )}

        {padronDetalles && (
          <div className="animate-fade-in" style={{ padding: '1.5rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid #10b981', borderRadius: '8px', textAlign: 'left' }}>
            <h3 style={{ color: '#6ee7b7', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle size={20} /> Padrón Encontrado
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', color: 'white', marginBottom: '1.5rem' }}>
              <div><span style={{ color: 'var(--text-secondary)' }}>Número:</span> {padronDetalles.numero_padron}</div>
              <div><span style={{ color: 'var(--text-secondary)' }}>Tipo:</span> {padronDetalles.tipo}</div>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>{padronDetalles?.tipo?.toLowerCase()?.includes('urbano') ? 'Localidad:' : 'Secc. Catastral:'}</span>
                {' '}
                {padronDetalles?.tipo?.toLowerCase()?.includes('urbano') ? padronDetalles?.localidad : padronDetalles?.seccion_catastral}
              </div>
              <div><span style={{ color: 'var(--text-secondary)' }}>Área:</span> {padronDetalles.area}</div>
            </div>
            
            <button 
              className="btn-primary" 
              style={{ background: '#10b981', width: '100%', justifyContent: 'center' }}
              onClick={() => { 
                setPadronSeleccionado(padronDetalles.id); 
                setStep(2); 
              }}
            >
              Confirmar Padrón y Continuar
            </button>
          </div>
        )}
      </div>
    </div>
  );

  const renderPaso2 = () => (
    <div className="animate-fade-in">
      <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', color: 'var(--text-primary)' }}>Paso 2: Detalles del Trámite</h2>
      <div style={{ background: 'rgba(255,255,255,0.05)', padding: '2rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)' }}>
        
        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '8px', border: '1px solid #3b82f6' }}>
          <span style={{ color: '#93c5fd', fontSize: '0.9rem' }}>Padrón Seleccionado: </span>
          <span style={{ color: 'white', fontWeight: 'bold' }}>
            Nº {padronDetalles?.numero_padron} ({padronDetalles?.tipo} - {padronDetalles?.tipo?.toLowerCase()?.includes('urbano') ? padronDetalles?.localidad : `Secc. ${padronDetalles?.seccion_catastral}`})
          </span>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Tipo de Trámite *</label>
          <select className="input-field" value={tipoTramite} onChange={(e) => setTipoTramite(e.target.value)}>
            <option value="">Seleccione el tipo de trámite...</option>
            {opciones?.tiposTramite?.map(tt => (
              <option key={tt.id} value={tt.id}>{tt.nombre}</option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '2rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Archivos Técnicos ({opciones?.configuracion?.extensiones_permitidas || '.pdf'})</label>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
            Máximo por archivo: {opciones?.configuracion?.tamano_maximo_archivo_mb || 10} MB | 
            Total permitido: {opciones?.configuracion?.tamano_maximo_total_mb || 50} MB
          </p>

          <input 
            type="file" 
            ref={fileInputRef} 
            multiple
            onChange={(e) => {
              const files = Array.from(e.target.files);
              setFileError('');

              let newFiles = [...archivoTecnico];
              let hasError = false;

              for (const file of files) {
                // Verificar extensión
                const ext = '.' + file.name.split('.').pop().toLowerCase();
                const permitidas = (opciones?.configuracion?.extensiones_permitidas || '.pdf,.zip,.rar').split(',').map(s => s.trim().toLowerCase());
                if (!permitidas.includes(ext)) {
                  setFileError(`El archivo ${file.name} tiene una extensión no permitida.`);
                  hasError = true;
                  break;
                }

                // Verificar tamaño individual
                const sizeMb = file.size / (1024 * 1024);
                const maxSize = opciones?.configuracion?.tamano_maximo_archivo_mb || 10;
                if (sizeMb > maxSize) {
                  setFileError(`El archivo ${file.name} excede el máximo permitido de ${maxSize}MB.`);
                  hasError = true;
                  break;
                }

                newFiles.push(file);
              }

              if (!hasError) {
                // Verificar tamaño total
                const totalMb = newFiles.reduce((sum, f) => sum + f.size, 0) / (1024 * 1024);
                const maxTotal = opciones?.configuracion?.tamano_maximo_total_mb || 50;
                if (totalMb > maxTotal) {
                  setFileError(`El peso total de los archivos supera el límite de ${maxTotal}MB.`);
                } else {
                  setArchivoTecnico(newFiles);
                }
              }

              // Limpiar el input para permitir seleccionar el mismo archivo después de borrarlo
              e.target.value = null;
            }} 
            style={{ display: 'none' }} 
            accept={opciones?.configuracion?.extensiones_permitidas || '.pdf,.zip,.rar'} 
          />

          <div 
            onClick={() => fileInputRef.current.click()}
            style={{ 
              padding: '1.5rem', 
              border: '1px dashed rgba(255,255,255,0.2)', 
              borderRadius: '8px', 
              textAlign: 'center',
              cursor: 'pointer',
              background: 'transparent',
              transition: 'all 0.2s ease-in-out',
              marginBottom: '1rem'
            }}
            className="hover:bg-opacity-10"
          >
            <Upload size={24} style={{ color: 'var(--text-secondary)', margin: '0 auto 0.5rem auto' }} />
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Haz clic para seleccionar o agregar archivos</p>
          </div>

          {fileError && (
            <div style={{ color: '#fca5a5', fontSize: '0.85rem', marginBottom: '1rem', textAlign: 'center' }}>
              {fileError}
            </div>
          )}

          {archivoTecnico.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {archivoTecnico.map((file, index) => (
                <div key={index} className="animate-fade-in" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 1rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '6px', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <File size={16} color="#3b82f6" />
                    <span style={{ color: 'white', fontSize: '0.9rem' }}>{file.name}</span>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>({(file.size / (1024 * 1024)).toFixed(2)} MB)</span>
                  </div>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      setArchivoTecnico(archivoTecnico.filter((_, i) => i !== index));
                      setFileError('');
                    }}
                    style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '0.8rem' }}
                  >
                    Eliminar
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <button className="btn-primary" style={{ background: 'transparent', border: '1px solid var(--glass-border)' }} onClick={() => setStep(1)}>
            Atrás
          </button>
          <button 
            className="btn-primary" 
            disabled={!tipoTramite || fileError} 
            style={{ opacity: (!tipoTramite || fileError) ? 0.5 : 1 }}
            onClick={() => setStep(3)}
          >
            Continuar
          </button>
        </div>
      </div>
    </div>
  );

  const renderPaso3 = () => (
    <div className="animate-fade-in" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
      <CheckCircle size={64} color="#10b981" style={{ margin: '0 auto 1.5rem auto' }} />
      <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'white' }}>Resumen de Solicitud</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Se creará un expediente para el Padrón {padronDetalles?.numero_padron}.
      </p>
      
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
        <button className="btn-primary" style={{ background: 'transparent', border: '1px solid var(--glass-border)' }} onClick={() => setStep(2)}>
          Modificar
        </button>
        <button className="btn-primary" style={{ background: '#10b981' }} onClick={async () => {
          if (isSearching) return;
          setIsSearching(true);
          try {
            const formData = new FormData();
            formData.append('padron_id', padronSeleccionado);
            formData.append('tipo_tramite_id', tipoTramite);
            
            for (let i = 0; i < archivoTecnico.length; i++) {
              formData.append('archivos', archivoTecnico[i]);
            }

            const response = await fetch('/api/solicitudes/enviar/', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`
                // Note: NO Content-Type header when using FormData, fetch sets it automatically with the boundary
              },
              body: formData
            });

            if (response.ok) {
              alert('¡Solicitud Enviada Exitosamente!');
              onBack();
            } else {
              const errData = await response.json();
              alert('Error al enviar: ' + (errData.error || 'Problema en el servidor'));
            }
          } catch (err) {
            console.error(err);
            alert('Error de conexión al enviar la solicitud.');
          } finally {
            setIsSearching(false);
          }
        }} disabled={isSearching}>
          {isSearching ? 'Enviando...' : 'Confirmar y Enviar'} {isSearching ? null : <CheckCircle size={18} style={{ marginLeft: '8px' }} />}
        </button>
      </div>
    </div>
  );

  return (
    <div className="animate-fade-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <header className="header" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button onClick={onBack} style={{ background: 'transparent', border: 'none', color: '#60a5fa', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
            <ArrowLeft size={24} />
          </button>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Iniciar Nueva Solicitud</h1>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              Paso {step} de 3
            </p>
          </div>
        </div>
      </header>

      {/* Barra de progreso simple */}
      <div style={{ display: 'flex', gap: '4px', marginBottom: '2rem' }}>
        <div style={{ height: '4px', flex: 1, background: step >= 1 ? '#3b82f6' : 'rgba(255,255,255,0.1)', borderRadius: '2px' }} />
        <div style={{ height: '4px', flex: 1, background: step >= 2 ? '#3b82f6' : 'rgba(255,255,255,0.1)', borderRadius: '2px' }} />
        <div style={{ height: '4px', flex: 1, background: step >= 3 ? '#10b981' : 'rgba(255,255,255,0.1)', borderRadius: '2px' }} />
      </div>

      {step === 1 && renderPaso1()}
      {step === 2 && renderPaso2()}
      {step === 3 && renderPaso3()}
    </div>
  );
}
