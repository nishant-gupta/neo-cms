# CMS Architecture Diagrams (V1)

This document provides a diagrammatic view of the technical architecture and implementation approach described in `TECHNICAL_DESIGN.md`.

---

## 1) System Context and Core Components

```mermaid
flowchart LR
    %% Users
    E[Editor / Publisher] --> UI[CMS Admin UI]
    V[Website Visitor] --> CDN[Cloud CDN / Firebase Hosting]

    %% Authoring and content APIs
    UI --> API[Cloud Run API]
    API --> FS[(Firestore)]
    API --> DOCS[Google Docs API]
    API --> TASKS[Cloud Tasks]

    %% Asset upload and processing
    UI -->|Request signed URL| API
    UI -->|Direct upload via signed URL| GCSA[(GCS: cms-assets-prod)]
    GCSA --> EVT[Object Finalize Event]
    EVT --> APROC[Cloud Run Asset Processor]
    APROC --> GCSD[(GCS: cms-assets-derivatives)]
    APROC --> FS

    %% Build and publish
    TASKS --> BUILD[Cloud Run Build Worker]
    BUILD --> ELEVENTY[Eleventy Static Generator]
    ELEVENTY --> PREVIEW[(GCS: cms-site-preview)]
    ELEVENTY --> PROD[(GCS: cms-site-prod)]
    PREVIEW --> CDN
    PROD --> CDN
```

---

## 2) Content Lifecycle: Draft -> Preview -> Publish

```mermaid
sequenceDiagram
    autonumber
    actor Editor as Editor/Publisher
    participant UI as CMS Admin UI
    participant API as Cloud Run API
    participant Docs as Google Docs API
    participant FS as Firestore
    participant Tasks as Cloud Tasks
    participant Build as Build Worker (Cloud Run)
    participant Preview as GCS Preview Bucket
    participant Prod as GCS Prod Bucket

    Editor->>UI: Click "Sync Doc"
    UI->>API: POST /pages/{id}/sync-doc
    API->>Docs: Fetch document by docId
    Docs-->>API: Structured document JSON
    API->>API: Parse + sanitize + normalize
    API->>FS: Save normalized content + revision metadata
    API-->>UI: Sync success

    Editor->>UI: Click "Create Preview"
    UI->>API: POST /pages/{id}/preview
    API->>Tasks: Enqueue buildPreview(revisionId)
    Tasks->>Build: Execute preview build
    Build->>Preview: Write /rev/{revisionId}/ artifacts
    Build->>FS: Mark revision preview_ready
    API-->>UI: Return preview URL

    Editor->>UI: Click "Publish"
    UI->>API: POST /pages/{id}/publish
    API->>API: Validate role + state transition
    API->>Tasks: Enqueue buildProd(revisionId)
    Tasks->>Build: Execute prod build
    Build->>Prod: Write production artifacts
    Build->>FS: Mark revision published + audit event
    API-->>UI: Publish success
```

---

## 3) Deployment Topology (Dev / Staging / Prod)

```mermaid
flowchart TB
    GH[GitHub Repo]
    CI[GitHub Actions / Cloud Build]

    GH --> CI

    subgraph DEV[Dev Environment]
      DEV_API[Cloud Run API]
      DEV_BUILD[Cloud Run Build Worker]
      DEV_FS[(Firestore)]
      DEV_BUCKETS[(GCS Buckets)]
    end

    subgraph STG[Staging Environment]
      STG_API[Cloud Run API]
      STG_BUILD[Cloud Run Build Worker]
      STG_FS[(Firestore)]
      STG_BUCKETS[(GCS Buckets)]
      STG_CDN[CDN / Hosting]
    end

    subgraph PROD[Production Environment]
      PROD_API[Cloud Run API]
      PROD_BUILD[Cloud Run Build Worker]
      PROD_FS[(Firestore)]
      PROD_BUCKETS[(GCS Buckets)]
      PROD_CDN[CDN / Hosting]
      Users[Public Users]
    end

    CI --> DEV
    CI --> STG
    CI --> PROD
    PROD_CDN --> Users
```

---

## 4) Data Model Relationships

```mermaid
erDiagram
    PAGE ||--o{ REVISION : has
    PAGE }o--o{ ASSET : references
    REVISION }o--o{ ASSET : bundles

    PAGE {
      string id
      string docId
      string slug
      string status
      string currentRevisionId
      datetime updatedAt
    }

    REVISION {
      string id
      string pageId
      string docSnapshotHash
      string artifactPath
      string status
      string createdBy
      datetime createdAt
    }

    ASSET {
      string id
      string bucket
      string object
      string mimeType
      string variantsJson
      datetime updatedAt
    }
```

---

## 5) V1 Delivery Timeline (7 Weeks)

```mermaid
gantt
    title V1 CMS Execution Timeline
    dateFormat  YYYY-MM-DD
    axisFormat  %b %d

    section Discovery
    Requirements and templates lock         :done, d1, 2026-03-02, 7d

    section Platform
    GCP setup + auth + IAM baseline         :active, p1, 2026-03-09, 7d
    Content and asset APIs                  :p2, 2026-03-16, 7d
    Google Docs ingestion + sanitizer       :p3, 2026-03-23, 7d

    section Site and Workflows
    Eleventy templates + preview pipeline   :p4, 2026-03-30, 7d
    Publish approvals + audit + rollback    :p5, 2026-04-06, 7d

    section Hardening
    Lighthouse CI + observability + go-live :p6, 2026-04-13, 7d
```

---

## 6) Architectural Approach (Summary)

1. Keep authoring simple with Google Docs.
2. Keep runtime minimal by publishing static site artifacts.
3. Keep operations light with serverless managed GCP components.
4. Keep performance high using strict budgets and Lighthouse gates.
5. Keep governance safe with revisioned previews, approvals, and audit logging.

