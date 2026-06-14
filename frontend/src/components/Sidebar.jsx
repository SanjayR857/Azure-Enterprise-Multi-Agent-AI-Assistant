import React, { useState } from 'react';

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
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now - d;
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  const handleDeleteClick = (e, sessionId) => {
    e.stopPropagation();
    if (deleteConfirm === sessionId) {
      onDeleteSession(sessionId);
      setDeleteConfirm(null);
    } else {
      setDeleteConfirm(sessionId);
      setTimeout(() => setDeleteConfirm(null), 3000);
    }
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
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          aria-label="Toggle sidebar"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {isCollapsed ? (
              <><line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="18" x2="21" y2="18" /></>
            ) : (
              <><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></>
            )}
          </svg>
        </button>
      </div>

      {/* New Chat Button */}
      <button className="new-chat-btn" onClick={onNewChat} id="new-chat-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        <span>New Chat</span>
      </button>

      {/* Session List */}
      <div className="sessions-list">
        <div className="sessions-label">
          <span>Recent Conversations</span>
          <span className="session-count">{sessions.length}</span>
        </div>

        {sessions.length === 0 ? (
          <div className="sessions-empty">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.3">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <p>No conversations yet</p>
            <p className="hint">Start a new chat to begin</p>
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
                <div className="session-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </div>
                <div className="session-info">
                  <span className="session-title">{session.title}</span>
                  <span className="session-preview">{session.preview || 'No messages yet'}</span>
                </div>
                <div className="session-actions">
                  <span className="session-time">{formatDate(session.updatedAt)}</span>
                  <button
                    className={`session-delete-btn ${deleteConfirm === session.id ? 'confirm' : ''}`}
                    onClick={(e) => handleDeleteClick(e, session.id)}
                    title={deleteConfirm === session.id ? 'Click again to confirm' : 'Delete session'}
                    aria-label="Delete session"
                  >
                    {deleteConfirm === session.id ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>
                    ) : (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /></svg>
                    )}
                  </button>
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
