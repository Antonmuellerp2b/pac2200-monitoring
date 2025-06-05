#!/bin/sh
set -e

# Load .env variables from project root
env_path="$(dirname "$0")/.env"
if [ -f "$env_path" ]; then
  set -a
  . "$env_path"
  set +a
else
  echo ".env file not found at $env_path" >&2
  exit 1
fi

# Render the template to influxdb.yaml
cd "$(dirname "$0")"
envsubst < influxdb.yaml.template > ./grafana/provisioning/datasources/influxdb.yaml
