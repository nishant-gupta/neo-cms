# EPIC-1 Terraform Baseline

This module provisions the EPIC-1 storage baseline with private-by-default buckets:

- `<prefix>-<env>-assets`
- `<prefix>-<env>-derivatives`
- `<prefix>-<env>-preview`
- `<prefix>-<env>-prod`

## Security defaults

All buckets are configured with:
- `uniform_bucket_level_access = true`
- `public_access_prevention = "enforced"`
- no public IAM bindings

This ensures uploads are only possible via authenticated workflows such as signed URLs from the backend.

## Usage

```bash
cd infra/terraform/epic1
terraform init
terraform plan -var="project_id=<your-gcp-project-id>" -var="environment=dev"
terraform apply -var="project_id=<your-gcp-project-id>" -var="environment=dev"
```

## Notes

- Use unique `name_prefix` per project/organization to avoid global GCS name collisions.
- Preview bucket includes a 30-day lifecycle cleanup rule for stale artifacts.
