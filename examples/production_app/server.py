"""
Production Reference Microservice Instrumented with Prometheus Python Client.
Demonstrates standard and multiprocess metrics exposition, custom histograms,
gauges, counters, health probes, and error tracking.
"""

import http.server
import json
import os
import random
import sys
import time
from urllib.parse import urlparse

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
    multiprocess,
)

# Detect if running in multiprocess mode
IS_MULTIPROC = "PROMETHEUS_MULTIPROC_DIR" in os.environ

if IS_MULTIPROC:
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
else:
    from prometheus_client import REGISTRY as registry

# Business & Infrastructure Metrics
APP_INFO = Info("app_build", "Application build and runtime metadata")
APP_INFO.info({
    "version": "1.0.0",
    "environment": os.getenv("APP_ENV", "production"),
    "python_version": sys.version.split()[0],
})

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total count of HTTP requests handled by the service",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

HTTP_REQUESTS_IN_FLIGHT = Gauge(
    "http_requests_in_flight",
    "Current number of HTTP requests being actively processed",
    multiprocess_mode="livesum" if IS_MULTIPROC else "all",
)

APP_EXCEPTIONS_TOTAL = Counter(
    "app_exceptions_total",
    "Total count of unhandled exceptions caught by handler",
    ["exception_type"],
)


class InstrumentedHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler with automated Prometheus instrumentation."""

    def log_message(self, format, *args):
        # Override standard noisy server logging with clean stdout output
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")
        sys.stdout.flush()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        method = "GET"
        start_time = time.perf_counter()

        HTTP_REQUESTS_IN_FLIGHT.inc()
        status_code = 200

        try:
            if path == "/metrics":
                data = generate_latest(registry)
                self.send_response(200)
                self.send_header("Content-Type", CONTENT_TYPE_LATEST)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

            elif path == "/healthz":
                body = json.dumps({"status": "healthy"}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            elif path == "/ready":
                body = json.dumps({"status": "ready"}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            elif path == "/api/data":
                # Simulate business computation with latency and 5% simulated error
                simulated_delay = random.uniform(0.01, 0.08)
                time.sleep(simulated_delay)

                if random.random() < 0.05:
                    status_code = 500
                    APP_EXCEPTIONS_TOTAL.labels(exception_type="SimulatedDatabaseTimeout").inc()
                    body = json.dumps({"error": "Internal database timeout"}).encode("utf-8")
                else:
                    body = json.dumps({
                        "message": "Data retrieved successfully",
                        "records": random.randint(10, 100),
                    }).encode("utf-8")

                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            else:
                body = json.dumps({
                    "service": "prometheus-python-sample",
                    "endpoints": ["/metrics", "/healthz", "/ready", "/api/data"],
                }).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        except Exception as exc:
            status_code = 500
            APP_EXCEPTIONS_TOTAL.labels(exception_type=type(exc).__name__).inc()
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error": "Internal Server Error"}')

        finally:
            duration = time.perf_counter() - start_time
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=path).observe(duration)
            HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=path, status=str(status_code)).inc()
            HTTP_REQUESTS_IN_FLIGHT.dec()


def run_server(port: int = 8000):
    server_address = ("", port)
    httpd = http.server.HTTPServer(server_address, InstrumentedHandler)
    print(f"Starting instrumented server on port {port} (multiprocess={IS_MULTIPROC})...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully.")
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    run_server(port)
