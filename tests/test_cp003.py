from __future__ import annotations

import copy
import unittest

from murat_ads_control.diagnostics import diagnose
from murat_ads_control.models import OutcomeState
from murat_ads_control.normalize import normalize
from murat_ads_control.provider import RawAdsSnapshot


def _base_payload() -> dict:
    return {
        "account": {
            "id": "cp003-account",
            "name": "CP-003 contract account",
            "status": "ENABLED",
            "eligibility": "ELIGIBLE",
        },
        "campaigns": [
            {
                "id": "cp003-campaign",
                "name": "CP-003 campaign",
                "status": "ENABLED",
                "serving_status": "ELIGIBLE",
                "start_date": "2026-01-01",
                "end_date": None,
                "budget": {"amount_micros": 10_000_000, "period": "DAILY", "status": "ACTIVE"},
                "bidding": {"strategy": "MANUAL_CPC", "requires_conversions": False},
                "targeting": {"locations": ["Almaty"], "languages": ["ru"], "restrictions": []},
                "conversion": {
                    "configured": False,
                    "primary_action_count": 0,
                    "usable_count": 0,
                    "recent_count": 0,
                    "tracking_status": "NOT_CONFIGURED",
                },
                "performance": {
                    "window_days": 30,
                    "impressions": 100,
                    "clicks": 10,
                    "cost_micros": 1_000_000,
                    "api_evidence_complete": True,
                },
                "ad_groups": [
                    {
                        "id": "cp003-group",
                        "name": "CP-003 group",
                        "status": "ENABLED",
                        "serving_status": "ELIGIBLE",
                        "ads": [
                            {
                                "id": "cp003-ad",
                                "name": "CP-003 ad",
                                "status": "ENABLED",
                                "policy_status": "APPROVED",
                                "serving_status": "ELIGIBLE",
                            }
                        ],
                        "keywords": [
                            {
                                "id": "cp003-keyword",
                                "text": "custom furniture",
                                "status": "ENABLED",
                                "serving_status": "ELIGIBLE",
                                "low_search_volume": False,
                            }
                        ],
                    }
                ],
            }
        ],
    }


def _diagnose(payload: dict):
    snapshot = RawAdsSnapshot.from_mapping(payload, source="cp003-contract")
    return diagnose(normalize(snapshot), as_of="2026-09-17")


class Checkpoint003Tests(unittest.TestCase):
    def test_all_eight_rule_families_have_explainable_findings(self) -> None:
        scenarios: list[tuple[str, callable, str]] = []

        def campaign_disabled(payload: dict) -> None:
            payload["campaigns"][0]["status"] = "PAUSED"

        scenarios.append(("campaign state/date", campaign_disabled, "Campaign is not enabled"))

        def budget_block(payload: dict) -> None:
            payload["campaigns"][0]["budget"]["amount_micros"] = 0

        scenarios.append(("budget/bidding", budget_block, "Campaign budget is not usable"))

        def disapproved_ad(payload: dict) -> None:
            ad = payload["campaigns"][0]["ad_groups"][0]["ads"][0]
            ad["policy_status"] = "DISAPPROVED"
            ad["serving_status"] = "NOT_ELIGIBLE"

        scenarios.append(("ad policy", disapproved_ad, "Ad requires Google policy action"))

        def disabled_group(payload: dict) -> None:
            group = payload["campaigns"][0]["ad_groups"][0]
            group["status"] = "PAUSED"
            group["serving_status"] = "NOT_ELIGIBLE"

        scenarios.append(("ad group", disabled_group, "Ad group is not eligible"))

        def low_search_volume(payload: dict) -> None:
            keyword = payload["campaigns"][0]["ad_groups"][0]["keywords"][0]
            keyword["serving_status"] = "LOW_SEARCH_VOLUME"
            keyword["low_search_volume"] = True

        scenarios.append(("keywords", low_search_volume, "Most keywords have low search volume"))

        def targeting_restriction(payload: dict) -> None:
            payload["campaigns"][0]["targeting"]["restrictions"] = [
                {"type": "LOCATION", "status": "RESTRICTED", "detail": "conflicting location criterion"}
            ]

        scenarios.append(("targeting", targeting_restriction, "Targeting contains a delivery restriction"))

        def conversion_bidding(payload: dict) -> None:
            campaign = payload["campaigns"][0]
            campaign["bidding"] = {"strategy": "TARGET_CPA", "requires_conversions": True}
            campaign["conversion"] = {
                "configured": True,
                "primary_action_count": 1,
                "usable_count": 0,
                "recent_count": 0,
                "tracking_status": "NO_RECENT_DATA",
            }

        scenarios.append(("conversion-dependent bidding", conversion_bidding, "Conversion-dependent bidding has no usable recent history"))

        def zero_auction_activity(payload: dict) -> None:
            payload["campaigns"][0]["performance"].update(
                {"impressions": 0, "clicks": 0, "cost_micros": 0, "api_evidence_complete": True}
            )

        scenarios.append(("zero auction activity", zero_auction_activity, "Technically eligible campaign has zero recent impressions"))

        for label, mutate, expected_title in scenarios:
            with self.subTest(rule_family=label):
                payload = copy.deepcopy(_base_payload())
                mutate(payload)
                result = _diagnose(payload)
                titles = {finding.title for finding in result.findings}
                self.assertIn(expected_title, titles)
                finding = next(item for item in result.findings if item.title == expected_title)
                self.assertTrue(finding.evidence)
                self.assertTrue(finding.recommended_action)
                self.assertTrue(finding.confidence)
                self.assertTrue(finding.uncertainty)

    def test_multiple_simultaneous_signals_are_preserved_not_collapsed(self) -> None:
        payload = _base_payload()
        campaign = payload["campaigns"][0]
        campaign["bidding"] = {"strategy": "TARGET_CPA", "requires_conversions": True}
        campaign["conversion"] = {
            "configured": True,
            "primary_action_count": 1,
            "usable_count": 0,
            "recent_count": 0,
            "tracking_status": "NO_RECENT_DATA",
        }
        campaign["targeting"]["restrictions"] = [
            {"type": "LOCATION", "status": "RESTRICTED", "detail": "conflicting location criterion"}
        ]
        campaign["performance"].update({"impressions": 0, "clicks": 0, "cost_micros": 0})

        result = _diagnose(payload)
        titles = {finding.title for finding in result.findings}
        self.assertIn("Conversion-dependent bidding has no usable recent history", titles)
        self.assertIn("Targeting contains a delivery restriction", titles)
        self.assertIn("Technically eligible campaign has zero recent impressions", titles)
        self.assertEqual(result.outcome, OutcomeState.WARNING)

    def test_outcome_precedence_is_deterministic_without_hiding_findings(self) -> None:
        payload = _base_payload()
        campaign = payload["campaigns"][0]
        campaign["status"] = "PAUSED"
        ad = campaign["ad_groups"][0]["ads"][0]
        ad["policy_status"] = "DISAPPROVED"
        ad["serving_status"] = "NOT_ELIGIBLE"

        result = _diagnose(payload)
        statuses = {finding.status for finding in result.findings}
        self.assertIn(OutcomeState.BLOCKED, statuses)
        self.assertIn(OutcomeState.GOOGLE_ACTION_REQUIRED, statuses)
        self.assertEqual(result.outcome, OutcomeState.BLOCKED)

    def test_ok_is_emitted_when_no_observed_problem_exists(self) -> None:
        result = _diagnose(_base_payload())
        self.assertEqual(result.outcome, OutcomeState.OK)
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].status, OutcomeState.OK)
        self.assertEqual(result.findings[0].title, "No blocker observed in the evaluated fields")


if __name__ == "__main__":
    unittest.main()
