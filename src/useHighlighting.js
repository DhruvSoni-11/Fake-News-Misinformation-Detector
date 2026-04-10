// src/hooks/useHighlighting.js
// Highlights suspicious phrases returned by the backend inside displayed article text.
// Usage: const { highlightedHTML } = useHighlighting(text, suspiciousPhrases);

import { useMemo } from "react";

/**
 * @param {string} text - original article/news text to display
 * @param {Array<{phrase: string, start: number, end: number}>} suspiciousPhrases
 *   - array of phrase objects returned by /analyze endpoint
 * @returns {{ highlightedHTML: string }} - safe HTML string with <mark> spans
 */
export function useHighlighting(text, suspiciousPhrases = []) {
  const highlightedHTML = useMemo(() => {
    if (!text || suspiciousPhrases.length === 0) {
      return escapeHtml(text || "");
    }

    // Sort phrases by start position
    const sorted = [...suspiciousPhrases].sort((a, b) => a.start - b.start);

    let result = "";
    let cursor = 0;

    for (const { phrase, start, end } of sorted) {
      if (start < cursor) continue; // skip overlapping
      // Append text before this phrase
      result += escapeHtml(text.slice(cursor, start));
      // Wrap phrase in a highlighted span
      result += `<mark class="highlight-suspicious" title="Potentially manipulative language">${escapeHtml(
        text.slice(start, end)
      )}</mark>`;
      cursor = end;
    }

    // Append remaining text
    result += escapeHtml(text.slice(cursor));
    return result;
  }, [text, suspiciousPhrases]);

  return { highlightedHTML };
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}