# Diff Log

Record meaningful behavioral/product diffs here. This is not a replacement for Git history; it explains **what changed and why it matters**.

## DIFF-000 — Project memory initialized

**Date:** 2026-09-16

### Added
- `README.md`
- `AGENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/PRODUCT_ARCHITECTURE_AND_IDEAS.md`
- `docs/PROJECT_RULES.md`
- `docs/DECISIONS.md`
- `docs/EXPERIMENTS.md`
- `docs/CHECKPOINTS.md`
- `docs/HANDOFFS.md`
- `docs/DIFF_LOG.md`

### Behavioral impact
No runtime behavior yet. This change establishes canonical project memory, scope boundaries, deep-change gates, and the first experiment.

### Why
Prevent architecture ideas, monetization concepts, experiment state, and handoff context from disappearing between sessions or agents.

---

## DIFF-001 — CP-001 fixture-driven diagnostic vertical slice

**Date:** 2026-09-16
**Commit/PR:** local CP-001 implementation

### Before

The repository contained project contracts and documentation only. There was no executable read/load, normalization, diagnostic, or reporting path.

### After

A standard-library-only Python runtime loads sanitized JSON through a one-operation read-only provider contract, normalizes it, evaluates evidence-backed delivery rules, and renders JSON plus Markdown reports. Five fixtures cover the required blocker and uncertainty cases.

### Files changed

- `murat_ads_control/` — provider contract, fixture loader, normalized models, diagnostics, reports, CLI, and safe future environment contract.
- `fixtures/` — five sanitized diagnostic fixtures.
- `tests/test_cp001.py` — five critical contract/end-to-end tests.
- `README.md`, `.gitignore` — local fixture run instructions and generated-file hygiene.
- `docs/CHECKPOINTS.md`, `docs/DECISIONS.md`, `docs/HANDOFFS.md`, `docs/DIFF_LOG.md` — durable checkpoint records.

### Behavioral impact

Fixture input can now be run through `LOAD/READ → NORMALIZE → DIAGNOSE → REPORT`. Reports distinguish `OK`, `WARNING`, `BLOCKED`, and `GOOGLE_ACTION_REQUIRED`, and findings preserve evidence and uncertainty. No Google Ads write capability or real authentication was added.

### Why

Prove the smallest safe business path before introducing a real provider dependency or credentials.

### Evidence

`python -m unittest discover -s tests -v` — 5 passed; `git diff --check` — passed.

### Rollback note

Remove the CP-001 runtime, fixtures, and tests as one slice; project governance docs remain independently useful.

---

## Template

### DIFF-NNN — Title

**Date:** YYYY-MM-DD  
**Commit/PR:**

### Before

### After

### Files changed

### Behavioral impact

### Why

### Evidence

### Rollback note
