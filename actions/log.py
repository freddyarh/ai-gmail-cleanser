"""
Append-only JSON log for Gmail actions performed by the cleanser.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def append_action_log(entries: list[dict[str, Any]], path: Path) -> None:
    """
    Append action records to a JSON log file.

    Args:
        entries: One dict per action (message id, action taken, labels, etc.).
        path: Log file path (parent directories are created if needed).
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    existing: list[dict[str, Any]] = []
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except json.JSONDecodeError:
            existing = []

    timestamp = datetime.now(timezone.utc).isoformat()
    for entry in entries:
        entry.setdefault("logged_at", timestamp)

    path.write_text(json.dumps(existing + entries, indent=2))
