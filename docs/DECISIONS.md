# Decisions

Lightweight ADR-style log. Add a new entry for decisions that materially affect scope, architecture, security, product boundary, or monetization.

## ADR-001 — Independent product layer

**Status:** Accepted  
**Decision:** Keep Murat Ads Control as an independent repository/product layer rather than merging it into Business Discovery or MPE.  
**Reason:** Its responsibility is acquisition-platform integration and control; Business Discovery owns business hypotheses, while MPE owns governance/experiments. Independence also preserves future commercial/SaaS potential.

## ADR-002 — First experiment is read-only diagnostics

**Status:** Accepted  
**Decision:** First working vertical slice is Google Ads read-only diagnostics for `bek-mebel.kz`.  
**Reason:** It proves business value quickly without UI, database, billing, or campaign mutation.

## ADR-003 — Stable conceptual boundary

**Status:** Accepted  
**Decision:** Organize the product around `Workspace`, `Adapter`, and `Capability` abstractions.  
**Reason:** Keeps provider integrations separate from business functions and supports later plugin/capability monetization without building the full platform now.

## ADR-004 — Human approval for spend-affecting actions

**Status:** Accepted  
**Decision:** Any future campaign enablement, budget increase, destructive change, or spend-affecting mutation requires explicit human approval. New campaigns should initially be created as `PAUSED`.

## Template

### ADR-NNN — Title

**Status:** Proposed / Accepted / Superseded / Rejected  
**Date:** YYYY-MM-DD  
**Context:**  
**Decision:**  
**Consequences:**  
**Evidence / links:**
