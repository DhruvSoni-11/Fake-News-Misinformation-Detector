import React from 'react';
import CredibilityMeter from './CredibilityMeter';
import HighlightedText from './HighlightedText';
import './ResultCard.css';

/**
 * Real /analyze response shape:
 * {
 *   cleaned_text:             string   — translated/cleaned version of the input
 *   score:                    number   — 0–100 credibility score
 *   label:                    string   — "Real" | "Suspicious" | "Fake"
 *   keywords_detected:        string[] — manipulation keywords found
 *   sentiment:                string   — "Positive" | "Negative" | "Neutral"
 *   sentiment_polarity:       number   — -1.0 to 1.0
 *   sentiment_subjectivity:   number   — 0.0 to 1.0
 *   word_count:               number
 *   source:                   string   — "text" | "url"
 * }
 */
function ResultCard({ result, originalText }) {
  const {
    cleaned_text,
    score,
    label,
    keywords_detected,
    sentiment,
    sentiment_polarity,
    sentiment_subjectivity,
    word_count,
    source,
  } = result;

  const credScore = typeof score === 'number' ? score : 50;

  // Map label → visual class
  const labelLower = (label || '').toLowerCase();
  const verdictClass =
    labelLower === 'real' ? 'verdict-real' :
    labelLower === 'fake' ? 'verdict-fake' :
    'verdict-uncertain'; // "suspicious" or anything else

  const scoreColor =
    credScore >= 65 ? '#00e676' :
    credScore >= 40 ? '#ffb830' :
    '#ff3b3b';

  // Sentiment tag colour
  const sentimentClass =
    (sentiment || '').toLowerCase() === 'positive' ? 'tag-green' :
    (sentiment || '').toLowerCase() === 'negative' ? 'tag-red'  :
    'tag-default';

  // Polarity bar width (map -1…1 to 0…100%)
  const polarityPct = Math.round(((sentiment_polarity + 1) / 2) * 100);

  // Subjectivity bar
  const subjectivityPct = Math.round((sentiment_subjectivity || 0) * 100);

  return (
    <div className="result-card" role="region" aria-label="Analysis results">

      {/* ── Header ── */}
      <div className="result-header">
        <span className="result-label">ANALYSIS COMPLETE</span>
        <span className={`verdict-badge ${verdictClass}`}>
          {(label || 'UNKNOWN').toUpperCase()}
        </span>
      </div>

      {/* ── Score + top stats ── */}
      <div className="scores-row">
        <div className="score-block">
          <CredibilityMeter score={credScore} color={scoreColor} />
          <div className="score-label">
            <span className="score-number" style={{ color: scoreColor }}>
              {Math.round(credScore)}
            </span>
            <span className="score-unit">/100</span>
          </div>
          <p className="score-caption">credibility score</p>
        </div>

        <div className="score-divider" />

        <div className="score-stats">
          {/* Sentiment */}
          <div className="stat-row">
            <span className="stat-label">SENTIMENT</span>
            <span className={`tag ${sentimentClass}`}>
              {(sentiment || 'N/A').toUpperCase()}
            </span>
          </div>

          {/* Polarity bar */}
          <div className="stat-row">
            <span className="stat-label">POLARITY</span>
            <div className="bar-wrap">
              <div
                className="bar-fill"
                style={{
                  width: `${polarityPct}%`,
                  background:
                    sentiment_polarity > 0.1 ? '#00e676' :
                    sentiment_polarity < -0.1 ? '#ff3b3b' :
                    '#ffb830',
                }}
              />
            </div>
            <span className="stat-val">
              {sentiment_polarity != null ? sentiment_polarity.toFixed(2) : '—'}
            </span>
          </div>

          {/* Subjectivity bar */}
          <div className="stat-row">
            <span className="stat-label">SUBJECTIVITY</span>
            <div className="bar-wrap">
              <div
                className="bar-fill"
                style={{
                  width: `${subjectivityPct}%`,
                  background: subjectivityPct > 60 ? '#ffb830' : '#4d9fff',
                }}
              />
            </div>
            <span className="stat-val">
              {sentiment_subjectivity != null ? sentiment_subjectivity.toFixed(2) : '—'}
            </span>
          </div>

          {/* Word count + source */}
          <div className="stat-row">
            <span className="stat-label">WORDS</span>
            <span className="stat-val-plain">{word_count ?? '—'}</span>
            {source && (
              <span className="tag tag-default" style={{ marginLeft: 'auto' }}>
                via {source.toUpperCase()}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* ── Keywords detected ── */}
      {keywords_detected && keywords_detected.length > 0 && (
        <div className="section-block">
          <h3 className="detail-title">MANIPULATION KEYWORDS DETECTED</h3>
          <div className="tags">
            {keywords_detected.map((kw, i) => (
              <span key={i} className="tag tag-red">
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* ── Cleaned / translated text ── */}
      {cleaned_text && cleaned_text !== originalText && (
        <div className="section-block">
          <h3 className="detail-title">
            CLEANED TEXT
            {source === 'text' && originalText && originalText.trim() !== cleaned_text.trim()
              ? ' (TRANSLATED TO ENGLISH)'
              : ''}
          </h3>
          <p className="cleaned-text">{cleaned_text}</p>
        </div>
      )}

      {/* ── Original text with keywords highlighted ── */}
      {originalText && keywords_detected && keywords_detected.length > 0 && (
        <div className="section-block">
          <h3 className="detail-title">ORIGINAL TEXT — KEYWORDS HIGHLIGHTED</h3>
          <HighlightedText text={originalText} keywords={keywords_detected} />
        </div>
      )}
    </div>
  );
}

export default ResultCard;