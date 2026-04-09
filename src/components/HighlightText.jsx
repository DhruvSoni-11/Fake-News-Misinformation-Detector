import React from 'react';

const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const HighlightText = ({ text, highlights }) => {
  // Function to process the text and inject highlighted spans
  const getHighlightedText = () => {
    if (!text) {
      return 'No original text available for annotation yet.';
    }

    if (!highlights || highlights.length === 0) {
      return text;
    }

    let processedText = [text];

    // Iterate through each highlight and split the text chunks accordingly
    highlights.forEach((highlight) => {
      if (!highlight?.text) {
        return;
      }

      const newProcessedText = [];
      
      processedText.forEach((chunk) => {
        // If the chunk is a string, check if it contains the highlight text
        if (typeof chunk === 'string') {
          // Case-insensitive split that captures the matching text
          const parts = chunk.split(new RegExp(`(${escapeRegExp(highlight.text)})`, 'gi'));
          
          parts.forEach((part) => {
            if (part.toLowerCase() === highlight.text.toLowerCase()) {
              newProcessedText.push({ type: 'highlight', text: part, reason: highlight.reason });
            } else if (part) {
              newProcessedText.push(part);
            }
          });
        } else {
          // If it's already a processed highlight object, just keep it
          newProcessedText.push(chunk);
        }
      });
      
      processedText = newProcessedText;
    });

    // Render the final array of strings and highlight objects
    return processedText.map((chunk, index) => {
      if (typeof chunk === 'string') {
        return <React.Fragment key={index}>{chunk}</React.Fragment>;
      }
      return (
        <span
          key={index}
          className="highlight-span"
          data-reason={chunk.reason}
          title={chunk.reason} // Fallback for accessibility
          aria-label={`${chunk.text}: ${chunk.reason}`}
        >
          {chunk.text}
        </span>
      );
    });
  };

  return (
    <div className="analyzed-text">
      {getHighlightedText()}
    </div>
  );
};

export default HighlightText;
