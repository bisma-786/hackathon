/**
 * Error Boundary Component for the Chatbot
 * Catches JavaScript errors anywhere in the child component tree
 */

import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service
    console.error('Chatbot Error Boundary caught an error:', error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div className="chatbot-error-boundary">
          <div className="error-message">
            <h3>Oops! Something went wrong with the chatbot.</h3>
            <p>We're sorry, but the chatbot encountered an error.</p>
            <button
              className="error-retry-button"
              onClick={() => {
                // Reset the error state to try re-rendering the component
                this.setState({ hasError: false, error: null, errorInfo: null });
              }}
            >
              Try Again
            </button>
            {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
              <details className="error-details" style={{ whiteSpace: 'pre-wrap' }}>
                {this.state.error && this.state.error.toString()}
                <br />
                {this.state.errorInfo.componentStack}
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;