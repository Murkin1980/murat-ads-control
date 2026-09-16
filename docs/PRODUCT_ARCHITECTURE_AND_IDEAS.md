# Product Architecture & Ideas

Canonical product-thinking document for Murat Ads Control.

This file preserves future architecture, monetization ideas, adapters/capabilities, experiment boundaries, and implementation status. It is intentionally broader than the current MVP. Implementation must remain minimal and evidence-driven.

## Status legend

- `IDEA` — captured, not validated
- `PLANNED` — approved direction, not started
- `EXPERIMENT` — being tested on a narrow real case
- `IMPLEMENTING` — actively being built
- `IMPLEMENTED` — working and verified
- `HOLD` — deliberately postponed
- `REJECTED` — intentionally not pursued

`IMPLEMENTED` requires evidence, not code existence alone.

## Product thesis

Build an independent acquisition automation layer that hides advertising/analytics platform complexity behind a simple, auditable interface.

Long-term direction:

```text
Client / Business
      ↓
Workspace
      ↓
Core
      ↓
Adapters
      ├── Google Ads
      ├── Google Search Console
      ├── GA4
      ├── Meta Ads
      ├── WhatsApp / CRM
      └── future providers
      ↓
Capabilities
      ├── Ads Diagnostics
      ├── Campaign Builder
      ├── Campaign Recipe / Reuse
      ├── SEO Opportunity Finder
      ├── Landing Audit
      ├── Lead Tracking
      ├── Budget Monitoring
      └── Performance Alerts
```

Current status: `EXPERIMENT`

## Immediate experiment

### Goal

Prove that automated Google Ads diagnostics can explain delivery/spend problems faster and more clearly than manual investigation in Google Ads UI.

### First real case

- Site: `bek-mebel.kz`
- Problem: campaign appears healthy in the UI but does not meaningfully deliver/spend
- Mode: read-only
- Output: concise diagnosis with evidence and recommended next test

### MVP boundary

```text
AUTH → READ ADS STATE → NORMALIZE → DIAGNOSE → REPORT
```

Do not add yet:
- SaaS UI
- billing
- MiniBase integration unless proven necessary
- Search Console
- SEO automation
- campaign creation
- campaign cloning
- Meta Ads
- autonomous optimization

Status: `EXPERIMENT`

## Core abstractions

### Workspace
One business/client context.
Status: `PLANNED`

### Adapter
Technical integration with an external provider.

Candidates:
- `GoogleAdsAdapter` — `EXPERIMENT`
- `SearchConsoleAdapter` — `IDEA`
- `GA4Adapter` — `IDEA`
- `MetaAdsAdapter` — `IDEA`
- `WhatsAppAdapter` — `IDEA`
- `CRMAdapter` — `IDEA`

### Capability
User-facing business function.

Candidates:
- `AdsDiagnosticsCapability` — `EXPERIMENT`
- `CampaignBuilderCapability` — `IDEA`
- `CampaignRecipeCapability` — `IDEA`
- `SeoOpportunityCapability` — `IDEA`
- `LandingAuditCapability` — `IDEA`
- `LeadTrackingCapability` — `IDEA`
- `BudgetMonitoringCapability` — `IDEA`
- `PerformanceAlertsCapability` — `IDEA`

## Campaign Builder

Future capability: turn a simple business brief into a Campaign Blueprint with budget, geo, ad groups, keywords, negatives, responsive ads, landing, conversion target, and starting bidding configuration.

Safety rule: new campaigns must initially be created as `PAUSED`; human approval is required before enabling spend.

Status: `IDEA`

## Campaign Recipe

Successful campaign structures should be preserved as provider-independent recipes, not copied only by Google campaign ID.

A recipe may preserve:
- ad-group structure
- keyword clusters
- negative keyword patterns
- headline/description patterns
- starting bidding configuration
- landing strategy
- geo strategy
- conversion-goal pattern

When reused, replace brand, domain, landing, geo, budget, offer, contacts, and conversion identifiers.

Long-term value: a library of proven acquisition scenarios becomes proprietary operational knowledge.

Status: `IDEA`

## Search Console / SEO Opportunity Mining

Future read-only capability to find:
- question-style long-tail queries
- high impressions + low CTR
- realistic ranking opportunities
- queries already tied to existing pages
- missing-content opportunities
- FAQ opportunities

No mass AI page generation by default.

Status: `IDEA`

## Multi-account Google layer

Do not create a separate product integration for every landing page.

Target:

```text
One product OAuth application
        ↓
Multiple Google connections
        ↓
Multiple Ads accounts / GSC properties
        ↓
Workspace bindings
```

For Google Ads, Manager Account (MCC) may be used where appropriate.

Status: `PLANNED`

## Secret handling

Secrets never enter Git.

Candidate secret classes:
- Google OAuth credentials
- refresh tokens
- Google Ads developer token
- provider API credentials
- webhook signing secrets

Target rule:
- runtime secret store for secrets
- database only for non-secret metadata/references
- agents do not receive unrestricted permanent credentials

Status: `PLANNED`

## Productization / monetization

Potential packaging:

### Start
- Google Ads diagnostics
- delivery monitoring
- understandable problem reports

### Growth
- diagnostics
- campaign creation
- Search Console
- SEO opportunities
- Campaign Recipes

### Pro
- multiple sites/accounts
- reusable recipes
- automated recommendations
- reports/alerts
- advanced integrations

Possible revenue models:
- SaaS subscription
- capability add-ons
- managed automation

Pricing is intentionally not fixed yet.

Status: `IDEA`

## Plugin model

Important distinction:

**Adapter** = technical provider connection.

**Capability / Plugin** = business function exposed to the user.

A capability may use several adapters. Preserve this separation as the product grows.

Status: `PLANNED`

## Internal use before external SaaS

First prove on internal businesses:
1. `bek-mebel.kz` — diagnostics
2. Salamat Mebel — later campaign/SEO experiments
3. other internal sites/landings

Only after repeated internal success add multi-client SaaS complexity.

Status: `PLANNED`

## Architecture reduction principle

1. Build the smallest real vertical prototype.
2. Prove value with real evidence.
3. Inspect what was actually necessary.
4. Remove unnecessary layers.
5. Keep the smallest stable core.
6. Add the next capability only after that.

Do not design a large AI marketing platform in advance.

## Current implementation matrix

| Area | Status |
|---|---|
| Product thesis | `PLANNED` |
| Independent repository | `IMPLEMENTED` |
| Bek Mebel diagnostic experiment | `EXPERIMENT` |
| Workspace abstraction | `PLANNED` |
| Adapter interface | `PLANNED` |
| Google Ads adapter | `EXPERIMENT` |
| Ads diagnostics | `EXPERIMENT` |
| Human approval boundary | `PLANNED` |
| Secret isolation | `PLANNED` |
| Google Search Console adapter | `IDEA` |
| SEO Opportunity Finder | `IDEA` |
| Campaign Builder | `IDEA` |
| Campaign Recipe | `IDEA` |
| Campaign cloning/reuse | `IDEA` |
| GA4 adapter | `IDEA` |
| Meta Ads adapter | `IDEA` |
| SaaS billing | `HOLD` |
| Client SaaS UI | `HOLD` |
| Plugin marketplace | `HOLD` |
| Automatic budget optimization | `HOLD` |

## Deep-change gates

Explicit approval required before:
- autonomous spend changes
- automatically enabling campaigns
- budget changes without approval
- deleting campaigns/ads
- storing new sensitive credentials
- introducing a new persistent production database
- multi-tenant billing infrastructure
- plugin marketplace
- merging core responsibilities into another repository

## Repository role

This repository remains an independent product/application layer. It may integrate with MPE and reuse components, but should not be merged into Business Discovery merely for organizational convenience.

## Next concrete step

Build only the Bek Mebel read-only Google Ads diagnostic prototype.

Success first. Architecture reduction second. Product expansion third.
