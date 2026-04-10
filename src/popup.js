const API_BASE = "http://localhost:8000"; // Change to your deployed backend URL

const analyzeBtn = document.getElementById("analyzeBtn");
const resultDiv = document.getElementById("result");

function scoreColor(score) {
  if (score >= 70) return "#22c55e";
  if (score >= 40) return "#f59e0b";
  return "#ef4444";
}

function renderResult(data) {
  const { credibility_score, manipulation_score, risk_level, language, source, verified_sources } = data;
  const color = scoreColor(credibility_score);

  const langLine = language?.language_name
    ? `<p class="label">🌐 Language: <strong>${language.language_name}</strong>${language.is_indian_language ? " 🇮🇳" : ""}</p>`
    : "";

  const sourceLine = source
    ? `<p class="label">🔗 Source: <strong>${source.domain}</strong> — ${source.label} (${source.credibility_score}/100)</p>`
    : "";

  const sourceLinks =
    verified_sources && verified_sources.length > 0
      ? `<div class="sources"><strong>✅ Verified coverage:</strong><ul style="margin:4px 0;padding-left:14px">` +
        verified_sources
          .slice(0, 3)
          .map((s) => `<li><a href="${s.url}" target="_blank">${s.title}</a></li>`)
          .join("") +
        `</ul></div>`
      : "";

  resultDiv.innerHTML = `
    <div style="margin-top:10px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-weight:700;font-size:0.9rem">Credibility Score</span>
        <span style="font-weight:800;font-size:1.2rem;color:${color}">${credibility_score}<span style="font-size:0.7rem;color:#6b7280">/100</span></span>
      </div>
      <div class="score-bar">
        <div class="score-fill" style="width:${credibility_score}%;background:${color}"></div>
      </div>

      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px">
        <span style="font-size:0.8rem;color:#374151">Manipulation Risk</span>
        <span class="badge ${risk_level}">${risk_level.toUpperCase()}</span>
      </div>
      <div class="score-bar" style="margin-top:4px">
        <div class="score-fill" style="width:${manipulation_score}%;background:#f59e0b"></div>
      </div>
      <p class="label">Manipulation score: ${manipulation_score}/100</p>

      ${langLine}
      ${sourceLine}
      ${sourceLinks}
    </div>
  `;
}

function renderError(message) {
  resultDiv.innerHTML = `<p class="error">❌ ${message}</p>`;
}

analyzeBtn.addEventListener("click", async () => {
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing…";
  resultDiv.innerHTML = `<p class="label" style="margin-top:8px">Fetching page content…</p>`;

  try {
    // 1. Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // 2. Ask content script for the page text
    let pageData;
    try {
      pageData = await chrome.tabs.sendMessage(tab.id, { type: "GET_PAGE_TEXT" });
    } catch {
      // Content script may not be injected on chrome:// pages etc.
      renderError("Cannot analyze this page (restricted URL).");
      return;
    }

    if (!pageData?.text || pageData.text.trim().length < 20) {
      renderError("Not enough text found on this page.");
      return;
    }

    resultDiv.innerHTML = `<p class="label" style="margin-top:8px">Running AI analysis…</p>`;

    // 3. Call backend /analyze
    const response = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: pageData.text, url: pageData.url }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      renderError(err.detail || `Server error (${response.status})`);
      return;
    }

    const data = await response.json();
    renderResult(data);

    // 4. Store last result locally for history page
    chrome.storage.local.get("history", ({ history = [] }) => {
      history.unshift({ url: pageData.url, score: data.credibility_score, ts: Date.now() });
      chrome.storage.local.set({ history: history.slice(0, 50) });
    });
  } catch (err) {
    renderError("Could not connect to the backend. Make sure it is running.");
    console.error(err);
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze This Page";
  }
});