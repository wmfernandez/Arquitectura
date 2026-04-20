import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ error, errorInfo });
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', background: '#fee2e2', color: '#991b1b', borderRadius: '8px', margin: '2rem' }}>
          <h2>Algo salió mal al cargar el componente.</h2>
          <details style={{ whiteSpace: 'pre-wrap', marginTop: '1rem', background: 'rgba(255,255,255,0.5)', padding: '1rem' }}>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </details>
          <button 
            onClick={() => this.props.onBack && this.props.onBack()} 
            style={{ marginTop: '1rem', padding: '0.5rem 1rem', background: '#ef4444', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Volver
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
