"""
Action handlers — one class per applied action (Open/Closed, Strategy pattern).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from actions.label_names import labels_for_email
from actions.label_repository import LabelRepository
from actions.policy import resolve_applied_action
from actions.types import ActionResult, ClassifiedEmail, GmailService


class ActionHandler(ABC):
    """Interface for applying one kind of Gmail action to a message."""

    @abstractmethod
    def apply(
        self,
        service: GmailService,
        labels: LabelRepository,
        email: ClassifiedEmail,
        *,
        dry_run: bool,
    ) -> ActionResult:
        """Perform or simulate the action and return a log-friendly result."""


class _LabelModifyHandler(ActionHandler):
    """Base handler that applies labels and optional inbox label removals."""

    def __init__(
        self,
        description: str,
        *,
        remove_inbox: bool = False,
    ) -> None:
        self._description = description
        self._remove_inbox = remove_inbox

    def apply(
        self,
        service: GmailService,
        labels: LabelRepository,
        email: ClassifiedEmail,
        *,
        dry_run: bool,
    ) -> ActionResult:
        msg_id = str(email["id"])
        label_names = labels_for_email(email)
        add_ids = labels.ids_for_names(label_names)
        body: dict[str, Any] = {"addLabelIds": add_ids}
        if self._remove_inbox:
            body["removeLabelIds"] = ["INBOX"]

        if dry_run:
            return {
                "message_id": msg_id,
                "action_applied": self._description,
                "labels": label_names,
                "dry_run": True,
            }

        service.users().messages().modify(
            userId="me", id=msg_id, body=body
        ).execute()
        return {
            "message_id": msg_id,
            "action_applied": self._description,
            "labels": label_names,
            "dry_run": False,
        }


class TrashHandler(ActionHandler):
    """Move a message to Trash (only when live delete is allowed)."""

    def apply(
        self,
        service: GmailService,
        labels: LabelRepository,
        email: ClassifiedEmail,
        *,
        dry_run: bool,
    ) -> ActionResult:
        msg_id = str(email["id"])
        label_names = labels_for_email(email)

        if dry_run:
            return {
                "message_id": msg_id,
                "action_applied": "would move to trash",
                "labels": label_names,
                "dry_run": True,
            }

        service.users().messages().trash(userId="me", id=msg_id).execute()
        return {
            "message_id": msg_id,
            "action_applied": "trashed",
            "labels": label_names,
            "dry_run": False,
        }


_HANDLERS: dict[str, ActionHandler] = {
    "keep": _LabelModifyHandler("keep"),
    "archive": _LabelModifyHandler("archive", remove_inbox=True),
    "review": _LabelModifyHandler("review"),
    "pending_delete": _LabelModifyHandler(
        "labeled for pending delete (not trashed)"
    ),
    "delete": TrashHandler(),
}


def handler_for(email: ClassifiedEmail) -> ActionHandler:
    """Return the handler responsible for the resolved action on this email."""
    applied = resolve_applied_action(email)
    return _HANDLERS.get(applied, _HANDLERS["review"])
