# Decisions

Lightweight ADR-style log. Add a new entry for decisions that materially affect scope, architecture, security, product boundary, or monetization.

## ADR-001 — Independent product layer

**Status:** Accepted  
**Decision:** Keep Murat Ads Control as an independent repository/product layer rather than merging it into Business Discovery or MPE.  
**Reason:** Its responsibility is acquisition-platform integration and control; Business Discovery owns business hypotheses, while MPE owns governance/experiments. Independence also preserves future commercial/SaaS potential.

## ADR-002 — First experiment is read-only diagnostics

**Status:** Accepted  
**Decision:** First working vertical slice is Google Ads read-only diagnostics for `bek-mebel.kz`.  
**Reason:** It proves business value quickly without UI, database, billing, or campaign mutation.

## ADR-003 — Stable conceptual boundary

**Status:** Accepted  
**Decision:** Organize the product around `Workspace`, `Adapter`, and `Capability` abstractions.  
**Reason:** Keeps provider integrations separate from business functions and supports later plugin/capability monetization without building the full platform now.

## ADR-004 — Human approval for spend-affecting actions

**Status:** Accepted  
**Decision:** Any future campaign enablement, budget increase, destructive change, or spend-affecting mutation requires explicit human approval. New campaigns should initially be created as `PAUSED`.

## ADR-005 — Standard-library fixture runtime for CP-001

**Status:** Accepted
**Date:** 2026-09-16
**Context:** CP-001 needs to prove the complete diagnostic path before real Google credentials are available.
**Decision:** Use Python with only the standard library, a narrow `ReadOnlyAdsProvider` protocol, sanitized JSON fixtures, and a CLI that renders JSON and Markdown. Keep real Google authentication and the Google client dependency out of CP-001; expose only environment-variable names for the later runtime hook.
**Consequences:** The checkpoint has no install-time runtime dependency and is deterministic/easy to test. A later checkpoint must implement a real read-only Google adapter behind the provider protocol and validate its response shape.
**Evidence:** `python -m unittest discover -s tests -v` passes all 5 CP-001 tests; all five required fixtures run end-to-end.

## ADR-006 — Official Google Ads client only at the real-provider boundary

**Status:** Accepted
**Date:** 2026-09-16
**Context:** CP-002 needs one real Google Ads read path while preserving the standard-library fixture and diagnostic core.
**Decision:** Add only the official `google-ads>=25.0.0` dependency. Import it lazily when `--google-ads` is selected, load credentials through the client's environment loader after fail-closed validation, and keep the provider contract limited to `read_state()`.
**Consequences:** Fixture mode has no Google dependency at runtime; real mode requires the documented package and runtime environment variables. The provider owns GAQL and SDK mapping, while normalization, diagnostics, and reports remain provider-independent. No mutation service is imported or wrapped.
**Evidence / links:** `murat_ads_control/google_ads.py`, `requirements.txt`, and the CP-002 mocked provider tests.

## Template

### ADR-NNN — Title

**Status:** Proposed / Accepted / Superseded / Rejected  
**Date:** YYYY-MM-DD  
**Context:**  
**Decision:**  
**Consequences:**  
**Evidence / links:**
