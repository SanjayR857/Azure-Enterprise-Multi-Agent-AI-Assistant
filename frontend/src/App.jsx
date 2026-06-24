import React, { useEffect, useRef } from 'react';
import { AuthenticatedTemplate, UnauthenticatedTemplate, useMsal } from '@azure/msal-react';
import { loginRequest } from './authConfig';
import Sidebar from './components/Sidebar';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import useChat from './hooks/useChat';
import './App.css';

import LandingPage from './components/LandingPage';

export default function App() {
  return (
    <>
      <AuthenticatedTemplate>
        <MainApp />
      </AuthenticatedTemplate>
      <UnauthenticatedTemplate>
        <LandingPage />
      </UnauthenticatedTemplate>
    </>
  );
}

function MainApp() {
  const {
    sessions,
    activeSessionId,
    messages,
    isLoading,
    isSending,
    healthStatus,
    latency,
    tokenStats,
    startHealthCheck,
    loadSessions,
    loadHistory,
    sendMessage,
    deleteSession,
    startNewChat,
    togglePin,
  } = useChat();

  const messagesEndRef = useRef(null);
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);

  // Initialize: load sessions + start health checks
  useEffect(() => {
    loadSessions();
    const cleanup = startHealthCheck();
    return cleanup;
  }, [loadSessions, startHealthCheck]);

  // Initial load from URL hash
  useEffect(() => {
    if (activeSessionId) {
      loadHistory(activeSessionId);
    }
    // Only run this once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Handle back/forward navigation
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash;
      if (hash.startsWith('#/chat/')) {
        const id = hash.replace('#/chat/', '');
        if (id !== activeSessionId) {
          loadHistory(id);
        }
      } else if (hash === '' || hash === '#/') {
        startNewChat();
      }
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [activeSessionId, loadHistory, startNewChat]);

  // Resizing logic
  const isResizing = useRef(false);

  const startResizing = React.useCallback(() => {
    isResizing.current = true;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }, []);

  const stopResizing = React.useCallback(() => {
    isResizing.current = false;
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }, []);

  const resize = React.useCallback((e) => {
    if (isResizing.current) {
      const newWidth = e.clientX;
      if (newWidth >= 200 && newWidth <= 800) {
        document.documentElement.style.setProperty('--sidebar-width', `${newWidth}px`);
      }
    }
  }, []);

  useEffect(() => {
    window.addEventListener('mousemove', resize);
    window.addEventListener('mouseup', stopResizing);
    return () => {
      window.removeEventListener('mousemove', resize);
      window.removeEventListener('mouseup', stopResizing);
    };
  }, [resize, stopResizing]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isSending]);

  // Handle sending a message
  const handleSend = async (text) => {
    await sendMessage(text, activeSessionId);
  };

  // Handle selecting a session
  const handleSelectSession = (sessionId) => {
    if (sessionId === activeSessionId) return;
    loadHistory(sessionId);
  };

  return (
    <div className="app-layout">
      {/* Floating toggle button — visible when sidebar is collapsed */}
      <button
        className={`sidebar-toggle-btn ${sidebarCollapsed ? 'visible' : ''}`}
        onClick={() => setSidebarCollapsed(false)}
        title="Open sidebar"
        aria-label="Open sidebar"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={startNewChat}
        onDeleteSession={deleteSession}
        onTogglePin={togglePin}
        healthStatus={healthStatus}
        latency={latency}
        tokenStats={tokenStats}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Resizer Handle */}
      {!sidebarCollapsed && (
        <div className="sidebar-resizer" onMouseDown={startResizing} />
      )}

      <main className="chat-main">
        {/* Background ambient decoration */}
        <div className="ambient-bg">
          <div className="ambient-orb orb-1" />
          <div className="ambient-orb orb-2" />
          <div className="ambient-orb orb-3" />
        </div>

        {/* Chat area */}
        <div className="chat-container">
          {/* Messages or Empty State */}
          <div className="messages-area" id="messages-area">
            {messages.length === 0 && !isLoading ? (
              <div className="empty-state">
                <div className="empty-icon-wrapper">
                  <div className="empty-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="url(#emptyGrad)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <defs>
                        <linearGradient id="emptyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#6366f1" />
                          <stop offset="50%" stopColor="#8b5cf6" />
                          <stop offset="100%" stopColor="#22d3ee" />
                        </linearGradient>
                      </defs>
                      <path d="M12 8V4H8" />
                      <rect width="16" height="12" x="4" y="8" rx="2" />
                      <path d="M2 14h2" />
                      <path d="M20 14h2" />
                      <path d="M15 13v2" />
                      <path d="M9 13v2" />
                    </svg>
                  </div>
                  <div className="empty-glow" />
                </div>
                <h2 className="empty-title">Enterprise AI Assistant</h2>
                <p className="empty-subtitle">
                  Powered by multi-agent orchestration with search, tools, and RAG capabilities.
                </p>
              </div>
            ) : (
              <>
                {isLoading && messages.length === 0 && (
                  <div className="loading-state">
                    <div className="loading-spinner" />
                    <p>Loading conversation...</p>
                  </div>
                )}
                {messages.map((msg, idx) => (
                  <ChatMessage key={msg.id} message={msg} index={idx} />
                ))}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <ChatInput
            onSend={handleSend}
            isSending={isSending}
            hasMessages={messages.length > 0}
          />
        </div>
      </main>
    </div>
  );
}
