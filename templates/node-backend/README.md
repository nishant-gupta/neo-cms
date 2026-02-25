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
- `POST /api/v1/assets/signed-upload-url`

Example request body:

```json
{
  "mimeType": "image/png",
  "originalFileName": "hero.png"
}
```

## Cloud Run container

```bash
docker build -t neo-cms-api-template .
docker run -p 8080:8080 --env-file .env neo-cms-api-template
```

## Suggested next steps

1. Add auth middleware for Google OAuth and role checks.
2. Add page, revision, and publish endpoints from technical design.
3. Connect Cloud Tasks handlers for preview/publish jobs.
4. Add CI workflow for test/build/deploy.
