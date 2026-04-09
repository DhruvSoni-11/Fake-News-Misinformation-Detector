/**
 * Simulates an API call to a backend service for text analysis.
 * @param {string} text - The news article or text snippet to analyze.
 * @returns {Promise<Object>} The analysis result.
 */
export const analyzeText = async (text) => {
  // In a production environment with a real backend, you would use axios:
  // const response = await axios.post('https://your-api-domain.com/analyze', { text });
  // return response.data;

  // Mocking the API response for frontend development
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        data: {
          isFake: true,
          confidenceScore: 0.85,
          highlightedPhrases: [
            { text: "shocking truth", reason: "Sensationalism" }
          ]
        }
      });
    }, 1500);
  });
};
