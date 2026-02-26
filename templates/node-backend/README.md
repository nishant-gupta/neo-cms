# Minimal Node Backend Template

Production-ready starter for the neo-cms backend on Cloud Run.

## Stack

- Node.js 20 + TypeScript
- Fastify API server
- Zod validation
- Pino structured logging
- Google Cloud SDK clients (Storage, Firestore, Cloud Tasks)

## Included production basics

- Security middleware (`@fastify/helmet`)
- CORS support (`@fastify/cors`)
- Google OAuth ID token verification support (`google-auth-library`)
- Role-based access controls for `editor`, `publisher`, `admin`
- Health and readiness endpoints (`/healthz`, `/readyz`)
- Centralized error and not-found handlers
- Graceful shutdown on `SIGTERM`/`SIGINT`
- Dockerfile for Cloud Run deployment
- Basic automated tests with Vitest

## Quickstart

```bash
npm install
cp .env.example .env
npm run dev
```

## Build and run

```bash
npm run build
npm start
```

## Test

```bash
npm test
```

## API endpoints (starter)

- `GET /healthz`
- `GET /readyz`
- `GET /api/v1/auth/me` (requires `editor+`)
- `GET /api/v1/admin/access-check` (requires `admin`)
- `POST /api/v1/assets/signed-upload-url` (requires `editor+`)

Example request body:

```json
{
  "mimeType": "image/png",
  "originalFileName": "hero.png"
}
```

## Authentication and roles

Protected endpoints require `Authorization: Bearer <token>`.

- `AUTH_MODE=google`:
  - verifies Google ID tokens via OAuth2
  - enforces role mapping from email lists (`RBAC_*_EMAILS`)
- `AUTH_MODE=mock` (default outside production):
  - use mock bearer token format: `Bearer mock:user@example.com`
  - useful for local development and automated tests

Typical role policy:
- Editors: upload assets, create and edit drafts
- Publishers: editor permissions + publish actions
- Admins: full access

## Cloud Run container

```bash
docker build -t neo-cms-api-template .
docker run -p 8080:8080 --env-file .env neo-cms-api-template
```

## Suggested next steps

1. Add page, revision, and publish endpoints from technical design.
2. Connect Cloud Tasks handlers for preview/publish jobs.
3. Add CI workflow for test/build/deploy.
4. Add Terraform provisioning for Firestore, Cloud Run, and Cloud Tasks.
