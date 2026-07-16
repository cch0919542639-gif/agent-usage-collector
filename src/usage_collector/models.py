from __future__ import annotations

from dataclasses import dataclass, field
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
            "source_identifier": self.source_identifier,
            "event_id": self.event_id,
            "occurred_at": self.occurred_at,
            "captured_at": self.captured_at,
            "model": self.model,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "cost": self.cost,
            "quota": self.quota,
            "source_reliability": self.source_reliability,
            "source_provenance": self.source_provenance,
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
