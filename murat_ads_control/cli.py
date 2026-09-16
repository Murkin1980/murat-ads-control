"""Command-line entry point for fixture and read-only Google Ads diagnostics."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .config import ConfigurationError
from .diagnostics import diagnose
from .google_ads import GoogleAdsClientError, GoogleAdsDependencyError, GoogleAdsProvider, GoogleAdsReadError
from .normalize import normalize
from .provider import ReadOnlyAdsProvider, load_fixture
from .report import report_json, report_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a read-only Google Ads diagnostic.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixture", help="Path to a sanitized JSON provider fixture")
    mode.add_argument("--google-ads", action="store_true", help="Read one configured Google Ads customer")
    parser.add_argument("--as-of", default=date.today().isoformat(), help="ISO date used for campaign date-bound checks")
    parser.add_argument("--json-out", help="Write the machine-readable report to this path")
    parser.add_argument("--markdown-out", help="Write the human-readable report to this path")
    return parser


def _render(provider: ReadOnlyAdsProvider, *, as_of: str) -> tuple[str, str]:
    # Both fixture and Google providers implement the same one-method contract.
    snapshot = provider.read_state()
    normalized = normalize(snapshot)
    result = diagnose(normalized, as_of=as_of)
    return report_json(result), report_markdown(result)


def run_fixture(fixture: str | Path, *, as_of: str) -> tuple[str, str]:
    """Execute the existing LOAD/READ -> NORMALIZE -> DIAGNOSE -> REPORT path."""

    return _render(load_fixture(fixture), as_of=as_of)


def run_google_ads(*, as_of: str) -> tuple[str, str]:
    """Execute the real provider path with environment-injected credentials."""

    return _render(GoogleAdsProvider.from_environment(), as_of=as_of)


def _write(path: str, content: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.fixture:
            machine_report, human_report = run_fixture(args.fixture, as_of=args.as_of)
        else:
            machine_report, human_report = run_google_ads(as_of=args.as_of)
    except (ConfigurationError, GoogleAdsDependencyError, GoogleAdsClientError, GoogleAdsReadError, OSError, ValueError) as exc:
        # Provider exceptions intentionally contain configuration names or safe
        # exception types, never SDK payloads or credential values.
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
