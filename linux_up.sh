#!/bin/bash
# linux_up.sh - Start PAC2200 stack on Linux as non-root user
# Usage: ./linux_up.sh [docker-compose args]

set -eu

# Render all required YAML/config files
./render_influxdb_yaml.sh
./render_contact_points_yaml.sh
./render_power_imbalance_rule.sh
./render_power_sum_max_rule.sh
./render_telegraf.conf.template.sh

# Export UID/GID for non-root Grafana
export MY_UID=$(id -u)
export MY_GID=$(id -g)

# Start Docker Compose
exec docker compose up "$@"
