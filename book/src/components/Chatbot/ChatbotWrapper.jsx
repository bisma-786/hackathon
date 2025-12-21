/**
 * Chatbot Wrapper Component
 * SSR-safe wrapper that ensures browser-only execution for chatbot functionality
 */

import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import { Chatbot } from './Chatbot';

/**
 * ChatbotWrapper Component
 * Provides SSR-safe rendering by wrapping the chatbot in BrowserOnly
 * @param {Object} props - Component properties (same as Chatbot)
 */
export const ChatbotWrapper = (props) => {
  return (
    <BrowserOnly fallback={<div className="chatbot-placeholder">Loading chatbot...</div>}>
      {() => <Chatbot {...props} />}
    </BrowserOnly>
  );
};

export default ChatbotWrapper;