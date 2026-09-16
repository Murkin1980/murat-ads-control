# Arena Task — Murat Ads Control MVP / EXP-001

## Mission

Implement the smallest possible read-only Google Ads diagnostic prototype for the real Bek Mebel case.

Business question:

> Why does the existing Google Ads campaign for `bek-mebel.kz` appear healthy in the Google UI but fail to meaningfully deliver/spend?

The MVP must answer that question with evidence. Do not build the future platform.

## Mandatory reading order

Before changing code, read:
1. `README.md`
2. `AGENTS.md`
3. `docs/PROJECT_RULES.md`
4. `docs/ARCHITECTURE.md`
5. `docs/PRODUCT_ARCHITECTURE_AND_IDEAS.md`
6. `docs/EXPERIMENTS.md`
7. `docs/ROADMAP_MVP.md`
8. `docs/CHECKPOINTS.md`
9. `docs/HANDOFFS.md`
10. `docs/DIFF_LOG.md`
11. `docs/DECISIONS.md`

Treat repository docs as source of truth.

## New Idea Filter result

`EXTEND_EXISTING`

Do not create another repository or another service unless a hard blocker proves it necessary.

## Scope

Implement only this vertical slice:

```text
AUTH → READ ADS STATE → NORMALIZE → DIAGNOSE → REPORT
```

The first implementation must support fixtures/mocks before real credentials are required.

## Hard constraints

- Read-only Google Ads access only.
- No campaign/account/ad/ad-group/keyword mutations.
- No budget changes.
- No enabling/disabling entities.
- No automatic optimization.
- No Search Console, GA4, Meta Ads, billing, SaaS UI, marketplace, MiniBase, or multi-tenant platform work.
- No secrets in Git, fixtures, logs, reports, tests, or chat output.
- Do not add broad abstractions unless needed by the current diagnostic path.
- Keep dependencies minimal.
- Prefer provider interfaces + fixtures sufficient to swap real Google data later.
- Tests should protect critical contracts, not inflate test count.

## Required outputs

### 1. Minimal project runtime
Choose the smallest practical runtime/tooling for this task and document the choice in `docs/DECISIONS.md`.

### 2. Read-only provider contract
Provide a narrow Google Ads provider interface able to supply only the fields needed by diagnostics.

### 3. Normalized diagnostic model
Use a small internal model so diagnostic rules are not coupled directly to raw Google API response shapes.

### 4. Diagnostic engine v0
At minimum evaluate:
- account/customer eligibility/status where observable;
- campaign enabled/paused/removed and date bounds;
- budget/bidding configuration relevant to delivery;
- ad-group state;
- ad approval/policy/eligibility state;
- keyword eligibility and low-search-volume conditions;
- relevant geo/language/targeting restrictions where observable;
- conversion configuration/history relevant to bidding;
- recent impressions/clicks/cost sufficient to distinguish zero-delivery from low-delivery.

Do not pretend to know a root cause when evidence is insufficient.

### 5. Finding schema
Each finding should contain:
- status/severity;
- short title;
- concrete cause or hypothesis;
- evidence;
- affected entity/identifier without leaking secrets;
- recommended next test/action;
- confidence/uncertainty.

Supported top-level outcome states:
- `OK`
- `WARNING`
- `BLOCKED`
- `GOOGLE_ACTION_REQUIRED`

### 6. Report output
Produce both:
- machine-readable JSON;
- concise human-readable Markdown/text report.

The human report should answer the business question first, then evidence, then next action.

### 7. Fixture evidence
Create fixtures representing at least these meaningful cases:
- disabled/date-blocked campaign;
- ads not eligible/disapproved;
- majority of keywords low search volume/ineligible;
- conversion-dependent bidding with no usable conversion history;
- technically eligible campaign with zero recent impressions where API evidence is insufficient for a definitive root cause.

### 8. Safe real-account hook
Prepare configuration for later real Google Ads credentials, but do not fabricate credentials or commit placeholders that look real.

Use environment/runtime secret injection only.

## Checkpoint discipline

Work checkpoint by checkpoint.

### CP-01
Repository contracts + fixture-driven end-to-end path.

STOP after CP-01 and report:
- files changed;
- architecture chosen;
- tests run/results;
- anything intentionally omitted;
- exact next step for CP-02.

Do not continue into real Google credentials or CP-02 unless the user explicitly continues the task.

## Documentation obligations

Before stopping CP-01, update:
- `docs/CHECKPOINTS.md`
- `docs/HANDOFFS.md`
- `docs/DIFF_LOG.md`
- `docs/DECISIONS.md` if a meaningful architectural decision was made.

Do not mark ideas `IMPLEMENTED` without working evidence.

## Definition of done for CP-01

- fixture/mock input can run end-to-end through `READ/LOAD → NORMALIZE → DIAGNOSE → REPORT`;
- diagnostic findings are evidence-backed;
- critical tests pass;
- secret scan/manual secret review is clean;
- no mutation code path exists;
- repository remains small;
- docs reflect actual state.

## Final response format

Return:

1. `CP-01 RESULT: PASS | BLOCKED`
2. Git branch + HEAD SHA
3. Files changed
4. What works end-to-end
5. Tests/checks and exact results
6. Risks/blockers
7. Architecture reductions already made
8. `NEXT: CP-02 — Google Ads read-only connection`

If blocked, do not broaden scope. State the smallest blocker and evidence.
