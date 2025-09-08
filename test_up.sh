#!/bin/zsh
set -e

# Render templates wie gewohnt
./render_influxdb_yaml.sh
./render_contact_points_yaml.sh
./render_power_imbalance_rule.sh
./render_power_sum_max_rule.sh

# Starte Docker Compose mit temporärem Projekt-Namen
# -p test_project verhindert Überschreiben der echten Container
# --build stellt sicher, dass Änderungen im Code genutzt werden
exec docker compose -p test_project up --build "$@"

