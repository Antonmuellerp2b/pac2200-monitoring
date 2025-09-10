#!/bin/zsh
# mac_up.sh - Start all services for PAC2200 monitoring stack.
# Renders all needed config files and starts docker compose.
# Usage: ./mac_up.sh [docker-compose-args...]

set -eu

# Render influxdb.yaml from template using .env
./render_influxdb_yaml.sh

# Render contact-points.yaml from template using .env
./render_contact_points_yaml.sh

# Render power_imbalance_rule.yaml from template using .env
./render_power_imbalance_rule.sh

# Render power_sum_max_rule.yaml from template using .env
./render_power_sum_max_rule.sh

# Start docker compose with any arguments passed to this script
exec docker compose up "$@"