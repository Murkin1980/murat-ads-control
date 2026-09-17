# Checkpoints

Durable project state. Add a checkpoint after meaningful milestones, experiment state changes, merges, or before handing work to another agent/session.

## CP-000 — Project initialized

**Date:** 2026-09-16  
**Status:** COMPLETE

### State
- Independent repository selected: `Murkin1980/murat-ads-control`.
- Product boundary defined: acquisition automation/control layer.
- First experiment fixed: read-only Google Ads diagnostics for `bek-mebel.kz`.
- Initial governance/docs initialized.
- MVP roadmap and Arena task packet added.
- No production Google Ads mutation capability exists.

### Next checkpoint
`CP-001 — Repository contracts + fixture-driven diagnostic path`.

---

## CP-001 — Repository contracts + fixture-driven diagnostic path

**Date:** 2026-09-16  
**Status:** COMPLETE

### Entering state
Documentation and project boundaries existed; no runtime implementation existed.

### Changes
- Added a Python standard-library-only runtime with a small CLI: `python -m murat_ads_control`.
- Added the one-operation `ReadOnlyAdsProvider` protocol and sanitized JSON `FixtureAdsProvider`.
- Added normalization into provider-independent account, campaign, ad group, ad, keyword, targeting, conversion, performance, and finding models.
- Added evidence-backed v0 diagnostic rules for account/campaign state and dates, budget/bidding, ad groups, ad policy eligibility, keyword low-search-volume/ineligibility, targeting restrictions, conversion-dependent bidding, and zero/low recent delivery.
- Added deterministic JSON and concise Markdown report renderers.
- Added five sanitized fixtures covering the required diagnostic cases and critical contract tests.
- Added a runtime environment configuration hook that names future Google Ads secret variables without loading or storing their values.

### Evidence
- `python -m unittest discover -s tests -v` — 5 tests passed.
- Every required fixture completed `LOAD/READ → NORMALIZE → DIAGNOSE → REPORT`.
- `git diff --check` passed.
- No Google client dependency, credential, or provider write operation was added.

### Exit state
The fixture-driven read-only vertical slice is working. Findings include status/severity, evidence, affected entity, recommendation, confidence, and uncertainty. The real-account experiment remains pending.

### Next checkpoint
`CP-002 — Google Ads read-only connection`.

---

## CP-002 — Google Ads read-only connection

**Date:** 2026-09-16  
**Status:** PENDING_EXTERNAL_CREDENTIALS

### Entering state
CP-001 fixture provider, normalized model, diagnostics, reports, and CLI were complete. No official Google Ads dependency or real adapter existed.

### Changes
- Added `GoogleAdsProvider` behind the existing one-operation `ReadOnlyAdsProvider.read_state()` contract.
- Added runtime-only configuration validation for one customer ID, four required Google Ads credential environment names, and optional `GOOGLE_ADS_LOGIN_CUSTOMER_ID`.
- Added the official `google-ads` dependency only for `--google-ads` mode; fixture mode remains standard-library-only.
- Added six read-only GAQL slices: customer status, campaign configuration, 30-day campaign performance, ads/ad groups, keywords, and campaign location/language targeting.
- Mapped SDK-shaped responses into the existing raw snapshot and provider-independent normalized model without SDK objects entering diagnostics.
- Extended the CLI with mutually exclusive `--fixture` and `--google-ads` modes.
- Added mocked provider tests for credential failure, mappings, report output, and absence of mutation methods.
- PR #1 merged the CP-001/CP-002 implementation into `main` on 2026-09-17.

### Evidence
- `python -m unittest discover -s tests -v` — 8 tests passed in Arena implementation evidence.
- Fixture mode still runs and produces the same CP-001 report structure.
- `--google-ads` without credentials fails closed with configuration field names only.
- Official client import/API surface was verified from `google-ads>=25.0.0` in an isolated environment.
- Real Google Ads account access was independently confirmed on 2026-09-17 through an already-connected read-only OAuth connector for account `9687071768` (`bek mebel`).
- The connector returned live/cached-live campaign data for `Performance Max-1`, including 12,700 impressions, 949 clicks, USD 20.43 spend, and 0 conversions for 2026-08-17 through 2026-09-16.
- This external read proves the target account is reachable, but it does **not** prove the repository's own `GoogleAdsProvider` runtime path because the repository runtime credential variables are still unavailable here.

### Exit state
The code is merged to `main`, the target Google Ads account is reachable read-only, and the mocked provider vertical slice works through `READ → NORMALIZE → DIAGNOSE → REPORT`. Repository-native real-account E2E validation remains pending; no Google Ads mutation service or method is wrapped or exposed.

### Blocker
Provide/inject the repository runtime credential set (`GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`, plus `GOOGLE_ADS_CUSTOMER_ID=9687071768`) in an execution environment that can run `python -m murat_ads_control --google-ads`. Credential values must not be committed or written into project docs.

### Next checkpoint
Repository-native E2E validation remains the only unfinished CP-002 exit criterion.

---

## CP-003 — Diagnostic engine v0 contract

**Date:** 2026-09-17  
**Status:** COMPLETE

### Entering state
The diagnostic engine had already been implemented as part of the CP-001 vertical slice, but CP-003 acceptance criteria were not independently proven as a checkpoint.

### Changes
- Reused the existing diagnostic engine instead of creating a duplicate layer.
- Added focused checkpoint tests for all eight rule families in the MVP roadmap.
- Added coverage proving multiple simultaneous findings are preserved instead of collapsed into a single explanation.
- Added deterministic outcome-precedence coverage for `BLOCKED`, `GOOGLE_ACTION_REQUIRED`, `WARNING`, and `OK` behavior.
- Added one minimal GitHub Actions guard that runs the repository unit tests on pull requests and pushes to `main`.
- PR #2 merged the CP-003 proof pass into `main`.

### Evidence
- GitHub Actions run `35222278182` completed successfully on Python 3.12 / Ubuntu.
- `python -m unittest discover -s tests -v` completed successfully in that run.
- The CP-003 suite proves account/campaign state or date blockers, unusable budget, ad policy eligibility, ad-group eligibility, keyword low-search-volume/ineligibility, targeting restrictions, conversion-dependent bidding without usable history, and zero/near-zero auction activity.
- Findings retain evidence, recommended action, confidence, and uncertainty.
- Simultaneous `BLOCKED` and `GOOGLE_ACTION_REQUIRED` findings remain visible while the overall outcome follows deterministic precedence.

### Exit state
The v0 diagnostic contract is proven without adding another engine or abstraction. CP-003 is complete independently of the still-pending CP-002 repository-native credentialed read.

### Next checkpoint
`CP-004 — Bek Mebel real diagnostic / EXP-001 decision` can be prepared from external read-only evidence, but final EXP-001 PASS requires the repository-native CP-002 E2E read.

---

## Planned sequence

- `CP-002` — Google Ads read-only connection (implementation merged; repository-native real validation pending)
- `CP-003` — Diagnostic engine v0 contract — COMPLETE
- `CP-004` — Bek Mebel real diagnostic / EXP-001 decision
- `CP-005` — Reduction pass: remove everything not needed by the proven core

Canonical detail: `docs/ROADMAP_MVP.md`.

---

## Template

### CP-NNN — Title

**Date:** YYYY-MM-DD  
**Status:** PLANNED / IN_PROGRESS / BLOCKED / COMPLETE

### Entering state

### Changes

### Evidence

### Exit state

### Blockers

### Next checkpoint
