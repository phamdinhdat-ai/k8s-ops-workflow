"""Memory store for persistent session context."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class MemoryStore:
    """Persistent memory for session context and RCA history."""
    
    def __init__(self, storage_path: str = "./data/memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.session_file = self.storage_path / "sessions.json"
        self.rca_file = self.storage_path / "rca_history.json"
        self._init_storage()
    
    def _init_storage(self):
        """Initialize storage files if they don't exist."""
        if not self.session_file.exists():
            self.session_file.write_text(json.dumps({}))
        if not self.rca_file.exists():
            self.rca_file.write_text(json.dumps([]))
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session context by ID."""
        sessions = json.loads(self.session_file.read_text())
        return sessions.get(session_id)
    
    def save_session_context(self, session_id: str, context: Dict[str, Any]):
        """Save session context."""
        sessions = json.loads(self.session_file.read_text())
        sessions[session_id] = {
            **context,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.session_file.write_text(json.dumps(sessions, indent=2))
    
    def save_rca_finding(self, finding: Dict[str, Any]):
        """Save RCA finding to history."""
        history = json.loads(self.rca_file.read_text())
        finding["timestamp"] = datetime.utcnow().isoformat()
        history.append(finding)
        self.rca_file.write_text(json.dumps(history, indent=2))
    
    def get_recent_rca(self, service: str, namespace: str, days: int = 7) -> Optional[Dict[str, Any]]:
        """Get recent RCA for same service."""
        history = json.loads(self.rca_file.read_text())
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        
        for entry in reversed(history):
            if entry.get("service") == service and entry.get("namespace") == namespace:
                entry_time = datetime.fromisoformat(entry["timestamp"]).timestamp()
                if entry_time > cutoff:
                    return entry
        return None
    
    def get_conversation_history(self, session_id: str, limit: int = 3) -> List[Dict[str, str]]:
        """Get recent conversation turns."""
        context = self.get_session_context(session_id)
        if not context or "history" not in context:
            return []
        return context["history"][-limit:]
