output "bucket_names" {
  description = "Core CMS bucket names by functional purpose."
  value       = { for key, bucket in google_storage_bucket.core : key => bucket.name }
}

output "firestore_database" {
  description = "Firestore database metadata."
  value = var.create_firestore_database ? {
    name        = google_firestore_database.default[0].name
    location_id = google_firestore_database.default[0].location_id
    type        = google_firestore_database.default[0].type
  } : {
    name        = "(default)"
    location_id = var.firestore_location
    type        = "FIRESTORE_NATIVE"
  }
}

output "cloud_run_services" {
  description = "Cloud Run service names for the dev baseline."
  value = {
    api    = google_cloud_run_v2_service.api.name
    worker = google_cloud_run_v2_service.worker.name
  }
}

output "cloud_tasks_queues" {
  description = "Cloud Tasks queue names."
  value = {
    preview_builds   = google_cloud_tasks_queue.preview_builds.name
    asset_processing = google_cloud_tasks_queue.asset_processing.name
  }
}
