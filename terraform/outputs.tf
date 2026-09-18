output "namespace_name" {
  description = "Created Kubernetes namespace name"
  value       = kubernetes_namespace.apps.metadata[0].name
}

output "service_name" {
  description = "Kubernetes Service name"
  value       = kubernetes_service.app_service.metadata[0].name
}

output "metrics_port" {
  description = "Service port for scraping Prometheus metrics"
  value       = 9090
}

output "application_port" {
  description = "Service port for HTTP application requests"
  value       = var.app_port
}
