"""Small provider-independent models used by the diagnostic capability."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OutcomeState(str, Enum):
    """Top-level outcome states exposed by a diagnostic report."""

    OK = "OK"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    GOOGLE_ACTION_REQUIRED = "GOOGLE_ACTION_REQUIRED"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKER = "BLOCKER"


@dataclass(frozen=True)
class Evidence:
    source: str
    field: str
    value: Any
    note: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "field": self.field,
            "value": self.value,
            "note": self.note,
        }


@dataclass(frozen=True)
class EntityRef:
    kind: str
    identifier: str
    name: str | None = None

    def as_dict(self) -> dict[str, str]:
        result = {"kind": self.kind, "identifier": self.identifier}
        if self.name:
            result["name"] = self.name
        return result


@dataclass(frozen=True)
class Budget:
    amount_micros: int
    period: str
    status: str


@dataclass(frozen=True)
class Bidding:
    strategy: str
    requires_conversions: bool
    target_cpa_micros: int | None = None
    target_roas: float | None = None


@dataclass(frozen=True)
class TargetingRestriction:
    restriction_type: str
    status: str
    detail: str


@dataclass(frozen=True)
class Targeting:
    locations: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    restrictions: tuple[TargetingRestriction, ...] = ()


@dataclass(frozen=True)
class ConversionConfig:
    configured: bool
    primary_action_count: int
    usable_count: int
    recent_count: int
    tracking_status: str


@dataclass(frozen=True)
class PerformanceSnapshot:
    window_days: int
    impressions: int
    clicks: int
    cost_micros: int
    api_evidence_complete: bool


@dataclass(frozen=True)
class Ad:
    identifier: str
    name: str
    status: str
    policy_status: str
    serving_status: str


@dataclass(frozen=True)
class Keyword:
    identifier: str
    text: str
    status: str
    serving_status: str
    low_search_volume: bool


@dataclass(frozen=True)
class AdGroup:
    identifier: str
    name: str
    status: str
    serving_status: str
    ads: tuple[Ad, ...] = ()
    keywords: tuple[Keyword, ...] = ()


@dataclass(frozen=True)
class Campaign:
    identifier: str
    name: str
    status: str
    serving_status: str
    start_date: str | None
    end_date: str | None
    budget: Budget
    bidding: Bidding
    targeting: Targeting
    conversion: ConversionConfig
    performance: PerformanceSnapshot
    ad_groups: tuple[AdGroup, ...] = ()


@dataclass(frozen=True)
class Account:
    identifier: str
    name: str
    status: str
    eligibility: str


@dataclass(frozen=True)
class NormalizedAdsState:
    account: Account
    campaigns: tuple[Campaign, ...]
    source: str = "provider"


@dataclass(frozen=True)
class DiagnosticFinding:
    status: OutcomeState
    severity: Severity
    title: str
    cause: str
    evidence: tuple[Evidence, ...]
    affected_entity: EntityRef
    recommended_action: str
    confidence: str
    uncertainty: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "severity": self.severity.value,
            "title": self.title,
            "cause": self.cause,
            "evidence": [item.as_dict() for item in self.evidence],
            "affected_entity": self.affected_entity.as_dict(),
            "recommended_action": self.recommended_action,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


@dataclass(frozen=True)
class DiagnosticResult:
    outcome: OutcomeState
    findings: tuple[DiagnosticFinding, ...]
    as_of_date: str
    account: Account
    campaigns_evaluated: int

    @property
    def summary(self) -> str:
        if self.outcome is OutcomeState.BLOCKED:
            return "Evidence indicates one or more delivery blockers that should be resolved before expecting normal delivery."
        if self.outcome is OutcomeState.GOOGLE_ACTION_REQUIRED:
            return "Google Ads action is required on an entity policy or eligibility issue before delivery can be trusted."
        if self.outcome is OutcomeState.WARNING:
            return "Delivery is not explained by a confirmed blocker; the evidence points to a warning or a controlled next test."
        return "No delivery blocker was observed in the fields evaluated by this read-only diagnostic."

    @property
    def next_action(self) -> str:
        if self.findings:
            return self.findings[0].recommended_action
        return "No action is indicated by the available evidence."

    def as_dict(self) -> dict[str, Any]:
        return {
            "report_version": "0.1",
            "outcome": self.outcome.value,
            "summary": self.summary,
            "as_of_date": self.as_of_date,
            "account": {
                "identifier": self.account.identifier,
                "name": self.account.name,
                "status": self.account.status,
                "eligibility": self.account.eligibility,
            },
            "campaigns_evaluated": self.campaigns_evaluated,
            "next_action": self.next_action,
            "findings": [finding.as_dict() for finding in self.findings],
        }
