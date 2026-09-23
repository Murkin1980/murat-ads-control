# Experiments

## EXP-001 — Bek Mebel Google Ads diagnostics

**Status:** EXPERIMENT  
**Target:** `bek-mebel.kz`  
**Question:** Why does the existing Google Ads campaign not meaningfully deliver/spend although the UI appears healthy?

### Hypothesis
A small read-only diagnostic engine can identify or materially narrow the delivery blocker faster and more clearly than manual investigation in Google Ads UI.

### Allowed scope

```text
AUTH → READ ADS STATE → NORMALIZE → DIAGNOSE → REPORT
```

### Forbidden in this experiment
- campaign/account mutation
- budget changes
- enabling/disabling entities
- UI build
- database/platform build
- GSC/GA4/Meta integration
- automatic optimization

### PASS criteria
1. Real account state is read successfully.
2. Root cause is identified or materially narrowed.
3. Findings include evidence.
4. Result is clearer/actionable versus manual UI inspection.
5. Zero production mutations.

### Evidence
Pending.

### Result
Pending.

---

## EXP-002 — Qoopia cross-session project memory

**Status:** IDEA / NEXT EXPERIMENT  
**Primary target:** `ai-microtask-factory` or MPE Core experiment workflow  
**Secondary target:** `murat-ads-control` after the first diagnostic checkpoint  
**Question:** Can Qoopia act as a retrievable cross-session memory/cache for Arena, Codex, and ChatGPT without replacing Git/Markdown as the project source of truth?

### Hypothesis
Qoopia can reduce context loss between fresh agent sessions by retrieving the current checkpoint, latest decisions, handoffs, experiment evidence, and next step from an existing project with less manual re-explanation.

### Architecture boundary

```text
Git / Markdown = authoritative source of truth
Qoopia          = retrievable memory/cache
Agents          = consumers
```

Qoopia must not become the only copy of project state. If Qoopia is unavailable, an agent must still be able to recover from repository files.

### Recommended first test
Use an existing project with frequent fresh sessions, preferably `ai-microtask-factory` / MPE Core. Seed or index a bounded set of canonical project documents, open a genuinely fresh agent session, and ask it to recover the current state without giving it the answer in the prompt.

### PASS criteria
1. Fresh session identifies the correct current checkpoint.
2. Fresh session identifies the latest material decision and its rationale.
3. Fresh session identifies the current blocker, if any.
4. Fresh session identifies the next intended step.
5. Retrieved state matches Git/Markdown truth with no invented project facts.
6. Recovery requires materially less manual context than the current workflow.
7. Qoopia can be disabled/rebuilt without losing authoritative project history.

### FAIL indicators
- stale or contradictory state is presented as current;
- invented decisions or blockers;
- agents trust Qoopia over newer repository state;
- setup/maintenance cost exceeds the context-recovery benefit;
- project becomes dependent on Qoopia availability.

### Evidence
Pending.

### Result
Pending.

---

## EXP-003 — Airtop Google Ads browser diagnostics

**Status:** IDEA / READY_TO_TEST  
**Target:** `bek-mebel.kz` Google Ads account  
**Question:** Can Airtop inspect the real Google Ads UI and materially narrow or identify why the campaign does not deliver/spend, without requiring the blocked direct Google Ads API credential path?

### Hypothesis
Airtop can act as a temporary browser-execution adapter for read-only Google Ads diagnostics: open the authenticated account, inspect campaign/ad group/ad/keyword states and relevant UI evidence, and produce a traceable diagnosis that can be compared with Murat Ads Control's own diagnostic model.

### Allowed scope

```text
HUMAN LOGIN / AUTHORIZED SESSION
  ↓
AIRTOP READ-ONLY BROWSER INSPECTION
  ↓
CAPTURE EVIDENCE
  ↓
MURAT ADS CONTROL DIAGNOSIS / COMPARISON
  ↓
REPORT
```

### First-run checks
- campaign / ad group / ad / keyword effective status;
- impressions and delivery history;
- eligibility / policy / disapproval / limited status;
- search volume and keyword constraints;
- negative keywords or exclusions that may block traffic;
- geographic targeting;
- bidding strategy and budget;
- conversion-tracking dependencies relevant to the current bidding strategy;
- Quality Score / ad rank signals when available in the UI;
- any explicit Google Ads diagnostics, recommendations, warnings, or account-level restrictions relevant to delivery.

### Forbidden in the first experiment
- publishing or enabling a campaign;
- changing bids, budgets, targeting, keywords, negatives, ads, assets, conversions, or account settings;
- autonomous optimization;
- automatic approval;
- storing Google credentials in the repository;
- making Airtop a mandatory production dependency;
- replacing the direct Google Ads API path without evidence and a separate decision.

### PASS criteria
1. Airtop successfully reaches the authorized Google Ads account.
2. It inspects the relevant campaign state without production mutations.
3. Root cause is identified or materially narrowed with reproducible UI evidence.
4. The result adds information beyond the current blocked API path/manual inspection.
5. Findings can be translated into a concrete Murat Ads Control diagnostic rule or next action.
6. Zero production mutations.

### Execution note
This experiment is **not executed by Arena itself**. Arena/Codex may prepare prompts, scripts, evidence templates, compare outputs, and update repository artifacts. The live authenticated browser session runs through Airtop (or another authorized browser surface) with the owner controlling login/approval.

### Evidence
Pending owner Airtop registration and first authorized read-only Google Ads session.

### Result
Pending.

## Template

### EXP-NNN — Name

**Status:** IDEA / EXPERIMENT / PASS / FAIL / HOLD  
**Target:**  
**Question:**  
**Hypothesis:**  
**Allowed scope:**  
**Forbidden:**  
**PASS criteria:**  
**Evidence:**  
**Result:**
