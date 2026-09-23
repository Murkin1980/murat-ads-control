<!-- MPE:SCOPE-CHANGE-CONTROL:START -->
## Mandatory first read — MPE Scope & Change Control

Before planning, coding, refactoring, dependency changes, testing strategy, deployment, or checkpoint execution, read:

- `docs/governance/SCOPE-CHANGE-CONTROL.md`

Read it before project-specific source-of-truth documents. Then follow this repository's local rules and the current checkpoint/spec.

The scope policy governs minimal change, reuse, checkpoint boundaries, deep-change, testing, evidence, change-size/merge-pressure, merge/deploy authority, and stopping conditions.

If a local rule appears to conflict with the scope policy, apply the documented source-of-truth priority. Do not silently weaken either rule; surface a deep-change conflict when required.
<!-- MPE:SCOPE-CHANGE-CONTROL:END -->

# AGENTS.md

## Project mission

Build the smallest evidence-driven acquisition automation core, starting with read-only Google Ads diagnostics for `bek-mebel.kz`.

## Mandatory operating rules

1. Prefer the smallest working vertical slice over platform-building.
2. Do not add UI, database, billing, marketplace, Meta Ads, GSC, GA4, or autonomous optimization unless a later checkpoint explicitly authorizes it.
3. Never commit secrets, OAuth refresh tokens, Google Ads developer tokens, credentials, or copied production account data.
4. Production advertising access begins read-only.
5. Any future mutation capability must be explicit, minimal, auditable, and human-approved.
6. New campaign creation, when eventually implemented, must default to `PAUSED`.
7. No autonomous enabling, budget increases, destructive mutations, or account-wide changes without explicit human approval.
8. Every meaningful implementation step must update the relevant durable memory docs: `CHECKPOINTS.md`, `HANDOFFS.md`, `DIFF_LOG.md`, `EXPERIMENTS.md`, and/or `DECISIONS.md`.
9. Preserve evidence. Do not claim `IMPLEMENTED`, `PASS`, or a root cause without reproducible evidence.
10. Do not duplicate responsibilities owned by MPE, Business Discovery, Leadgen Agent, MiniBase, or Salamat Projects Dashboard.

## Current allowed scope

```text
AUTH
  ↓
READ ADS STATE
  ↓
NORMALIZE
  ↓
DIAGNOSE
  ↓
REPORT
```

## First experiment

Question: **Why does the Google Ads campaign for `bek-mebel.kz` not meaningfully deliver/spend although the UI appears healthy?**

PASS requires:
- real account state read successfully;
- root cause identified or materially narrowed;
- evidence attached to conclusions;
- result is clearer/actionable compared with manual Google Ads UI inspection;
- zero production mutations.

## Deep-change gate

Stop and request explicit approval before:
- adding a persistent production database;
- enabling campaign/account mutations;
- adding autonomous spend changes;
- introducing multi-tenant billing;
- creating a plugin marketplace;
- merging this project into another repository;
- changing the fundamental Adapter / Capability / Workspace boundary.
