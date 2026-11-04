#!/usr/bin/env bash
set -euo pipefail

export ENVIRONMENT="production"
export PORT="8000"

log_info() {
  echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] [INFO] $1"
}

start_application() {
  log_info "Initializing CloudSphere Service on port ${PORT}..."
  python -m server
}

start_application
