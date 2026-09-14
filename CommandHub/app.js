// ==========================================
// CONFIGURATION & AUTH
// ==========================================
const REPO_OWNER = "samsivaji1297-byte";
const REPO_NAME = "FMMediaEnterprises-Hub";

let currentTab = "pending";

function getGitHubToken() {
  return localStorage.getItem('GH_PAT') || '';
}

function saveGitHubToken(token) {
  localStorage.setItem('GH_PAT', token);
}

function getFormattedCurrentDateTime() {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
}

// ==========================================
// TAB SWITCHING & FEED CONTROL
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  loadDeck();
});

function switchTab(tab) {
  currentTab = tab;
  document.getElementById("tab-pending").classList.toggle("active", tab === "pending");
  document.getElementById("tab-released").classList.toggle("active", tab === "released");
  loadDeck();
}

function loadDeck() {
  if (currentTab === "pending") {
    fetchPendingDispatches();
  } else {
    fetchReleasedArchive();
  }
}

// ==========================================
// 1. PENDING QUEUE FEED
// ==========================================
async function fetchPendingDispatches() {
  const feedContainer = document.getElementById("feed-container");
  feedContainer.innerHTML = '<div class="loading">Loading pending queue...</div>';

  try {
    const response = await fetch(`https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/MemoryVault/dashboard_feed.json?t=${Date.now()}`);
    if (!response.ok) throw new Error(`HTTP error ${response.status}`);

    const items = await response.json();
    if (!Array.isArray(items) || items.length === 0) {
      feedContainer.innerHTML = '<div class="empty-state">No pending dispatches in queue.</div>';
      return;
    }

    feedContainer.innerHTML = "";
    items.forEach(item => {
      feedContainer.appendChild(createPendingCard(item));
    });

  } catch (err) {
    console.error("Error loading pending feed:", err);
    feedContainer.innerHTML = `<div class="error-state">Unable to load pending queue.<br><small>${err.message}</small></div>`;
  }
}

function createPendingCard(item) {
  const card = document.createElement("div");
  card.className = "card";
  card.id = `card-${item.id}`;

  const platform = item.platform || "General";
  const content = item.content || item.text || "";
  const itemId = item.id || Date.now();

  card.innerHTML = `
    <div class="card-header">
      <span class="badge">${platform}</span>
      <span class="timestamp-tag">ID: ${itemId}</span>
    </div>
    <div class="card-body">
      <p class="content-text" id="text-${itemId}">${content}</p>
    </div>
    <div class="card-actions">
      <button class="btn btn-secondary" onclick="copyCardContent('${itemId}')">Copy Text</button>
      <div class="timestamp-group">
        <input type="datetime-local" id="time-${itemId}" value="${getFormattedCurrentDateTime()}" />
        <button id="btn-dist-${itemId}" class="btn btn-primary" onclick="markAsDistributed('${itemId}', '${platform}')">Distributed</button>
      </div>
    </div>
  `;
  return card;
}

// ==========================================
// 2. RELEASED ARCHIVE FEED
// ==========================================
async function fetchReleasedArchive() {
  const feedContainer = document.getElementById("feed-container");
  feedContainer.innerHTML = '<div class="loading">Loading released archive...</div>';

  try {
    const response = await fetch(`https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/MemoryVault/released_content.json?t=${Date.now()}`);
    if (!response.ok) {
      if (response.status === 404) {
        feedContainer.innerHTML = '<div class="empty-state">No released dispatches archived yet.</div>';
        return;
      }
      throw new Error(`HTTP error ${response.status}`);
    }

    const items = await response.json();
    if (!Array.isArray(items) || items.length === 0) {
      feedContainer.innerHTML = '<div class="empty-state">No released dispatches archived yet.</div>';
      return;
    }

    feedContainer.innerHTML = "";
    items.forEach(item => {
      feedContainer.appendChild(createReleasedCard(item));
    });

  } catch (err) {
    console.error("Error loading released feed:", err);
    feedContainer.innerHTML = `<div class="error-state">Unable to load released archive.<br><small>${err.message}</small></div>`;
  }
}

function createReleasedCard(item) {
  const card = document.createElement("div");
  card.className = "card";

  const platform = item.platform || "General";
  const content = item.content || "";
  const releasedAt = item.distributed_at ? new Date(item.distributed_at).toLocaleString() : "Unknown Date";
  const echoStage = item.echo_stage || "Active Lifecycle";

  card.innerHTML = `
    <div class="card-header">
      <span class="badge">${platform}</span>
      <span class="timestamp-tag">Released: ${releasedAt}</span>
    </div>
    <div class="card-body">
      <p class="content-text">${content}</p>
    </div>
    <div class="card-actions">
      <button class="btn btn-secondary" onclick="navigator.clipboard.writeText(\`${content}\`)">Copy Archived Text</button>
    </div>
  `;
  return card;
}

function copyCardContent(itemId) {
  const textElem = document.getElementById(`text-${itemId}`);
  if (textElem) {
    navigator.clipboard.writeText(textElem.innerText).then(() => alert("Copied text!"));
  }
}

// ==========================================
// ONE-TAP DISTRIBUTED DISPATCH (WEBHOOK)
// ==========================================
async function markAsDistributed(dispatchId, platform) {
  let token = getGitHubToken();
  if (!token) {
    token = prompt("Enter your GitHub Personal Access Token (PAT):");
    if (!token) return alert("Action canceled: Token required.");
    saveGitHubToken(token);
  }

  const textElem = document.getElementById(`text-${dispatchId}`);
  const mutatedText = textElem ? textElem.innerText : "";
  const dateInput = document.getElementById(`time-${dispatchId}`);
  const distributedAt = dateInput ? dateInput.value : getFormattedCurrentDateTime();

  const button = document.getElementById(`btn-dist-${dispatchId}`);
  if (button) {
    button.disabled = true;
    button.innerText = "Archiving...";
  }

  try {
    const response = await fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/dispatches`, {
      method: "POST",
      headers: {
        "Accept": "application/vnd.github+json",
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        event_type: "archive_dispatch",
        client_payload: {
          dispatch_id: String(dispatchId),
          platform: platform,
          mutated_text: mutatedText,
          distributed_at: distributedAt
        }
      })
    });

    if (response.ok || response.status === 204) {
      const cardNode = document.getElementById(`card-${dispatchId}`);
      if (cardNode) {
        cardNode.style.opacity = "0.4";
        cardNode.style.pointerEvents = "none";
      }
      alert("Dispatched! Archived to released content.");
      setTimeout(() => { loadDeck(); }, 1000);
    } else {
      const errData = await response.json();
      alert(`Dispatch failed: ${errData.message || response.statusText}`);
      if (button) {
        button.disabled = false;
        button.innerText = "Distributed";
      }
    }
  } catch (err) {
    console.error("Dispatch webhook error:", err);
    alert("Network error sending dispatch event.");
    if (button) {
      button.disabled = false;
      button.innerText = "Distributed";
    }
  }
}
