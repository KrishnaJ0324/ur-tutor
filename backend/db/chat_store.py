"""
db/chat_store.py
----------------
Session-scoped chat history stored as JSON files in db/sessions/.
Each session gets one file keyed by user_id.
Files are created on first message and deleted when the session ends
(browser tab close / page reload) via the /session/end endpoint.
All files are also wiped on server startup so stale sessions never accumulate.
"""
import json
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = Path(__file__).parent / "sessions"


def _session_path(user_id: str) -> Path:
    SESSIONS_DIR.mkdir(exist_ok=True)
    return SESSIONS_DIR / f"{user_id}.json"


def save_message(user_id: str, role: str, content: str) -> None:
    path = _session_path(user_id)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "messages": [],
        }
    data["messages"].append(
        {"role": role, "content": content, "timestamp": datetime.utcnow().isoformat()}
    )
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_history(user_id: str) -> list:
    path = _session_path(user_id)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("messages", [])


def delete_session(user_id: str) -> None:
    path = _session_path(user_id)
    if path.exists():
        path.unlink()


def clear_all_sessions() -> None:
    """Wipe every session file — called on server startup."""
    if SESSIONS_DIR.exists():
        for f in SESSIONS_DIR.glob("*.json"):
            f.unlink()
