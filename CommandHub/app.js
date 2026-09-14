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
// INITIALIZATION & TAB SWITCHING
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

// Robust Multi-Path JSON Reader
async function fetchVaultJSON(filename) {
  const paths = [
    `../MemoryVault/${filename}`,
    `/MemoryVault/${filename}`,
    `MemoryVault/${filename}`,
    `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/MemoryVault/${filename}`
  ];

  for (const path of paths) {
    try {
      const response = await fetch(`${path}?t=${Date.now()}`);
      if (response.ok) {
        return await response.json();
      }
    } catch (e) {
      console.warn(`Path failed: ${path}`);
    }
  }
  return null;
}

// ==========================================
// 1. UNIVERSAL SIGNAL TRANSMIT (WEBHOOK)
// ==========================================
async function submitSignal() {
  const inputElem = document.getElementById("signal-input");
  const typeElem = document.getElementById("signal-type");
  const btn = document.getElementById("btn-capture");

  const text = inputElem.value.trim();
  const signalType = typeElem.value;

  if (!text) return alert("Please enter a signal or idea first.");

  let token = getGitHubToken();
  if (!token) {
    token = prompt("Enter your GitHub Personal Access Token (PAT):");
    if (!token) return alert("Token required to transmit signals.");
    saveGitHubToken(token);
  }

  btn.disabled = true;
  btn.innerText = "Transmitting...";

  try {
    const response = await fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/dispatches`, {
      method: "POST",
      headers: {
        "Accept": "application/vnd.github+json",
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        event_type: "signal_capture",
        client_payload: {
          raw_text: text,
          signal_type: signalType,
          captured_at: new Date().toISOString()
        }
      })
    });

    if (response.ok || response.status === 204) {
      alert("Signal Transmitted! Pipeline processing started.");
      inputElem.value = "";
    } else {
      const errData = await response.json();
      alert(`Signal transmit failed: ${errData.message || response.statusText}`);
    }
  } catch (err) {
    console.error("Signal transmit error:", err);
    alert("Network error transmitting signal.");
  } finally {
    btn.disabled = false;
    btn.innerText = "Transmit Signal";
  }
}

// ==========================================
// 2. PENDING QUEUE FEED
// ==========================================
async function fetchPendingDispatches() {
  const feedContainer = document.getElementById("feed-container");
  feedContainer.innerHTML = '<div class="loading">Loading pending dispatches...</div>';

  const rawData = await fetchVaultJSON("dashboard_feed.json");

  if (!rawData) {
    feedContainer.innerHTML = `<div class="error-state">Unable to load MemoryVault/dashboard_feed.json.</div>`;
    return;
  }

  // Normalize items whether rawData is a direct Array or a wrapped Object
  let items = Array.isArray(rawData) ? rawData : (rawData.items || rawData.dispatches || []);

  if (items.length === 0) {
    feedContainer.innerHTML = '<div class="empty-state">No pending dispatches in queue. You are all caught up!</div>';
    return;
  }

  feedContainer.innerHTML = "";
  items.forEach((item, idx) => {
    feedContainer.appendChild(createPendingCard(item, idx));
  });
}

function createPendingCard(item, idx) {
  const card = document.createElement("div");
  card.className = "card";
  const itemId = item.id || `dispatch-${idx}-${Date.now()}`;
  card.id = `card-${itemId}`;

  const platform = item.platform || item.target_platform || "General";
  const content = item.content || item.mutated_text || item.text || "";

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
// 3. RELEASED ARCHIVE FEED
// ==========================================
async function fetchReleasedArchive() {
  const feedContainer = document.getElementById("feed-container");
  feedContainer.innerHTML = '<div class="loading">Loading released archive...</div>';

  const rawData = await fetchVaultJSON("released_content.json");

  if (!rawData) {
    feedContainer.innerHTML = '<div class="empty-state">No released dispatches archived yet.</div>';
    return;
  }

  let items = Array.isArray(rawData) ? rawData : (rawData.items || rawData.dispatches || []);

  if (items.length === 0) {
    feedContainer.innerHTML = '<div class="empty-state">No released dispatches archived yet.</div>';
    return;
  }

  feedContainer.innerHTML = "";
  items.forEach(item => {
    feedContainer.appendChild(createReleasedCard(item));
  });
}

function createReleasedCard(item) {
  const card = document.createElement("div");
  card.className = "card";

  const platform = item.platform || "General";
  const content = item.content || item.mutated_text || "";
  const releasedAt = item.distributed_at ? new Date(item.distributed_at).toLocaleString() : "Released";

  card.innerHTML = `
    <div class="card-header">
      <span class="badge">${platform}</span>
      <span class="timestamp-tag">${releasedAt}</span>
    </div>
    <div class="card-body">
      <p class="content-text">${content}</p>
    </div>
    <div class="card-actions">
      <button class="btn btn-secondary" onclick="navigator.clipboard.writeText(\`${content.replace(/`/g, '\\`')}\`)">Copy Archived Text</button>
    </div>
  `;
  return card;
}

function copyCardContent(itemId) {
  const textElem = document.getElementById(`text-${itemId}`);
  if (textElem) {
    navigator.clipboard.writeText(textElem.innerText).then(() => alert("Copied dispatch content to clipboard!"));
  }
}

// ==========================================
// 4. ONE-TAP DISTRIBUTED DISPATCH (WEBHOOK)
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
