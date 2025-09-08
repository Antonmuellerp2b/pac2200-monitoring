#!/bin/bash
# linux_up.sh - Universal script to start PAC2200 stack on Linux
# Handles permissions for Grafana and chooses the correct Docker Compose command.
# Usage: ./linux_up.sh [docker-compose-args...]

set -eu

# Detect which Docker Compose command to use
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "Error: neither docker-compose nor docker compose found."
    exit 1
fi

echo "Using $COMPOSE_CMD"

# Set permissions for Grafana directory to current user
if [ "$(uname)" = "Linux" ]; then
    echo "Setting Grafana directories ownership to $USER"
    sudo chown -R "$USER":"$USER" ./grafana
fi

# Render all required YAML files from templates
./render_influxdb_yaml.sh
./render_contact_points.sh
./render_power_imbalance_rule.sh
./render_power_sum_max_rule.sh

# Ensure Grafana data directory is writable by Grafana user (472:472)
if [ "$(uname)" = "Linux" ]; then
    echo "Setting Grafana data directory ownership to 472:472"
    sudo chown -R 472:472 ./grafana
fi

# Start Docker Compose with any arguments passed to the script
exec $COMPOSE_CMD up -d "$@"
