"""
Action executor — coordinates label repository and action handlers (Dependency Inversion).
"""

from __future__ import annotations

from actions.handlers import handler_for
from actions.label_repository import LabelRepository
from actions.policy import resolve_applied_action
from actions.types import ActionResult, ClassifiedEmail, GmailService


def effective_action(email: ClassifiedEmail) -> str:
    """Public alias for the resolved action (used by CLI preview)."""
    return resolve_applied_action(email)


def apply_email_action(
    service: GmailService,
    labels: LabelRepository,
    email: ClassifiedEmail,
    *,
    dry_run: bool,
) -> ActionResult:
    """Apply the appropriate handler for one classified email."""
    return handler_for(email).apply(service, labels, email, dry_run=dry_run)


def apply_email_actions(
    service: GmailService,
    emails: list[ClassifiedEmail],
    *,
    dry_run: bool,
) -> list[ActionResult]:
    """Apply actions for a batch of classified emails using one label repository."""
    labels = LabelRepository(service)
    return [
        apply_email_action(service, labels, email, dry_run=dry_run)
        for email in emails
    ]
