# EPIC-1 / US-1.1 - Provision core GCP resources

## Story

As a platform engineer, I want buckets, Firestore, Cloud Run, and Cloud Tasks provisioned so that feature implementation can begin.

## Implementation in this repository

- Terraform baseline: `infra/terraform/`
  - `main.tf` provisions:
    - 4 private buckets (`assets`, `derivatives`, `preview`, `prod`)
    - Firestore default database
    - Cloud Tasks queues
    - Cloud Run API and worker services in `dev`
  - `dev.tfvars.example` provides starter configuration.
- Firestore collection bootstrap script:
  - `scripts/firestore_migrations/bootstrap_collections.py`
  - Creates sentinel docs in `pages`, `assets`, and `revisions`
- Convenience deploy script:
  - `scripts/deploy/dev_apply.sh`

## Acceptance criteria mapping

- [x] Buckets created: assets, derivatives, preview, prod.
- [x] Firestore collections created or migration scripts ready.
- [x] Cloud Run services deployed to `dev` (via Terraform apply).
