// src/components/AnalysisResult.jsx
// Renders credibility score, manipulation flags, highlighted suspicious text,
// language info, and verified source suggestions.

import React from "react";
import { useHighlighting } from "../hooks/useHighlighting";

// ---- Credibility badge color ----
function scoreColor(score) {
  if (score >= 70) return "#22c55e"; // green
  if (score >= 40) return "#f59e0b"; // amber
  return "#ef4444";                  // red
}

function riskBadgeStyle(risk) {
  const colors = { low: "#22c55e", medium: "#f59e0b", high: "#ef4444" };
  return {
    backgroundColor: colors[risk] || "#6b7280",
    color: "#fff",
    padding: "2px 10px",
    borderRadius: "12px",
    fontSize: "0.75rem",
    fontWeight: 600,
    textTransform: "uppercase",
  };
}

// ---- Sub-components ----
function ScoreRing({ score }) {
  const color = scoreColor(score);
  return (
    <div style={{ textAlign: "center", marginBottom: "1rem" }}>
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="50" fill="none" stroke="#e5e7eb" strokeWidth="12" />
        <circle
          cx="60" cy="60" r="50"
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeDasharray={`${(score / 100) * 314} 314`}
          strokeLinecap="round"
          transform="rotate(-90 60 60)"
        />
        <text x="60" y="55" textAnchor="middle" fontSize="22" fontWeight="bold" fill={color}>
          {score}
        </text>
        <text x="60" y="72" textAnchor="middle" fontSize="11" fill="#6b7280">
          / 100
        </text>
      </svg>
      <p style={{ margin: 0, fontSize: "0.85rem", color: "#6b7280" }}>Credibility Score</p>
    </div>
  );
}

function LanguageBadge({ language }) {
  if (!language) return null;
  return (
    <div style={{ marginBottom: "0.75rem" }}>
      <span style={{ fontWeight: 600 }}>Language Detected: </span>
      <span>{language.language_name}</span>
      {language.is_indian_language && (
        <span style={{ marginLeft: "8px", fontSize: "0.75rem", color: "#6366f1" }}>
          🇮🇳 Regional Language
        </span>
      )}
    </div>
  );
}

function ManipulationPanel({ manipulationScore, riskLevel, flags, sentiment }) {
  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1rem", marginBottom: "1rem" }}>
      <h3 style={{ margin: "0 0 0.5rem" }}>
        Emotional Manipulation{" "}
        <span style={riskBadgeStyle(riskLevel)}>{riskLevel} risk</span>
      </h3>
      <p style={{ margin: "0 0 0.5rem", fontSize: "0.9rem", color: "#6b7280" }}>
        Manipulation score: <strong>{manipulationScore}/100</strong>
      </p>
      {sentiment && (
        <p style={{ margin: "0 0 0.5rem", fontSize: "0.9rem" }}>
          Sentiment: <strong>{sentiment.label}</strong> ({(sentiment.confidence * 100).toFixed(0)}% confidence)
        </p>
      )}
      {flags && Object.keys(flags).length > 0 && (
        <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.2rem", fontSize: "0.85rem" }}>
          {Object.entries(flags)
            .filter(([, v]) => v > 0)
            .map(([key, count]) => (
              <li key={key}>
                {key.replace(/_/g, " ")}: <strong>{count}</strong>
              </li>
            ))}
        </ul>
      )}
    </div>
  );
}

function HighlightedText({ text, suspiciousPhrases }) {
  const { highlightedHTML } = useHighlighting(text, suspiciousPhrases);

  if (!text) return null;
  return (
    <div style={{ marginBottom: "1rem" }}>
      <h3 style={{ marginBottom: "0.5rem" }}>Article Text</h3>
      <style>{`
        .highlight-suspicious {
          background-color: #fef08a;
          border-bottom: 2px solid #f59e0b;
          cursor: help;
        }
      `}</style>
      {/* eslint-disable-next-line react/no-danger */}
      <p
        style={{ fontSize: "0.9rem", lineHeight: 1.7 }}
        dangerouslySetInnerHTML={{ __html: highlightedHTML }}
      />
      {suspiciousPhrases.length > 0 && (
        <p style={{ fontSize: "0.78rem", color: "#f59e0b", margin: 0 }}>
          ⚠️ {suspiciousPhrases.length} suspicious phrase{suspiciousPhrases.length > 1 ? "s" : ""} highlighted
        </p>
      )}
    </div>
  );
}

function SourcePanel({ source }) {
  if (!source) return null;
  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: "8px", padding: "1rem", marginBottom: "1rem" }}>
      <h3 style={{ margin: "0 0 0.5rem" }}>Source: {source.domain}</h3>
      <p style={{ margin: 0, fontSize: "0.9rem" }}>
        Credibility: <strong style={{ color: scoreColor(source.credibility_score) }}>
          {source.credibility_score}/100
        </strong>{" "}
        — {source.label}
      </p>
      {!source.is_known && (
        <p style={{ margin: "0.4rem 0 0", fontSize: "0.8rem", color: "#6b7280" }}>
          ℹ️ This domain is not in our verified database.
        </p>
      )}
    </div>
  );
}

function VerifiedSources({ sources }) {
  if (!sources || sources.length === 0) return null;
  return (
    <div style={{ border: "1px solid #d1fae5", borderRadius: "8px", padding: "1rem", marginBottom: "1rem", background: "#f0fdf4" }}>
      <h3 style={{ margin: "0 0 0.75rem" }}>✅ Verified Sources for this Story</h3>
      <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.85rem" }}>
        {sources.map((s, i) => (
          <li key={i} style={{ marginBottom: "0.4rem" }}>
            <a href={s.url} target="_blank" rel="noopener noreferrer">
              {s.title}
            </a>{" "}
            <span style={{ color: "#6b7280" }}>— {s.source}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ---- Main component ----
/**
 * AnalysisResult — renders the full analysis response from /analyze endpoint
 *
 * Props:
 *   result: object — the JSON response from POST /analyze
 *   originalText: string — the text the user submitted (for highlighting)
 */
export default function AnalysisResult({ result, originalText }) {
  if (!result) return null;

  const {
    credibility_score,
    manipulation_score,
    risk_level,
    language,
    source,
    verified_sources,
    suspicious_phrases,
    flags,
    sentiment,
  } = result;

  return (
    <div style={{ maxWidth: "680px", margin: "0 auto", fontFamily: "system-ui, sans-serif" }}>
      <ScoreRing score={credibility_score} />
      <LanguageBadge language={language} />
      <ManipulationPanel
        manipulationScore={manipulation_score}
        riskLevel={risk_level}
        flags={flags}
        sentiment={sentiment}
      />
      <SourcePanel source={source} />
      <VerifiedSources sources={verified_sources} />
      <HighlightedText text={originalText} suspiciousPhrases={suspicious_phrases} />
    </div>
  );
}