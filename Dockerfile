# Multi-stage production-ready Dockerfile for Prometheus Python Client Applications
# ==============================================================================

# Stage 1: Build stage
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build essentials if needed for binary extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment to isolate installed dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy library source and metadata
COPY pyproject.toml README.md LICENSE NOTICE /build/
COPY prometheus_client/ /build/prometheus_client/

# Build and install wheel
RUN pip install --upgrade pip && \
    pip install --no-cache-dir /build

# Stage 2: Minimal hardened runtime image
FROM python:3.12-slim AS runner

# Set standardized container environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PROMETHEUS_MULTIPROC_DIR="/tmp/metrics" \
    PORT=8000

# Install minimal runtime security updates
RUN apt-get update && apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /sbin/nologin -d /app appuser

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appgroup /opt/venv /opt/venv

# Prepare application and multiprocess metrics directories with non-root ownership
WORKDIR /app
RUN mkdir -p /app /tmp/metrics && \
    chown -R appuser:appgroup /app /tmp/metrics && \
    chmod 777 /tmp/metrics

# Copy application files (if any) or default entrypoint
COPY --chown=appuser:appgroup tools/simple_client.py /app/main.py

# Switch to non-root user
USER appuser:appgroup

# Health check using Python's standard library urllib
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + str(8000) + '/').read()" || exit 1

# Expose default HTTP server port
EXPOSE 8000

# Default entrypoint runs the python client server
ENTRYPOINT ["python", "/app/main.py"]
