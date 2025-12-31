import React from 'react';
import Layout from '@theme/Layout';
import ChatbotWidget from '../ChatbotWidget/ChatbotWidget';

const LayoutWithChatbot = ({ children, ...props }) => {
  return (
    <Layout {...props}>
      <div style={{ position: 'relative', minHeight: '100vh' }}>
        <main style={{ flex: 1 }}>
          {children}
        </main>
        {/* Floating chatbot widget */}
        <ChatbotWidget position="bottom-right" size="medium" />
      </div>
    </Layout>
  );
};

export default LayoutWithChatbot;