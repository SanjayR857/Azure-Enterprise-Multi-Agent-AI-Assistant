import React, { useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function MarkdownRenderer({ content }) {
  const handleClick = useCallback((e) => {
    const copyBtn = e.target.closest('.code-copy-btn');
    if (!copyBtn) return;

    const codeId = copyBtn.getAttribute('data-code-id');
    const codeEl = document.getElementById(codeId);
    if (!codeEl) return;

    navigator.clipboard.writeText(codeEl.textContent).then(() => {
      const span = copyBtn.querySelector('span');
      if (span) {
        span.textContent = 'Copied!';
        setTimeout(() => { span.textContent = 'Copy'; }, 2000);
      }
    });
  }, []);

  const components = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      if (!inline && match) {
        const lang = match[1];
        const codeId = 'cb-' + Math.random().toString(36).substring(2, 9);
        return (
          <div className="code-block" data-lang={lang}>
            <div className="code-header">
              <span className="code-lang">{lang.toUpperCase()}</span>
              <button className="code-copy-btn" data-code-id={codeId} type="button">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
                <span>Copy</span>
              </button>
            </div>
            <pre style={{ margin: 0, padding: 0, background: 'transparent' }}>
              <code id={codeId} className={className} {...props}>
                {children}
              </code>
            </pre>
          </div>
        );
      }
      return (
        <code className="inline-code" {...props}>
          {children}
        </code>
      );
    }
  };

  return (
    <div className="markdown-body" onClick={handleClick}>
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        components={components}
      >
        {content || ''}
      </ReactMarkdown>
    </div>
  );
}
