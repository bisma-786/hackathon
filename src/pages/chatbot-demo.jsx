import React from 'react';
import Layout from '@theme/Layout';
import Chatbot from '../components/Chatbot';

export default function ChatbotDemo() {
  return (
    <Layout title="AI Assistant" description="Interactive AI assistant for the textbook">
      <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ marginBottom: '2rem' }}>
          <h1>AI Assistant for the Textbook</h1>
          <p>Ask questions about the book content and get answers powered by our RAG system.</p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '2rem',
          minHeight: '600px'
        }}>
          <div>
            <h2>About This Book</h2>
            <p>This AI-driven textbook covers Physical AI & Humanoid Robotics, providing comprehensive knowledge on ROS 2, simulation environments, and embodied intelligence systems.</p>

            <h3>Key Topics</h3>
            <ul>
              <li>Fundamentals of Physical AI</li>
              <li>Digital Twin Technology</li>
              <li>AI Robot Brains</li>
              <li>Vision-Language-Action Systems</li>
              <li>Autonomous Humanoid Capabilities</li>
            </ul>
          </div>

          <div style={{ border: '1px solid #ddd', borderRadius: '8px', height: 'fit-content' }}>
            <Chatbot />
          </div>
        </div>
      </div>
    </Layout>
  );
}