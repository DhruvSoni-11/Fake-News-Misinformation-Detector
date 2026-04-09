/**
 * Converts a decimal score (0 to 1) into a formatted percentage string.
 * @param {number} decimal - The decimal score to format.
 * @returns {string} The formatted percentage (e.g., "85%").
 */
export const formatPercentage = (decimal) => {
  if (typeof decimal !== 'number') return '0%';
  return `${Math.round(decimal * 100)}%`;
};