#!/bin/bash
set -e

# Set permissions for the current user
[ "$(uname)" = "Linux" ] && sudo chown -R "$USER":"$USER" ./grafana || true

# Render influxdb.yaml from template using .env
./render_influxdb_yaml.sh

# Render contact-points.yaml from template using .env
./render_contact_points_yaml.sh

# Set permissions for Grafana data directory
[ "$(uname)" = "Linux" ] && sudo chown -R 472:472 ./grafana || true

# Start docker compose
exec docker-compose up "$@"
