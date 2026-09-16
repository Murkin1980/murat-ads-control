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

### Evidence
- `python -m unittest discover -s tests -v` — 8 tests passed.
- Fixture mode still runs and produces the same CP-001 report structure.
- `--google-ads` without credentials fails closed with configuration field names only.
- Official client import/API surface was verified from `google-ads>=25.0.0` in an isolated environment.
- Real-account validation: `PENDING_EXTERNAL_CREDENTIALS`; no credential environment variables were available.

### Exit state
The real-provider mocked vertical slice works through `READ → NORMALIZE → DIAGNOSE → REPORT`. No Google Ads mutation service or method is wrapped or exposed. Real-account evidence is intentionally not claimed.

### Next checkpoint
`CP-003 — Diagnostic engine v0 on real provider data` (proposal only; not implemented in this checkpoint).

---

## Planned sequence

- `CP-002` — Google Ads read-only connection (implementation complete; real validation pending)
- `CP-003` — Diagnostic engine v0 on real provider data
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
