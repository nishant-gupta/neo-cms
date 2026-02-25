# EPIC-1 / US-1.1 Terraform Baseline

This module provisions the core Google Cloud baseline required by EPIC-1 US-1.1.

## What gets provisioned

- Four private GCS buckets:
  - `<prefix>-<env>-assets`
  - `<prefix>-<env>-derivatives`
  - `<prefix>-<env>-preview`
  - `<prefix>-<env>-prod`
- Firestore default database (`FIRESTORE_NATIVE`)
- Cloud Tasks queues:
  - `<prefix>-<env>-preview-builds`
  - `<prefix>-<env>-asset-processing`
- Cloud Run services in `dev`:
  - `<prefix>-<env>-api`
  - `<prefix>-<env>-worker`

## Prerequisites

- Terraform `>= 1.6`
- `gcloud` authenticated to the target project
- Required IAM permissions to create storage, Firestore, Cloud Run, and Cloud Tasks resources

## Usage

```bash
cd infra/terraform
cp dev.tfvars.example dev.tfvars
# Edit dev.tfvars values
terraform init
terraform plan -var-file="dev.tfvars"
terraform apply -var-file="dev.tfvars"
```

If the target project already has a default Firestore database, set:

```hcl
create_firestore_database = false
```

## Firestore collection bootstrap

After the database exists, initialize core collections with:

```bash
python3 scripts/firestore_migrations/bootstrap_collections.py --project-id "<your-gcp-project-id>"
```

Run from repository root.
