# Project Rules

## Purpose
Keep Murat Ads Control small, auditable, and evidence-driven while preserving future product ideas.

## Rules

1. Default to extending the current core, not adding parallel systems.
2. New substantial ideas must pass the Murat Project Engineer New Idea Filter before implementation.
3. Prefer experiments that answer one real business question.
4. No production mutations during the first Google Ads diagnostic experiment.
5. Secrets never enter Git, chat logs intended for commit, screenshots, fixtures, or example configs.
6. Add only tests that protect real checkpoints; avoid test bloat.
7. Every meaningful change must leave durable evidence in project docs.
8. `IMPLEMENTED` means verified behavior, not merely merged code.
9. Preserve provider-specific details behind adapters where practical.
10. Human approval is mandatory before any future action that can spend money, enable campaigns, increase budgets, delete entities, or materially change targeting.

## Required durable records

- `docs/DECISIONS.md` — why a product/architecture choice was made
- `docs/EXPERIMENTS.md` — hypothesis, scope, evidence, result
- `docs/CHECKPOINTS.md` — current durable state
- `docs/HANDOFFS.md` — session/agent transfer notes
- `docs/DIFF_LOG.md` — meaningful behavioral diffs

## Status vocabulary

`IDEA`, `PLANNED`, `EXPERIMENT`, `IMPLEMENTING`, `IMPLEMENTED`, `HOLD`, `REJECTED`.

## Deep-change approval required for

- new persistent production database
- new repository split/merge
- autonomous campaign mutations
- autonomous spend changes
- SaaS billing / multi-tenant production model
- plugin marketplace
- fundamental change to Workspace / Adapter / Capability boundaries
