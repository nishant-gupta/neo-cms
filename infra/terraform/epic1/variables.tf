variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for regional resources"
  type        = string
  default     = "us-central1"
}

variable "bucket_location" {
  description = "GCS bucket location (region or multi-region, e.g. US)"
  type        = string
  default     = "US"
}

variable "environment" {
  description = "Deployment environment (dev/staging/prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "name_prefix" {
  description = "Prefix used for naming resources"
  type        = string
  default     = "neo-cms"
}

variable "labels" {
  description = "Additional labels applied to resources"
  type        = map(string)
  default     = {}
}

variable "create_firestore_database" {
  description = "Whether to create the Firestore default database resource via Terraform."
  type        = bool
  default     = false
}

variable "firestore_location" {
  description = "Firestore location (for example: us-central, nam5, eur3)."
  type        = string
  default     = "us-central"
}

variable "api_image" {
  description = "Container image for the API Cloud Run service."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello:latest"
}

variable "worker_image" {
  description = "Container image for the worker Cloud Run service."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello:latest"
}

variable "allow_unauthenticated_api" {
  description = "Allow unauthenticated invocation for the API Cloud Run service."
  type        = bool
  default     = false
}

variable "allow_unauthenticated_worker" {
  description = "Allow unauthenticated invocation for the worker Cloud Run service."
  type        = bool
  default     = false
}

variable "cloud_run_ingress" {
  description = "Ingress setting for Cloud Run v2 services."
  type        = string
  default     = "INGRESS_TRAFFIC_ALL"
}

variable "cloud_run_timeout_seconds" {
  description = "Request timeout in seconds for Cloud Run services."
  type        = number
  default     = 300
}

variable "cloud_run_concurrency" {
  description = "Maximum concurrent requests per Cloud Run instance."
  type        = number
  default     = 80
}

variable "cloud_run_min_instances" {
  description = "Minimum instances for Cloud Run services."
  type        = number
  default     = 0
}

variable "cloud_run_max_instances" {
  description = "Maximum instances for Cloud Run services."
  type        = number
  default     = 5
}

variable "cloud_run_cpu" {
  description = "CPU limit for Cloud Run containers."
  type        = string
  default     = "1"
}

variable "cloud_run_memory" {
  description = "Memory limit for Cloud Run containers."
  type        = string
  default     = "512Mi"
}
