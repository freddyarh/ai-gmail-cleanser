"""
Action policy — decides which Gmail operation applies to a classified email.

Single responsibility: business rules and safety overrides (no API calls).
"""

from __future__ import annotations

from actions.types import ClassifiedEmail
from config.settings import NEVER_AUTO_DELETE

AppliedAction = str  # keep | archive | review | pending_delete | delete


def is_protected_from_delete(email: ClassifiedEmail) -> bool:
    """Return True when delete or pending-delete must not be applied."""
    if email.get("category") == "job_offer":
        return True
    if email.get("category") == "important" and email.get("priority") == "high":
        return True
    return False


def resolve_applied_action(email: ClassifiedEmail) -> AppliedAction:
    """
    Map LLM ``recommended_action`` to the action the executor will perform.

    Delete suggestions become ``pending_delete`` when auto-delete is disabled,
    or ``review`` for protected messages.
    """
    suggested = str(email.get("recommended_action", "review"))
    if suggested != "delete":
        return suggested
    if is_protected_from_delete(email):
        return "review"
    if NEVER_AUTO_DELETE:
        return "pending_delete"
    return "delete"
