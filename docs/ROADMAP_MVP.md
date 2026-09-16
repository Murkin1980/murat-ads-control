# Murat Ads Control — MVP Roadmap

## Objective

Prove on the real `bek-mebel.kz` Google Ads account that a small read-only diagnostic engine can explain why the campaign is not meaningfully delivering/spending, with evidence clearer than the Google Ads UI.

## Principle

Build the smallest real vertical slice first. Do not pre-build the future SaaS/platform.

```text
AUTH → READ → NORMALIZE → DIAGNOSE → REPORT
```

After each checkpoint, remove unnecessary complexity before adding the next layer.

## CP-01 — Repository + contracts

**Goal:** establish executable boundaries before integration work.

Deliverables:
- minimal runtime/tooling choice documented;
- config contract for Google Ads identifiers without secrets;
- provider interface for read-only Google Ads access;
- normalized diagnostic data model;
- report contract;
- tests only for critical contracts.

Exit criteria:
- no production credentials committed;
- no write/mutate API paths exist;
- project can run against fixtures/mocks end-to-end;
- `CHECKPOINTS.md`, `HANDOFFS.md`, `DIFF_LOG.md` updated.

## CP-02 — Google Ads read-only connection

**Goal:** authenticate and read account/campaign state safely.

Read only what the diagnostic needs:
- account/customer identity and status;
- campaign status, dates, budget and bidding strategy;
- ad groups;
- ads and policy/approval state;
- keywords, keyword status and relevant diagnostics;
- targeting needed to explain delivery;
- recent performance: impressions, clicks, cost;
- conversion configuration relevant to bidding/delivery.

Exit criteria:
- real account data can be fetched for Bek Mebel;
- sensitive credentials are injected only through runtime secrets/environment;
- raw evidence can be saved locally or as sanitized evidence artifacts;
- zero mutation capability.

## CP-03 — Diagnostic engine v0

**Goal:** turn raw Google state into a small set of explainable findings.

Initial rule families only:
1. account/campaign disabled or date blocked;
2. budget/bidding configuration likely preventing delivery;
3. ads disapproved/limited/not eligible;
4. ad groups disabled;
5. keywords ineligible, low-search-volume, or otherwise unable to serve;
6. targeting too narrow or conflicting where observable;
7. conversion-dependent bidding without usable conversion history;
8. campaign is technically eligible but has zero/near-zero auction activity, requiring a controlled next test.

Every finding must include:
- severity;
- cause;
- evidence;
- affected entity;
- recommended next test/action;
- confidence or uncertainty note.

Exit criteria:
- fixture tests cover the core rules;
- contradictory evidence is surfaced instead of hidden;
- engine can output `OK`, `WARNING`, `BLOCKED`, or `GOOGLE_ACTION_REQUIRED`.

## CP-04 — Bek Mebel real diagnostic

**Goal:** answer the real business question.

Run read-only against `bek-mebel.kz` Google Ads account and produce one concise report.

PASS if:
1. real account state is read successfully;
2. root cause is identified or materially narrowed;
3. conclusions include evidence;
4. result is clearer/actionable compared with manual UI inspection;
5. zero production mutations occurred.

If PASS: mark `EXP-001` PASS and freeze the evidence.
If FAIL: record exactly what the API could not explain and why.

## CP-05 — Reduction pass

**Goal:** remove everything that was not necessary to produce the successful diagnostic.

Questions:
- Which abstractions were unnecessary?
- Which fields were never used?
- Which dependencies can be removed?
- Can the diagnostic rules be simpler?
- Can setup/auth be made easier without weakening security?

Exit criteria:
- minimal stable core documented in `ARCHITECTURE.md`;
- dead/unused layers removed;
- `DIFF_LOG.md` records the reduction.

## Post-MVP gates — not part of EXP-001

Only after EXP-001 PASS, consider one at a time:
- create campaign in `PAUSED` state;
- Campaign Recipe abstraction;
- Search Console adapter + SEO Opportunity Finder;
- GA4/conversion attribution;
- multi-account/workspace model;
- Meta Ads adapter;
- client-facing productization/monetization.

Each must pass the New Idea Filter and get its own experiment/checkpoint.
