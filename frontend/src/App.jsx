import React, { useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import useChat from './hooks/useChat';
import './App.css';

export default function App() {
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
  } = useChat();

  const messagesEndRef = useRef(null);
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);

  // Initialize: load sessions + start health checks
  useEffect(() => {
    loadSessions();
    const cleanup = startHealthCheck();
    return cleanup;
  }, [loadSessions, startHealthCheck]);

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
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={startNewChat}
        onDeleteSession={deleteSession}
        healthStatus={healthStatus}
        latency={latency}
        tokenStats={tokenStats}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

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
