/**
 * Root Layout Component
 * Wraps the entire application and includes the chatbot component
 */

import React from 'react';
import Chatbot from '@site/src/components/Chatbot/Chatbot';

// Default layout wrapper that includes the chatbot
export default function Root({ children }) {
  return (
    <>
      {children}
      <Chatbot
        config={{
          apiEndpoint: process.env.CHATBOT_API_ENDPOINT || 'http://localhost:8000'
        }}
        options={{
          showSources: true,
          enableSelectedText: true
        }}
      />
    </>
  );
}