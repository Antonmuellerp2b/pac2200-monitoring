#!/bin/bash
# Render contact-points.yaml from template and .env

set -e

# Load .env variables
if [ -f ".env" ]; then
  set -a
  source .env
  set +a
fi

TEMPLATE="grafana/provisioning/alerting/contact-points.yaml.template"
OUTPUT="grafana/provisioning/alerting/contact-points.yaml"

if [ -z "$ALERT_EMAIL_RECIPIENT" ]; then
  echo "ALERT_EMAIL_RECIPIENT is not set in .env!"
  exit 1
fi

sed "s/{{ALERT_EMAIL_RECIPIENT}}/$ALERT_EMAIL_RECIPIENT/g" "$TEMPLATE" > "$OUTPUT"
echo "Rendered $OUTPUT with ALERT_EMAIL_RECIPIENT=$ALERT_EMAIL_RECIPIENT"
