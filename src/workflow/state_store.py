"""
State persistence and management for Hưng Phát BPMN 2.0 Multi-Agent Workflow.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from src.paths import get_artifacts_dir


class WorkflowStateStore:
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = get_artifacts_dir() / "workflow_state.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def save_state(self, state: Dict[str, Any]):
        serializable = {}
        for k, v in state.items():
            if hasattr(v, "__dict__"):
                serializable[k] = v.__dict__
            elif isinstance(v, list) and v and hasattr(v[0], "__dict__"):
                serializable[k] = [item.__dict__ for item in v]
            elif isinstance(v, dict) and v and any(hasattr(val, "__dict__") for val in v.values()):
                serializable[k] = {
                    sub_k: (sub_v.__dict__ if hasattr(sub_v, "__dict__") else sub_v)
                    for sub_k, sub_v in v.items()
                }
            else:
                serializable[k] = v

        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(serializable, f, default=str, ensure_ascii=False, indent=2)
        except (OSError, PermissionError):
            pass

    def load_state(self) -> Optional[Dict[str, Any]]:
        if not self.storage_path.exists():
            return None
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
