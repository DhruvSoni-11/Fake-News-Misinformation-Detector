import React from 'react';
import ScoreGauge from './ScoreGauge';
import HighlightText from './HighlightText';
import { formatPercentage } from '../utils/helpers';

const ResultCard = ({ result, originalText }) => {
  if (!result) return null;

  const { isFake, confidenceScore, highlightedPhrases } = result;
  const needsReview = isFake || confidenceScore > 0.5;
  const uniqueReasons = Array.from(
    new Set((highlightedPhrases || []).map((phrase) => phrase.reason).filter(Boolean))
  );
  const statusLabel = needsReview ? 'Likely Fake News' : 'Likely Real News';
  const statusSummary = needsReview
    ? 'The language carries stronger signs of manipulation, sensationalism, or unsupported certainty.'
    : 'The copy appears more measured, with fewer signals that suggest overt manipulation.'
    ;
  const signalProfile =
    confidenceScore >= 0.7 ? 'High volatility' : confidenceScore >= 0.4 ? 'Mixed signal' : 'Calmer tone';

  return (
    <section className="result-card card">
      <div className="result-header">
        <div>
          <p className="panel-kicker">Analysis dossier</p>
          <h2>{statusLabel}</h2>
          <p className="result-summary">{statusSummary}</p>
        </div>
        <div className={`result-pill ${needsReview ? 'status-fake' : 'status-real'}`}>
          {needsReview ? 'Escalate' : 'Monitor'}
        </div>
      </div>

      <div className="result-metrics">
        <div className="metric-tile">
          <span className="metric-label">Confidence</span>
          <strong className="metric-value">{formatPercentage(confidenceScore)}</strong>
          <p className="metric-note">Returned probability from the current analysis model.</p>
        </div>
        <div className="metric-tile">
          <span className="metric-label">Flagged phrases</span>
          <strong className="metric-value">{highlightedPhrases?.length || 0}</strong>
          <p className="metric-note">Highlighted segments worth a second editorial read.</p>
        </div>
        <div className="metric-tile">
          <span className="metric-label">Signal profile</span>
          <strong className="metric-value">{signalProfile}</strong>
          <p className="metric-note">A quick read on how aggressive the language feels.</p>
        </div>
      </div>

      <ScoreGauge score={confidenceScore} />

      <div className="detail-grid">
        <div className="detail-card">
          <div className="detail-heading">
            <h3>Detected patterns</h3>
            <span>{uniqueReasons.length} cues</span>
          </div>

          {uniqueReasons.length > 0 ? (
            <div className="reason-list">
              {uniqueReasons.map((reason) => (
                <span className="reason-chip" key={reason}>
                  {reason}
                </span>
              ))}
            </div>
          ) : (
            <p className="detail-note">
              No specific suspicious phrases were returned for this submission.
            </p>
          )}
        </div>

        <div className="detail-card detail-card-wide">
          <div className="detail-heading">
            <h3>Marked transcript</h3>
            <span>Hover highlights for detail</span>
          </div>
          <p className="detail-note">
            Highlighted sections show where the text triggered suspicion in the scan.
          </p>
          <HighlightText text={originalText} highlights={highlightedPhrases} />
        </div>
      </div>
    </section>
  );
};

export default ResultCard;
