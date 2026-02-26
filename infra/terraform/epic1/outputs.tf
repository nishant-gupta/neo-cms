output "assets_bucket_name" {
  description = "GCS bucket for original uploads"
  value       = google_storage_bucket.assets.name
}

output "derivatives_bucket_name" {
  description = "GCS bucket for transformed assets"
  value       = google_storage_bucket.derivatives.name
}

output "preview_bucket_name" {
  description = "GCS bucket for preview artifacts"
  value       = google_storage_bucket.preview.name
}

output "prod_bucket_name" {
  description = "GCS bucket for production artifacts"
  value       = google_storage_bucket.prod.name
}

output "cloud_run_runtime_service_account_email" {
  description = "Service account used by Cloud Run API/worker services"
  value       = google_service_account.cloud_run_runtime.email
}

output "api_service_name" {
  description = "Cloud Run API service name"
  value       = google_cloud_run_v2_service.api.name
}

output "api_service_uri" {
  description = "Cloud Run API service URI"
  value       = google_cloud_run_v2_service.api.uri
}

output "worker_service_name" {
  description = "Cloud Run worker service name"
  value       = google_cloud_run_v2_service.worker.name
}

output "worker_service_uri" {
  description = "Cloud Run worker service URI"
  value       = google_cloud_run_v2_service.worker.uri
}

output "cloud_tasks_queue_build_preview" {
  description = "Cloud Tasks queue for preview builds"
  value       = google_cloud_tasks_queue.build_preview.name
}

output "cloud_tasks_queue_build_prod" {
  description = "Cloud Tasks queue for production builds"
  value       = google_cloud_tasks_queue.build_prod.name
}

output "cloud_tasks_queue_process_asset" {
  description = "Cloud Tasks queue for asset processing"
  value       = google_cloud_tasks_queue.process_asset.name
}

output "firestore_database_name" {
  description = "Firestore database name when created by this module"
  value       = length(google_firestore_database.default) > 0 ? google_firestore_database.default[0].name : null
}
