#!/bin/bash
set -e

# Load variables from .env file
source .env

TEMPLATE="grafana/provisioning/alerting/power_sum_max.yaml.template"
OUTPUT="grafana/provisioning/alerting/power_sum_max_rule.yaml"

# Create output directory if it does not exist
mkdir -p "$(dirname "$OUTPUT")"

# Replace placeholders in template with environment variables
sed \
  -e "s|{{DATASOURCE_UID}}|$DATASOURCE_UID|g" \
  -e "s|{{INFLUXDB_BUCKET}}|$INFLUXDB_BUCKET|g" \
  -e "s|{{TOTAL_POWER_THRESHOLD_KW}}|$TOTAL_POWER_THRESHOLD_KW|g" \
  "$TEMPLATE" > "$OUTPUT"

echo "✅ Alert rule rendered to $OUTPUT"
