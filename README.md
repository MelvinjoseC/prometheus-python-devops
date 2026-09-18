# Prometheus Python Client

[![CI](https://github.com/MelvinjoseC/client_python/actions/workflows/ci.yaml/badge.svg)](https://github.com/MelvinjoseC/client_python/actions/workflows/ci.yaml)
[![CodeQL](https://github.com/MelvinjoseC/client_python/actions/workflows/codeql.yaml/badge.svg)](https://github.com/MelvinjoseC/client_python/actions/workflows/codeql.yaml)
[![Security Scan](https://github.com/MelvinjoseC/client_python/actions/workflows/security-scan.yaml/badge.svg)](https://github.com/MelvinjoseC/client_python/actions/workflows/security-scan.yaml)
[![Docker Publish](https://github.com/MelvinjoseC/client_python/actions/workflows/docker-publish.yaml/badge.svg)](https://github.com/MelvinjoseC/client_python/actions/workflows/docker-publish.yaml)
[![License](https://img.shields.io/badge/License-Apache_2.0_AND_BSD--2--Clause-blue.svg)](LICENSE)

The official Python client for [Prometheus](https://prometheus.io) monitoring system.

---

## Installation

```bash
pip install prometheus-client
```

This package is available on [PyPI](https://pypi.org/project/prometheus-client/).

---

## Quickstart

```python
from prometheus_client import start_http_server, Counter
import time

# Create a metric to track request count
REQUESTS = Counter('hello_requests_total', 'Total HTTP requests.')

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    print("Metrics server started at http://localhost:8000/metrics")
    
    # Generate some metric activity.
    while True:
        REQUESTS.inc()
        time.sleep(1)
```

---

## DevOps & Cloud-Native Observability

This repository includes enterprise-grade DevOps automation, containerization, and monitoring assets:

### 1. Local Observability Sandbox
Launch a complete local sandbox with the instrumented app, Prometheus, Grafana, and Alertmanager:

```bash
make compose-up
```

* **App & Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)
* **Prometheus UI**: [http://localhost:9090](http://localhost:9090)
* **Grafana Dashboard**: [http://localhost:3000](http://localhost:3000) (`admin` / `admin`)
* **Alertmanager UI**: [http://localhost:9093](http://localhost:9093)

### 2. Kubernetes & Helm Deployment
Deploy the instrumented microservice to Kubernetes with built-in `ServiceMonitor` CRD support:

```bash
helm upgrade --install prometheus-python-app ./charts/prometheus-python-app \
  --namespace monitoring-apps \
  --create-namespace
```

### 3. Architecture & Operational Runbooks
Refer to [DEVOPS.md](DEVOPS.md) for:
* End-to-end CI/CD architecture diagrams
* Multi-stage hardened Docker containerization guidelines
* Multiprocess mode in-memory tmpfs configuration
* Operational runbooks for incident response (`TargetDown`, `HighErrorRate`, `HighLatencyP99`, `ProcessHighMemoryUsage`)

---

## Documentation & Links

* **Documentation**: [https://prometheus.github.io/client_python](https://prometheus.github.io/client_python)
* **Releases & Changelog**: [GitHub Releases](https://github.com/MelvinjoseC/client_python/releases)
* **PyPI**: [https://pypi.org/project/prometheus-client](https://pypi.org/project/prometheus-client)
* **DevOps Guide**: [DEVOPS.md](DEVOPS.md)
