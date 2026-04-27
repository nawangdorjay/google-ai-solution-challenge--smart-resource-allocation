import json
import os
from datetime import datetime

# Creates the file inside the exact same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "match_history.json")
MAX_HISTORY = 30

def log_result(request_id, request_title, matches):
    """Stores the match result into a local JSON file, keeping only the last 30 entries."""
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            pass

    history.append({
        "request_id": request_id,
        "request_title": request_title,
        "matches": matches,
        "timestamp": datetime.now().isoformat()
    })

    # Keep only the last 30
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def get_history() -> list:
    """Return all stored match history entries (up to MAX_HISTORY)."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def clear_history():
    """Delete all stored match history (admin use)."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
