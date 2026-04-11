import React from 'react';
import './CredibilityMeter.css';

function CredibilityMeter({ score, color, invert }) {
  const clamped = Math.max(0, Math.min(100, score));
  const radius = 54;
  const circumference = Math.PI * radius; // half-circle arc length
  const filled = invert
    ? (clamped / 100) * circumference        // manipulation: fill = bad
    : (clamped / 100) * circumference;       // credibility: fill = good
  const offset = circumference - filled;

  return (
    <div className="credibility-meter">
      <svg viewBox="0 0 140 80" width="130" height="75">
        {/* Background track */}
        <path
          d="M 14,70 A 56,56 0 0,1 126,70"
          fill="none"
          stroke="rgba(255,255,255,0.07)"
          strokeWidth="7"
          strokeLinecap="round"
        />
        {/* Filled arc */}
        <path
          className="meter-fill"
          d="M 14,70 A 56,56 0 0,1 126,70"
          fill="none"
          stroke={color || '#4d9fff'}
          strokeWidth="7"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
        {/* Tick marks at 0, 25, 50, 75, 100 */}
        {[0, 25, 50, 75, 100].map((tick) => {
          const angle = (-180 + (tick / 100) * 180) * (Math.PI / 180);
          const cx = 70 + 56 * Math.cos(angle);
          const cy = 70 + 56 * Math.sin(angle);
          return <circle key={tick} cx={cx} cy={cy} r="2.5" fill="rgba(255,255,255,0.1)" />;
        })}
      </svg>
    </div>
  );
}

export default CredibilityMeter;