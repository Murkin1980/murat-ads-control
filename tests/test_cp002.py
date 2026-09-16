from __future__ import annotations

import json
import unittest
from types import SimpleNamespace

from murat_ads_control.config import ConfigurationError, GoogleAdsRuntimeConfig
from murat_ads_control.diagnostics import diagnose
from murat_ads_control.google_ads import GoogleAdsProvider
from murat_ads_control.normalize import normalize
from murat_ads_control.report import report_json, report_markdown


def _ns(**values: object) -> SimpleNamespace:
    return SimpleNamespace(**values)


class FakeGoogleAdsService:
    def __init__(self) -> None:
        self.queries: list[str] = []
        self._rows = {
            "customer": [
                _ns(customer=_ns(id=1234567890, descriptive_name="Fixture Google Ads account", status="ENABLED"))
            ],
            "campaign": [
                _ns(
                    campaign=_ns(
                        id=42,
                        name="Fixture Search campaign",
                        status="ENABLED",
                        serving_status="SERVING",
                        start_date="2026-01-01",
                        end_date=None,
                        bidding_strategy_type="TARGET_CPA",
                        target_cpa=_ns(target_cpa_micros=5000000),
                        target_roas=_ns(target_roas=0.0),
                    ),
                    campaign_budget=_ns(amount_micros=10000000, period="DAILY", status="ENABLED"),
                    metrics=_ns(impressions=0, clicks=0, cost_micros=0, conversions=0.0),
                )
            ],
            "campaign_performance": [
                _ns(campaign=_ns(id=42), metrics=_ns(impressions=0, clicks=0, cost_micros=0, conversions=0.0))
            ],
            "ad_group_ad": [
                _ns(
                    campaign=_ns(id=42),
                    ad_group=_ns(id=7, name="Fixture ad group", status="ENABLED"),
                    ad_group_ad=_ns(
                        ad=_ns(id=8, name="Fixture responsive search ad"),
                        status="ENABLED",
                        policy_summary=_ns(approval_status="APPROVED"),
                    ),
                )
            ],
            "ad_group_criterion": [
                _ns(
                    campaign=_ns(id=42),
                    ad_group=_ns(id=7, name="Fixture ad group", status="ENABLED"),
                    ad_group_criterion=_ns(
                        criterion_id=9,
                        status="ENABLED",
                        system_serving_status="ELIGIBLE",
                        keyword=_ns(text="fixture keyword"),
                        negative=False,
                    ),
                )
            ],
            "campaign_criterion": [
                _ns(
                    campaign=_ns(id=42),
                    campaign_criterion=_ns(
                        type="LOCATION",
                        status="ENABLED",
                        negative=False,
                        location=_ns(geo_target_constant="geoTargetConstants/1001"),
                        language=None,
                    ),
                ),
                _ns(
                    campaign=_ns(id=42),
                    campaign_criterion=_ns(
                        type="LANGUAGE",
                        status="ENABLED",
                        negative=False,
                        location=None,
                        language=_ns(language_constant="languageConstants/1000"),
                    ),
                ),
            ],
        }

    def search(self, *, customer_id: str, query: str):
        self.queries.append(query)
        if "metrics.impressions" in query and "FROM campaign" in query:
            return iter(self._rows["campaign_performance"])
        for key in sorted(self._rows, key=len, reverse=True):
            if f"FROM {key}" in query:
                return iter(self._rows[key])
        raise AssertionError(f"unexpected query: {query}")


class FakeGoogleAdsClient:
    def __init__(self, service: FakeGoogleAdsService) -> None:
        self.service = service

    def get_service(self, name: str) -> FakeGoogleAdsService:
        self.requested_service = name
        return self.service


class Checkpoint002Tests(unittest.TestCase):
    def test_missing_credentials_fail_closed_without_values(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "GOOGLE_ADS_DEVELOPER_TOKEN") as context:
            GoogleAdsProvider.from_environment({"GOOGLE_ADS_CUSTOMER_ID": "fixture-customer"})
        self.assertNotIn("fixture-customer", str(context.exception))
        self.assertIn("GOOGLE_ADS_CLIENT_SECRET", str(context.exception))

    def test_mocked_google_provider_maps_and_reaches_report(self) -> None:
        service = FakeGoogleAdsService()
        config = GoogleAdsRuntimeConfig(customer_id="1234567890", login_customer_id=None)
        provider = GoogleAdsProvider(config, FakeGoogleAdsClient(service))

        snapshot = provider.read_state()
        normalized = normalize(snapshot)
        result = diagnose(normalized, as_of="2026-09-16")
        payload = json.loads(report_json(result))
        markdown = report_markdown(result)

        self.assertEqual(snapshot.source, "google-ads")
        self.assertEqual(normalized.account.identifier, "1234567890")
        self.assertEqual(normalized.campaigns[0].identifier, "42")
        self.assertEqual(normalized.campaigns[0].ad_groups[0].ads[0].policy_status, "APPROVED")
        self.assertEqual(normalized.campaigns[0].targeting.locations, ("1001",))
        self.assertEqual(normalized.campaigns[0].targeting.languages, ("1000",))
        self.assertEqual(payload["outcome"], "WARNING")
        self.assertIn("Technically eligible campaign has zero recent impressions", markdown)
        self.assertEqual(len(service.queries), 6)

    def test_provider_and_reports_expose_no_mutation_or_credentials(self) -> None:
        provider_public_methods = {
            name
            for name in dir(GoogleAdsProvider)
            if not name.startswith("_") and callable(getattr(GoogleAdsProvider, name))
        }
        self.assertEqual(provider_public_methods, {"from_environment", "read_state"})
        forbidden = {"mutate", "create", "update", "delete", "remove", "enable", "pause"}
        self.assertFalse(any(any(word in name.lower() for word in forbidden) for name in provider_public_methods))

        service = FakeGoogleAdsService()
        provider = GoogleAdsProvider(GoogleAdsRuntimeConfig("1234567890", None), FakeGoogleAdsClient(service))
        result = diagnose(normalize(provider.read_state()), as_of="2026-09-16")
        rendered = report_json(result) + report_markdown(result)
        for environment_name in GoogleAdsRuntimeConfig("1234567890", None).secret_environment_names:
            self.assertNotIn(environment_name, rendered)


if __name__ == "__main__":
    unittest.main()
