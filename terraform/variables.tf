variable "namespace" {
  description = "Target Kubernetes namespace for deployment"
  type        = string
  default     = "monitoring-apps"
}

variable "environment" {
  description = "Deployment environment (production, staging, sandbox)"
  type        = string
  default     = "production"
}

variable "replica_count" {
  description = "Number of application pod replicas"
  type        = number
  default     = 3
}

variable "image_repository" {
  description = "Container image repository URL"
  type        = string
  default     = "ghcr.io/melvinjosec/client_python"
}

variable "image_tag" {
  description = "Container image tag"
  type        = string
  default     = "latest"
}

variable "app_port" {
  description = "Port exposed by the application and metrics endpoint"
  type        = number
  default     = 8000
}

variable "enable_multiprocess" {
  description = "Enable multiprocess metrics aggregation via memory-mapped files"
  type        = bool
  default     = true
}
