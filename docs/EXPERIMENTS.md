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
