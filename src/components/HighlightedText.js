import React from 'react';
import './HighlightedText.css';

/**
 * Highlights every occurrence of each keyword (case-insensitive) inside text.
 * keywords: string[]  — e.g. ["shocking", "secret"]
 */
function HighlightedText({ text, keywords }) {
  if (!text || !keywords || keywords.length === 0) return null;

  // Build a regex that matches any keyword, case-insensitive
  const escaped = keywords.map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const pattern = new RegExp(`(${escaped.join('|')})`, 'gi');

  const parts = text.split(pattern);

  return (
    <div className="highlighted-text">
      {parts.map((part, i) =>
        pattern.test(part) ? (
          <mark key={i} className="suspicious-phrase" title="Manipulation keyword">
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </div>
  );
}

export default HighlightedText;