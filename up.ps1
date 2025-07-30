# zum Starten in Windows: powershell -ExecutionPolicy Bypass -File .\up.ps1

# PowerShell-Skript: start-influxdb.ps1
$ErrorActionPreference = "Stop"

# Render influxdb.yaml aus der Vorlage mit .env
./render_influxdb_yaml.ps1

# Render contact-points.yaml aus der Vorlage mit default.env
./render_contact_points_yaml.ps1

# Docker Compose mit allen übergebenen Argumenten starten
docker compose up @Args
