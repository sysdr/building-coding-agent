"""Claims ledger: every claim must carry a falsification condition."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path

REQUIRED_FIELDS = ("statement", "would_disprove")
MIN_DISPROOF_CHARS = 25
LEDGER_PATH = Path(".apr/claims.json")


class ClaimValidationError(ValueError):
    """Raised when a claim is not falsifiable as written."""


@dataclass(frozen=True)
class Claim:
    claim_id: str
    statement: str
    would_disprove: str
    status: str = "recorded"


def validate_claim(data: dict) -> None:
    """Reject a claim that cannot, even in principle, be proven wrong."""
    missing = [f for f in REQUIRED_FIELDS if not data.get(f, "").strip()]
    if missing:
        raise ClaimValidationError(
            f"missing required field(s): {', '.join(missing)}"
        )
    statement = data["statement"].strip().lower()
    disproof = data["would_disprove"].strip()
    if disproof.lower() == statement:
        raise ClaimValidationError("would_disprove restates the statement")
    if len(disproof) < MIN_DISPROOF_CHARS:
        raise ClaimValidationError(
            "would_disprove is too short to be a real falsification condition"
        )


def record(statement: str, would_disprove: str) -> Claim:
    payload = {"statement": statement, "would_disprove": would_disprove}
    validate_claim(payload)
    digest = hashlib.sha256(
        (statement + would_disprove).encode("utf-8")
    ).hexdigest()[:8]
    claim = Claim(claim_id=digest, **payload)
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if LEDGER_PATH.exists():
        existing = json.loads(LEDGER_PATH.read_text())
    existing.append(asdict(claim))
    LEDGER_PATH.write_text(json.dumps(existing, indent=2))
    return claim
