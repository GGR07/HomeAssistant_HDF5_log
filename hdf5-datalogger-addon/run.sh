#!/usr/bin/with-contenv bashio
set -euo pipefail

bashio::log.info "Starting HDF5 DataLogger add-on"
exec python3 /app/main.py
