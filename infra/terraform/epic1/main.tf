terraform {
  required_version = ">= 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  base_name = "${var.name_prefix}-${var.environment}"
  required_services = toset([
    "cloudtasks.googleapis.com",
    "firestore.googleapis.com",
    "iam.googleapis.com",
    "run.googleapis.com"
  ])
  cloud_run_service_account_roles = toset([
    "roles/cloudtasks.enqueuer",
    "roles/datastore.user",
    "roles/logging.logWriter",
    "roles/storage.objectAdmin"
  ])
  labels = merge(
    {
      managed_by = "terraform"
      epic       = "epic-1"
      env        = var.environment
    },
    var.labels
  )
}

resource "google_project_service" "required" {
  for_each = local.required_services

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_storage_bucket" "assets" {
  name                        = "${local.base_name}-assets"
  location                    = var.bucket_location
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  labels                      = local.labels

  versioning {
    enabled = true
  }

  depends_on = [google_project_service.required]
}

resource "google_storage_bucket" "derivatives" {
  name                        = "${local.base_name}-derivatives"
  location                    = var.bucket_location
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  labels                      = local.labels

  versioning {
    enabled = true
  }

  depends_on = [google_project_service.required]
}

resource "google_storage_bucket" "preview" {
  name                        = "${local.base_name}-preview"
  location                    = var.bucket_location
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  labels                      = local.labels

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.required]
}

resource "google_storage_bucket" "prod" {
  name                        = "${local.base_name}-prod"
  location                    = var.bucket_location
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  labels                      = local.labels

  versioning {
    enabled = true
  }

  depends_on = [google_project_service.required]
}

resource "google_firestore_database" "default" {
  count = var.create_firestore_database ? 1 : 0

  project                     = var.project_id
  name                        = "(default)"
  location_id                 = var.firestore_location
  type                        = "FIRESTORE_NATIVE"
  app_engine_integration_mode = "DISABLED"
  concurrency_mode            = "OPTIMISTIC"

  lifecycle {
    prevent_destroy = true
  }

  depends_on = [google_project_service.required]
}

resource "google_cloud_tasks_queue" "build_preview" {
  name     = "${local.base_name}-build-preview"
  location = var.region

  rate_limits {
    max_concurrent_dispatches = 5
    max_dispatches_per_second = 10
  }

  retry_config {
    max_attempts = 5
  }

  depends_on = [google_project_service.required]
}

resource "google_cloud_tasks_queue" "build_prod" {
  name     = "${local.base_name}-build-prod"
  location = var.region

  rate_limits {
    max_concurrent_dispatches = 2
    max_dispatches_per_second = 4
  }

  retry_config {
    max_attempts = 5
  }

  depends_on = [google_project_service.required]
}

resource "google_cloud_tasks_queue" "process_asset" {
  name     = "${local.base_name}-process-asset"
  location = var.region

  rate_limits {
    max_concurrent_dispatches = 10
    max_dispatches_per_second = 20
  }

  retry_config {
    max_attempts = 5
  }

  depends_on = [google_project_service.required]
}

resource "google_service_account" "cloud_run_runtime" {
  account_id   = "${var.name_prefix}-${var.environment}-run"
  display_name = "Cloud Run runtime (${var.environment})"

  depends_on = [google_project_service.required]
}

resource "google_project_iam_member" "cloud_run_runtime_roles" {
  for_each = local.cloud_run_service_account_roles

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloud_run_runtime.email}"
}

resource "google_cloud_run_v2_service" "api" {
  name     = "${local.base_name}-api"
  location = var.region
  ingress  = var.cloud_run_ingress

  deletion_protection = false

  template {
    service_account                  = google_service_account.cloud_run_runtime.email
    timeout                          = "${var.cloud_run_timeout_seconds}s"
    max_instance_request_concurrency = var.cloud_run_concurrency

    scaling {
      min_instance_count = var.cloud_run_min_instances
      max_instance_count = var.cloud_run_max_instances
    }

    containers {
      image = var.api_image

      resources {
        limits = {
          cpu    = var.cloud_run_cpu
          memory = var.cloud_run_memory
        }
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GCS_ASSETS_BUCKET"
        value = google_storage_bucket.assets.name
      }

      env {
        name  = "CLOUD_TASKS_QUEUE_BUILD_PREVIEW"
        value = google_cloud_tasks_queue.build_preview.name
      }

      env {
        name  = "CLOUD_TASKS_QUEUE_BUILD_PROD"
        value = google_cloud_tasks_queue.build_prod.name
      }

      env {
        name  = "CLOUD_TASKS_QUEUE_PROCESS_ASSET"
        value = google_cloud_tasks_queue.process_asset.name
      }
    }
  }

  depends_on = [google_project_iam_member.cloud_run_runtime_roles]
}

resource "google_cloud_run_v2_service_iam_member" "api_public_invoker" {
  count = var.allow_unauthenticated_api ? 1 : 0

  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service" "worker" {
  name     = "${local.base_name}-worker"
  location = var.region
  ingress  = var.cloud_run_ingress

  deletion_protection = false

  template {
    service_account                  = google_service_account.cloud_run_runtime.email
    timeout                          = "${var.cloud_run_timeout_seconds}s"
    max_instance_request_concurrency = var.cloud_run_concurrency

    scaling {
      min_instance_count = 0
      max_instance_count = var.cloud_run_max_instances
    }

    containers {
      image = var.worker_image

      resources {
        limits = {
          cpu    = var.cloud_run_cpu
          memory = var.cloud_run_memory
        }
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
    }
  }

  depends_on = [google_project_iam_member.cloud_run_runtime_roles]
}

resource "google_cloud_run_v2_service_iam_member" "worker_public_invoker" {
  count = var.allow_unauthenticated_worker ? 1 : 0

  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.worker.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
