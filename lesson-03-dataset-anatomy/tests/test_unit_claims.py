import json
import tempfile
import unittest
from pathlib import Path

from apr.claims import ClaimValidationError, append_claim, load_ledger, validate_claim


class TestClaims(unittest.TestCase):
    def test_rejects_missing_would_disprove(self):
        with self.assertRaisesRegex(ClaimValidationError, "missing required field"):
            validate_claim({"statement": "the swarm beats a single agent", "would_disprove": ""})

    def test_rejects_restated_disproof(self):
        with self.assertRaisesRegex(ClaimValidationError, "restates"):
            validate_claim(
                {
                    "statement": "The swarm beats the baseline",
                    "would_disprove": "the swarm beats the baseline",
                }
            )

    def test_rejects_too_short_disproof(self):
        with self.assertRaisesRegex(ClaimValidationError, "too short"):
            validate_claim({"statement": "X works", "would_disprove": "it fails"})

    def test_accepts_a_real_falsifiable_claim(self):
        validate_claim(
            {
                "statement": "A minimal single-agent scaffold resolves at least as many "
                "dev-slice instances as a three-role swarm at equal token budget.",
                "would_disprove": "The swarm resolves strictly more instances than the "
                "single agent on the same 20-instance slice at equal or lower cost.",
            }
        )  # no exception raised is the assertion

    def test_append_claim_writes_to_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claims.json"
            append_claim(
                statement="Gold patches must reproduce at 100% before any agent is trusted.",
                would_disprove="A gold-patch run on the dev slice scores below 100%.",
                path=path,
            )
            ledger = load_ledger(path)
            self.assertEqual(len(ledger), 1)
            self.assertEqual(ledger[0]["status"], "recorded")
            self.assertEqual(json.loads(path.read_text()), ledger)


if __name__ == "__main__":
    unittest.main()
