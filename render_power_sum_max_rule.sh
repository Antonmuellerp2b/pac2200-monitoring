#!/bin/bash
# render_power_sum_max_rule.sh - Render Grafana power_sum_max_rule.yaml from template using .env variables.
# Usage: ./render_power_sum_max_rule.sh

set -eu

# Load .env variables from project root
if [ -f ".env" ]; then
  set -a
  . .env
  set +a
else
  echo ".env file not found in current directory" >&2
  exit 1
fi

TEMPLATE="grafana/provisioning/alerting/power_sum_max.yaml.template"
OUTPUT="grafana/provisioning/alerting/power_sum_max_rule.yaml"

# Check required variables
: "${DATASOURCE_UID:?DATASOURCE_UID not set in .env!}"
: "${INFLUXDB_BUCKET:?INFLUXDB_BUCKET not set in .env!}"
: "${TOTAL_POWER_THRESHOLD_KW:?TOTAL_POWER_THRESHOLD_KW not set in .env!}"

# Create output directory if it does not exist
mkdir -p "$(dirname "$OUTPUT")"

# Replace placeholders in template with environment variables, skip comment lines
grep -v '^#' "$TEMPLATE" | sed \
  -e "s|{{DATASOURCE_UID}}|$DATASOURCE_UID|g" \
  -e "s|{{INFLUXDB_BUCKET}}|$INFLUXDB_BUCKET|g" \
  -e "s|{{TOTAL_POWER_THRESHOLD_KW}}|$TOTAL_POWER_THRESHOLD_KW|g" \
  > "$OUTPUT"

echo "Rendered $OUTPUT with DATASOURCE_UID=$DATASOURCE_UID, INFLUXDB_BUCKET=$INFLUXDB_BUCKET, TOTAL_POWER_THRESHOLD_KW=$TOTAL_POWER_THRESHOLD_KW"
