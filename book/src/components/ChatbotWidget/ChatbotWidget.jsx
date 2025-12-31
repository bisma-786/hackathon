import React, { useState, useEffect } from 'react';
import Chatbot from '../Chatbot/Chatbot';

const ChatbotWidget = ({ position = 'bottom-right', size = 'medium' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return null;
  }

  const getSizeStyles = () => {
    switch(size) {
      case 'small':
        return { width: '300px', height: '400px' };
      case 'large':
        return { width: '500px', height: '600px' };
      case 'medium':
      default:
        return { width: '400px', height: '500px' };
    }
  };

  const getPositionStyles = () => {
    switch(position) {
      case 'bottom-left':
        return { bottom: '20px', left: '20px' };
      case 'top-right':
        return { top: '20px', right: '20px' };
      case 'top-left':
        return { top: '20px', left: '20px' };
      case 'bottom-right':
      default:
        return { bottom: '20px', right: '20px' };
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        style={{
          position: 'fixed',
          ...getPositionStyles(),
          zIndex: 1000,
          backgroundColor: 'transparent',
          color: 'white',
          border: 'none',
          borderRadius: '50%',
          width: '60px',
          height: '60px',
          fontSize: '24px',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 'bold',
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
          padding: '5px',
        }}
        onMouseEnter={(e) => {
          e.target.style.transform = 'scale(1.1)';
          e.target.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.2)';
        }}
        onMouseLeave={(e) => {
          e.target.style.transform = 'scale(1)';
          e.target.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
        }}
        aria-label="Open AI Assistant"
      >
        <img
          src="/img/cuterobo.jpg.png"
          alt="AI Assistant"
          style={{
            width: '45px',
            height: '45px',
            objectFit: 'cover',
          }}
        />
      </button>
    );
  }

  return (
    <div
      style={{
        position: 'fixed',
        ...getPositionStyles(),
        zIndex: 1000,
        width: getSizeStyles().width,
        height: getSizeStyles().height,
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
        borderRadius: '12px',
        overflow: 'hidden',
        backgroundColor: 'white',
      }}
    >
      <div style={{ height: '100%', overflow: 'auto' }}>
        <Chatbot onClose={() => setIsOpen(false)} />
      </div>
    </div>
  );
};

export default ChatbotWidget;