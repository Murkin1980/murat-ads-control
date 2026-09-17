from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from murat_ads_control.cli import main, run_fixture
from murat_ads_control.config import GoogleAdsRuntimeConfig
from murat_ads_control.diagnostics import diagnose
from murat_ads_control.models import OutcomeState
from murat_ads_control.normalize import normalize
from murat_ads_control.provider import FixtureAdsProvider
from murat_ads_control.report import BUSINESS_QUESTION


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


class Checkpoint001Tests(unittest.TestCase):
    def test_all_required_fixtures_run_through_the_vertical_slice(self) -> None:
        expected = {
            "disabled_date_blocked_campaign.json": OutcomeState.BLOCKED.value,
            "disapproved_ads.json": OutcomeState.GOOGLE_ACTION_REQUIRED.value,
            "majority_low_search_volume.json": OutcomeState.WARNING.value,
            "conversion_bidding_no_history.json": OutcomeState.WARNING.value,
            "eligible_zero_impressions.json": OutcomeState.WARNING.value,
        }
        for filename, expected_outcome in expected.items():
            with self.subTest(filename=filename):
                machine, human = run_fixture(FIXTURES / filename, as_of="2026-09-16")
                payload = json.loads(machine)
                self.assertEqual(payload["outcome"], expected_outcome)
                self.assertIn("findings", payload)
                self.assertIn("Answer to the business question", human)
                self.assertTrue(payload["findings"])

    def test_provider_snapshot_is_read_only_from_capability_perspective(self) -> None:
        provider = FixtureAdsProvider.from_path(FIXTURES / "eligible_zero_impressions.json")
        first = provider.read_state()
        first.account["status"] = "DISABLED"  # type: ignore[index]
        second = provider.read_state()
        self.assertEqual(second.account["status"], "ENABLED")
        self.assertEqual(len(second.campaigns), 1)

    def test_findings_keep_evidence_and_uncertainty(self) -> None:
        provider = FixtureAdsProvider.from_path(FIXTURES / "conversion_bidding_no_history.json")
        result = diagnose(normalize(provider.read_state()), as_of="2026-09-16")
        finding = next(item for item in result.findings if "conversion" in item.title.lower())
        self.assertEqual(finding.status, OutcomeState.WARNING)
        fields = {item.field for item in finding.evidence}
        self.assertIn("campaign.conversion.usable_count", fields)
        self.assertTrue(finding.uncertainty)
        self.assertTrue(finding.recommended_action)

    def test_cli_writes_both_report_formats(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "report.json"
            markdown_path = Path(directory) / "report.md"
            exit_code = main(
                [
                    "--fixture",
                    str(FIXTURES / "eligible_zero_impressions.json"),
                    "--as-of",
                    "2026-09-16",
                    "--json-out",
                    str(json_path),
                    "--markdown-out",
                    str(markdown_path),
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8"))["business_question"], BUSINESS_QUESTION)
            self.assertIn("Technically eligible campaign has zero recent impressions", markdown_path.read_text(encoding="utf-8"))

    def test_runtime_hook_names_environment_secrets_without_loading_values(self) -> None:
        config = GoogleAdsRuntimeConfig.from_environment({"GOOGLE_ADS_CUSTOMER_ID": "fixture-account"})
        self.assertEqual(config.customer_id, "fixture-account")
        self.assertIn("GOOGLE_ADS_REFRESH_TOKEN", config.secret_environment_names)
        self.assertNotIn("refresh_token", config.__dict__)


if __name__ == "__main__":
    unittest.main()
