# Murat Ads Control

**Acquisition Automation Layer** for simple, auditable control of advertising and acquisition platforms.

## Current objective

Prove on the real `bek-mebel.kz` Google Ads account that automated read-only diagnostics can explain delivery/spend problems faster and more clearly than manual inspection in the Google Ads UI.

## Current scope

```text
AUTH → READ ADS STATE → NORMALIZE → DIAGNOSE → REPORT
```

No campaign mutation, automatic spend changes, SaaS UI, billing, GSC, GA4, Meta Ads, or multi-tenant product work in the first experiment.

## Canonical docs

- `AGENTS.md` — rules for Arena/Codex/agents
- `docs/PRODUCT_ARCHITECTURE_AND_IDEAS.md` — long-term product ideas + implementation status
- `docs/ARCHITECTURE.md` — current technical architecture and boundaries
- `docs/PROJECT_RULES.md` — minimal project governance
- `docs/ROADMAP_MVP.md` — checkpoint-by-checkpoint MVP roadmap
- `docs/ARENA_MVP_TASK.md` — canonical Arena task packet for the first implementation checkpoint
- `docs/EXPERIMENTS.md` — experiment registry and PASS/FAIL evidence
- `docs/CHECKPOINTS.md` — durable progress checkpoints
- `docs/HANDOFFS.md` — session/agent handoffs
- `docs/DIFF_LOG.md` — meaningful changes and why they happened
- `docs/DECISIONS.md` — lightweight architecture/product decisions

## Product boundary

Murat Ads Control is independent from MPE, Business Discovery, Leadgen Agent, and Salamat Projects Dashboard.

- **MPE** governs experiments and approvals.
- **Business Discovery** produces business hypotheses.
- **Leadgen Agent** handles outbound lead generation and outreach.
- **Murat Ads Control** handles paid/organic acquisition platform integration, diagnostics, and later controlled campaign automation.
- **Salamat Projects Dashboard** remains read-only portfolio monitoring.

## First target

`bek-mebel.kz` — diagnose why the existing Google Ads campaign appears healthy but does not meaningfully deliver/spend.

## Start here for Arena

Open `docs/ARENA_MVP_TASK.md` and execute only `CP-001`. Stop after CP-001 and report results before attempting real Google credentials or CP-002.

## CP-001 local run

The fixture-driven path uses only the Python standard library:

```bash
python -m unittest discover -s tests -v
python -m murat_ads_control \
  --fixture fixtures/eligible_zero_impressions.json \
  --as-of 2026-09-16 \
  --json-out report.json \
  --markdown-out report.md
```

This implements `LOAD/READ → NORMALIZE → DIAGNOSE → REPORT` for sanitized fixtures. Real Google Ads authentication is intentionally deferred to CP-002.
