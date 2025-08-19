#!/usr/bin/env bash
set -euo pipefail

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
TEMPLATE="$SCRIPT_DIR/grafana/provisioning/alerting/render_power_imbalance_rule.yaml.template"
OUTPUT="$SCRIPT_DIR/grafana/provisioning/alerting/render_power_imbalance_rule.yaml"

# .env laden
if [[ -f "$ENV_FILE" ]]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo ".env file not found at $ENV_FILE"
    exit 1
fi

# Prüfen, dass alle nötigen Variablen gesetzt sind
: "${THRESHOLD:?THRESHOLD not set in .env!}"
: "${MIN_PHASE_VALUE:?MIN_PHASE_VALUE not set in .env!}"
: "${DATASOURCE_UID:?DATASOURCE_UID not set in .env!}"
: "${INFLUXDB_BUCKET:?INFLUXDB_BUCKET not set in .env!}"

# Template rendern
sed \
    -e "s|{{THRESHOLD}}|$THRESHOLD|g" \
    -e "s|{{MIN_PHASE_VALUE}}|$MIN_PHASE_VALUE|g" \
    -e "s|{{DATASOURCE_UID}}|$DATASOURCE_UID|g" \
    -e "s|{{INFLUXDB_BUCKET}}|$INFLUXDB_BUCKET|g" \
    "$TEMPLATE" > "$OUTPUT"

echo "Rendered $OUTPUT with THRESHOLD=$THRESHOLD, MIN_PHASE_VALUE=$MIN_PHASE_VALUE, DATASOURCE_UID=$DATASOURCE_UID, INFLUXDB_BUCKET=$INFLUXDB_BUCKET"
