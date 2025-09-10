#!/bin/bash
# render_contact_points_yaml.sh - Render Grafana contact-points.yaml from template using .env variables.
# Usage: ./render_contact_points_yaml.sh

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

TEMPLATE="grafana/provisioning/alerting/contact-points.yaml.template"
OUTPUT="grafana/provisioning/alerting/contact-points.yaml"

if [ -z "${ALERT_EMAIL_RECIPIENT:-}" ]; then
  echo "ALERT_EMAIL_RECIPIENT is not set in .env!" >&2
  exit 1
fi

if [ -z "${SITE_ID:-}" ]; then
  echo "SITE_ID is not set in .env!" >&2
  exit 1
fi

# Render template, skip comment lines
grep -v '^#' "$TEMPLATE" | \
sed \
  -e "s/{{ALERT_EMAIL_RECIPIENT}}/$ALERT_EMAIL_RECIPIENT/g" \
  -e "s/{{SITE_ID}}/$SITE_ID/g" \
  > "$OUTPUT"

echo "Rendered $OUTPUT with ALERT_EMAIL_RECIPIENT=$ALERT_EMAIL_RECIPIENT and SITE_ID=$SITE_ID"