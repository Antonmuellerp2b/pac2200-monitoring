#!/bin/bash
set -e

# Render influxdb.yaml from template using .env
./render_influxdb_yaml.sh

# Start docker compose with any arguments passed to this script
exec docker-compose up "$@"

# Change ownership of the grafana data directory to UID 472 (Grafana user)
# to avoid permission issues when running the Grafana Docker container
sudo chown -R 472:472 ./grafana