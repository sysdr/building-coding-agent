"""The claims ledger.

A claim is only useful if it says what would prove it wrong. This module
rejects any claim missing a `would_disprove` field, or where that field
just restates the claim. Gate 5 (Lesson 36) reads this same file to check
whether the multi-agent swarm's claim was actually confirmed or falsified.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LEDGER_PATH = Path(".apr/claims.json")
REQUIRED_FIELDS = ("statement", "would_disprove")


class ClaimValidationError(ValueError):
    """Raised when a claim is missing required fields or is not falsifiable."""


@dataclass
class Claim:
    statement: str
    would_disprove: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    status: str = "recorded"  # recorded | confirmed | falsified


def validate_claim(data: dict) -> None:
    missing = [f for f in REQUIRED_FIELDS if not data.get(f, "").strip()]
    if missing:
        raise ClaimValidationError(f"missing required field(s): {', '.join(missing)}")

    statement = data["statement"].strip().lower()
    disprove = data["would_disprove"].strip().lower()
    if disprove == statement:
        raise ClaimValidationError(
            "would_disprove restates the statement — it must describe a "
            "distinct, observable result that contradicts the claim"
        )
    if len(data["would_disprove"].strip()) < 15:
        raise ClaimValidationError(
            "would_disprove is too short to be a real falsification condition"
        )


def load_ledger(path: Path = DEFAULT_LEDGER_PATH) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text())


def append_claim(statement: str, would_disprove: str, path: Path = DEFAULT_LEDGER_PATH) -> Claim:
    validate_claim({"statement": statement, "would_disprove": would_disprove})
    claim = Claim(statement=statement, would_disprove=would_disprove)
    ledger = load_ledger(path)
    ledger.append(asdict(claim))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2) + "\n")
    return claim
