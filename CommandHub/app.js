// --- CONFIGURATION / LOCAL STORAGE HELPERS ---
function getGitHubToken() {
  return localStorage.getItem('GH_PAT') || '';
}

function saveGitHubToken(token) {
  localStorage.setItem('GH_PAT', token);
}

// Set default local datetime for inputs (YYYY-MM-THH:mm format)
function getFormattedCurrentDateTime() {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
}

// --- ONE-TAP DISTRIBUTED DISPATCH ---
async function markAsDistributed(dispatchId, platform, mutatedText) {
  const token = getGitHubToken();
  if (!token) {
    const inputToken = prompt("Enter your GitHub Personal Access Token (PAT):");
    if (!inputToken) return alert("GitHub Token required to archive dispatches.");
    saveGitHubToken(inputToken);
  }

  const dateInput = document.getElementById(`time-${dispatchId}`);
  const distributedAt = dateInput ? dateInput.value : getFormattedCurrentDateTime();

  const button = document.getElementById(`btn-dist-${dispatchId}`);
  if (button) {
    button.disabled = true;
    button.innerText = "Archiving...";
  }

  // Repository Dispatch API Endpoint
  // Replace OWNER/REPO with your actual GitHub username and repository name
  const REPO_OWNER = "YOUR_GITHUB_USERNAME"; 
  const REPO_NAME = "YOUR_REPO_NAME";

  try {
    const response = await fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/dispatches`, {
      method: "POST",
      headers: {
        "Accept": "application/vnd.github+json",
        "Authorization": `Bearer ${getGitHubToken()}`,
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

    if (response.ok) {
      // Opti-remove card from UI immediately for snappy feed feeling
      const cardNode = document.getElementById(`card-${dispatchId}`);
      if (cardNode) cardNode.remove();
      alert("Dispatched! GitHub Action triggered to update repository state.");
    } else {
      const errData = await response.json();
      alert(`Dispatch failed: ${errData.message || response.statusText}`);
      if (button) {
        button.disabled = false;
        button.innerText = "Distributed";
      }
    }
  } catch (err) {
    console.error("Error triggering dispatch action:", err);
    alert("Network error sending dispatch event.");
    if (button) {
      button.disabled = false;
      button.innerText = "Distributed";
    }
  }
}
