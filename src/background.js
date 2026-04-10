const API_BASE = "http://localhost:8000";

// ---------------------------------------------------------------------------
// Context menu — right-click on selected text → "Check Credibility"
// ---------------------------------------------------------------------------
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "check-credibility",
    title: "Check Credibility with AI Analyzer",
    contexts: ["selection"],
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== "check-credibility") return;

  const selectedText = info.selectionText?.trim();
  if (!selectedText || selectedText.length < 20) return;

  try {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: selectedText, url: tab.url }),
    });

    if (!response.ok) return;
    const data = await response.json();

    // Update badge with credibility score
    const score = data.credibility_score;
    const color = score >= 70 ? "#22c55e" : score >= 40 ? "#f59e0b" : "#ef4444";

    chrome.action.setBadgeText({ text: String(score), tabId: tab.id });
    chrome.action.setBadgeBackgroundColor({ color, tabId: tab.id });

    // Show a notification
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon48.png",
      title: "Credibility Score: " + score + "/100",
      message:
        data.risk_level === "high"
          ? "⚠️ High manipulation risk detected."
          : data.risk_level === "medium"
          ? "⚡ Medium manipulation risk."
          : "✅ Content appears credible.",
    });
  } catch (err) {
    console.error("Background fetch error:", err);
  }
});

// Clear badge when user navigates away
chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status === "loading") {
    chrome.action.setBadgeText({ text: "", tabId });
  }
});