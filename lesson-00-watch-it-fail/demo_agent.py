#!/usr/bin/env python3
"""demo_agent.py — Lesson 0's pinned, single-file, deliberately unambitious agent.

No planner, no reviewer, no retrieval, no package scaffold: a system prompt, a bash tool,
a loop that stops when the model says it's done or a turn cap is hit. This file is meant
to be read top to bottom in under two minutes.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

MAX_TURNS = 8
TRANSCRIPT_DIR = Path(".apr/demo")
INSTANCES_DIR = Path(__file__).parent / "fixtures" / "instances"
REFERENCE_TRANSCRIPTS_DIR = Path(__file__).parent / "fixtures" / "reference_transcripts"

SYSTEM_PROMPT = (
    "You are a coding agent with a single tool: bash. You are given a git repository "
    "with a failing test suite and an issue describing the bug. Explore the repo, "
    "write a patch, and stop when you believe the failing test now passes. "
    "Respond with a JSON object: either {\"bash\": \"<command>\"} to run a shell "
    "command, or {\"done\": true} to stop."
)


# --------------------------------------------------------------------------
# Model client: a real API path, and a deterministic fixture path for offline
# verification. This lesson's whole point is that a *scripted* agent would be
# safe and pointless — so the fixture path exists only to let `make test` and
# `make verify` run in CI without a paid model call, never to fake the actual
# demo. Running `apr demo --instance a|b` for real requires APR_MODEL_API_KEY.
# --------------------------------------------------------------------------
class ModelClient:
    def call(self, system_prompt: str, history: list[dict]) -> dict:
        raise NotImplementedError


class AnthropicModelClient(ModelClient):
    """Real API path. Not exercised by any test in this lesson — no key is held
    by the environment that built this zip. Uses only the standard library so
    this file has zero third-party dependencies."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-5"):
        self.api_key = api_key
        self.model = model

    def call(self, system_prompt: str, history: list[dict]) -> dict:
        import urllib.request

        body = json.dumps(
            {
                "model": self.model,
                "max_tokens": 1024,
                "system": system_prompt,
                "messages": history,
            }
        ).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read())
        # Newer models may prepend a "thinking" block; take the first text block.
        text = next(
            (block["text"] for block in payload.get("content", []) if block.get("type") == "text"),
            None,
        )
        if text is None:
            raise RuntimeError(f"Anthropic response had no text content: {payload!r}")
        text = text.strip()
        if text.startswith("```"):
            # Models sometimes wrap JSON in a fenced code block.
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)


class FixtureModelClient(ModelClient):
    """Deterministic, offline. Plays back a scripted response list keyed to
    the instance under test, advancing one step per call. Used by tests and
    by `make verify` — never presented as a claim about a real model's
    behavior. See fixtures/instances/*.json for the scripted turns."""

    def __init__(self, turns: list[dict]):
        self._turns = list(turns)
        self._i = 0

    def call(self, system_prompt: str, history: list[dict]) -> dict:
        if self._i >= len(self._turns):
            return {"done": True}
        turn = self._turns[self._i]
        self._i += 1
        return turn


# --------------------------------------------------------------------------
# The agent loop — the ~80 lines the article promises. This is the whole
# thing; nothing else in this file is agent logic.
# --------------------------------------------------------------------------
@dataclass
class RunResult:
    transcript: list[dict] = field(default_factory=list)
    turns_used: int = 0
    resolved: bool = False
    stopped_reason: str = ""


def run_bash_tool(command: str, cwd: Path) -> str:
    try:
        proc = subprocess.run(
            command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30
        )
        return (proc.stdout + proc.stderr)[-4000:]
    except subprocess.TimeoutExpired:
        return "[bash tool timed out after 30s]"


def run_agent(model: ModelClient, repo_dir: Path, issue_text: str) -> RunResult:
    history = [{"role": "user", "content": f"Issue:\n{issue_text}\n\nRepo is at {repo_dir}."}]
    transcript = [{"role": "system", "content": SYSTEM_PROMPT}, dict(history[0])]
    turns = 0
    stopped_reason = "turn_cap"

    while turns < MAX_TURNS:
        response = model.call(SYSTEM_PROMPT, history)
        transcript.append({"role": "assistant", "content": response})

        if response.get("done"):
            stopped_reason = "model_done"
            break

        command = response.get("bash", "")
        output = run_bash_tool(command, repo_dir)
        history.append({"role": "assistant", "content": json.dumps(response)})
        history.append({"role": "user", "content": f"$ {command}\n{output}"})
        transcript.append({"role": "tool", "content": {"command": command, "output": output}})
        turns += 1

    resolved = check_resolved(repo_dir)
    return RunResult(transcript=transcript, turns_used=turns, resolved=resolved, stopped_reason=stopped_reason)


def check_resolved(repo_dir: Path) -> bool:
    """Run this instance's test command and report pass/fail. No grading
    subtlety here on purpose — Lesson 9 is where 'resolved' gets a real
    definition. This is the crude version the article's hook depends on."""
    test_cmd = (repo_dir / "TEST_CMD").read_text().strip()
    proc = subprocess.run(test_cmd, shell=True, cwd=repo_dir, capture_output=True, text=True, timeout=30)
    return proc.returncode == 0


# --------------------------------------------------------------------------
# Instance staging: copy a prepared fixture repo to a scratch dir so repeated
# runs never mutate the shipped fixture.
# --------------------------------------------------------------------------
def stage_instance(instance_id: str) -> tuple[Path, str, list[dict]]:
    spec_path = INSTANCES_DIR / f"instance_{instance_id}.json"
    spec = json.loads(spec_path.read_text())

    workdir = Path(tempfile.mkdtemp(prefix=f"apr-demo-{instance_id}-"))
    repo_dir = workdir / "repo"
    shutil.copytree(INSTANCES_DIR / spec["repo_fixture"], repo_dir)

    return repo_dir, spec["issue_text"], spec["fixture_turns"]


def get_model(live: bool) -> ModelClient:
    if live:
        api_key = os.environ.get("APR_MODEL_API_KEY")
        if not api_key:
            print("APR_MODEL_API_KEY not set — nothing in this lesson works without one.", file=sys.stderr)
            sys.exit(1)
        return AnthropicModelClient(api_key)
    return None  # filled in per-instance by the caller with fixture turns


def cmd_demo(args: argparse.Namespace) -> int:
    repo_dir, issue_text, fixture_turns = stage_instance(args.instance)
    live = bool(os.environ.get("APR_MODEL_API_KEY")) and not args.fixture
    model = AnthropicModelClient(os.environ["APR_MODEL_API_KEY"]) if live else FixtureModelClient(fixture_turns)

    result = run_agent(model, repo_dir, issue_text)

    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = TRANSCRIPT_DIR / f"instance_{args.instance}.json"
    out_path.write_text(json.dumps({
        "instance": args.instance,
        "backend": "fixture" if not live else "live",
        "turns_used": result.turns_used,
        "stopped_reason": result.stopped_reason,
        "resolved": result.resolved,
        "transcript": result.transcript,
    }, indent=2))

    label = "RESOLVED" if result.resolved else "NOT RESOLVED"
    print(f"instance {args.instance} [{'fixture' if not live else 'live'} backend]: {label} "
          f"in {result.turns_used} turns ({result.stopped_reason})")
    print(f"transcript: {out_path}")
    shutil.rmtree(repo_dir.parent, ignore_errors=True)
    return 0


def cmd_predict(args: argparse.Namespace) -> int:
    seal_path = Path("predictions.txt") if args.out is None else Path(args.out)
    if seal_path.exists():
        print(f"{seal_path} already sealed — this file is written once, on purpose.", file=sys.stderr)
        return 1
    seal_path.write_text(args.guess.strip() + "\n" + f"# sealed {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
    print(f"prediction sealed to {seal_path} — unread until Lesson 9's failure taxonomy exists to check it.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="demo_agent.py")
    sub = parser.add_subparsers(dest="command", required=True)

    demo_p = sub.add_parser("demo", help="run the pinned agent against a prepared instance")
    demo_p.add_argument("--instance", choices=["a", "b"], required=True)
    demo_p.add_argument("--fixture", action="store_true",
                         help="force the offline fixture backend even if APR_MODEL_API_KEY is set")
    demo_p.set_defaults(func=cmd_demo)

    predict_p = sub.add_parser("predict", help="seal a one-sentence prediction before Lesson 9")
    predict_p.add_argument("guess")
    predict_p.add_argument("--out", default=None)
    predict_p.set_defaults(func=cmd_predict)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
