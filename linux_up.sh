#!/bin/bash
# linux_up.sh - Start PAC2200 stack on Linux, ensuring correct permissions for Grafana.
# Renders all needed config files and starts docker compose.
# Usage: ./linux_up.sh [docker-compose-args...]

set -eu

# Set permissions for the current user (Linux only)
if [ "$(uname)" = "Linux" ]; then
  sudo chown -R "$USER":"$USER" ./grafana
fi

# Render influxdb.yaml from template using .env
./render_influxdb_yaml.sh

# Render contact-points.yaml from template using .env
./render_contact_points_yaml.sh

# Render power_imbalance_rule.yaml from template using .env
./render_power_imbalance_rule.sh

# Render power_sum_max_rule.yaml from template using .env
./render_power_sum_max_rule.sh

# Set permissions for Grafana data directory (Linux only)
if [ "$(uname)" = "Linux" ]; then
  sudo chown -R 472:472 ./grafana
fi

# Start docker compose with any arguments passed to this script
exec docker compose up "$@"