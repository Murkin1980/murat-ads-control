# Architecture

## Current architecture

```text
Operator / Agent
      ↓
Murat Ads Control
      ↓
GoogleAdsAdapter (read-only)
      ↓
Google Ads API
      ↓
Normalizer
      ↓
AdsDiagnosticsCapability
      ↓
Evidence-backed report
```

## Stable abstractions

### Workspace
Business/client context. Examples: Bek Mebel, Salamat Mebel, Tuba, external client.

### Adapter
Technical integration with an external provider. First adapter: `GoogleAdsAdapter`.

Future candidates only when justified: Search Console, GA4, Meta Ads, WhatsApp/CRM.

### Capability
User-facing business function that consumes one or more adapters. First capability: `AdsDiagnosticsCapability`.

Future candidates: Campaign Builder, Campaign Recipe, SEO Opportunity Finder, Landing Audit, Lead Tracking, Budget Monitoring, Performance Alerts.

## Current normalized model

Add only what the first working capability needs. Likely minimum:

- Workspace
- Account
- Campaign
- AdGroup
- Ad
- Keyword
- Budget
- Conversion
- PerformanceSnapshot
- DiagnosticFinding
- Recommendation

Do not pre-build the full future schema.

## Provider boundary

Google-specific fields stay inside the adapter where practical. Capabilities consume normalized data and provider evidence references.

## Safety boundary

Agents do not receive permanent production credentials directly. Secrets live in protected runtime secret storage. Repository files contain only names, schemas, and setup instructions.

## Future control path

```text
Agent / UI
   ↓
validated intent
   ↓
Capability
   ↓
Policy / approval gate
   ↓
Adapter
   ↓
Provider API
```

Any future mutation path must remain auditable and human-approved.

## Non-goals for MVP

- SaaS dashboard
- billing
- plugin marketplace
- generic AI marketer
- automatic budget optimization
- cross-provider orchestration
- mass SEO content generation
- full CRM
