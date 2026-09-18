"""
Gunicorn configuration for multi-worker Prometheus multiprocess metrics collection.
Ensures worker pid metrics are cleaned up on worker termination to avoid metric bloat.
"""

import os
from prometheus_client import multiprocess

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = int(os.getenv("WORKERS", "4"))
worker_class = "sync"
timeout = 30
keepalive = 2


def child_exit(server, worker):
    """
    Called just after a worker exited, in the master process.
    Cleans up memory-mapped metrics files for dead worker processes.
    """
    multiprocess.mark_process_dead(worker.pid)
