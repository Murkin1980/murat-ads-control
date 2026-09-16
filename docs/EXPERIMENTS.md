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
