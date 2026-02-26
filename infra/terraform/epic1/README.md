# EPIC-1 Terraform Baseline

This module provisions the EPIC-1 platform baseline:

- `<prefix>-<env>-assets`
- `<prefix>-<env>-derivatives`
- `<prefix>-<env>-preview`
- `<prefix>-<env>-prod`
- Cloud Tasks queues for preview, publish, and asset processing
- Cloud Run API and worker services (dev/staging/prod naming)
- Cloud Run runtime service account + baseline IAM roles
- Optional Firestore default database provisioning

## Security defaults

All buckets are configured with:
- `uniform_bucket_level_access = true`
- `public_access_prevention = "enforced"`
- no public IAM bindings

This ensures uploads are only possible via authenticated workflows such as signed URLs from the backend.

Cloud Run services are private by default (`allow_unauthenticated_api=false`, `allow_unauthenticated_worker=false`).

## Usage

```bash
cd infra/terraform/epic1
cp dev.tfvars.example dev.tfvars
terraform init
terraform plan -var-file="dev.tfvars"
terraform apply -var-file="dev.tfvars"
```

If Firestore is not yet initialized in your project, include:

```bash
terraform apply \
  -var="project_id=<your-gcp-project-id>" \
  -var="environment=dev" \
  -var="create_firestore_database=true"
```

## Important variables

- `api_image`: Cloud Run API container image
- `worker_image`: Cloud Run worker container image
- `create_firestore_database`: create Firestore default DB when needed
- `allow_unauthenticated_api`: public API invoker toggle (default `false`)
- `allow_unauthenticated_worker`: public worker invoker toggle (default `false`)

## Notes

- Use unique `name_prefix` per project/organization to avoid global GCS name collisions.
- Preview bucket includes a 30-day lifecycle cleanup rule for stale artifacts.
- To deploy to `dev`, provide deployable API/worker images via `api_image` and `worker_image`.
