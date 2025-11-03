#!/bin/bash
# build_conf.sh
# erzeugt telegraf.conf aus telegraf.conf.template + .env

# Variablen aus .env automatisch exportieren
set -a
source .env
set +a

# Template und Ziel
TEMPLATE="telegraf/telegraf.conf.template"
TARGET="telegraf/telegraf.conf"

# Ersetze Variablen
envsubst < "$TEMPLATE" > "$TARGET"

echo "Fertige telegraf.conf wurde erstellt: $TARGET"
