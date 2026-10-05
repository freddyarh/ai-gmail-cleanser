"""
Prompt templates for LLM-based email classification.
"""

from __future__ import annotations

from config.settings import ACTIONS, CATEGORIES, JOB_FOCUSES, PRIORITIES

SYSTEM_PROMPT = f"""You are an email triage assistant. Classify each email into exactly one category, assign a priority, recommend an action, and write a one-sentence summary.

Categories (pick one): {", ".join(CATEGORIES)}
Priorities (pick one): {", ".join(PRIORITIES)}
Recommended actions (pick one): {", ".join(ACTIONS)}

Guidelines:
- important: personal messages, deadlines, replies needed, work-critical mail
- newsletter: subscriptions, digests, regular content updates (not job recruiting)
- promotional: sales, discounts, marketing campaigns
- social: LinkedIn, GitHub, Twitter/X, community notifications
- notification: receipts, confirmations, shipping updates, system alerts
- spam: suspicious, irrelevant, or unwanted bulk mail
- job_offer: recruiting outreach, hiring messages, interview invites, role applications for software or AI/ML positions
- other: anything that does not fit the categories above

For job_offer only, set job_focus to one of: {", ".join(JOB_FOCUSES)}
- software: software engineering, full-stack, backend, frontend, DevOps, mobile
- ai_ml: machine learning, AI, LLM, data science, MLOps, research engineer
- other: job-related but unclear or non-technical role
For all non-job_offer categories, set job_focus to null.

Respond with valid JSON only, using this exact schema:
{{
  "category": "<one category>",
  "job_focus": "<software|ai_ml|other|null>",
  "priority": "<one priority>",
  "recommended_action": "<one action>",
  "confidence": <float between 0 and 1>,
  "summary": "<one concise sentence>"
}}"""


def build_user_prompt(email: dict[str, str]) -> str:
    """
    Build the user message sent to the LLM for a single parsed email.

    Args:
        email: Parsed email dict with ``sender``, ``subject``, and ``snippet``.

    Returns:
        Formatted prompt string for the chat completion API.
    """
    return (
        f"From: {email.get('sender', 'Unknown')}\n"
        f"Subject: {email.get('subject', '(no subject)')}\n"
        f"Body preview:\n{email.get('snippet', '')}"
    )
