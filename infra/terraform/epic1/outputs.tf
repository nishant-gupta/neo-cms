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
