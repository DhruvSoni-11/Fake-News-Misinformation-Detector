import React, { useState } from 'react';
import ResultCard from './ResultCard';
import './Analyzer.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

function Analyzer() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [submittedText, setSubmittedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze.');
      return;
    }
    setError('');
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text.trim() }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(
          Array.isArray(errData.detail)
            ? errData.detail.map((d) => d.msg).join(', ')
            : errData.detail || `Server error: ${res.status}`
        );
      }

      const data = await res.json();
      setResult(data);
      setSubmittedText(text);
    } catch (err) {
      setError(
        err.message ||
          'Failed to connect. Make sure the backend is running:\n  uvicorn main:app --reload --port 5000'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText('');
    setResult(null);
    setError('');
    setSubmittedText('');
  };

  return (
    <div className="analyzer">
      <div className="analyzer-hero">
        <h1 className="hero-title">
          Detect <span className="hero-accent">Fake News</span>
          <br />& Misinformation
        </h1>
        <p className="hero-sub">
          Paste an article, headline, or social post. Supports Hindi and 10 regional Indian
          languages. Scores credibility, flags emotional manipulation, and surfaces verified sources.
        </p>
      </div>

      <div className="input-card">
        <textarea
          className="text-input"
          placeholder="Paste a news article, headline, tweet… Hindi & regional languages supported"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.ctrlKey) handleAnalyze();
          }}
          rows={8}
        />
        <div className="input-footer">
          <span className="input-hint">Ctrl+Enter to analyze</span>
          <div className="input-actions">
            {text && (
              <button className="btn-ghost" onClick={handleClear}>
                CLEAR
              </button>
            )}
            <button
              className="btn-analyze"
              onClick={handleAnalyze}
              disabled={loading || !text.trim()}
            >
              {loading ? (
                <span className="btn-loading">
                  <span className="spinner" />
                  SCANNING…
                </span>
              ) : (
                'ANALYZE'
              )}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-icon">!</span>
          <pre className="error-text">{error}</pre>
        </div>
      )}

      {loading && (
        <div className="loading-state">
          <div className="loading-bars">
            {[...Array(12)].map((_, i) => (
              <div
                key={i}
                className="loading-bar"
                style={{ animationDelay: `${i * 0.08}s` }}
              />
            ))}
          </div>
          <p className="loading-text">Running NLP pipeline…</p>
        </div>
      )}

      {result && !loading && (
        <ResultCard result={result} originalText={submittedText} />
      )}
    </div>
  );
}

export default Analyzer;