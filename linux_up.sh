#!/bin/bash
# linux_up.sh - Universal script to start PAC2200 stack on Linux
# Handles permissions for Grafana
# Usage: ./linux_up.sh [docker-compose-args...]

set -eu

# Render all required YAML files from templates
./render_influxdb_yaml.sh
./render_contact_points_yaml.sh
./render_power_imbalance_rule.sh
./render_power_sum_max_rule.sh
./render_telegraf.conf.template.sh

# Start docker compose
exec docker compose up "$@"
