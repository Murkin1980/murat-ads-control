"""Normalize provider-shaped snapshots into the small internal model."""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping

from .models import (
    Account,
    Ad,
    AdGroup,
    Bidding,
    Budget,
    Campaign,
    ConversionConfig,
    Keyword,
    NormalizedAdsState,
    PerformanceSnapshot,
    Targeting,
    TargetingRestriction,
)
from .provider import RawAdsSnapshot


class NormalizationError(ValueError):
    """Raised when the provider response cannot support a diagnostic run."""


def _object(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise NormalizationError(f"{field} must be an object")
    return value


def _array(value: Any, field: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise NormalizationError(f"{field} must be an array")
    return value


def _text(value: Any, field: str, *, default: str = "") -> str:
    if value is None:
        return default
    if not isinstance(value, str):
        raise NormalizationError(f"{field} must be a string")
    return value


def _status(value: Any, field: str, *, default: str = "UNKNOWN") -> str:
    return _text(value, field, default=default).upper()


def _integer(value: Any, field: str, *, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NormalizationError(f"{field} must be a number")
    return int(value)


def _number(value: Any, field: str, *, default: float | None = None) -> float | None:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NormalizationError(f"{field} must be a number")
    return float(value)


def _boolean(value: Any, field: str, *, default: bool = False) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise NormalizationError(f"{field} must be a boolean")
    return value


def _date_string(value: Any, field: str) -> str | None:
    if value is None or value == "":
        return None
    result = _text(value, field)
    try:
        date.fromisoformat(result)
    except ValueError as exc:
        raise NormalizationError(f"{field} must be an ISO date") from exc
    return result


def _identifier(raw: Mapping[str, Any], field: str, *, fallback: str) -> str:
    value = raw.get("id", raw.get("identifier", fallback))
    result = _text(value, f"{field}.id", default=fallback)
    if not result:
        raise NormalizationError(f"{field}.id must not be empty")
    return result


def _normalize_ad(raw: Mapping[str, Any], path: str, index: int) -> Ad:
    identifier = _identifier(raw, path, fallback=f"ad-{index + 1}")
    return Ad(
        identifier=identifier,
        name=_text(raw.get("name"), f"{path}.name", default=identifier),
        status=_status(raw.get("status"), f"{path}.status"),
        policy_status=_status(
            raw.get("policy_status", raw.get("approval_status")),
            f"{path}.policy_status",
            default="UNKNOWN",
        ),
        serving_status=_status(raw.get("serving_status"), f"{path}.serving_status"),
    )


def _normalize_keyword(raw: Mapping[str, Any], path: str, index: int) -> Keyword:
    identifier = _identifier(raw, path, fallback=f"keyword-{index + 1}")
    status = _status(raw.get("status"), f"{path}.status")
    serving_status = _status(raw.get("serving_status"), f"{path}.serving_status")
    low_search_volume = _boolean(
        raw.get("low_search_volume"),
        f"{path}.low_search_volume",
        default=(status == "LOW_SEARCH_VOLUME" or serving_status == "LOW_SEARCH_VOLUME"),
    )
    return Keyword(
        identifier=identifier,
        text=_text(raw.get("text", raw.get("keyword")), f"{path}.text", default=identifier),
        status=status,
        serving_status=serving_status,
        low_search_volume=low_search_volume,
    )


def _normalize_ad_group(raw: Mapping[str, Any], path: str, index: int) -> AdGroup:
    identifier = _identifier(raw, path, fallback=f"ad-group-{index + 1}")
    raw_ads = _array(raw.get("ads"), f"{path}.ads")
    raw_keywords = _array(raw.get("keywords"), f"{path}.keywords")
    return AdGroup(
        identifier=identifier,
        name=_text(raw.get("name"), f"{path}.name", default=identifier),
        status=_status(raw.get("status"), f"{path}.status"),
        serving_status=_status(raw.get("serving_status"), f"{path}.serving_status"),
        ads=tuple(
            _normalize_ad(_object(item, f"{path}.ads[{item_index}]"), f"{path}.ads[{item_index}]", item_index)
            for item_index, item in enumerate(raw_ads)
        ),
        keywords=tuple(
            _normalize_keyword(
                _object(item, f"{path}.keywords[{item_index}]"),
                f"{path}.keywords[{item_index}]",
                item_index,
            )
            for item_index, item in enumerate(raw_keywords)
        ),
    )


def _normalize_targeting(raw: Any, path: str) -> Targeting:
    data = _object(raw or {}, path)
    locations = tuple(_text(item, f"{path}.locations[]") for item in _array(data.get("locations"), f"{path}.locations"))
    languages = tuple(_text(item, f"{path}.languages[]") for item in _array(data.get("languages"), f"{path}.languages"))
    restrictions: list[TargetingRestriction] = []
    for index, item in enumerate(_array(data.get("restrictions"), f"{path}.restrictions")):
        restriction = _object(item, f"{path}.restrictions[{index}]")
        restrictions.append(
            TargetingRestriction(
                restriction_type=_status(
                    restriction.get("type", restriction.get("restriction_type")),
                    f"{path}.restrictions[{index}].type",
                ),
                status=_status(restriction.get("status"), f"{path}.restrictions[{index}].status"),
                detail=_text(restriction.get("detail"), f"{path}.restrictions[{index}].detail"),
            )
        )
    return Targeting(locations=locations, languages=languages, restrictions=tuple(restrictions))


def _normalize_conversion(raw: Any, path: str) -> ConversionConfig:
    data = _object(raw or {}, path)
    return ConversionConfig(
        configured=_boolean(data.get("configured"), f"{path}.configured"),
        primary_action_count=_integer(data.get("primary_action_count"), f"{path}.primary_action_count"),
        usable_count=_integer(data.get("usable_count"), f"{path}.usable_count"),
        recent_count=_integer(data.get("recent_count"), f"{path}.recent_count"),
        tracking_status=_status(data.get("tracking_status"), f"{path}.tracking_status"),
    )


def _normalize_performance(raw: Any, path: str) -> PerformanceSnapshot:
    data = _object(raw or {}, path)
    return PerformanceSnapshot(
        window_days=_integer(data.get("window_days"), f"{path}.window_days"),
        impressions=_integer(data.get("impressions"), f"{path}.impressions"),
        clicks=_integer(data.get("clicks"), f"{path}.clicks"),
        cost_micros=_integer(data.get("cost_micros"), f"{path}.cost_micros"),
        api_evidence_complete=_boolean(
            data.get("api_evidence_complete"), f"{path}.api_evidence_complete", default=False
        ),
    )


def _normalize_campaign(raw: Mapping[str, Any], index: int) -> Campaign:
    path = f"campaigns[{index}]"
    identifier = _identifier(raw, path, fallback=f"campaign-{index + 1}")
    budget = _object(raw.get("budget", {}), f"{path}.budget")
    bidding = _object(raw.get("bidding", {}), f"{path}.bidding")
    raw_ad_groups = _array(raw.get("ad_groups"), f"{path}.ad_groups")
    return Campaign(
        identifier=identifier,
        name=_text(raw.get("name"), f"{path}.name", default=identifier),
        status=_status(raw.get("status"), f"{path}.status"),
        serving_status=_status(raw.get("serving_status"), f"{path}.serving_status"),
        start_date=_date_string(raw.get("start_date"), f"{path}.start_date"),
        end_date=_date_string(raw.get("end_date"), f"{path}.end_date"),
        budget=Budget(
            amount_micros=_integer(budget.get("amount_micros"), f"{path}.budget.amount_micros"),
            period=_status(budget.get("period"), f"{path}.budget.period"),
            status=_status(budget.get("status"), f"{path}.budget.status"),
        ),
        bidding=Bidding(
            strategy=_status(bidding.get("strategy"), f"{path}.bidding.strategy"),
            requires_conversions=_boolean(
                bidding.get("requires_conversions"), f"{path}.bidding.requires_conversions"
            ),
            target_cpa_micros=_integer(
                bidding.get("target_cpa_micros"), f"{path}.bidding.target_cpa_micros", default=0
            )
            or None,
            target_roas=_number(bidding.get("target_roas"), f"{path}.bidding.target_roas"),
        ),
        targeting=_normalize_targeting(raw.get("targeting", {}), f"{path}.targeting"),
        conversion=_normalize_conversion(raw.get("conversion", {}), f"{path}.conversion"),
        performance=_normalize_performance(raw.get("performance", {}), f"{path}.performance"),
        ad_groups=tuple(
            _normalize_ad_group(_object(item, f"{path}.ad_groups[{item_index}]"), f"{path}.ad_groups[{item_index}]", item_index)
            for item_index, item in enumerate(raw_ad_groups)
        ),
    )


def normalize(snapshot: RawAdsSnapshot) -> NormalizedAdsState:
    """Convert a provider snapshot into provider-independent diagnostic data."""

    account_data = _object(snapshot.account, "account")
    account = Account(
        identifier=_identifier(account_data, "account", fallback="account"),
        name=_text(account_data.get("name"), "account.name", default="Unnamed account"),
        status=_status(account_data.get("status"), "account.status"),
        eligibility=_status(account_data.get("eligibility"), "account.eligibility"),
    )
    campaigns = tuple(
        _normalize_campaign(_object(item, f"campaigns[{index}]"), index)
        for index, item in enumerate(snapshot.campaigns)
    )
    return NormalizedAdsState(account=account, campaigns=campaigns, source=snapshot.source)
