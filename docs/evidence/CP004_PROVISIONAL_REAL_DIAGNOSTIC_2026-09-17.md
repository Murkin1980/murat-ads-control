# CP-004 provisional real diagnostic — 2026-09-17

## Status

`PROVISIONAL / NOT EXP-001 PASS`

This evidence was collected read-only from the connected Bek Mebel Google Ads account through an external OAuth connector. It is useful business evidence, but it is not repository-native `GoogleAdsProvider` E2E evidence.

## Observed 30-day delivery

Window: 2026-08-17 through 2026-09-16.

- Campaign: `Performance Max-1`
- Campaign status: `ENABLED`
- Campaign type: `PERFORMANCE_MAX`
- Impressions: `12,700`
- Clicks: `949`
- Spend: `USD 20.43`
- CTR: `7.47%`
- Conversions: `0`

## What this rules out

The original working hypothesis that the campaign is effectively not delivering is not supported by this 30-day evidence. The account produced substantial impressions and clicks during the observed window.

Therefore CP-004 should not report "zero/near-zero auction activity" as the primary current explanation for this campaign.

## What is materially narrowed

The unresolved business problem has moved downstream from delivery to conversion evidence:

1. Google Ads is recording traffic.
2. Google Ads is recording zero conversions in the observed window.
3. The available external evidence does not distinguish between:
   - conversion tracking not recording the intended business action;
   - traffic reaching the site but not completing the intended action;
   - the intended conversion action being configured differently from the business goal.

No one of those causes is claimed without additional evidence.

## Current finding

**Status:** `WARNING`

**Cause:** Campaign delivery is present, but no conversions are recorded in the observed 30-day window.

**Evidence:** 12,700 impressions, 949 clicks, USD 20.43 spend, 0 conversions.

**Affected entity:** Bek Mebel / `Performance Max-1`.

**Recommended next test:** complete repository-native read-only E2E, then inspect the conversion configuration/evidence returned by the same trusted path before proposing any campaign mutation.

**Confidence:** `HIGH` that delivery exists and recorded conversions are zero for the observed window; `LOW` on the underlying conversion root cause until conversion configuration is read and verified.

**Uncertainty:** external connector evidence cannot close the repository-native authentication checkpoint and does not prove why conversions are zero.

## EXP-001 decision

`PENDING`

Do not mark EXP-001 PASS yet. Remaining hard gate: run the repository's own `python -m murat_ads_control --google-ads` path with runtime-injected credentials and freeze the resulting sanitized evidence.

## Safety

No Google Ads mutation was performed while collecting this evidence.
