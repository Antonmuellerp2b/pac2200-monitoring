#!/bin/bash
# linux_up.sh - Universal script to start PAC2200 stack on Linux
# Handles permissions for Grafana and chooses the correct Docker Compose command.
# Usage: ./linux_up.sh [docker-compose-args...]

set -eu

# Set permissions for Grafana directory to current user
if [ "$(uname)" = "Linux" ]; then
    echo "Setting Grafana directories ownership to $USER"
    sudo chown -R "$USER":"$USER" ./grafana
fi

# Render all required YAML files from templates
./render_influxdb_yaml.sh
./render_contact_points_yaml.sh
./render_power_imbalance_rule.sh
./render_power_sum_max_rule.sh

# Make Grafana directories writable by everyone
if [ "$(uname)" = "Linux" ]; then
    echo "Setting Grafana directories writable by all users"
    chmod -R a+rwX ./grafana
fi

# Start docker compose
exec docker compose up "$@"