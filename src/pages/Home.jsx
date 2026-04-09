import React, { useState } from 'react';
import InputBox from '../components/InputBox';
import ResultCard from '../components/ResultCard';
import { analyzeText } from '../services/api';

const scanSignals = [
  'Sensational phrasing',
  'Manipulative certainty',
  'Confidence scoring',
];

const reviewCues = [
  {
    title: 'Emotional pressure',
    description: 'Phrases that push urgency, shock, or fear instead of evidence.',
  },
  {
    title: 'Unsupported certainty',
    description: 'Claims that sound absolute without grounding or sourcing.',
  },
  {
    title: 'Pattern hotspots',
    description: 'Highlighted segments that deserve a second editorial read.',
  },
];

const Home = () => {
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [resultData, setResultData] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (text) => {
    setIsLoading(true);
    setError(null);
    setInputText(text); // Store the original text to pass to the ResultCard for highlighting

    try {
      const response = await analyzeText(text);
      setResultData(response.data);
    } catch (err) {
      setError('An error occurred while analyzing the text. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const wordCount = inputText.trim() ? inputText.trim().split(/\s+/).length : 0;
  const flaggedCount = resultData?.highlightedPhrases?.length ?? 0;
  const reviewState = resultData
    ? resultData.isFake || resultData.confidenceScore > 0.5
      ? 'Elevated'
      : 'Measured'
    : 'Waiting';

  return (
    <div className="app-shell">
      <section className="hero-panel">
        <div className="hero-copy card">
          <span className="eyebrow">Editorial Verification Studio</span>
          <h1>Read the signal behind the story.</h1>
          <p className="hero-summary">
            Paste a headline, article, or viral post and get a sharper visual read on
            tone, certainty, and suspicious language patterns.
          </p>
          <div className="hero-tag-row">
            {scanSignals.map((signal) => (
              <span className="hero-tag" key={signal}>
                {signal}
              </span>
            ))}
          </div>
        </div>

        <aside className="hero-aside card">
          <p className="panel-kicker">Live board</p>
          <h2>What this scan surfaces</h2>
          <div className="signal-list">
            {reviewCues.map((cue) => (
              <div className="signal-item" key={cue.title}>
                <span className="signal-index" aria-hidden="true">
                  {cue.title.slice(0, 2).toUpperCase()}
                </span>
                <div className="signal-copy">
                  <h3>{cue.title}</h3>
                  <p>{cue.description}</p>
                </div>
              </div>
            ))}
          </div>
        </aside>
      </section>

      <main className="workspace-grid">
        <div className="workspace-main">
          <InputBox onSubmit={handleAnalyze} isLoading={isLoading} />

          {error && (
            <div className="feedback-banner feedback-error card" role="alert">
              <p className="panel-kicker">Analysis interrupted</p>
              <p>{error}</p>
            </div>
          )}

          {isLoading && (
            <div className="loading-card card" role="status" aria-live="polite">
              <div className="loading-radar" aria-hidden="true">
                <span className="loading-ring loading-ring-one" />
                <span className="loading-ring loading-ring-two" />
                <span className="loading-core" />
              </div>
              <div className="loading-copy">
                <p className="panel-kicker">Running analysis</p>
                <h3>Scanning tone, certainty, and sensational phrasing</h3>
                <p>
                  Analyzing text patterns and cross-referencing signal hotspots in the
                  submitted copy.
                </p>
                <div className="loading-lines" aria-hidden="true">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            </div>
          )}
        </div>

        <aside className="workspace-side">
          <div className="side-card card">
            <div className="side-card-header">
              <div>
                <p className="panel-kicker">Current scan</p>
                <h3>{reviewState} review pressure</h3>
              </div>
              <span className={`status-dot ${reviewState === 'Elevated' ? 'status-dot-alert' : ''}`} />
            </div>

            <div className="status-row">
              <span>Submitted words</span>
              <strong>{wordCount || 'Waiting'}</strong>
            </div>
            <div className="status-row">
              <span>Flagged phrases</span>
              <strong>{flaggedCount}</strong>
            </div>
            <div className="status-row">
              <span>Engine state</span>
              <strong>{isLoading ? 'Processing' : 'Ready'}</strong>
            </div>
          </div>

          <div className="side-card card">
            <p className="panel-kicker">Review cues</p>
            <h3>Best used for fast editorial triage</h3>
            <ul className="cue-list">
              <li>Paste the most emotionally charged paragraph for the clearest read.</li>
              <li>Use highlights to isolate claims that sound absolute or sensational.</li>
              <li>Pair the score with source-checking before publishing or sharing.</li>
            </ul>
          </div>
        </aside>
      </main>

      {!isLoading && resultData && (
        <ResultCard result={resultData} originalText={inputText} />
      )}
    </div>
  );
};

export default Home;
