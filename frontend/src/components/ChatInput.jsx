import React, { useState, useRef, useEffect } from 'react';

const SUGGESTIONS = [
  "Explain how multi-agent systems work",
  "What is RAG and how does it improve LLMs?",
  "Write a Python function to merge two sorted arrays",
  "Summarize the key concepts of LangGraph",
];

/**
 * Auto-resizing chat input with send button and suggestion chips.
 */
export default function ChatInput({ onSend, isSending, hasMessages }) {
  const [value, setValue] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 180) + 'px';
  }, [value]);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || isSending) return;
    onSend(trimmed);
    setValue('');
    // Reset height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setValue(suggestion);
    textareaRef.current?.focus();
  };

  return (
    <div className="chat-input-wrapper">
      {/* Suggestion chips — shown when no messages yet */}
      {!hasMessages && (
        <div className="suggestions-container">
          <p className="suggestions-label">Try asking...</p>
          <div className="suggestions-grid">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                className="suggestion-chip"
                onClick={() => handleSuggestionClick(s)}
                type="button"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                </svg>
                <span>{s}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="input-bar">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything..."
          rows={1}
          disabled={isSending}
          id="chat-input-textarea"
          aria-label="Chat message input"
        />
        <button
          className={`send-button ${value.trim() && !isSending ? 'active' : ''}`}
          onClick={handleSubmit}
          disabled={!value.trim() || isSending}
          type="button"
          id="send-message-btn"
          aria-label="Send message"
        >
          {isSending ? (
            <div className="send-spinner" />
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </div>

      <p className="input-hint">
        Press <kbd>Enter</kbd> to send · <kbd>Shift + Enter</kbd> for new line
      </p>
    </div>
  );
}
