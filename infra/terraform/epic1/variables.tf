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
