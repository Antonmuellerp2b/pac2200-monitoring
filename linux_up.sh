#!/bin/bash
set -e

# Render influxdb.yaml from template using .env
./render_influxdb_yaml.sh

# Start docker compose with any arguments passed to this script
exec docker-compose up "$@"