"""Command-line entry point for the fixture-driven diagnostic path."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .diagnostics import diagnose
from .normalize import normalize
from .provider import load_fixture
from .report import report_json, report_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a read-only Google Ads diagnostic against a sanitized fixture.")
    parser.add_argument("--fixture", required=True, help="Path to a sanitized JSON provider fixture")
    parser.add_argument("--as-of", default=date.today().isoformat(), help="ISO date used for campaign date-bound checks")
    parser.add_argument("--json-out", help="Write the machine-readable report to this path")
    parser.add_argument("--markdown-out", help="Write the human-readable report to this path")
    return parser


def run_fixture(fixture: str | Path, *, as_of: str) -> tuple[str, str]:
    """Execute LOAD/READ -> NORMALIZE -> DIAGNOSE -> REPORT."""

    provider = load_fixture(fixture)
    snapshot = provider.read_state()
    normalized = normalize(snapshot)
    result = diagnose(normalized, as_of=as_of)
    return report_json(result), report_markdown(result)


def _write(path: str, content: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        machine_report, human_report = run_fixture(args.fixture, as_of=args.as_of)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.json_out:
        _write(args.json_out, machine_report)
    if args.markdown_out:
        _write(args.markdown_out, human_report)
    if not args.json_out and not args.markdown_out:
        print(machine_report, end="")
        print("\n--- HUMAN REPORT ---\n")
        print(human_report, end="")
    else:
        if args.json_out:
            print(f"JSON report: {args.json_out}")
        if args.markdown_out:
            print(f"Markdown report: {args.markdown_out}")
    return 0
