from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath
from typing import Any


FIELD_ORDER = (
    "provider",
    "source_identifier",
    "event_id",
    "occurred_at",
    "captured_at",
    "model",
    "tokens_input",
    "tokens_output",
    "cost",
    "quota",
    "source_reliability",
    "source_provenance",
)

_RE_TRAVERSAL = re.compile(r"(?:^|[/\\])\.\.(?:[/\\]|$)")
_RE_WIN_DRIVE = re.compile(r"^[A-Za-z]:[/\\]")
_RE_UNC = re.compile(r"^[/\\]{2}")


def _is_absolute_path(value: str) -> bool:
    if not value:
        return False
    if value.startswith("/"):
        return True
    try:
        p = Path(value)
        if p.is_absolute():
            return True
    except (ValueError, TypeError):
        pass
    try:
        wp = PureWindowsPath(value)
        if wp.is_absolute():
            return True
    except (ValueError, TypeError):
        pass
    if _RE_WIN_DRIVE.match(value):
        return True
    if _RE_UNC.match(value):
        return True
    return False


def _is_traversal_path(value: str) -> bool:
    if not value:
        return False
    return bool(_RE_TRAVERSAL.search(value))


def _hash_path(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"path-hash:{digest[:16]}"


def sanitize_path_field(value: str | None) -> str | None:
    if value is None:
        return None
    if not _is_absolute_path(value) and not _is_traversal_path(value):
        return value
    return _hash_path(value)


@dataclass(frozen=True)
class NormalizedUsageRecord:
    provider: str
    source_identifier: str
    event_id: str
    occurred_at: str
    captured_at: str
    source_reliability: str = "unknown"

    model: str | None = None
    tokens_input: int | None = None
    tokens_output: int | None = None
    cost: float | None = None
    quota: str | None = None
    source_provenance: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def dedupe_key(self) -> tuple[str, str]:
        return (self.provider, self.event_id)

    def to_row(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "source_identifier": sanitize_path_field(self.source_identifier) or "",
            "event_id": self.event_id,
            "occurred_at": self.occurred_at,
            "captured_at": self.captured_at,
            "model": self.model,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "cost": self.cost,
            "quota": self.quota,
            "source_reliability": self.source_reliability,
            "source_provenance": sanitize_path_field(self.source_provenance),
        }

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> NormalizedUsageRecord:
        return cls(
            provider=row["provider"],
            source_identifier=row["source_identifier"],
            event_id=row["event_id"],
            occurred_at=row["occurred_at"],
            captured_at=row["captured_at"],
            model=row.get("model"),
            tokens_input=row.get("tokens_input"),
            tokens_output=row.get("tokens_output"),
            cost=row.get("cost"),
            quota=row.get("quota"),
            source_reliability=row.get("source_reliability", "unknown"),
            source_provenance=row.get("source_provenance"),
        )
