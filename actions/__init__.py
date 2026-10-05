"""Gmail action execution for Phase 3 of the AI Gmail Cleanser Agent."""

from actions.executor import apply_email_actions, effective_action
from actions.pending_delete import (
    fetch_pending_delete_emails,
    trash_pending_delete_emails,
)

__all__ = [
    "apply_email_actions",
    "effective_action",
    "fetch_pending_delete_emails",
    "trash_pending_delete_emails",
]
