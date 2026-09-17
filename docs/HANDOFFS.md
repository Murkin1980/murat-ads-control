# Handoffs

Use this file to preserve session-to-session and agent-to-agent context.

Each meaningful work session should append one handoff before stopping, especially after merges, blocked experiments, credential/setup changes, or scope changes.

## HANDOFF-000 — Project initialization

**Date:** 2026-09-16  
**From:** project initialization session  
**To:** next Arena/Codex/ChatGPT session

### Current objective
Build only the read-only Google Ads diagnostic prototype for `bek-mebel.kz`.

### Current scope
```text
AUTH → READ ADS STATE → NORMALIZE → DIAGNOSE → REPORT
```

### Completed
- repository role defined;
- product architecture/ideas captured;
- project rules and deep-change gates captured;
- first experiment registered;
- CP-000 created.

### Not started
- Google Ads API auth setup;
- real account read;
- normalizer;
- diagnostics engine;
- report generation.

### Critical boundaries
- no production mutations;
- no UI/database/SaaS work;
- no GSC/GA4/Meta work;
- no secrets in Git;
- do not broaden scope until EXP-001 proves value.

### Next action
Create CP-001: prove authenticated read-only Google Ads access to the target account and capture evidence without exposing credentials.

---

## HANDOFF-001 — CP-001 complete, fixture path ready

**Date:** 2026-09-16
**From:** Arena implementation session
**To:** next Arena/Codex/agent session

### Objective
Complete only CP-001: prove a minimal fixture-driven read-only path for Google Ads diagnostics.

### Completed
- Added `ReadOnlyAdsProvider` and `FixtureAdsProvider`.
- Added normalized internal models and v0 evidence-backed diagnostic rules.
- Added JSON and Markdown report renderers plus the `python -m murat_ads_control` CLI.
- Added five sanitized fixtures: disabled/date-blocked campaign, disapproved ad, majority low-search-volume keywords, conversion bidding without usable history, and eligible zero-impression campaign.
- Added five tests covering the end-to-end path, provider snapshot isolation, evidence/uncertainty, CLI reports, and safe environment configuration names.
- Updated checkpoint, decision, diff, and handoff records.

### Current state
CP-001 is complete. `python -m unittest discover -s tests -v` passes 5 tests. No Google client, credentials, API call, or write operation exists.

### Evidence / refs
- Run: `python -m murat_ads_control --fixture fixtures/eligible_zero_impressions.json --as-of 2026-09-16 --json-out <path> --markdown-out <path>`
- Required fixtures are under `fixtures/`.
- Runtime entry point: `murat_ads_control/cli.py`.

### Decisions made
Python standard library only for this checkpoint; real authentication is intentionally deferred. The runtime hook names environment variables but never stores secret values.

### Blockers
No CP-001 blockers. Real-account evidence is not available and is intentionally deferred to CP-002.

### Do not do
Do not add Google credentials, a Google client dependency, CP-002 integration, mutations, UI, database, GSC, GA4, Meta, MiniBase, or SaaS scope in this checkpoint.

### Exact next action
Begin `CP-002 — Google Ads read-only connection`: implement and test a real read-only adapter behind the existing provider contract using runtime-injected secrets only.

---

## HANDOFF-002 — CP-002 adapter complete, external account pending

**Date:** 2026-09-16
**From:** Arena implementation session
**To:** next Arena/Codex/agent session

### Objective
Implement only the real Google Ads read-only connection behind the existing CP-001 provider contract.

### Completed
- Added `GoogleAdsProvider.read_state()` with no provider write service or mutation method.
- Added runtime fail-closed credential presence checks and optional MCC login customer ID.
- Added official `google-ads>=25.0.0` dependency only for real mode.
- Added six focused GAQL reads and mapping into the existing normalized model.
- Added `--google-ads`; fixture mode remains unchanged.
- Added three CP-002 tests; all CP-001 tests remain green.
- Updated checkpoint, decision, diff, and README records.

### Current state
The mocked real-provider path reaches `READ → NORMALIZE → DIAGNOSE → REPORT`. Real-account validation is `PENDING_EXTERNAL_CREDENTIALS`; required credential environment variables were absent in this execution environment.

### Evidence / refs
- Runtime adapter: `murat_ads_control/google_ads.py`
- Runtime configuration: `murat_ads_control/config.py`
- Dependency: `requirements.txt`
- Read-only mode: `python -m murat_ads_control --google-ads`

### Decisions made
Keep one provider method, use six minimum query slices, load credentials through the official client's environment loader, and keep SDK objects and raw API payloads outside the normalized/reporting layers.

### Blockers
No implementation blocker. External credentials are required for a real account smoke run.

### Do not do
Do not add mutation services, OAuth web UI, databases, account discovery, multi-tenancy, GSC, GA4, Meta, MiniBase, SaaS, or CP-003 logic.

### Exact next action
When approved and credentials are available, run one sanitized `--google-ads` read-only smoke report. Then propose only the smallest CP-003 work for real-provider diagnostic evidence.

---

## Template

### HANDOFF-NNN — Title

**Date:** YYYY-MM-DD  
**From:**  
**To:**

### Objective

### Completed

### Current state

### Evidence / refs

### Decisions made

### Blockers

### Do not do

### Exact next action
