"""Machine-readable and concise human-readable report renderers."""

from __future__ import annotations

import json
from typing import Any

from .models import DiagnosticFinding, DiagnosticResult


BUSINESS_QUESTION = (
    "Why does the existing Google Ads campaign for bek-mebel.kz appear healthy "
    "but fail to meaningfully deliver or spend?"
)


def report_json(result: DiagnosticResult) -> str:
    """Serialize a stable JSON report without raw provider payloads."""

    payload: dict[str, Any] = result.as_dict()
    payload["business_question"] = BUSINESS_QUESTION
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def _finding_markdown(finding: DiagnosticFinding, index: int) -> list[str]:
    lines = [
        f"### {index}. [{finding.status.value}] {finding.title}",
        f"- **Severity:** {finding.severity.value}",
        f"- **Cause:** {finding.cause}",
        f"- **Affected entity:** {finding.affected_entity.kind} `{finding.affected_entity.identifier}`",
    ]
    if finding.affected_entity.name:
        lines.append(f"- **Entity name:** {finding.affected_entity.name}")
    lines.extend(
        [
            "- **Evidence:**",
            *[f"  - `{item.field}` = `{item.value}` — {item.note}" for item in finding.evidence],
            f"- **Recommended next action:** {finding.recommended_action}",
            f"- **Confidence:** {finding.confidence}",
            f"- **Uncertainty:** {finding.uncertainty}",
            "",
        ]
    )
    return lines


def report_markdown(result: DiagnosticResult) -> str:
    """Render a report that answers the business question before listing details."""

    lines = [
        "# Google Ads delivery diagnostic",
        "",
        f"**Outcome:** `{result.outcome.value}`  ",
        f"**As of:** `{result.as_of_date}`  ",
        f"**Account:** {result.account.name} (`{result.account.identifier}`)",
        "",
        "## Answer to the business question",
        "",
        BUSINESS_QUESTION,
        "",
        result.summary,
        "",
        f"**First recommended action:** {result.next_action}",
        "",
        "## Evidence-backed findings",
        "",
    ]
    lines.extend(line for index, finding in enumerate(result.findings, 1) for line in _finding_markdown(finding, index))
    lines.extend(
        [
            "## Evaluated scope",
            "",
            f"- Campaigns evaluated: `{result.campaigns_evaluated}`",
            "- Read-only fields: account eligibility, campaign state/date bounds, budget and bidding, ad groups, ads/policy state, keywords, targeting restrictions, conversion configuration, and recent impressions/clicks/cost.",
            "- The report contains normalized evidence only; it does not include raw provider payloads or credentials.",
            "",
        ]
    )
    return "\n".join(lines)
