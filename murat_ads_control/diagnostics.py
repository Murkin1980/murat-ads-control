"""Evidence-backed diagnostic rules for the normalized ads state."""

from __future__ import annotations

from datetime import date
from typing import Iterable

from .models import (
    Ad,
    AdGroup,
    Campaign,
    DiagnosticFinding,
    DiagnosticResult,
    EntityRef,
    Evidence,
    Keyword,
    NormalizedAdsState,
    OutcomeState,
    Severity,
)


_ELIGIBLE = {"ENABLED", "ELIGIBLE", "ACTIVE", "APPROVED"}
_INELIGIBLE = {"DISABLED", "PAUSED", "REMOVED", "NOT_ELIGIBLE", "INELIGIBLE", "UNKNOWN"}
_RESTRICTED = {"BLOCKED", "LIMITED", "NOT_ELIGIBLE", "RESTRICTED", "CONFLICTING"}
_POLICY_ACTION = {"DISAPPROVED", "REJECTED", "POLICY_VIOLATION", "LIMITED"}
_CONVERSION_BIDDING = {"MAXIMIZE_CONVERSIONS", "TARGET_CPA", "TARGET_ROAS", "MAXIMIZE_CONVERSION_VALUE"}
_LOW_IMPRESSION_THRESHOLD = 10


def _entity(campaign: Campaign, *, kind: str = "campaign", identifier: str | None = None, name: str | None = None) -> EntityRef:
    return EntityRef(kind=kind, identifier=identifier or campaign.identifier, name=name or campaign.name)


def _finding(
    *,
    status: OutcomeState,
    severity: Severity,
    title: str,
    cause: str,
    evidence: Iterable[Evidence],
    affected_entity: EntityRef,
    recommended_action: str,
    confidence: str,
    uncertainty: str,
) -> DiagnosticFinding:
    return DiagnosticFinding(
        status=status,
        severity=severity,
        title=title,
        cause=cause,
        evidence=tuple(evidence),
        affected_entity=affected_entity,
        recommended_action=recommended_action,
        confidence=confidence,
        uncertainty=uncertainty,
    )


def _date_block(campaign: Campaign, as_of: date) -> tuple[str, str] | None:
    if campaign.start_date and as_of < date.fromisoformat(campaign.start_date):
        return "start_date", f"starts on {campaign.start_date}, after the diagnostic date"
    if campaign.end_date and as_of > date.fromisoformat(campaign.end_date):
        return "end_date", f"ended on {campaign.end_date}, before the diagnostic date"
    return None


def _campaign_is_active(campaign: Campaign, as_of: date) -> bool:
    return (
        campaign.status == "ENABLED"
        and campaign.serving_status in _ELIGIBLE
        and _date_block(campaign, as_of) is None
        and campaign.budget.status in {"ACTIVE", "ENABLED", "ELIGIBLE"}
        and campaign.budget.amount_micros > 0
    )


def _ad_is_eligible(ad: Ad) -> bool:
    return ad.status in _ELIGIBLE and ad.serving_status in _ELIGIBLE and ad.policy_status in _ELIGIBLE


def _keyword_is_eligible(keyword: Keyword) -> bool:
    return (
        keyword.status in _ELIGIBLE
        and keyword.serving_status in _ELIGIBLE
        and not keyword.low_search_volume
    )


def _diagnose_account(state: NormalizedAdsState) -> list[DiagnosticFinding]:
    findings: list[DiagnosticFinding] = []
    entity = EntityRef("account", state.account.identifier, state.account.name)
    if state.account.status != "ENABLED":
        findings.append(
            _finding(
                status=OutcomeState.BLOCKED,
                severity=Severity.BLOCKER,
                title="Account is not enabled",
                cause=f"The account status is {state.account.status}, so campaign delivery cannot be assumed.",
                evidence=(Evidence("provider", "account.status", state.account.status, "account status"),),
                affected_entity=entity,
                recommended_action="Resolve the account status in Google Ads, then rerun the read-only diagnostic.",
                confidence="HIGH",
                uncertainty="The snapshot does not explain why Google assigned this account status.",
            )
        )
    if state.account.eligibility not in _ELIGIBLE:
        findings.append(
            _finding(
                status=OutcomeState.BLOCKED,
                severity=Severity.BLOCKER,
                title="Account eligibility is not confirmed",
                cause=f"The account eligibility value is {state.account.eligibility}.",
                evidence=(Evidence("provider", "account.eligibility", state.account.eligibility, "account eligibility"),),
                affected_entity=entity,
                recommended_action="Check the account eligibility or billing/policy notice in Google Ads; no account change is performed here.",
                confidence="HIGH",
                uncertainty="The provider snapshot does not include the detailed eligibility reason.",
            )
        )
    return findings


def _diagnose_campaign_state(campaign: Campaign, as_of: date) -> list[DiagnosticFinding]:
    findings: list[DiagnosticFinding] = []
    entity = _entity(campaign)
    if campaign.status != "ENABLED":
        findings.append(
            _finding(
                status=OutcomeState.BLOCKED,
                severity=Severity.BLOCKER,
                title="Campaign is not enabled",
                cause=f"The campaign status is {campaign.status}; a paused or removed campaign cannot serve normally.",
                evidence=(Evidence("provider", "campaign.status", campaign.status, "campaign status"),),
                affected_entity=entity,
                recommended_action="Confirm whether the campaign should be enabled with the account owner; this tool does not change campaign state.",
                confidence="HIGH",
                uncertainty="The diagnostic cannot infer whether the status was intentional.",
            )
        )
    if campaign.serving_status not in _ELIGIBLE:
        findings.append(
            _finding(
                status=OutcomeState.BLOCKED,
                severity=Severity.BLOCKER,
                title="Campaign is not eligible to serve",
                cause=f"The provider reports campaign serving status {campaign.serving_status}.",
                evidence=(Evidence("provider", "campaign.serving_status", campaign.serving_status, "serving status"),),
                affected_entity=entity,
                recommended_action="Inspect the campaign's serving-status details in Google Ads and address the reported blocker.",
                confidence="HIGH",
                uncertainty="The normalized contract records the status but not a provider-specific explanation code.",
            )
        )
    date_block = _date_block(campaign, as_of)
    if date_block:
        field, detail = date_block
        findings.append(
            _finding(
                status=OutcomeState.BLOCKED,
                severity=Severity.BLOCKER,
                title="Campaign is outside its date bounds",
                cause=f"The campaign {detail}.",
                evidence=(
                    Evidence("provider", f"campaign.{field}", getattr(campaign, field), f"evaluated against {as_of.isoformat()}"),
                    Evidence("diagnostic", "as_of_date", as_of.isoformat(), "date used for the date-bound check"),
                ),
                affected_entity=entity,
                recommended_action="Verify the intended campaign start/end dates with the account owner; no dates are changed here.",
                confidence="HIGH",
                uncertainty="Date bounds alone do not explain why the UI may look healthy outside the active window.",
            )
        )
    if campaign.budget.status not in {"ACTIVE", "ENABLED", "ELIGIBLE"} or campaign.budget.amount_micros <= 0:
        findings.append(
            _finding(
                status=OutcomeState.BLOCKED,
                severity=Severity.BLOCKER,
                title="Campaign budget is not usable",
                cause="The budget is inactive or has no positive daily amount in the provider snapshot.",
                evidence=(
                    Evidence("provider", "campaign.budget.status", campaign.budget.status, "budget status"),
                    Evidence("provider", "campaign.budget.amount_micros", campaign.budget.amount_micros, "budget amount in micros"),
                ),
                affected_entity=entity,
                recommended_action="Review the budget configuration in Google Ads with the account owner; do not change it automatically.",
                confidence="HIGH",
                uncertainty="A usable budget does not guarantee impressions, so this rule does not diagnose auction demand.",
            )
        )
    if campaign.bidding.requires_conversions or campaign.bidding.strategy in _CONVERSION_BIDDING:
        if not campaign.conversion.configured or campaign.conversion.usable_count <= 0 or campaign.conversion.recent_count <= 0:
            findings.append(
                _finding(
                    status=OutcomeState.WARNING,
                    severity=Severity.WARNING,
                    title="Conversion-dependent bidding has no usable recent history",
                    cause=f"{campaign.bidding.strategy} is configured, but usable conversions are {campaign.conversion.usable_count} and recent conversions are {campaign.conversion.recent_count}.",
                    evidence=(
                        Evidence("provider", "campaign.bidding.strategy", campaign.bidding.strategy, "bidding strategy"),
                        Evidence("provider", "campaign.conversion.configured", campaign.conversion.configured, "conversion configuration present"),
                        Evidence("provider", "campaign.conversion.usable_count", campaign.conversion.usable_count, "usable conversion actions"),
                        Evidence("provider", "campaign.conversion.recent_count", campaign.conversion.recent_count, "recent conversions"),
                    ),
                    affected_entity=entity,
                    recommended_action="Verify primary conversion actions and recent conversion tracking before treating automated bidding as a reliable delivery explanation.",
                    confidence="MEDIUM",
                    uncertainty="This is a delivery risk/hypothesis, not proof that bidding alone caused the observed spend level.",
                )
            )
    for restriction in campaign.targeting.restrictions:
        if restriction.status in _RESTRICTED:
            findings.append(
                _finding(
                    status=OutcomeState.WARNING,
                    severity=Severity.WARNING,
                    title="Targeting contains a delivery restriction",
                    cause=f"The {restriction.restriction_type} targeting is marked {restriction.status}: {restriction.detail or 'no detail supplied'}.",
                    evidence=(
                        Evidence("provider", "campaign.targeting.restriction_type", restriction.restriction_type, "targeting restriction type"),
                        Evidence("provider", "campaign.targeting.restriction_status", restriction.status, "targeting restriction status"),
                        Evidence("provider", "campaign.targeting.restriction_detail", restriction.detail, "provider detail"),
                    ),
                    affected_entity=entity,
                    recommended_action="Review the affected location/language/targeting restriction in Google Ads before widening or changing anything.",
                    confidence="MEDIUM",
                    uncertainty="The fixture contract does not include auction-level reach estimates for the restriction.",
                )
            )
    return findings


def _diagnose_ad_group(campaign: Campaign, group: AdGroup) -> list[DiagnosticFinding]:
    findings: list[DiagnosticFinding] = []
    group_entity = _entity(campaign, kind="ad_group", identifier=group.identifier, name=group.name)
    if group.status not in _ELIGIBLE or group.serving_status not in _ELIGIBLE:
        findings.append(
            _finding(
                status=OutcomeState.BLOCKED,
                severity=Severity.BLOCKER,
                title="Ad group is not eligible",
                cause=f"The ad group status is {group.status} and serving status is {group.serving_status}.",
                evidence=(
                    Evidence("provider", "ad_group.status", group.status, "ad group status"),
                    Evidence("provider", "ad_group.serving_status", group.serving_status, "ad group serving status"),
                ),
                affected_entity=group_entity,
                recommended_action="Review the ad group status and serving details with the account owner; no entity status is changed here.",
                confidence="HIGH",
                uncertainty="The provider snapshot does not include a detailed status reason.",
            )
        )
    if not group.ads:
        findings.append(
            _finding(
                status=OutcomeState.BLOCKED,
                severity=Severity.BLOCKER,
                title="Ad group has no ads",
                cause="No ads were returned for the ad group, so it cannot serve an ad impression.",
                evidence=(Evidence("provider", "ad_group.ads", 0, "ads returned"),),
                affected_entity=group_entity,
                recommended_action="Add or restore an approved ad through an explicitly approved Google Ads workflow; this diagnostic is read-only.",
                confidence="HIGH",
                uncertainty="The snapshot may be incomplete if the provider query did not return all ads.",
            )
        )
    for ad in group.ads:
        if not _ad_is_eligible(ad):
            action_required = ad.policy_status in _POLICY_ACTION
            findings.append(
                _finding(
                    status=OutcomeState.GOOGLE_ACTION_REQUIRED if action_required else OutcomeState.BLOCKED,
                    severity=Severity.BLOCKER,
                    title="Ad is not eligible to serve" if not action_required else "Ad requires Google policy action",
                    cause=f"The ad has status {ad.status}, serving status {ad.serving_status}, and policy status {ad.policy_status}.",
                    evidence=(
                        Evidence("provider", "ad.status", ad.status, "ad status"),
                        Evidence("provider", "ad.serving_status", ad.serving_status, "ad serving status"),
                        Evidence("provider", "ad.policy_status", ad.policy_status, "policy/approval status"),
                    ),
                    affected_entity=_entity(campaign, kind="ad", identifier=ad.identifier, name=ad.name),
                    recommended_action="Open the ad's policy/eligibility details in Google Ads and resolve or appeal the issue as appropriate.",
                    confidence="HIGH",
                    uncertainty="The provider snapshot does not include the full policy diagnostic text.",
                )
            )
    if not group.keywords:
        findings.append(
            _finding(
                status=OutcomeState.BLOCKED,
                severity=Severity.BLOCKER,
                title="Ad group has no keywords in the diagnostic snapshot",
                cause="No keywords were returned for the ad group, so keyword-driven search delivery cannot be confirmed.",
                evidence=(Evidence("provider", "ad_group.keywords", 0, "keywords returned"),),
                affected_entity=group_entity,
                recommended_action="Verify that the provider query includes the intended keywords; do not add or alter keywords automatically.",
                confidence="MEDIUM",
                uncertainty="The absence may reflect query scope rather than account state.",
            )
        )
    else:
        low_search = [keyword for keyword in group.keywords if keyword.low_search_volume]
        unavailable = [keyword for keyword in group.keywords if not _keyword_is_eligible(keyword)]
        if len(low_search) > len(group.keywords) / 2:
            status = OutcomeState.BLOCKED if len(low_search) == len(group.keywords) else OutcomeState.WARNING
            findings.append(
                _finding(
                    status=status,
                    severity=Severity.BLOCKER if status is OutcomeState.BLOCKED else Severity.WARNING,
                    title="Most keywords have low search volume",
                    cause=f"{len(low_search)} of {len(group.keywords)} keywords are marked low search volume.",
                    evidence=(
                        Evidence("provider", "ad_group.keywords.total", len(group.keywords), "keywords evaluated"),
                        Evidence("provider", "ad_group.keywords.low_search_volume", len(low_search), "low-search-volume keywords"),
                    ),
                    affected_entity=group_entity,
                    recommended_action="Validate demand with the account owner and plan a controlled keyword/demand test; no keywords are changed here.",
                    confidence="HIGH",
                    uncertainty="Low search volume is a platform eligibility signal, not proof of the broader business demand.",
                )
            )
        elif len(unavailable) > len(group.keywords) / 2:
            findings.append(
                _finding(
                    status=OutcomeState.WARNING,
                    severity=Severity.WARNING,
                    title="Most keywords are not eligible",
                    cause=f"{len(unavailable)} of {len(group.keywords)} keywords are not eligible based on status, serving status, or low search volume.",
                    evidence=(
                        Evidence("provider", "ad_group.keywords.total", len(group.keywords), "keywords evaluated"),
                        Evidence("provider", "ad_group.keywords.unavailable", len(unavailable), "keywords not eligible"),
                    ),
                    affected_entity=group_entity,
                    recommended_action="Inspect keyword status details and confirm the intended query coverage before making a controlled change.",
                    confidence="MEDIUM",
                    uncertainty="The normalized contract does not carry every provider-specific keyword diagnostic reason.",
                )
            )
    return findings


def _diagnose_performance(campaign: Campaign, as_of: date) -> list[DiagnosticFinding]:
    if not _campaign_is_active(campaign, as_of):
        return []
    all_groups_active = bool(campaign.ad_groups) and all(
        group.status in _ELIGIBLE and group.serving_status in _ELIGIBLE for group in campaign.ad_groups
    )
    eligible_ads = [ad for group in campaign.ad_groups for ad in group.ads if _ad_is_eligible(ad)]
    eligible_keywords = [keyword for group in campaign.ad_groups for keyword in group.keywords if _keyword_is_eligible(keyword)]
    if not (all_groups_active and eligible_ads and eligible_keywords):
        return []
    performance = campaign.performance
    if performance.impressions == 0:
        return [
            _finding(
                status=OutcomeState.WARNING,
                severity=Severity.WARNING,
                title="Technically eligible campaign has zero recent impressions",
                cause="The campaign, ad groups, ads, keywords, budget, and date bounds look eligible, but the recent performance window contains zero impressions.",
                evidence=(
                    Evidence("provider", "campaign.performance.window_days", performance.window_days, "recent performance window"),
                    Evidence("provider", "campaign.performance.impressions", performance.impressions, "recent impressions"),
                    Evidence("provider", "campaign.performance.clicks", performance.clicks, "recent clicks"),
                    Evidence("provider", "campaign.performance.cost_micros", performance.cost_micros, "recent cost in micros"),
                    Evidence("provider", "campaign.performance.api_evidence_complete", performance.api_evidence_complete, "snapshot completeness flag"),
                ),
                affected_entity=_entity(campaign),
                recommended_action="Run a bounded read-only refresh or a separately approved, controlled delivery test; do not infer a definitive root cause from this snapshot.",
                confidence="MEDIUM",
                uncertainty="The available API fields show zero activity but are insufficient to identify the auction-level cause.",
            )
        ]
    if performance.impressions < _LOW_IMPRESSION_THRESHOLD:
        return [
            _finding(
                status=OutcomeState.WARNING,
                severity=Severity.WARNING,
                title="Campaign has very low recent delivery",
                cause=f"The campaign received only {performance.impressions} impressions in the recent window.",
                evidence=(
                    Evidence("provider", "campaign.performance.window_days", performance.window_days, "recent performance window"),
                    Evidence("provider", "campaign.performance.impressions", performance.impressions, "recent impressions"),
                    Evidence("provider", "campaign.performance.clicks", performance.clicks, "recent clicks"),
                ),
                affected_entity=_entity(campaign),
                recommended_action="Compare a fresh read against the intended demand and targeting before proposing any approved campaign change.",
                confidence="MEDIUM",
                uncertainty="Low delivery has multiple possible causes not represented by this minimal contract.",
            )
        ]
    return []


def diagnose(state: NormalizedAdsState, *, as_of: str | date) -> DiagnosticResult:
    """Evaluate only observable state and preserve uncertainty in each finding."""

    evaluation_date = date.fromisoformat(as_of) if isinstance(as_of, str) else as_of
    findings = _diagnose_account(state)
    for campaign in state.campaigns:
        findings.extend(_diagnose_campaign_state(campaign, evaluation_date))
        for group in campaign.ad_groups:
            findings.extend(_diagnose_ad_group(campaign, group))
        findings.extend(_diagnose_performance(campaign, evaluation_date))

    if not findings:
        findings.append(
            _finding(
                status=OutcomeState.OK,
                severity=Severity.INFO,
                title="No blocker observed in the evaluated fields",
                cause="The account and evaluated campaign entities appear eligible and have recent activity.",
                evidence=(Evidence("diagnostic", "campaigns_evaluated", len(state.campaigns), "campaign count"),),
                affected_entity=EntityRef("account", state.account.identifier, state.account.name),
                recommended_action="Continue read-only monitoring; no change is indicated by this snapshot.",
                confidence="MEDIUM",
                uncertainty="This report does not evaluate fields outside the minimal diagnostic contract.",
            )
        )

    order = {
        OutcomeState.BLOCKED: 0,
        OutcomeState.GOOGLE_ACTION_REQUIRED: 1,
        OutcomeState.WARNING: 2,
        OutcomeState.OK: 3,
    }
    findings.sort(key=lambda finding: (order[finding.status], finding.severity.value))
    if any(finding.status is OutcomeState.BLOCKED for finding in findings):
        outcome = OutcomeState.BLOCKED
    elif any(finding.status is OutcomeState.GOOGLE_ACTION_REQUIRED for finding in findings):
        outcome = OutcomeState.GOOGLE_ACTION_REQUIRED
    elif any(finding.status is OutcomeState.WARNING for finding in findings):
        outcome = OutcomeState.WARNING
    else:
        outcome = OutcomeState.OK
    return DiagnosticResult(
        outcome=outcome,
        findings=tuple(findings),
        as_of_date=evaluation_date.isoformat(),
        account=state.account,
        campaigns_evaluated=len(state.campaigns),
    )
