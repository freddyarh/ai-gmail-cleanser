"""
Application settings loaded from environment variables.

Copy ``.env.example`` to ``.env`` and fill in your API key before running
``agent.py`` or ``cleanser.py``.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    return value in {"1", "true", "yes", "on"}


OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
MAX_EMAILS: int = int(os.getenv("MAX_EMAILS", "10"))

CATEGORIES: tuple[str, ...] = (
    "important",
    "newsletter",
    "promotional",
    "social",
    "notification",
    "spam",
    "job_offer",
    "other",
)
PRIORITIES: tuple[str, ...] = ("high", "medium", "low")
ACTIONS: tuple[str, ...] = ("keep", "archive", "delete", "review")
JOB_FOCUSES: tuple[str, ...] = ("software", "ai_ml", "other")

# Phase 3 — Gmail actions
DRY_RUN: bool = _env_bool("DRY_RUN", True)
AUTO_CONFIRM: bool = _env_bool("AUTO_CONFIRM", False)
NEVER_AUTO_DELETE: bool = _env_bool("NEVER_AUTO_DELETE", True)
ALLOW_LIVE_DELETE: bool = _env_bool("ALLOW_LIVE_DELETE", False)
PENDING_DELETE_LABEL: str = os.getenv("PENDING_DELETE_LABEL", "AI/Pending Delete")
REVIEW_LABEL: str = os.getenv("REVIEW_LABEL", "AI/Review")
LOG_PATH: Path = Path(os.getenv("LOG_PATH", "logs/actions.json"))
