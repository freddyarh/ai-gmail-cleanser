"""
Gmail label repository — lookup and create user labels (single I/O concern).
"""

from __future__ import annotations

from actions.types import GmailService


class LabelRepository:
    """Caches label name → ID mappings for the authenticated Gmail user."""

    def __init__(self, service: GmailService) -> None:
        self._service = service
        self._ids_by_name: dict[str, str] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        response = self._service.users().labels().list(userId="me").execute()
        self._ids_by_name = {
            label["name"]: label["id"]
            for label in response.get("labels", [])
            if "name" in label and "id" in label
        }
        self._loaded = True

    def id_for(self, name: str) -> str:
        """Return label ID, creating the label in Gmail when it does not exist."""
        self._load()
        if name in self._ids_by_name:
            return self._ids_by_name[name]

        created = (
            self._service.users()
            .labels()
            .create(
                userId="me",
                body={
                    "name": name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            )
            .execute()
        )
        self._ids_by_name[name] = created["id"]
        return created["id"]

    def ids_for_names(self, names: list[str]) -> list[str]:
        """Resolve a list of label names to Gmail label IDs."""
        return [self.id_for(name) for name in names]

    def has_label(self, name: str) -> bool:
        """Return True if the user already has a label with this name."""
        self._load()
        return name in self._ids_by_name
