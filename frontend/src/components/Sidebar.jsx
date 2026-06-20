import React, { useState } from 'react';
import { createPortal } from 'react-dom';

/**
 * Sidebar component — session list, new chat button, health status, token stats.
 */
export default function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  healthStatus,
  latency,
  tokenStats,
  isCollapsed,
  onToggleCollapse,
}) {
  const [openMenuId, setOpenMenuId] = useState(null);
  const [menuPos, setMenuPos] = useState({ top: 0, left: 0 });

  React.useEffect(() => {
    const handleGlobalClick = () => setOpenMenuId(null);
    if (openMenuId) {
      window.addEventListener('click', handleGlobalClick);
      window.addEventListener('resize', handleGlobalClick);
    }
    return () => {
      window.removeEventListener('click', handleGlobalClick);
      window.removeEventListener('resize', handleGlobalClick);
    };
  }, [openMenuId]);

  const handleMenuClick = (e, sessionId) => {
    e.stopPropagation();
    if (openMenuId === sessionId) {
      setOpenMenuId(null);
    } else {
      const rect = e.currentTarget.getBoundingClientRect();
      setMenuPos({
        top: rect.top,
        left: rect.right + 8 // Pop out 8px to the right of the button
      });
      setOpenMenuId(sessionId);
    }
  };

  const handleShareClick = (e, sessionId) => {
    e.stopPropagation();
    // Placeholder share functionality
    console.log("Share session", sessionId);
    setOpenMenuId(null);
  };

  const handleDeleteDropdownClick = (e, sessionId) => {
    e.stopPropagation();
    onDeleteSession(sessionId);
    setOpenMenuId(null);
  };

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      {/* Header */}
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <div className="brand-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="url(#brandGradient)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <defs>
                <linearGradient id="brandGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#6366f1" />
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
          <div className="brand-text">
            <span className="brand-name">Enterprise AI</span>
            <span className="brand-sub">Multi-Agent Assistant</span>
          </div>
        </div>

        <button
          className="collapse-btn"
          onClick={onToggleCollapse}
          title="Close sidebar"
          aria-label="Close sidebar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
      </div>

      {/* New Chat Button */}
      <button className="new-chat-btn" onClick={onNewChat} id="new-chat-btn">
        <span>New Chat</span>
      </button>

      {/* Session List */}
      <div className="sessions-list">
        <div className="sessions-label">
          <span>Recent History</span>
          <span className="session-count">{sessions.length}</span>
        </div>

        {sessions.length === 0 ? (
          <div className="sessions-empty">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.3">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <p>No conversations yet</p>
            <p className="hint">Start a new session to begin</p>
          </div>
        ) : (
          <div className="sessions-scroll">
            {sessions.map((session) => (
              <button
                key={session.id}
                className={`session-item ${activeSessionId === session.id ? 'active' : ''}`}
                onClick={() => onSelectSession(session.id)}
                id={`session-${session.id}`}
              >
                <div className="session-info">
                  <span className="session-title">{session.title}</span>
                </div>
                <div className="session-actions">
                  <div style={{ position: 'relative' }}>
                    <button
                      className={`session-menu-btn ${openMenuId === session.id ? 'active' : ''}`}
                      onClick={(e) => handleMenuClick(e, session.id)}
                      title="Menu options"
                      aria-label="Menu options"
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="none">
                        <circle cx="12" cy="12" r="2" />
                        <circle cx="12" cy="5" r="2" />
                        <circle cx="12" cy="19" r="2" />
                      </svg>
                    </button>
                    {openMenuId === session.id && createPortal(
                      <div className="session-dropdown" style={{ top: menuPos.top, left: menuPos.left, position: 'fixed' }} onClick={(e) => e.stopPropagation()}>
                        <button className="session-dropdown-item" onClick={(e) => handleShareClick(e, session.id)}>
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>
                          Share
                        </button>
                        <button className="session-dropdown-item danger" onClick={(e) => handleDeleteDropdownClick(e, session.id)}>
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /></svg>
                          Delete
                        </button>
                      </div>,
                      document.body
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer: Health + Stats */}
      <div className="sidebar-footer">
        {/* Token Stats */}
        {tokenStats.requests > 0 && (
          <div className="stats-panel">
            <div className="stat-row">
              <span>Requests</span>
              <strong>{tokenStats.requests}</strong>
            </div>
            <div className="stat-row">
              <span>Total Tokens</span>
              <strong>{tokenStats.totalTokens.toLocaleString()}</strong>
            </div>
          </div>
        )}

        {/* Health Status */}
        <div className="health-panel">
          <div className="health-indicator">
            <span className={`health-dot ${healthStatus}`} />
            <span className="health-text">
              {healthStatus === 'online' ? 'System Online' : healthStatus === 'checking' ? 'Connecting...' : 'Offline'}
            </span>
          </div>
          {latency !== null && (
            <span className="health-latency">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
              </svg>
              {latency}ms
            </span>
          )}
        </div>
      </div>
    </aside>
  );
}
