"""
Pure label-name resolution from classification fields (no Gmail I/O).
"""

from __future__ import annotations

from actions.policy import resolve_applied_action
from actions.types import ClassifiedEmail
from config.settings import PENDING_DELETE_LABEL, REVIEW_LABEL

_CATEGORY_LABELS: dict[str, str] = {
    "important": "AI/Important",
    "newsletter": "AI/Newsletter",
    "promotional": "AI/Promotional",
    "social": "AI/Social",
    "notification": "AI/Notification",
    "spam": "AI/Spam",
    "other": "AI/Other",
}

_JOB_LABELS: dict[str, str] = {
    "software": "AI/Job Offer — Software",
    "ai_ml": "AI/Job Offer — AI/ML",
    "other": "AI/Job Offer — Other",
}


def category_label(category: str, job_focus: str | None) -> str:
    """Return the Gmail label name for a classification category."""
    if category == "job_offer":
        return _JOB_LABELS.get(job_focus or "other", _JOB_LABELS["other"])
    return _CATEGORY_LABELS.get(category, _CATEGORY_LABELS["other"])


def labels_for_email(email: ClassifiedEmail) -> list[str]:
    """
    Build ordered, de-duplicated Gmail label names for a classified email.
    """
    category = str(email.get("category", "other"))
    names = [category_label(category, email.get("job_focus"))]

    applied = resolve_applied_action(email)
    suggested = str(email.get("recommended_action", "review"))

    if applied == "review" or suggested == "review":
        names.append(REVIEW_LABEL)
    if applied == "pending_delete" or (
        suggested == "delete" and applied != "review"
    ):
        names.append(PENDING_DELETE_LABEL)

    return list(dict.fromkeys(names))
