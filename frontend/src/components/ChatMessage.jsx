import React, { useState } from 'react';
import MarkdownRenderer from './MarkdownRenderer';

/**
 * Renders a single chat exchange (user question + AI response).
 */
export default function ChatMessage({ message, onDelete, onEdit, index }) {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editText, setEditText] = useState(message.humanMessage);

  const formatTime = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSaveEdit = async () => {
    if (editText.trim() && editText !== message.humanMessage) {
      setIsSaving(true);
      const success = await onEdit(message.id, editText);
      setIsSaving(false);
      if (success) {
        setIsEditing(false);
      }
    } else {
      setIsEditing(false);
    }
  };

  return (
    <div className="chat-message-group" style={{ animationDelay: `${Math.min(index * 0.05, 0.3)}s` }}>
      {/* User Message */}
      {message.humanMessage && (
        <div className="message-row user-row">
          <div className="message-content-wrapper">
            <div className="message-bubble user-bubble">
              {isEditing ? (
                <div className="edit-message-container">
                  <textarea 
                    value={editText} 
                    onChange={(e) => setEditText(e.target.value)}
                    className="edit-message-input"
                    rows={3}
                    disabled={isSaving}
                  />
                  <div className="edit-message-actions" style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '8px' }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => { setIsEditing(false); setEditText(message.humanMessage); }} disabled={isSaving}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '6px'}}>
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                      Close
                    </button>
                    <button className="btn btn-primary btn-sm" onClick={handleSaveEdit} disabled={isSaving}>
                      {isSaving ? (
                        <>
                          <svg className="btn-spinner" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{marginRight: '6px', animation: 'spin 1s linear infinite'}}>
                            <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                          </svg>
                          Sending...
                        </>
                      ) : (
                        <>
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '6px'}}>
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                          </svg>
                          Send
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ) : (
                <p>{message.humanMessage}</p>
              )}
            </div>
            {!isEditing && (
              <div className="message-meta user-meta">
                <span className="message-time">{formatTime(message.createdAt)}</span>
                <button className="icon-btn" onClick={() => setIsEditing(true)} title="Edit">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 20h9"></path>
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                  </svg>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI Response */}
      {message.aiMessage && (
        <div className="message-row ai-row">
          <div className="message-content-wrapper">
            <div id={`ai-msg-${index}`} className={`message-bubble ai-bubble ${message.isError ? 'error-bubble' : ''}`}>
              <MarkdownRenderer content={message.aiMessage} />
            </div>
            <div className="message-meta ai-meta">
              {message.model && (
                <>
                  <span className="ai-meta-item highlight">{message.model}</span>
                  <span className="ai-meta-divider">|</span>
                </>
              )}
              {message.latency && (
                <>
                  <span className="ai-meta-item">{message.latency}s</span>
                  <span className="ai-meta-divider">|</span>
                </>
              )}
              {message.tokens && (
                <>
                  <span className="ai-meta-item" title="Tokens">
                    {message.tokens.total}t
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{marginLeft: '2px', opacity: 0.7}}>
                      <circle cx="12" cy="12" r="10"></circle>
                      <line x1="12" y1="16" x2="12" y2="12"></line>
                      <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>
                  </span>
                  <span className="ai-meta-divider">|</span>
                </>
              )}
              <span className="ai-meta-item highlight">message</span>
              
              <button className="icon-btn" onClick={() => {
                const el = document.getElementById(`ai-msg-${index}`);
                if (el) {
                  navigator.clipboard.writeText(el.innerText);
                } else {
                  navigator.clipboard.writeText(message.aiMessage);
                }
              }} title="Copy">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
              </button>

              <button className="icon-btn" onClick={() => onDelete && onDelete(message.id)} title="Delete">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  <line x1="10" y1="11" x2="10" y2="17"></line>
                  <line x1="14" y1="11" x2="14" y2="17"></line>
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pending state — waiting for AI */}
      {message.isPending && !message.aiMessage && (
        <div className="message-row ai-row">
          <div className="message-content-wrapper">
            <div className="message-bubble ai-bubble thinking-bubble">
              <div className="typing-indicator">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
