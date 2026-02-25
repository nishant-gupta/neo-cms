locals {
  name_prefix = "${var.resource_prefix}-${var.environment}"

  required_services = toset([
    "artifactregistry.googleapis.com",
    "cloudtasks.googleapis.com",
    "firestore.googleapis.com",
    "iam.googleapis.com",
    "run.googleapis.com",
    "storage.googleapis.com",
  ])

  bucket_names = {
    assets      = "${local.name_prefix}-assets"
    derivatives = "${local.name_prefix}-derivatives"
    preview     = "${local.name_prefix}-preview"
    prod        = "${local.name_prefix}-prod"
  }

  runtime_roles = toset([
    "roles/cloudtasks.enqueuer",
    "roles/datastore.user",
    "roles/storage.objectAdmin",
  ])
}

resource "google_project_service" "required" {
  for_each = local.required_services

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_storage_bucket" "core" {
  for_each = local.bucket_names

  project                     = var.project_id
  name                        = each.value
  location                    = var.bucket_location
  storage_class               = "STANDARD"
  force_destroy               = false
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  depends_on = [google_project_service.required["storage.googleapis.com"]]
}

resource "google_firestore_database" "default" {
  count = var.create_firestore_database ? 1 : 0

  project     = var.project_id
  name        = "(default)"
  location_id = var.firestore_location
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.required["firestore.googleapis.com"]]
}

resource "google_cloud_tasks_queue" "preview_builds" {
  project  = var.project_id
  location = var.region
  name     = "${local.name_prefix}-preview-builds"

  rate_limits {
    max_concurrent_dispatches = 20
    max_dispatches_per_second = 10
  }

  retry_config {
    max_attempts = 5
  }

  depends_on = [google_project_service.required["cloudtasks.googleapis.com"]]
}

resource "google_cloud_tasks_queue" "asset_processing" {
  project  = var.project_id
  location = var.region
  name     = "${local.name_prefix}-asset-processing"

  rate_limits {
    max_concurrent_dispatches = 10
    max_dispatches_per_second = 5
  }

  retry_config {
    max_attempts = 5
  }

  depends_on = [google_project_service.required["cloudtasks.googleapis.com"]]
}

resource "google_service_account" "cloud_run_runtime" {
  project      = var.project_id
  account_id   = "${var.resource_prefix}-${var.environment}-run"
  display_name = "CMS ${var.environment} Cloud Run runtime"

  depends_on = [google_project_service.required["iam.googleapis.com"]]
}

resource "google_project_iam_member" "runtime_roles" {
  for_each = local.runtime_roles

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloud_run_runtime.email}"
}

resource "google_cloud_run_v2_service" "api" {
  project             = var.project_id
  location            = var.region
  name                = "${local.name_prefix}-api"
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloud_run_runtime.email
    timeout         = "300s"

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    containers {
      image = var.api_image

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "APP_ENV"
        value = var.environment
      }
    }
  }

  depends_on = [google_project_service.required["run.googleapis.com"]]
}

resource "google_cloud_run_v2_service" "worker" {
  project             = var.project_id
  location            = var.region
  name                = "${local.name_prefix}-worker"
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    service_account = google_service_account.cloud_run_runtime.email
    timeout         = "900s"

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    containers {
      image = var.worker_image

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }

      env {
        name  = "APP_ENV"
        value = var.environment
      }

      env {
        name  = "PREVIEW_QUEUE"
        value = google_cloud_tasks_queue.preview_builds.name
      }

      env {
        name  = "ASSET_QUEUE"
        value = google_cloud_tasks_queue.asset_processing.name
      }
    }
  }

  depends_on = [google_project_service.required["run.googleapis.com"]]
}
