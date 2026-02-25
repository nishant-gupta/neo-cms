# neo-cms

## Documentation

- [Lightweight CMS Technical Design](./TECHNICAL_DESIGN.md)
- [V1 Execution Backlog](./V1_EXECUTION_BACKLOG.md)
- [EPIC-1 / US-1.1 implementation notes](./docs/epics/EPIC-1-US-1.1.md)

## EPIC-1 progress

### US-1.1 Provision core GCP resources

Implemented baseline infrastructure artifacts:

- Terraform baseline in [`infra/terraform`](./infra/terraform/README.md)
- Firestore collection bootstrap script in
  [`scripts/firestore_migrations/bootstrap_collections.py`](./scripts/firestore_migrations/bootstrap_collections.py)
- Dev apply helper in [`scripts/deploy/dev_apply.sh`](./scripts/deploy/dev_apply.sh)