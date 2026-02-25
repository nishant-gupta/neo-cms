variable "project_id" {
  description = "GCP project ID where resources will be provisioned."
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "region" {
  description = "Default region for Cloud Run and Cloud Tasks."
  type        = string
  default     = "us-central1"
}

variable "bucket_location" {
  description = "Location for GCS buckets."
  type        = string
  default     = "US"
}

variable "firestore_location" {
  description = "Firestore location ID."
  type        = string
  default     = "us-central"
}

variable "create_firestore_database" {
  description = "Set false if the project already has a default Firestore database."
  type        = bool
  default     = true
}

variable "resource_prefix" {
  description = "Prefix used for named resources."
  type        = string
  default     = "cms"
}

variable "api_image" {
  description = "Container image for the CMS API Cloud Run service."
  type        = string
}

variable "worker_image" {
  description = "Container image for the CMS worker Cloud Run service."
  type        = string
}
