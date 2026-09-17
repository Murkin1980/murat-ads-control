"""Minimal strictly read-only Google Ads adapter.

The official client is imported only when Google Ads mode is selected. Tests can
inject a fake client, so the fixture path stays standard-library-only.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from .config import ConfigurationError, GoogleAdsRuntimeConfig
from .provider import RawAdsSnapshot, ReadOnlyAdsProvider


class GoogleAdsDependencyError(RuntimeError):
    """Raised when the optional official client is not installed."""


class GoogleAdsClientError(RuntimeError):
    """Raised without forwarding SDK credential or response payload details."""


class GoogleAdsReadError(RuntimeError):
    """Raised when a read-only Google Ads query cannot be completed."""


# These are deliberately the smallest query set for the current normalized
# model: account, campaign configuration, performance, ads, keywords, and targeting.
ACCOUNT_QUERY = """
    SELECT customer.id, customer.descriptive_name, customer.status
    FROM customer
    LIMIT 1
"""

CAMPAIGN_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.serving_status,
      campaign.start_date,
      campaign.end_date,
      campaign.bidding_strategy_type,
      campaign.target_cpa.target_cpa_micros,
      campaign.target_roas.target_roas,
      campaign_budget.amount_micros,
      campaign_budget.period,
      campaign_budget.status
    FROM campaign
"""

PERFORMANCE_QUERY = """
    SELECT
      campaign.id,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions
    FROM campaign
    WHERE segments.date DURING LAST_30_DAYS
"""

AD_QUERY = """
    SELECT
      campaign.id,
      ad_group.id,
      ad_group.name,
      ad_group.status,
      ad_group_ad.ad.id,
      ad_group_ad.ad.name,
      ad_group_ad.status,
      ad_group_ad.policy_summary.approval_status
    FROM ad_group_ad
"""

KEYWORD_QUERY = """
    SELECT
      campaign.id,
      ad_group.id,
      ad_group.name,
      ad_group.status,
      ad_group_criterion.criterion_id,
      ad_group_criterion.status,
      ad_group_criterion.system_serving_status,
      ad_group_criterion.keyword.text
    FROM ad_group_criterion
    WHERE ad_group_criterion.type = KEYWORD
      AND ad_group_criterion.negative = FALSE
"""

TARGETING_QUERY = """
    SELECT
      campaign.id,
      campaign_criterion.type,
      campaign_criterion.status,
      campaign_criterion.negative,
      campaign_criterion.location.geo_target_constant,
      campaign_criterion.language.language_constant
    FROM campaign_criterion
    WHERE campaign_criterion.type IN (LOCATION, LANGUAGE)
"""


ClientFactory = Callable[[GoogleAdsRuntimeConfig], Any]


def _default_client(_: GoogleAdsRuntimeConfig) -> Any:
    """Load the official client from its documented environment contract."""

    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError as exc:
        raise GoogleAdsDependencyError(
            "The official google-ads package is required for --google-ads; install requirements.txt"
        ) from exc
    try:
        return GoogleAdsClient.load_from_env()
    except Exception as exc:  # SDK messages may contain request/config details.
        raise GoogleAdsClientError(
            f"Google Ads client initialization failed: {type(exc).__name__}"
        ) from exc


def _value(value: Any, *path: str, default: Any = None) -> Any:
    for part in path:
        if value is None:
            return default
        if isinstance(value, Mapping):
            value = value.get(part)
        else:
            value = getattr(value, part, None)
    return default if value is None else value


def _text(value: Any, *, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _enum(value: Any, *, default: str = "UNKNOWN") -> str:
    if value is None:
        return default
    name = getattr(value, "name", None)
    if name:
        return str(name).upper()
    text = str(value)
    if "." in text:
        text = text.rsplit(".", 1)[-1]
    return text.upper()


def _integer(value: Any, *, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _number(value: Any, *, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _resource_id(value: Any, *, default: str) -> str:
    if value is None:
        return default
    text = _text(value)
    return text.rsplit("/", 1)[-1] or default


def _serving_status(value: Any) -> str:
    status = _enum(value)
    if status in {"SERVING", "ELIGIBLE", "ENABLED"}:
        return "ELIGIBLE"
    if status == "NONE":
        return "NOT_ELIGIBLE"
    return status


def _keyword_serving_status(value: Any) -> tuple[str, bool]:
    status = _enum(value)
    if status in {"ELIGIBLE", "SERVING", "ENABLED"}:
        return "ELIGIBLE", False
    if status in {"RARELY_SERVED", "LOW_SEARCH_VOLUME"}:
        return "LOW_SEARCH_VOLUME", True
    return status, False


def _empty_campaign(identifier: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "name": identifier,
        "status": "UNKNOWN",
        "serving_status": "UNKNOWN",
        "start_date": None,
        "end_date": None,
        "budget": {"amount_micros": 0, "period": "UNKNOWN", "status": "UNKNOWN"},
        "bidding": {"strategy": "UNKNOWN", "requires_conversions": False},
        "targeting": {"locations": [], "languages": [], "restrictions": []},
        "conversion": {
            "configured": False,
            "primary_action_count": 0,
            "usable_count": 0,
            "recent_count": 0,
            "tracking_status": "UNKNOWN",
        },
        "performance": {
            "window_days": 30,
            "impressions": 0,
            "clicks": 0,
            "cost_micros": 0,
            "api_evidence_complete": False,
        },
        "ad_groups": [],
    }


def _campaign_from_row(row: Any) -> dict[str, Any]:
    campaign_id = _resource_id(_value(row, "campaign", "id"), default="campaign-unknown")
    strategy = _enum(_value(row, "campaign", "bidding_strategy_type"))
    conversion_bidding = strategy in {
        "MAXIMIZE_CONVERSIONS",
        "MAXIMIZE_CONVERSION_VALUE",
        "TARGET_CPA",
        "TARGET_ROAS",
    }
    campaign: dict[str, Any] = {
        "id": campaign_id,
        "name": _text(_value(row, "campaign", "name"), default=campaign_id),
        "status": _enum(_value(row, "campaign", "status")),
        "serving_status": _serving_status(_value(row, "campaign", "serving_status")),
        "start_date": _value(row, "campaign", "start_date"),
        "end_date": _value(row, "campaign", "end_date"),
        "budget": {
            "amount_micros": _integer(_value(row, "campaign_budget", "amount_micros")),
            "period": _enum(_value(row, "campaign_budget", "period")),
            "status": _enum(_value(row, "campaign_budget", "status")),
        },
        "bidding": {
            "strategy": strategy,
            "requires_conversions": conversion_bidding,
            "target_cpa_micros": _integer(_value(row, "campaign", "target_cpa", "target_cpa_micros")) or None,
            "target_roas": _number(_value(row, "campaign", "target_roas", "target_roas")) or None,
        },
        "targeting": {"locations": [], "languages": [], "restrictions": []},
        "conversion": {
            # Recent campaign conversion metrics are the minimal history
            # evidence; conversion action payloads are intentionally not read.
            "configured": conversion_bidding,
            "primary_action_count": 1 if conversion_bidding else 0,
            "usable_count": 0,
            "recent_count": 0,
            "tracking_status": "NO_RECENT_DATA" if conversion_bidding else "NOT_CONFIGURED",
        },
        "performance": {
            "window_days": 30,
            "impressions": 0,
            "clicks": 0,
            "cost_micros": 0,
            "api_evidence_complete": False,
        },
        "ad_groups": [],
    }
    return campaign


def _apply_performance(campaign: dict[str, Any], row: Any) -> None:
    recent_conversions = _integer(_value(row, "metrics", "conversions"))
    campaign["performance"] = {
        "window_days": 30,
        "impressions": _integer(_value(row, "metrics", "impressions")),
        "clicks": _integer(_value(row, "metrics", "clicks")),
        "cost_micros": _integer(_value(row, "metrics", "cost_micros")),
        "api_evidence_complete": True,
    }
    configured = campaign["bidding"]["requires_conversions"] or recent_conversions > 0
    campaign["conversion"].update(
        {
            "configured": configured,
            "primary_action_count": 1 if configured else 0,
            "usable_count": 1 if recent_conversions > 0 else 0,
            "recent_count": recent_conversions,
            "tracking_status": "HAS_RECENT_DATA" if recent_conversions > 0 else ("NO_RECENT_DATA" if configured else "NOT_CONFIGURED"),
        }
    )


def _ensure_group(campaign: dict[str, Any], group_id: str, name: str, status: str) -> dict[str, Any]:
    for group in campaign["ad_groups"]:
        if group["id"] == group_id:
            return group
    group = {
        "id": group_id,
        "name": name or group_id,
        "status": status,
        "serving_status": "ELIGIBLE" if status == "ENABLED" else status,
        "ads": [],
        "keywords": [],
    }
    campaign["ad_groups"].append(group)
    return group


def _attach_ads(campaigns: dict[str, dict[str, Any]], rows: Iterable[Any]) -> None:
    for row in rows:
        campaign_id = _resource_id(_value(row, "campaign", "id"), default="campaign-unknown")
        campaign = campaigns.setdefault(campaign_id, _empty_campaign(campaign_id))
        group_id = _resource_id(_value(row, "ad_group", "id"), default="ad-group-unknown")
        group_status = _enum(_value(row, "ad_group", "status"))
        group = _ensure_group(campaign, group_id, _text(_value(row, "ad_group", "name"), default=group_id), group_status)
        ad_id = _resource_id(_value(row, "ad_group_ad", "ad", "id"), default="ad-unknown")
        policy_status = _enum(_value(row, "ad_group_ad", "policy_summary", "approval_status"))
        ad_status = _enum(_value(row, "ad_group_ad", "status"))
        group["ads"].append(
            {
                "id": ad_id,
                "name": _text(_value(row, "ad_group_ad", "ad", "name"), default=ad_id),
                "status": ad_status,
                "policy_status": policy_status,
                "serving_status": "ELIGIBLE" if ad_status == "ENABLED" and policy_status == "APPROVED" else "NOT_ELIGIBLE",
            }
        )


def _attach_keywords(campaigns: dict[str, dict[str, Any]], rows: Iterable[Any]) -> None:
    for row in rows:
        campaign_id = _resource_id(_value(row, "campaign", "id"), default="campaign-unknown")
        campaign = campaigns.setdefault(campaign_id, _empty_campaign(campaign_id))
        group_id = _resource_id(_value(row, "ad_group", "id"), default="ad-group-unknown")
        group_status = _enum(_value(row, "ad_group", "status"))
        group = _ensure_group(campaign, group_id, _text(_value(row, "ad_group", "name"), default=group_id), group_status)
        serving_status, low_search_volume = _keyword_serving_status(
            _value(row, "ad_group_criterion", "system_serving_status")
        )
        keyword_id = _resource_id(_value(row, "ad_group_criterion", "criterion_id"), default="keyword-unknown")
        group["keywords"].append(
            {
                "id": keyword_id,
                "text": _text(_value(row, "ad_group_criterion", "keyword", "text"), default=keyword_id),
                "status": _enum(_value(row, "ad_group_criterion", "status")),
                "serving_status": serving_status,
                "low_search_volume": low_search_volume,
            }
        )


def _attach_targeting(campaigns: dict[str, dict[str, Any]], rows: Iterable[Any]) -> None:
    for row in rows:
        campaign_id = _resource_id(_value(row, "campaign", "id"), default="campaign-unknown")
        campaign = campaigns.setdefault(campaign_id, _empty_campaign(campaign_id))
        criterion_type = _enum(_value(row, "campaign_criterion", "type"))
        status = _enum(_value(row, "campaign_criterion", "status"))
        negative = bool(_value(row, "campaign_criterion", "negative", default=False))
        if criterion_type == "LOCATION":
            location = _resource_id(
                _value(row, "campaign_criterion", "location", "geo_target_constant"),
                default="location-unknown",
            )
            campaign["targeting"]["locations"].append(location)
        elif criterion_type == "LANGUAGE":
            language = _resource_id(
                _value(row, "campaign_criterion", "language", "language_constant"),
                default="language-unknown",
            )
            campaign["targeting"]["languages"].append(language)
        if status != "ENABLED" or negative:
            campaign["targeting"]["restrictions"].append(
                {
                    "type": criterion_type,
                    "status": "RESTRICTED" if negative else status,
                    "detail": "negative criterion" if negative else "campaign criterion is not enabled",
                }
            )


class GoogleAdsProvider(ReadOnlyAdsProvider):
    """Google Ads implementation of the existing one-method provider contract."""

    def __init__(self, config: GoogleAdsRuntimeConfig, client: Any) -> None:
        self._config = config
        try:
            self._service = client.get_service("GoogleAdsService")
        except Exception as exc:
            raise GoogleAdsClientError(
                f"Google Ads service initialization failed: {type(exc).__name__}"
            ) from exc

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | None = None,
        *,
        client_factory: ClientFactory | None = None,
    ) -> "GoogleAdsProvider":
        config = GoogleAdsRuntimeConfig.from_environment(environ)
        config.require_credentials(environ)
        try:
            client = (client_factory or _default_client)(config)
        except (GoogleAdsDependencyError, GoogleAdsClientError):
            raise
        except Exception as exc:
            raise GoogleAdsClientError(
                f"Google Ads client initialization failed: {type(exc).__name__}"
            ) from exc
        return cls(config, client)

    def _search(self, query: str, label: str) -> list[Any]:
        try:
            return list(self._service.search(customer_id=self._config.customer_id, query=query))
        except Exception as exc:
            raise GoogleAdsReadError(
                f"Google Ads read query failed for {label}: {type(exc).__name__}"
            ) from exc

    def read_state(self) -> RawAdsSnapshot:
        """Read only the six query slices needed by normalization and rules."""

        account_rows = self._search(ACCOUNT_QUERY, "account")
        if not account_rows:
            raise GoogleAdsReadError("Google Ads account query returned no account data")
        account_row = account_rows[0]
        account_status = _enum(_value(account_row, "customer", "status"))
        account = {
            "id": _resource_id(_value(account_row, "customer", "id"), default=self._config.customer_id),
            "name": _text(_value(account_row, "customer", "descriptive_name"), default="Google Ads account"),
            "status": account_status,
            "eligibility": "ELIGIBLE" if account_status == "ENABLED" else account_status,
        }

        campaigns: dict[str, dict[str, Any]] = {}
        for row in self._search(CAMPAIGN_QUERY, "campaign configuration"):
            campaign = _campaign_from_row(row)
            campaigns[campaign["id"]] = campaign
        for row in self._search(PERFORMANCE_QUERY, "campaign performance"):
            campaign_id = _resource_id(_value(row, "campaign", "id"), default="campaign-unknown")
            campaign = campaigns.setdefault(campaign_id, _empty_campaign(campaign_id))
            _apply_performance(campaign, row)
        _attach_ads(campaigns, self._search(AD_QUERY, "ads and ad groups"))
        _attach_keywords(campaigns, self._search(KEYWORD_QUERY, "keywords"))
        _attach_targeting(campaigns, self._search(TARGETING_QUERY, "campaign targeting"))
        return RawAdsSnapshot(
            account=account,
            campaigns=tuple(campaigns.values()),
            source="google-ads",
        )
