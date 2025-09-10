#!/bin/zsh
set -e

# Stoppe alle Container des temporären Test-Projekts und lösche auch die Volumes
docker compose -p test_project down -v

echo "✅ Temporäres Testprojekt gestoppt und Volumes gelöscht."
