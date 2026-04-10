const API_BASE = "http://localhost:8000"; // Change to your deployed backend URL

function extractArticleText() {
  // Try <article> tag first, fall back to <main>, then body paragraphs
  const article = document.querySelector("article") || document.querySelector("main");
  if (article) return article.innerText.slice(0, 3000);
  // Fallback: concatenate all <p> tags
  return Array.from(document.querySelectorAll("p"))
    .map((p) => p.innerText)
    .join(" ")
    .slice(0, 3000);
}

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "GET_PAGE_TEXT") {
    const text = extractArticleText();
    const url = window.location.href;
    sendResponse({ text, url });
  }
  return true; // Keep channel open for async
});