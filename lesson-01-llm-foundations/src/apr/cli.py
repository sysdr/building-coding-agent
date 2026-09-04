"""Command line entry point. Plain argparse -- nothing here needs a framework."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from apr import __version__
from apr import doctor as doctor_mod
from apr import tokens as tok

DEFAULT_MODELS = Path("configs/models.json")


def _cmd_doctor(args: argparse.Namespace) -> int:
    results = doctor_mod.run_all()
    for r in results:
        print(r.render())
    ok = doctor_mod.all_critical_pass(results)
    print("PASS: environment doctor all critical checks green" if ok
          else "FAIL: environment doctor found a critical problem")
    return 0 if ok else 1


def _cmd_count(args: argparse.Namespace) -> int:
    text = Path(args.path).read_text()
    heuristic = tok.estimate_heuristic(text)
    pretok = tok.estimate_pretokens(text)
    try:
        exact = tok.count_exact(text)
    except tok.TokenizerUnavailable as exc:
        print(f"chars      {len(text)}")
        print(f"heuristic  {heuristic}  (chars/4)")
        print(f"pretokens  {pretok}")
        print(f"exact      unavailable -- {exc}")
        return 0
    print(f"chars      {len(text)}")
    print(f"exact      {exact}  ({tok.REFERENCE_ENCODING})")
    print(f"heuristic  {heuristic}  (chars/4)  "
          f"{(heuristic - exact) / exact * 100:+.1f}%")
    print(f"pretokens  {pretok}             "
          f"{(pretok - exact) / exact * 100:+.1f}%")
    return 0


def _cmd_price(args: argparse.Namespace) -> int:
    models = tok.load_models(args.models)
    text = Path(args.path).read_text()
    tokens_in, method = tok.count(text)
    tokens_out = args.output_tokens
    print(f"payload {args.path}: {tokens_in} input tokens ({method}), "
          f"{tokens_out} output tokens assumed\n")
    print(f"{'model':<14}{'input $/M':>11}{'output $/M':>12}{'cost':>12}")
    for name, m in models.items():
        print(f"{name:<14}{m.input_per_m:>11.2f}{m.output_per_m:>12.2f}"
              f"{m.cost(tokens_in, tokens_out):>12.6f}")
    lo, hi, ratio = tok.price_spread(models, tokens_in, tokens_out)
    print(f"\nspread: {ratio:.1f}x  (cheapest ${lo:.6f}, dearest ${hi:.6f})")
    return 0


def _cmd_loop(args: argparse.Namespace) -> int:
    models = tok.load_models(args.models)
    model = models[args.model]
    stable = tok.simulate_loop(model, turns=args.turns, stable_prefix=True)
    churned = tok.simulate_loop(model, turns=args.turns, stable_prefix=False)
    saving = (churned.total_usd - stable.total_usd) / churned.total_usd * 100
    print(f"model {model.name}, {args.turns} turns\n")
    print(f"{'prefix':<22}{'input tokens':>14}{'cached':>10}{'cost':>12}")
    print(f"{'stable (cacheable)':<22}{stable.total_tokens_in:>14}"
          f"{stable.cached_tokens_in:>10}{stable.total_usd:>12.6f}")
    print(f"{'mutated each turn':<22}{churned.total_tokens_in:>14}"
          f"{churned.cached_tokens_in:>10}{churned.total_usd:>12.6f}")
    print(f"\nstable prefix costs {saving:.1f}% less for identical work")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="apr", description="Autonomous Program Repair")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="check the local environment").set_defaults(
        func=_cmd_doctor)

    t = sub.add_parser("tokens", help="token accounting")
    tsub = t.add_subparsers(dest="subcommand", required=True)

    c = tsub.add_parser("count", help="exact vs heuristic token count")
    c.add_argument("path")
    c.set_defaults(func=_cmd_count)

    pr = tsub.add_parser("price", help="price one payload across the model table")
    pr.add_argument("path")
    pr.add_argument("--models", default=str(DEFAULT_MODELS))
    pr.add_argument("--output-tokens", type=int, default=500)
    pr.set_defaults(func=_cmd_price)

    lp = tsub.add_parser("loop", help="cached vs uncached tool loop")
    lp.add_argument("--models", default=str(DEFAULT_MODELS))
    lp.add_argument("--model", default="workhorse")
    lp.add_argument("--turns", type=int, default=10)
    lp.set_defaults(func=_cmd_loop)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
