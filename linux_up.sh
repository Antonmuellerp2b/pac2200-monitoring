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

export MY_UID=$(id -u)   # stores the current user's UID in MY_UID
export MY_GID=$(id -g)   # stores the current user's GID in MY_GID

# Start Docker Compose
exec docker compose up "$@"
