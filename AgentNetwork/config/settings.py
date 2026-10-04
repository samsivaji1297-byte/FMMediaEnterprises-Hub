import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
AGENT_NETWORK_DIR = BASE_DIR / "AgentNetwork"
VAULT_DIR = BASE_DIR / "MediaFactory" / "vault"

SEEDS_FILE = AGENT_NETWORK_DIR / "config" / "search_seeds.json"
QUEUE_FILE = VAULT_DIR / "queue.json"
PERFORMANCE_LOG = VAULT_DIR / "analytics_history.json"

# Meta / Instagram Credentials
IG_USER_ID = os.getenv("IG_USER_ID") or os.getenv("INSTAGRAM_ACCOUNT_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN") or os.getenv("INSTAGRAM_ACCESS_TOKEN")

# Operational Settings
ANALYTICS_QUERY_INTERVAL_HOURS = 24
