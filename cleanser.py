"""
AI Gmail Cleanser Agent — Phase 3: Classify, label, and safely triage Gmail.

Fetches unread mail, classifies with the Phase 2 LLM, applies Gmail labels
and archive actions. Delete suggestions are **never** trashed on this pass
when ``NEVER_AUTO_DELETE`` is true (default); they receive ``AI/Pending Delete``
instead.

Usage:
    python cleanser.py                    # classify + label (respects DRY_RUN)
    python cleanser.py --confirm-deletes  # trash messages labeled pending delete

Prerequisites:
    - Phase 1 OAuth (``credentials.json``; delete old ``token.json`` and re-auth)
    - ``.env`` with ``OPENAI_API_KEY`` and Phase 3 safety flags (see ``.env.example``)
"""

from __future__ import annotations

import argparse

from googleapiclient.errors import HttpError

from actions import (
    apply_email_actions,
    effective_action,
    fetch_pending_delete_emails,
    trash_pending_delete_emails,
)
from actions.log import append_action_log
from actions.pending_delete import ensure_pending_delete_label
from classifier import classify_emails
from config.settings import (
    ALLOW_LIVE_DELETE,
    AUTO_CONFIRM,
    DRY_RUN,
    LOG_PATH,
    MAX_EMAILS,
    NEVER_AUTO_DELETE,
    PENDING_DELETE_LABEL,
)
from data_pipeline import authenticate_gmail, fetch_unread_emails


def _prompt_yes_no(message: str) -> bool:
    if AUTO_CONFIRM:
        return True
    answer = input(f"{message} [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def _print_email_preview(index: int, email: dict) -> None:
    focus = email.get("job_focus")
    focus_text = f" | Focus: {focus}" if focus else ""
    applied = effective_action(email)
    print(f"--- Email {index} ---")
    print(f"  From:     {email.get('sender', 'Unknown')}")
    print(f"  Subject:  {email.get('subject', '(no subject)')}")
    print(
        f"  Category: {email.get('category')} | Priority: {email.get('priority')}"
        f"{focus_text}"
    )
    print(f"  Suggested: {email.get('recommended_action')} → Applied: {applied}")
    print(f"  Summary:  {email.get('summary')}")
    print()


def run_cleanser(*, dry_run: bool) -> None:
    """Fetch, classify, preview, confirm, and apply Gmail actions."""
    try:
        service = authenticate_gmail()
        emails = fetch_unread_emails(max_results=MAX_EMAILS, service=service)
    except FileNotFoundError as exc:
        print(f"Setup error: {exc}")
        return
    except HttpError as exc:
        print(f"Gmail API error: {exc}")
        return

    if not emails:
        print("No unread emails found in the inbox.")
        return

    print(f"\nFetched {len(emails)} unread email(s). Classifying...\n")

    try:
        classified = classify_emails(emails)
    except ValueError as exc:
        print(f"Configuration error: {exc}")
        return

    for index, email in enumerate(classified, start=1):
        _print_email_preview(index, email)

    mode = "DRY RUN" if dry_run else "LIVE"
    if not _prompt_yes_no(f"Apply {len(classified)} action(s)? ({mode})"):
        print("Cancelled. No changes made.")
        return

    ensure_pending_delete_label(service)
    results = apply_email_actions(service, classified, dry_run=dry_run)
    append_action_log(
        [
            {
                "mode": "cleanser",
                "sender": email.get("sender"),
                "subject": email.get("subject"),
                **result,
            }
            for email, result in zip(classified, results)
        ],
        LOG_PATH,
    )

    for email, result in zip(classified, results):
        prefix = "[DRY RUN] " if result.get("dry_run") else ""
        labels = ", ".join(result.get("labels", []))
        print(
            f"{prefix}✓ {email.get('sender')} — "
            f"{result.get('action_applied')} ({labels})"
        )

    deleted_count = sum(1 for r in results if r.get("action_applied") == "trashed")
    print(
        f"\nDone. {len(results)} action(s) processed. "
        f"{deleted_count} trashed. Log: {LOG_PATH}"
    )
    if NEVER_AUTO_DELETE:
        print(
            f"Delete suggestions were labeled '{PENDING_DELETE_LABEL}' only. "
            f"Run: python cleanser.py --confirm-deletes"
        )


def run_confirm_deletes(*, dry_run: bool) -> None:
    """Trash messages that were previously labeled for pending delete."""
    try:
        service = authenticate_gmail()
        pending = fetch_pending_delete_emails(service)
    except FileNotFoundError as exc:
        print(f"Setup error: {exc}")
        return
    except HttpError as exc:
        print(f"Gmail API error: {exc}")
        return

    if not pending:
        print(f"No messages with label '{PENDING_DELETE_LABEL}'.")
        return

    print(f"Found {len(pending)} message(s) with '{PENDING_DELETE_LABEL}':\n")
    for index, email in enumerate(pending, start=1):
        print(f"  {index}. {email['sender']} — {email['subject']}")

    if dry_run or not ALLOW_LIVE_DELETE:
        print(
            f"\n[DRY RUN] Would move {len(pending)} message(s) to Trash. "
            "Set DRY_RUN=false and ALLOW_LIVE_DELETE=true to trash for real."
        )
        trash_pending_delete_emails(service, pending, dry_run=True)
        return

    if not _prompt_yes_no(f"\nMove {len(pending)} message(s) to Trash"):
        print("Cancelled. No messages trashed.")
        return

    results = trash_pending_delete_emails(service, pending, dry_run=False)
    append_action_log(
        [{"mode": "confirm_deletes", **result} for result in results],
        LOG_PATH,
    )
    print(f"\nTrashed {len(results)} message(s). Log: {LOG_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Gmail Cleanser Agent — Phase 3")
    parser.add_argument(
        "--confirm-deletes",
        action="store_true",
        help="Trash messages labeled AI/Pending Delete (second pass)",
    )
    args = parser.parse_args()

    if args.confirm_deletes:
        run_confirm_deletes(dry_run=DRY_RUN)
    else:
        run_cleanser(dry_run=DRY_RUN)


if __name__ == "__main__":
    main()
