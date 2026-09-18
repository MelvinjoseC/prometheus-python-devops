# Terraform Infrastructure as Code for Prometheus-Instrumented Python Apps

resource "kubernetes_namespace" "apps" {
  metadata {
    name = var.namespace
    labels = {
      name                                  = var.namespace
      "pod-security.kubernetes.io/enforce" = "restricted"
    }
  }
}

resource "kubernetes_config_map" "app_config" {
  metadata {
    name      = "prometheus-python-config"
    namespace = kubernetes_namespace.apps.metadata[0].name
  }

  data = {
    APP_ENV = var.environment
    PORT    = tostring(var.app_port)
  }
}

resource "kubernetes_deployment" "app" {
  metadata {
    name      = "prometheus-python-app"
    namespace = kubernetes_namespace.apps.metadata[0].name
    labels = {
      "app.kubernetes.io/name" = "prometheus-python-app"
      "app.kubernetes.io/env"  = var.environment
    }
  }

  spec {
    replicas = var.replica_count

    selector {
      match_labels = {
        "app.kubernetes.io/name" = "prometheus-python-app"
      }
    }

    template {
      metadata {
        labels = {
          "app.kubernetes.io/name" = "prometheus-python-app"
        }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = tostring(var.app_port)
          "prometheus.io/path"   = "/metrics"
        }
      }

      spec {
        container {
          name  = "app"
          image = "${var.image_repository}:${var.image_tag}"

          port {
            name           = "http"
            container_port = var.app_port
          }

          port {
            name           = "metrics"
            container_port = var.app_port
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.app_config.metadata[0].name
            }
          }

          dynamic "env" {
            for_each = var.enable_multiprocess ? [1] : []
            content {
              name  = "PROMETHEUS_MULTIPROC_DIR"
              value = "/tmp/metrics"
            }
          }

          dynamic "volume_mount" {
            for_each = var.enable_multiprocess ? [1] : []
            content {
              name       = "multiproc-metrics"
              mount_path = "/tmp/metrics"
            }
          }

          resources {
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
          }

          liveness_probe {
            http_get {
              path = "/healthz"
              port = "http"
            }
            initial_delay_seconds = 10
            period_seconds        = 10
          }

          readiness_probe {
            http_get {
              path = "/ready"
              port = "http"
            }
            initial_delay_seconds = 5
            period_seconds        = 5
          }
        }

        dynamic "volume" {
          for_each = var.enable_multiprocess ? [1] : []
          content {
            name = "multiproc-metrics"
            empty_dir {
              medium     = "Memory"
              size_limit = "128Mi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "app_service" {
  metadata {
    name      = "prometheus-python-service"
    namespace = kubernetes_namespace.apps.metadata[0].name
    labels = {
      "app.kubernetes.io/name" = "prometheus-python-app"
    }
  }

  spec {
    selector = {
      "app.kubernetes.io/name" = "prometheus-python-app"
    }

    port {
      name        = "http"
      port        = var.app_port
      target_port = "http"
    }

    port {
      name        = "metrics"
      port        = 9090
      target_port = "metrics"
    }

    type = "ClusterIP"
  }
}
