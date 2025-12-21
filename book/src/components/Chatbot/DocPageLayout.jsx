/**
 * Doc Page Layout Component
 * Layout wrapper for documentation pages that includes the chatbot
 */

import React from 'react';
import Chatbot from '@site/src/components/Chatbot/Chatbot';

// Layout wrapper specifically for documentation pages
export default function DocPageLayout({ children, ...props }) {
  return (
    <>
      {children}
      <Chatbot
        pageContext={{
          url: typeof window !== 'undefined' ? window.location.href : '',
          title: typeof document !== 'undefined' ? document.title : ''
        }}
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