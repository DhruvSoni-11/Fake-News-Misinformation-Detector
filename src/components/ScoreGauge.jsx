import React from 'react';
import { formatPercentage } from '../utils/helpers';

const ScoreGauge = ({ score }) => {
  const boundedScore = Math.max(0, Math.min(1, score || 0));

  // Determine the color based on the likelihood of being fake
  const getGaugeColor = () => {
    if (boundedScore >= 0.7) return 'var(--fake-color)';    // High probability of fake
    if (boundedScore >= 0.4) return 'var(--warning-color)'; // Medium/Uncertain
    return 'var(--real-color)';                              // Likely real
  };

  const toneLabel =
    boundedScore >= 0.7
      ? 'High editorial risk'
      : boundedScore >= 0.4
        ? 'Mixed confidence'
        : 'Lower editorial risk';

  return (
    <div className="gauge-card">
      <div className="gauge-header">
        <div>
          <p className="panel-kicker">Confidence meter</p>
          <h3>{toneLabel}</h3>
        </div>
        <span className="gauge-score">{formatPercentage(boundedScore)}</span>
      </div>

      <div
        className="gauge-track"
        role="progressbar"
        aria-valuenow={boundedScore * 100}
        aria-valuemin="0"
        aria-valuemax="100"
      >
        <div className="gauge-zones" aria-hidden="true">
          <span className="gauge-zone gauge-zone-low" />
          <span className="gauge-zone gauge-zone-mid" />
          <span className="gauge-zone gauge-zone-high" />
        </div>
        <div
          className="gauge-fill"
          style={{
            width: `${boundedScore * 100}%`,
            backgroundColor: getGaugeColor(),
          }}
        />
        <div
          className="gauge-thumb"
          style={{ left: `${Math.max(4, Math.min(96, boundedScore * 100))}%` }}
        />
      </div>

      <div className="gauge-scale" aria-hidden="true">
        <span>Reliable</span>
        <span>Mixed</span>
        <span>High risk</span>
      </div>
    </div>
  );
};

export default ScoreGauge;
