import React, { useState } from 'react';

const samplePrompts = [
  {
    label: 'Viral Headline',
    text: 'Doctors are stunned by the shocking truth behind a common kitchen ingredient that could cure nearly everything overnight.',
  },
  {
    label: 'Election Claim',
    text: 'A leaked report proves the entire election was secretly overturned in three states, but the media refuses to tell the public.',
  },
  {
    label: 'Health Rumor',
    text: 'This miracle drink is being hidden by big companies because it can eliminate every toxin from your body in 24 hours.',
  },
];

const InputBox = ({ onSubmit, isLoading }) => {
  const [text, setText] = useState('');
  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;

  const handleSubmit = (e) => {
    e.preventDefault();
    // Prevent submission if it's empty or already loading
    if (text.trim() && !isLoading) {
      onSubmit(text);
    }
  };

  return (
    <div className="analysis-card card">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Story intake</p>
          <h2>Drop in the text you want to audit</h2>
        </div>
        <span className="panel-badge">{text.length} chars</span>
      </div>

      <form className="analysis-form" onSubmit={handleSubmit}>
        <label className="sr-only" htmlFor="story-input">
          News text input
        </label>

        <div className="textarea-shell">
        <textarea
          id="story-input"
          className="input-textarea"
          placeholder="Paste the news article or text snippet here to analyze..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={isLoading}
          aria-label="News text input"
        />

          <div className="textarea-footer">
            <p>Tip: include the most emotionally charged paragraph for the sharpest signal.</p>
            <span>{wordCount} words</span>
          </div>
        </div>

        <div className="action-row">
          <div className="prompt-hints">
            {samplePrompts.map((prompt) => (
              <button
                key={prompt.label}
                type="button"
                className="prompt-chip"
                onClick={() => setText(prompt.text)}
                disabled={isLoading}
              >
                {prompt.label}
              </button>
            ))}
          </div>

          <button
            type="submit"
            className="btn-primary btn-analyze"
            disabled={isLoading || !text.trim()}
          >
            {isLoading ? 'Scanning Story...' : 'Analyze Story'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default InputBox;
