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
export default function ChatInput({ onSend, isSending, hasMessages, uploadAttachment, deleteAttachment, activeSessionId }) {
  const [value, setValue] = useState('');
  const [pendingAttachments, setPendingAttachments] = useState([]);
  const [tempSessionId, setTempSessionId] = useState(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 180) + 'px';
  }, [value]);

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    e.target.value = '';
    
    const tempId = crypto.randomUUID();
    const newAtt = {
      id: tempId,
      filename: file.name,
      mime_type: file.type,
      isUploading: true
    };
    
    setPendingAttachments(prev => [...prev, newAtt]);
    
    try {
      let sessionId = activeSessionId || tempSessionId;
      if (!sessionId) {
        sessionId = crypto.randomUUID();
        setTempSessionId(sessionId);
      }
      
      const att = await uploadAttachment(file, sessionId);
      setPendingAttachments(prev => prev.map(a => a.id === tempId ? { ...att, isUploading: false } : a));
    } catch (err) {
      alert("Failed to upload attachment: " + err.message);
      setPendingAttachments(prev => prev.filter(a => a.id !== tempId));
    }
  };

  const removeAttachment = async (id) => {
    const att = pendingAttachments.find(a => a.id === id);
    if (!att) return;
    
    setPendingAttachments(prev => prev.filter(a => a.id !== id));
    
    if (!att.isUploading && deleteAttachment) {
      await deleteAttachment(att.id);
    }
  };

  const isUploadingAny = pendingAttachments.some(a => a.isUploading);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if ((!trimmed && pendingAttachments.length === 0) || isSending || isUploadingAny) return;
    onSend(trimmed, pendingAttachments, tempSessionId);
    setValue('');
    setPendingAttachments([]);
    setTempSessionId(null);
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

      {/* Pending Attachments */}
      {pendingAttachments.length > 0 && (
        <div className="pending-attachments" style={{ display: 'flex', gap: '8px', marginBottom: '8px', flexWrap: 'wrap', padding: '0 16px' }}>
          {pendingAttachments.map(att => (
            <div key={att.id} style={{ display: 'flex', alignItems: 'center', background: '#374151', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
              {att.isUploading ? (
                <div className="send-spinner" style={{ width: '14px', height: '14px', marginRight: '6px', borderWidth: '2px' }} />
              ) : (
                <span style={{ marginRight: '6px', display: 'flex' }}>
                  {!att.mime_type ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                      <polyline points="13 2 13 9 20 9" />
                    </svg>
                  ) : att.mime_type.includes('image') ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                      <circle cx="8.5" cy="8.5" r="1.5" />
                      <polyline points="21 15 16 10 5 21" />
                    </svg>
                  ) : att.mime_type.includes('pdf') ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                      <path d="M16 13H8" />
                      <path d="M16 17H8" />
                      <path d="M10 9H8" />
                    </svg>
                  ) : (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                      <polyline points="13 2 13 9 20 9" />
                    </svg>
                  )}
                </span>
              )}
              <span style={{ maxWidth: '150px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: att.isUploading ? '#9ca3af' : '#f3f4f6' }}>{att.filename}</span>
              <button onClick={() => removeAttachment(att.id)} style={{ background: 'none', border: 'none', color: '#ef4444', marginLeft: '4px', cursor: 'pointer', padding: 0 }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="input-bar">
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={handleFileChange} 
        />
        <div style={{ position: 'relative' }}>
          <button
            className="attachment-button"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            disabled={isSending || isUploadingAny}
            type="button"
            title="Attach file"
            style={{ background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer', padding: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ transition: 'transform 0.2s', transform: isMenuOpen ? 'rotate(45deg)' : 'rotate(0)' }}>
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
          </button>

          {isMenuOpen && (
            <div 
              style={{ 
                position: 'absolute', 
                bottom: '100%', 
                left: '0', 
                marginBottom: '12px',
                background: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '12px',
                padding: '8px',
                boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.3)',
                zIndex: 50,
                width: 'max-content',
                animation: 'fadeIn 0.2s ease-out'
              }}
            >
              <button 
                onClick={() => {
                  setIsMenuOpen(false);
                  fileInputRef.current?.click();
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  width: '100%',
                  textAlign: 'left',
                  transition: 'background 0.2s',
                  gap: '12px'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#374151'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <div style={{ 
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8',
                  borderRadius: '8px', padding: '8px'
                }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontSize: '14px', fontWeight: '500', color: '#f3f4f6' }}>Upload from computer</span>
                  <span style={{ fontSize: '12px', color: '#9ca3af', marginTop: '2px' }}>Images, documents, or PDFs</span>
                </div>
              </button>
            </div>
          )}
        </div>
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
          className={`send-button ${(value.trim() || pendingAttachments.length > 0) && !isSending && !isUploadingAny ? 'active' : ''}`}
          onClick={handleSubmit}
          disabled={(!value.trim() && pendingAttachments.length === 0) || isSending || isUploadingAny}
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
