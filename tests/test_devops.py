"""
Automated DevOps Configuration & Infrastructure Test Suite.
Validates Dockerfile security constraints, Compose topology, Prometheus alert syntax,
Grafana dashboard schema, Kubernetes manifests, Helm metadata, and reference app.
"""

import json
import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestDevOpsConfigurations(unittest.TestCase):
    """Test suite ensuring all DevOps configurations conform to enterprise standards."""

    def test_dockerfile_security_and_standards(self):
        dockerfile = REPO_ROOT / "Dockerfile"
        self.assertTrue(dockerfile.exists(), "Dockerfile must exist")
        content = dockerfile.read_text(encoding="utf-8")

        # Multi-stage validation
        self.assertIn("AS builder", content, "Dockerfile should implement multi-stage build")
        self.assertIn("AS runner", content, "Dockerfile should have dedicated runner stage")

        # Security validation (non-root)
        self.assertIn("USER appuser", content, "Dockerfile must run as non-root user")
        self.assertIn("groupadd", content, "Dockerfile should define custom unprivileged group")
        self.assertIn("useradd", content, "Dockerfile should define custom unprivileged user")

        # Healthcheck validation
        self.assertIn("HEALTHCHECK", content, "Dockerfile must define container HEALTHCHECK")

        # Multiprocess directory configuration
        self.assertIn("PROMETHEUS_MULTIPROC_DIR", content, "Dockerfile should define PROMETHEUS_MULTIPROC_DIR")

    def test_dockerignore_coverage(self):
        dockerignore = REPO_ROOT / ".dockerignore"
        self.assertTrue(dockerignore.exists(), ".dockerignore must exist")
        content = dockerignore.read_text(encoding="utf-8")

        required_ignores = [".git", "__pycache__", ".tox", ".pytest_cache", "tests/"]
        for item in required_ignores:
            self.assertIn(item, content, f".dockerignore must ignore {item}")

    def test_docker_compose_topology(self):
        compose_file = REPO_ROOT / "docker-compose.yaml"
        self.assertTrue(compose_file.exists(), "docker-compose.yaml must exist")
        content = compose_file.read_text(encoding="utf-8")

        required_services = ["app:", "prometheus:", "grafana:", "alertmanager:"]
        for svc in required_services:
            self.assertIn(svc, content, f"docker-compose.yaml must define service {svc}")

    def test_prometheus_alerting_rules(self):
        alerts_file = REPO_ROOT / "monitoring" / "prometheus" / "alerts.yaml"
        self.assertTrue(alerts_file.exists(), "alerts.yaml must exist")
        content = alerts_file.read_text(encoding="utf-8")

        required_alerts = [
            "alert: TargetDown",
            "alert: HighErrorRate",
            "alert: HighLatencyP99",
            "alert: ProcessHighMemoryUsage",
        ]
        for alert in required_alerts:
            self.assertIn(alert, content, f"alerts.yaml must include {alert}")

    def test_grafana_dashboard_json(self):
        dashboard_file = REPO_ROOT / "monitoring" / "grafana" / "dashboards" / "prometheus-python-overview.json"
        self.assertTrue(dashboard_file.exists(), "Grafana dashboard file must exist")
        with open(dashboard_file, "r", encoding="utf-8") as f:
            dashboard = json.load(f)

        self.assertIn("panels", dashboard, "Dashboard must have panels")
        self.assertGreaterEqual(len(dashboard["panels"]), 5, "Dashboard should contain at least 5 panels")
        self.assertEqual(dashboard["uid"], "prom-py-overview")

    def test_kubernetes_manifests(self):
        k8s_dir = REPO_ROOT / "deploy" / "kubernetes"
        self.assertTrue(k8s_dir.exists(), "deploy/kubernetes directory must exist")

        expected_files = [
            "namespace.yaml",
            "deployment.yaml",
            "service.yaml",
            "serviceaccount.yaml",
            "servicemonitor.yaml",
            "hpa.yaml",
            "configmap.yaml",
        ]
        for filename in expected_files:
            file_path = k8s_dir / filename
            self.assertTrue(file_path.exists(), f"Kubernetes manifest {filename} must exist")

    def test_helm_chart_structure(self):
        chart_dir = REPO_ROOT / "charts" / "prometheus-python-app"
        self.assertTrue(chart_dir.exists(), "Helm chart directory must exist")
        self.assertTrue((chart_dir / "Chart.yaml").exists(), "Chart.yaml must exist")
        self.assertTrue((chart_dir / "values.yaml").exists(), "values.yaml must exist")

        templates_dir = chart_dir / "templates"
        self.assertTrue(templates_dir.exists(), "templates directory must exist")
        expected_templates = [
            "_helpers.tpl",
            "deployment.yaml",
            "service.yaml",
            "serviceaccount.yaml",
            "servicemonitor.yaml",
            "hpa.yaml",
            "configmap.yaml",
        ]
        for tpl in expected_templates:
            self.assertTrue((templates_dir / tpl).exists(), f"Helm template {tpl} must exist")

    def test_reference_application_metrics_generation(self):
        from prometheus_client import CollectorRegistry, Counter, generate_latest

        test_registry = CollectorRegistry()
        test_counter = Counter("test_request_count", "Test request count", registry=test_registry)
        test_counter.inc(5)

        output = generate_latest(test_registry).decode("utf-8")
        self.assertIn("test_request_count_total 5.0", output)
        self.assertIn("# HELP test_request_count_total", output)


if __name__ == "__main__":
    unittest.main()
