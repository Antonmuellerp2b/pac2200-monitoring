#!/bin/bash
# build_conf.sh
# erzeugt telegraf.conf aus telegraf.conf.template + .env

# Lade Umgebungsvariablen aus .env
export $(grep -v '^#' .env | xargs)

# Template und Ziel
TEMPLATE="telegraf/telegraf.conf.template"
TARGET="telegraf/telegraf.conf"

# Ersetze Variablen
envsubst < "$TEMPLATE" > "$TARGET"

echo "Fertige telegraf.conf wurde erstellt: $TARGET"
