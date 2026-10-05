"""
Second-pass workflow: list and trash messages labeled for pending delete.
"""

from __future__ import annotations

from actions.label_repository import LabelRepository
from actions.types import GmailService
from config.settings import ALLOW_LIVE_DELETE, PENDING_DELETE_LABEL


def fetch_pending_delete_emails(
    service: GmailService,
    *,
    max_results: int = 50,
) -> list[dict[str, str]]:
    """
    List messages that carry the pending-delete label.

    Returns:
        List of dicts with ``id``, ``sender``, and ``subject``.
    """
    labels = LabelRepository(service)
    if not labels.has_label(PENDING_DELETE_LABEL):
        return []

    label_id = labels.id_for(PENDING_DELETE_LABEL)
    response = (
        service.users()
        .messages()
        .list(userId="me", labelIds=[label_id], maxResults=max_results)
        .execute()
    )

    emails: list[dict[str, str]] = []
    for item in response.get("messages", []):
        msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=item["id"],
                format="metadata",
                metadataHeaders=["From", "Subject"],
            )
            .execute()
        )
        headers = {
            h["name"].lower(): h.get("value", "")
            for h in msg.get("payload", {}).get("headers", [])
        }
        emails.append(
            {
                "id": msg["id"],
                "sender": headers.get("from", "Unknown"),
                "subject": headers.get("subject", "(no subject)"),
            }
        )
    return emails


def trash_pending_delete_emails(
    service: GmailService,
    emails: list[dict[str, str]],
    *,
    dry_run: bool,
) -> list[dict[str, str | bool]]:
    """
    Move pending-delete messages to Trash after explicit user confirmation.

    Requires ``ALLOW_LIVE_DELETE=true`` in the environment for live runs.
    """
    results: list[dict[str, str | bool]] = []
    for email in emails:
        msg_id = email["id"]
        if dry_run or not ALLOW_LIVE_DELETE:
            results.append(
                {
                    "message_id": msg_id,
                    "action_applied": "would trash",
                    "dry_run": True,
                }
            )
            continue

        service.users().messages().trash(userId="me", id=msg_id).execute()
        results.append(
            {
                "message_id": msg_id,
                "action_applied": "trashed",
                "dry_run": False,
            }
        )
    return results


def ensure_pending_delete_label(service: GmailService) -> None:
    """Create the pending-delete label if it does not exist yet."""
    LabelRepository(service).id_for(PENDING_DELETE_LABEL)
