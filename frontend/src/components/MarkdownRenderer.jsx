import React, { useCallback } from 'react';

/**
 * Converts a markdown string into safe HTML.
 * Supports: headers, bold, italic, inline code, fenced code blocks (with copy),
 * ordered/unordered lists, horizontal rules, blockquotes, and links.
 */
function markdownToHtml(text) {
  if (!text) return '';

  // Escape HTML
  let src = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Extract fenced code blocks first to protect them
  const codeBlocks = [];
  src = src.replace(/```(\w*)\n([\s\S]*?)```/g, (_match, lang, code) => {
    const language = lang || 'plaintext';
    const id = 'cb-' + Math.random().toString(36).substring(2, 9);
    const idx = codeBlocks.length;
    codeBlocks.push({ language, code: code.trimEnd(), id });
    return `\n__CODEBLOCK_${idx}__\n`;
  });

  // Process line by line
  const lines = src.split('\n');
  const html = [];
  let inUl = false, inOl = false, inBlockquote = false, inParagraph = false;

  const closeAll = () => {
    if (inUl) { html.push('</ul>'); inUl = false; }
    if (inOl) { html.push('</ol>'); inOl = false; }
    if (inBlockquote) { html.push('</blockquote>'); inBlockquote = false; }
    if (inParagraph) { html.push('</p>'); inParagraph = false; }
  };

  const closeParagraph = () => {
    if (inParagraph) { html.push('</p>'); inParagraph = false; }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Code block placeholder
    if (trimmed.match(/^__CODEBLOCK_\d+__$/)) {
      closeAll();
      html.push(trimmed);
      continue;
    }

    // Blank line
    if (trimmed === '') {
      closeAll();
      continue;
    }

    // Header
    const headerMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (headerMatch) {
      closeAll();
      const lvl = headerMatch[1].length;
      html.push(`<h${lvl}>${applyInline(headerMatch[2])}</h${lvl}>`);
      continue;
    }

    // Horizontal rule
    if (/^(---|\*\*\*|___)$/.test(trimmed)) {
      closeAll();
      html.push('<hr />');
      continue;
    }

    // Blockquote
    if (trimmed.startsWith('&gt; ') || trimmed === '&gt;') {
      closeParagraph();
      if (!inBlockquote) { html.push('<blockquote>'); inBlockquote = true; }
      html.push(`<p>${applyInline(trimmed.replace(/^&gt;\s?/, ''))}</p>`);
      continue;
    } else if (inBlockquote) {
      html.push('</blockquote>');
      inBlockquote = false;
    }

    // Unordered list
    const ulMatch = trimmed.match(/^[-*+]\s+(.+)$/);
    if (ulMatch) {
      closeParagraph();
      if (inOl) { html.push('</ol>'); inOl = false; }
      if (!inUl) { html.push('<ul>'); inUl = true; }
      html.push(`<li>${applyInline(ulMatch[1])}</li>`);
      continue;
    }

    // Ordered list
    const olMatch = trimmed.match(/^\d+\.\s+(.+)$/);
    if (olMatch) {
      closeParagraph();
      if (inUl) { html.push('</ul>'); inUl = false; }
      if (!inOl) { html.push('<ol>'); inOl = true; }
      html.push(`<li>${applyInline(olMatch[1])}</li>`);
      continue;
    }

    // Close lists if we're not in one anymore
    if (inUl) { html.push('</ul>'); inUl = false; }
    if (inOl) { html.push('</ol>'); inOl = false; }

    // Paragraph
    if (!inParagraph) {
      html.push('<p>');
      inParagraph = true;
      html.push(applyInline(line));
    } else {
      html.push('<br />' + applyInline(line));
    }
  }

  closeAll();

  let result = html.join('\n');

  // Restore code blocks
  codeBlocks.forEach((block, idx) => {
    const blockHtml = `<pre class="code-block" data-lang="${block.language}"><div class="code-header"><span class="code-lang">${block.language.toUpperCase()}</span><button class="code-copy-btn" data-code-id="${block.id}" type="button"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg><span>Copy</span></button></div><code id="${block.id}">${block.code}</code></pre>`;
    result = result.replace(`__CODEBLOCK_${idx}__`, blockHtml);
  });

  return result;
}

/** Apply inline formatting: bold, italic, inline code, links */
function applyInline(text) {
  if (!text) return '';
  let out = text;
  // Links [text](url)
  out = out.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  // Bold **text**
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  // Bold __text__
  out = out.replace(/__([^_]+)__/g, '<strong>$1</strong>');
  // Italic *text*
  out = out.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  // Italic _text_
  out = out.replace(/\b_([^_]+)_\b/g, '<em>$1</em>');
  // Inline code `text`
  out = out.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
  return out;
}

export default function MarkdownRenderer({ content }) {
  const htmlContent = markdownToHtml(content);

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

  return (
    <div
      className="markdown-body"
      onClick={handleClick}
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  );
}
