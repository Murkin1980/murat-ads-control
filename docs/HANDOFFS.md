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
