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
**Status:** PLANNED

### Entering state
Documentation and project boundaries exist; no runtime implementation exists yet.

### Required exit state
- minimal runtime/tooling selected and documented;
- fixture/mock path runs end-to-end through load/read → normalize → diagnose → report;
- narrow read-only provider contract exists;
- normalized diagnostic model exists;
- report contract exists;
- critical tests pass;
- no mutation code path exists;
- no secrets committed;
- handoff/diff/decision logs updated.

### Next checkpoint
`CP-002 — Google Ads read-only connection`.

---

## Planned sequence

- `CP-002` — Google Ads read-only connection
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
