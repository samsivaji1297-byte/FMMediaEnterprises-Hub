// ==========================================
// CONFIGURATION & LOCAL STORAGE AUTH
// ==========================================
const REPO_OWNER = "samsivaji1297-byte";
const REPO_NAME = "FMMediaEnterprises-Hub";

function getGitHubToken() {
  return localStorage.getItem('GH_PAT') || '';
}

function saveGitHubToken(token) {
  localStorage.setItem('GH_PAT', token);
}

function clearGitHubToken() {
  localStorage.removeItem('GH_PAT');
  alert("Stored GitHub token cleared.");
}

function getFormattedCurrentDateTime() {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
}

// ==========================================
// DATA FETCHING & RENDERING
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  fetchPendingDispatches();
});

async function fetchPendingDispatches() {
  const feedContainer = document.getElementById("feed-container");
  if (!feedContainer) return;

  feedContainer.innerHTML = '<div class="loading">Loading pending dispatches...</div>';

  try {
    // Pull feed directly from raw public github content
    const response = await fetch(`https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/MemoryVault/dashboard_feed.json?t=${Date.now()}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error status: ${response.status}`);
    }

    const items = await response.json();

    if (!Array.isArray(items) || items.length === 0) {
      feedContainer.innerHTML = '<div class="empty-state">No pending dispatches in queue. You are all caught up!</div>';
      return;
    }

    feedContainer.innerHTML = "";
    items.forEach(item => {
      feedContainer.appendChild(createMutationCard(item));
    });

  } catch (err) {
    console.error("Error loading feed:", err);
    feedContainer.innerHTML = `
      <div class="error-state">
        Unable to load MemoryVault/dashboard_feed.json.<br>
        <small>${err.message}</small>
      </div>`;
  }
}

function createMutationCard(item) {
  const card = document.createElement("div");
  card.className = "card";
  card.id = `card-${item.id}`;

  const platform = item.platform || "General";
  const content = item.content || item.text || "";
  const itemId = item.id || Date.now();

  card.innerHTML = `
    <div class="card-header">
      <span class="badge badge-${platform.toLowerCase()}">${platform}</span>
      <span class="id-tag">ID: ${itemId}</span>
    </div>
    
    <div class="card-body">
      <p class="content-text" id="text-${itemId}">${content}</p>
    </div>

    <div class="card-actions">
      <button class="btn btn-secondary" onclick="copyCardContent('${itemId}')">
        Copy Text
      </button>
      
      <div class="timestamp-group">
        <input 
          type="datetime-local" 
          id="time-${itemId}" 
          value="${getFormattedCurrentDateTime()}" 
        />
        <button 
          id="btn-dist-${itemId}" 
          class="btn btn-primary" 
          onclick="markAsDistributed('${itemId}', '${platform}')"
        >
          Distributed
        </button>
      </div>
    </div>
  `;

  return card;
}

function copyCardContent(itemId) {
  const textElem = document.getElementById(`text-${itemId}`);
  if (!textElem) return;

  navigator.clipboard.writeText(textElem.innerText).then(() => {
    alert("Copied content to clipboard!");
  }).catch(err => {
    console.error("Failed to copy text: ", err);
  });
}

// ==========================================
// ONE-TAP DISTRIBUTED DISPATCH (WEBHOOK)
// ==========================================
async function markAsDistributed(dispatchId, platform) {
  let token = getGitHubToken();

  // Prompt ONLY ONCE if token is not yet stored in device memory
  if (!token) {
    token = prompt("Enter your GitHub Personal Access Token (PAT) with repo write access:");
    if (!token) return alert("Action canceled: GitHub Token required to archive dispatches.");
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
      alert("Dispatched! GitHub Action triggered.");
      setTimeout(() => { if (cardNode) cardNode.remove(); }, 1000);
    } else {
      const errData = await response.json();
      if (response.status === 401) {
        alert("Token invalid. Clearing token—please re-enter when prompted.");
        clearGitHubToken();
      } else {
        alert(`Dispatch failed: ${errData.message || response.statusText}`);
      }
      if (button) {
        button.disabled = false;
        button.innerText = "Distributed";
      }
    }
  } catch (err) {
    console.error("Error sending dispatch webhook:", err);
    alert("Network error sending dispatch event.");
    if (button) {
      button.disabled = false;
      button.innerText = "Distributed";
    }
  }
}
