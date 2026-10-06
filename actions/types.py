"""Shared types for the Gmail action layer."""

from __future__ import annotations

from typing import Any, TypedDict


class ClassifiedEmail(TypedDict, total=False):
    id: str
    sender: str
    subject: str
    snippet: str
    category: str
    job_focus: str | None
    priority: str
    recommended_action: str
    confidence: float
    summary: str


class ActionResult(TypedDict, total=False):
    message_id: str
    action_applied: str
    labels: list[str]
    dry_run: bool


GmailService = Any
