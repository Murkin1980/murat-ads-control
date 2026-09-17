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

Read the canonical task and checkpoint docs before changing code. CP-001 is the fixture baseline; CP-002 adds only the strictly read-only Google Ads connection.

## CP-001 fixture run

Fixture mode uses only the Python standard library and remains available without Google credentials:

```bash
python -m unittest discover -s tests -v
python -m murat_ads_control \
  --fixture fixtures/eligible_zero_impressions.json \
  --as-of 2026-09-16 \
  --json-out /tmp/murat-report.json \
  --markdown-out /tmp/murat-report.md
```

## CP-002 Google Ads read-only run

Install the official client only when using Google Ads mode:

```bash
python -m pip install -r requirements.txt
```

Inject these names through the runtime environment. Values must not be placed in repository files, fixtures, reports, or logs:

- `GOOGLE_ADS_CUSTOMER_ID` — required customer ID;
- `GOOGLE_ADS_DEVELOPER_TOKEN` — required runtime secret;
- `GOOGLE_ADS_CLIENT_ID` — required runtime secret;
- `GOOGLE_ADS_CLIENT_SECRET` — required runtime secret;
- `GOOGLE_ADS_REFRESH_TOKEN` — required runtime secret;
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID` — optional MCC login customer ID.

Then run the same pipeline through the real provider:

```bash
python -m murat_ads_control \
  --google-ads \
  --as-of 2026-09-16 \
  --json-out /tmp/murat-google-report.json \
  --markdown-out /tmp/murat-google-report.md
```

Both modes implement `LOAD/READ → NORMALIZE → DIAGNOSE → REPORT`. Google Ads mode performs reads only; incomplete configuration fails closed.
