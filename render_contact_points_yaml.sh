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

if [ -z "$SITE_ID" ]; then
  echo "SITE_ID is not set in .env!"
  exit 1
fi

sed \
  -e "s/{{ALERT_EMAIL_RECIPIENT}}/$ALERT_EMAIL_RECIPIENT/g" \
  -e "s/{{SITE_ID}}/$SITE_ID/g" \
  "$TEMPLATE" > "$OUTPUT"

echo "Rendered $OUTPUT with ALERT_EMAIL_RECIPIENT=$ALERT_EMAIL_RECIPIENT and SITE_ID=$SITE_ID"
