import React from 'react';
import MarkdownRenderer from './MarkdownRenderer';

/**
 * Renders a single chat exchange (user question + AI response).
 */
export default function ChatMessage({ message, onDelete, index }) {
  const formatTime = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-message-group" style={{ animationDelay: `${Math.min(index * 0.05, 0.3)}s` }}>
      {/* User Message */}
      {message.humanMessage && (
        <div className="message-row user-row">
          <div className="message-content-wrapper">
            <div className="message-bubble user-bubble">
              <p>{message.humanMessage}</p>
            </div>
            <div className="message-meta user-meta">
              <span className="message-time">{formatTime(message.createdAt)}</span>
            </div>
          </div>
        </div>
      )}

      {/* AI Response */}
      {message.aiMessage && (
        <div className="message-row ai-row">

          <div className="message-content-wrapper">
            <div className={`message-bubble ai-bubble ${message.isError ? 'error-bubble' : ''}`}>
              <MarkdownRenderer content={message.aiMessage} />
            </div>
            <div className="message-meta ai-meta">
              <span className="message-time">{formatTime(message.createdAt)}</span>
              {message.tokens && (
                <div className="token-pills">
                  <span className="token-pill" title="Input tokens">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="17 1 21 5 17 9" /><path d="M3 11V9a4 4 0 0 1 4-4h14" /></svg>
                    {message.tokens.input}
                  </span>
                  <span className="token-pill" title="Output tokens">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="7 23 3 19 7 15" /><path d="M21 13v2a4 4 0 0 1-4 4H3" /></svg>
                    {message.tokens.output}
                  </span>
                  <span className="token-pill total-pill" title="Total tokens">Σ {message.tokens.total}</span>
                </div>
              )}
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
