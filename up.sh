#!/bin/zsh
set -e

# Render influxdb.yaml from template using .env
./grafana/provisioning/datasources/render_influxdb_yaml.sh

# Start docker compose with any arguments passed to this script
exec docker compose up "$@"