"""Token accounting: exact counts, heuristic estimates, and what they cost.

The whole lesson is here. Every later phase budgets context, cost and latency
in tokens, and all three are the same number wearing different hats. A number
you estimate to within 20% is not a budget, it is a hope -- which is why this
module ships an exact counter and keeps the heuristic only as the control that
proves the point.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

# Approximation of the GPT-4 (cl100k) pretokenizer, restricted to the ASCII
# ranges that dominate source code, diffs and tracebacks. Deliberately NOT a
# real tokenizer -- see estimate_heuristic().
_PRETOK = re.compile(
    r"'(?:[sdmt]|ll|ve|re)"
    r"|[^\r\n\w]?\w+"
    r"|\d{1,3}"
    r"| ?[^\s\w]+[\r\n]*"
    r"|\s*[\r\n]+"
    r"|\s+(?!\S)"
    r"|\s+"
)

# The naive rule of thumb this lesson exists to disprove.
_CHARS_PER_TOKEN = 4.0

REFERENCE_ENCODING = "cl100k_base"


class TokenizerUnavailable(RuntimeError):
    """Raised when an exact count is requested but no tokenizer is installed."""


# --------------------------------------------------------------- counting

def count_exact(text: str, encoding: str = REFERENCE_ENCODING) -> int:
    """Real BPE token count. Requires the `exact` extra (tiktoken).

    This is the only number you are allowed to budget against.
    """
    try:
        import tiktoken
    except ImportError as exc:  # pragma: no cover - exercised by the offline path
        raise TokenizerUnavailable(
            "exact counting needs tiktoken: pip install -e '.[exact]'"
        ) from exc
    return len(tiktoken.get_encoding(encoding).encode(text))


def estimate_heuristic(text: str) -> int:
    """The chars/4 rule of thumb. Kept as a control, not as an answer.

    Measured against the real tokenizer on this lesson's five fixture
    payloads it lands between -34.6% and +18.4%. The two-sided error is the
    important part: no single correction factor rescues it, because prose and
    code err in the opposite direction from terminal output.
    """
    return round(len(text) / _CHARS_PER_TOKEN)


def estimate_pretokens(text: str) -> int:
    """A better heuristic -- still not good enough. Shown for comparison."""
    return sum(max(1, math.ceil(len(p) / 6.0)) for p in _PRETOK.findall(text))


def count(text: str, exact: bool = True) -> tuple[int, str]:
    """Return (count, method). Falls back to the heuristic and says so."""
    if exact:
        try:
            return count_exact(text), "exact"
        except TokenizerUnavailable:
            pass
    return estimate_heuristic(text), "heuristic"


# --------------------------------------------------------------- pricing

@dataclass(frozen=True)
class Model:
    name: str
    input_per_m: float
    output_per_m: float
    cache_read_multiplier: float
    cache_write_multiplier: float

    def cost(self, tokens_in: int, tokens_out: int,
             cached_in: int = 0) -> float:
        """Cost in USD. `cached_in` is the slice of tokens_in served from cache."""
        fresh_in = max(0, tokens_in - cached_in)
        return (
            fresh_in / 1_000_000 * self.input_per_m
            + cached_in / 1_000_000 * self.input_per_m * self.cache_read_multiplier
            + tokens_out / 1_000_000 * self.output_per_m
        )


def load_models(path: str | Path) -> dict[str, Model]:
    """Load the reader-supplied price table.

    Prices are NOT baked into the package on purpose: they are the fastest-
    moving number in this course, and a stale hardcoded price is worse than no
    price at all because it looks authoritative.
    """
    data = json.loads(Path(path).read_text())
    return {
        name: Model(
            name=name,
            input_per_m=float(m["input_per_m"]),
            output_per_m=float(m["output_per_m"]),
            cache_read_multiplier=float(m.get("cache_read_multiplier", 1.0)),
            cache_write_multiplier=float(m.get("cache_write_multiplier", 1.0)),
        )
        for name, m in data["models"].items()
    }


def price_spread(models: dict[str, Model], tokens_in: int,
                 tokens_out: int) -> tuple[float, float, float]:
    """(cheapest, dearest, ratio) for one payload across the whole table."""
    costs = [m.cost(tokens_in, tokens_out) for m in models.values()]
    lo, hi = min(costs), max(costs)
    return lo, hi, (hi / lo if lo > 0 else float("inf"))


# --------------------------------------------------------------- the loop

@dataclass(frozen=True)
class LoopResult:
    total_usd: float
    total_tokens_in: int
    cached_tokens_in: int
    turns: int


def simulate_loop(model: Model, turns: int = 10, prefix_tokens: int = 4_000,
                  observation_tokens: int = 800, output_tokens: int = 300,
                  stable_prefix: bool = True) -> LoopResult:
    """Cost of a tool loop, with and without a cacheable prefix.

    The prefix is the system prompt plus the tool schemas: large, identical
    every turn, and therefore free to cache -- *if* you don't mutate it. Inject
    a timestamp or a turn counter into it and every turn pays full price. That
    single mistake is the difference the gate measures.
    """
    total = 0.0
    total_in = 0
    cached_in = 0
    history = 0
    for turn in range(turns):
        tokens_in = prefix_tokens + history + observation_tokens
        # The prefix is cacheable from the second turn on, and only while it
        # is byte-identical to the previous turn.
        cached = prefix_tokens if (stable_prefix and turn > 0) else 0
        total += model.cost(tokens_in, output_tokens, cached_in=cached)
        total_in += tokens_in
        cached_in += cached
        history += observation_tokens + output_tokens
    return LoopResult(total, total_in, cached_in, turns)


# --------------------------------------------------------------- fixtures

def load_reference_counts(path: str | Path) -> dict[str, int]:
    """Ground-truth counts recorded on the reference machine."""
    return json.loads(Path(path).read_text())["counts"]
