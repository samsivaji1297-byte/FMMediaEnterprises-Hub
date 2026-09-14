document.addEventListener("DOMContentLoaded", () => {
  const feedUrl = "../MemoryVault/dashboard_feed.json";
  const dispatchesContainer = document.getElementById("dispatches-container");

  // Load Dashboard Feed
  async function loadFeed() {
    try {
      const response = await fetch(`${feedUrl}?t=${Date.now()}`);
      if (!response.ok) throw new Error("Feed not found");
      const data = await response.json();
      renderDispatches(data.pending_dispatches || []);
    } catch (err) {
      dispatchesContainer.innerHTML = `<p class="empty-state">No active dispatches found in MemoryVault.</p>`;
    }
  }

  function renderDispatches(dispatches) {
    if (dispatches.length === 0) {
      dispatchesContainer.innerHTML = `<p class="empty-state">All clear. Zero pending dispatches.</p>`;
      return;
    }

    dispatchesContainer.innerHTML = dispatches.map(item => `
      <div class="dispatch-item">
        <h3>${escapeHtml(item.title)}</h3>
        <span class="domain-tag">${escapeHtml(item.domain)}</span>
        
        ${Object.entries(item.mutations || {}).map(([key, text]) => `
          <div class="mutation-block">
            <div class="mutation-header">
              <span>${key.replace('_', ' ')}</span>
              <button class="copy-btn" onclick="copyText('${escapeJs(text)}', this)">Copy</button>
            </div>
            <div class="mutation-text">${escapeHtml(text)}</div>
          </div>
        `).join('')}
      </div>
    `).join('');
  }

  window.copyText = (text, btn) => {
    navigator.clipboard.writeText(text).then(() => {
      const original = btn.innerText;
      btn.innerText = "Copied!";
      btn.style.backgroundColor = "#10b981";
      setTimeout(() => {
        btn.innerText = original;
        btn.style.backgroundColor = "";
      }, 1500);
    });
  };

  function escapeHtml(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function escapeJs(str) {
    return String(str).replace(/'/g, "\\'").replace(/\n/g, '\\n');
  }

  loadFeed();
});
