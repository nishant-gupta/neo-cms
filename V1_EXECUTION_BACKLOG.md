# V1 Execution Backlog

This backlog translates `TECHNICAL_DESIGN.md` into an actionable v1 delivery plan.

- Scope target: v1 MVP (3 templates, Google Docs ingestion, GCS assets, preview/publish, Lighthouse CI)
- Duration target: 7 weeks
- Delivery model: weekly milestones with acceptance gates

---

## 1) Epics Overview

| Epic ID | Epic Name | Outcome | Priority |
|---|---|---|---|
| EPIC-0 | Discovery and Foundations | Lock requirements, templates, and success criteria | P0 |
| EPIC-1 | Platform Setup and Security Baseline | Provision GCP services, auth, IAM, and environment baselines | P0 |
| EPIC-2 | Content and Asset APIs | Provide core APIs for pages, revisions, and assets | P0 |
| EPIC-3 | Google Docs Ingestion and Normalization | Convert docs into sanitized structured content | P0 |
| EPIC-4 | Static Site Rendering and Preview | Generate preview site revisions from normalized content | P0 |
| EPIC-5 | Publish, Governance, and Rollback | Controlled publishing with approvals, audit logs, rollback | P0 |
| EPIC-6 | Performance, Quality, and Operations | Lighthouse gates, observability, and production hardening | P1 |

---

## 2) Detailed Epics and User Stories

## EPIC-0: Discovery and Foundations (Week 1)

### US-0.1 Define page templates and content model
**As** a product owner  
**I want** agreed templates (Landing, Article, Basic Content) and required metadata  
**So that** engineering can build deterministic parsing and rendering.

**Acceptance Criteria**
- Template field list documented per template.
- Required metadata defined (`slug`, SEO fields, status).
- Sample Google Docs templates shared with editorial team.

### US-0.2 Define non-functional SLOs and KPI targets
**As** an engineering lead  
**I want** measurable v1 targets  
**So that** release quality can be objectively validated.

**Acceptance Criteria**
- Lighthouse target and page weight budget documented.
- Publish latency target defined (<2 min median).
- Cost guardrail documented (monthly target + alert threshold).

### US-0.3 Set delivery governance and environments
**As** a delivery manager  
**I want** a clear release and environment strategy  
**So that** releases are predictable.

**Acceptance Criteria**
- `dev/staging/prod` environment policy documented.
- Definition of Done for each epic agreed.
- Risk register initialized with owners.

---

## EPIC-1: Platform Setup and Security Baseline (Week 2)

### US-1.1 Provision core GCP resources
**As** a platform engineer  
**I want** buckets, Firestore, Cloud Run, and Cloud Tasks provisioned  
**So that** feature implementation can begin.

**Acceptance Criteria**
- Buckets created: assets, derivatives, preview, prod.
- Firestore collections created or migration scripts ready.
- Cloud Run services deployed to `dev`.

### US-1.2 Implement authentication and role model
**As** an admin  
**I want** role-based access for editors, publishers, and admins  
**So that** publishing is controlled.

**Acceptance Criteria**
- Google OAuth integrated for admin/API access.
- Roles enforced on protected endpoints.
- Unauthorized calls return expected 401/403 responses.

### US-1.3 Secure storage and upload paths
**As** a security engineer  
**I want** uploads restricted via signed URLs  
**So that** no public write path exists.

**Acceptance Criteria**
- `POST /assets/signed-upload-url` implemented.
- GCS buckets private by default.
- Signed upload expires and enforces mime restrictions.

---

## EPIC-2: Content and Asset APIs (Week 3)

### US-2.1 Create and update page metadata APIs
**As** an editor  
**I want** to create and edit page metadata  
**So that** content can enter workflow.

**Acceptance Criteria**
- `POST /pages` and `PUT /pages/{id}` implemented.
- Validation for slug uniqueness and required SEO fields.
- Firestore persistence with timestamps and user attribution.

### US-2.2 Asset metadata registration and retrieval
**As** an editor  
**I want** uploaded assets tracked with metadata and variants  
**So that** pages can reference optimized assets.

**Acceptance Criteria**
- `GET /assets/{id}` implemented.
- Metadata includes mime, dimensions, and variant list.
- Broken/missing asset references surface validation errors.

### US-2.3 Add revision tracking baseline
**As** a publisher  
**I want** each preview/publish to create immutable revisions  
**So that** changes are traceable.

**Acceptance Criteria**
- Revision IDs generated and persisted.
- Revision references page, doc hash, artifact path, and actor.
- Revision status transitions validated by tests.

---

## EPIC-3: Google Docs Ingestion and Normalization (Week 4)

### US-3.1 Sync content from Google Docs
**As** an editor  
**I want** to sync the linked Google Doc into CMS data  
**So that** authored content is importable without copy-paste.

**Acceptance Criteria**
- `POST /pages/{id}/sync-doc` implemented.
- Google Docs API integration retrieves structured doc content.
- Failure states return actionable errors.

### US-3.2 Parse and sanitize supported document blocks
**As** a platform engineer  
**I want** a whitelist parser for allowed block types  
**So that** generated HTML is safe and predictable.

**Acceptance Criteria**
- Supported blocks: headings, paragraphs, lists, links, images, tables, quotes.
- Unsupported styles are stripped and logged as warnings.
- Sanitization tests cover XSS and malformed content.

### US-3.3 Normalize parsed content to template schema
**As** a frontend engineer  
**I want** parsed content mapped to stable template data contracts  
**So that** rendering is deterministic.

**Acceptance Criteria**
- Normalized JSON schema documented and versioned.
- Template mapper passes snapshot tests for all 3 templates.
- Doc-to-schema transform includes stable ordering/id generation.

---

## EPIC-4: Static Site Rendering and Preview (Week 5)

### US-4.1 Build 3 page templates in Eleventy
**As** a frontend engineer  
**I want** template implementations for landing, article, and basic content  
**So that** all v1 page types are renderable.

**Acceptance Criteria**
- 3 templates render from normalized data.
- Pages include required SEO meta tags and canonical URLs.
- Accessibility baseline checks pass (semantic heading order, alt text rules).

### US-4.2 Implement revisioned preview builds
**As** an editor  
**I want** immutable preview URLs for each revision  
**So that** reviewers can validate exact output before publish.

**Acceptance Criteria**
- `POST /pages/{id}/preview` triggers preview build.
- Preview artifact stored under `rev/{revisionId}` path.
- Preview URL returned and accessible with expected content.

### US-4.3 Implement asset optimization for rendering
**As** a performance engineer  
**I want** responsive optimized image variants used in templates  
**So that** Lighthouse performance remains high.

**Acceptance Criteria**
- AVIF/WebP variants generated for configured widths.
- Templates emit `srcset`/`sizes`.
- Large raw images are never used directly on rendered pages.

---

## EPIC-5: Publish, Governance, and Rollback (Week 6)

### US-5.1 Add publish endpoint and approvals
**As** a publisher  
**I want** approved revisions only to be publishable  
**So that** accidental releases are prevented.

**Acceptance Criteria**
- `POST /pages/{id}/publish` implemented.
- Role check: only publishers/admins can publish.
- Publish action enforces allowed status transitions.

### US-5.2 Implement audit logging and revision history
**As** an auditor  
**I want** full traceability for preview and publish actions  
**So that** compliance and debugging are possible.

**Acceptance Criteria**
- Actor, timestamp, revision ID, and action recorded.
- API for revision detail (`GET /revisions/{id}`) available.
- Publish and rollback events included in logs.

### US-5.3 Add rollback mechanism
**As** an operator  
**I want** one-click rollback to previous known-good revision  
**So that** production incidents can be mitigated quickly.

**Acceptance Criteria**
- Previous production artifacts retained by policy.
- Rollback runbook documented and tested in staging.
- Rollback operation completes within target window.

---

## EPIC-6: Performance, Quality, and Operations (Week 7)

### US-6.1 Integrate CI checks and Lighthouse gates
**As** an engineering team  
**I want** CI to block regressions  
**So that** v1 quality stays consistent.

**Acceptance Criteria**
- CI pipeline runs lint, tests, build, and Lighthouse checks.
- Lighthouse thresholds enforced for 3 representative pages.
- Failing checks block deployment to production.

### US-6.2 Add observability and alerting
**As** an SRE  
**I want** visibility into job health, failures, and latency  
**So that** incidents are detected early.

**Acceptance Criteria**
- Dashboards for build success rate, publish latency, API errors.
- Alerts configured for failure-rate and latency SLO breaches.
- Logs include correlation ID for preview/publish pipelines.

### US-6.3 Production readiness review
**As** a release manager  
**I want** final readiness sign-off  
**So that** v1 can launch safely.

**Acceptance Criteria**
- Security checklist completed (IAM, bucket access, sanitization).
- Cost review completed with baseline and forecast.
- Go-live checklist signed by engineering + product owners.

---

## 3) Week-by-Week Milestones (7-Week Plan)

| Week | Milestone | Deliverables | Exit Criteria |
|---|---|---|---|
| Week 1 | Requirements and model lock | Template specs, metadata schema, SLO/KPI definitions | Signed-off scope and success metrics |
| Week 2 | Platform ready in dev | GCP resources, auth, IAM roles, signed upload endpoint | Core infra reachable and secured |
| Week 3 | CRUD and revision core | Page APIs, asset metadata APIs, revision entities | End-to-end create/edit metadata flow works |
| Week 4 | Docs ingestion complete | Google Docs sync, parser, sanitizer, normalized schema | Sample docs import successfully without unsafe output |
| Week 5 | Preview site live | Eleventy templates, preview builds, revision preview URLs | Editors can preview all 3 templates |
| Week 6 | Publish governance live | Publish endpoint, approvals, audit logs, rollback runbook | Controlled publish + tested rollback in staging |
| Week 7 | Quality gates and go-live | Lighthouse CI thresholds, dashboards/alerts, readiness checklist | v1 launch sign-off complete |

---

## 4) Cross-Epic Dependencies

- EPIC-0 -> EPIC-1: templates and metadata must be finalized first.
- EPIC-1 -> EPIC-2/3: auth, buckets, and service baseline required.
- EPIC-2 + EPIC-3 -> EPIC-4: preview rendering depends on normalized content + asset metadata.
- EPIC-4 -> EPIC-5: publish flow depends on revisioned preview artifacts.
- EPIC-5 -> EPIC-6: governance in place before final readiness sign-off.

---

## 5) Prioritized MVP Story Cutline

If timeline risk appears, keep the following as non-negotiable v1:
1. US-1.1, US-1.2, US-1.3
2. US-2.1, US-2.3
3. US-3.1, US-3.2
4. US-4.1, US-4.2
5. US-5.1, US-5.2
6. US-6.1

Lower-priority deferrable items:
- advanced optimization variants beyond baseline widths
- extra dashboard dimensions
- non-critical workflow polish

---

## 6) Definition of Done (V1)

V1 is considered complete when all of the following are true:
- Editors can author in Google Docs and sync content to CMS.
- Assets upload to GCS through signed URLs and are optimized.
- Draft content can be previewed via immutable revision URLs.
- Approved content can be published and rolled back.
- Lighthouse CI thresholds pass for agreed key pages.
- Security, observability, and cost guardrails are in place.

