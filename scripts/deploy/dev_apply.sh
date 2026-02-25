#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TF_DIR="${ROOT_DIR}/infra/terraform"
TFVARS_FILE="${TFVARS_FILE:-${TF_DIR}/dev.tfvars}"

if [[ ! -f "${TFVARS_FILE}" ]]; then
  echo "Missing tfvars file: ${TFVARS_FILE}" >&2
  echo "Copy infra/terraform/dev.tfvars.example to infra/terraform/dev.tfvars and fill values." >&2
  exit 1
fi

if [[ -z "${PROJECT_ID:-}" ]]; then
  echo "PROJECT_ID is required for Firestore bootstrap." >&2
  echo "Example: PROJECT_ID=my-project-id scripts/deploy/dev_apply.sh" >&2
  exit 1
fi

terraform -chdir="${TF_DIR}" init
terraform -chdir="${TF_DIR}" plan -var-file="${TFVARS_FILE}"
terraform -chdir="${TF_DIR}" apply -var-file="${TFVARS_FILE}" -auto-approve

python3 "${ROOT_DIR}/scripts/firestore_migrations/bootstrap_collections.py" --project-id "${PROJECT_ID}"

echo "US-1.1 baseline apply completed for project ${PROJECT_ID}."
