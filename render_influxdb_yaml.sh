#!/bin/sh
set -e

# Load .env variables from project root
if [ -f ".env" ]; then
  set -a
  . .env
  set +a
else
  echo ".env file not found in current directory" >&2
  exit 1
fi

# Render the template to influxdb.yaml
mkdir -p ./grafana/provisioning/datasources
envsubst < influxdb.yaml.template > ./grafana/provisioning/datasources/influxdb.yaml
