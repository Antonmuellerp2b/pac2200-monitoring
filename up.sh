#!/bin/zsh
set -e

# Render influxdb.yaml from template using .env
./render_influxdb_yaml.sh

# Render contact-points.yaml from template using .env
./render_contact_points_yaml.sh

# Start docker compose with any arguments passed to this script
exec docker compose up "$@"