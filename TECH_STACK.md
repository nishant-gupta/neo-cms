# Technical Stack (v1)

This document defines the recommended technical stack for v1 delivery, aligned with `TECHNICAL_DESIGN.md` and `V1_EXECUTION_BACKLOG.md`.

## Why this stack

The project is static-first and event-driven:
- Google Docs for authoring
- GCS for assets and static artifacts
- Firestore for metadata and workflow state
- Cloud Run + Cloud Tasks for async pipelines

Given this shape, Node.js with TypeScript provides fast iteration and low operational overhead while staying production-ready.

## Recommended stack

### Runtime and language
- Node.js 20 LTS
- TypeScript (strict mode)

### Backend framework and API foundations
- Fastify (HTTP server)
- Zod (request and environment validation)
- Pino (structured logging)

### Google Cloud platform services
- Cloud Run (API and worker services)
- Cloud Tasks (background job orchestration)
- Firestore (metadata, revisions, assets)
- Cloud Storage (assets, derivatives, preview, prod buckets)
- Secret Manager (runtime secrets)
- Cloud Logging + Cloud Monitoring (observability)

### Infrastructure and delivery
- Terraform (GCP provisioning and IAM)
- Docker (container packaging for Cloud Run)
- GitHub Actions (CI: lint, test, build, deploy)

## Recommended repository conventions

- Keep infrastructure in `infra/terraform`.
- Keep backend service in `templates/node-backend` (starter) and later promote to `services/api` for implementation.
- Use environment names consistently: `dev`, `staging`, `prod`.
- Prefer one service account per workload with least privilege IAM.

## Java compatibility note

Java (Spring Boot 3 + Java 21) is also a valid option if the team later needs stronger domain layering and stricter enterprise conventions. For current v1 scope and speed-to-delivery, Node.js + TypeScript is recommended as default.

## EPIC-1 mapping

This stack directly supports EPIC-1 stories:
- US-1.1 Provision core GCP resources via Terraform.
- US-1.2 Implement auth and role model in Cloud Run API.
- US-1.3 Secure signed upload paths with GCS and IAM.

