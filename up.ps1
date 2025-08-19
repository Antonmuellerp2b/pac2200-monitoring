# zum Starten in Windows: powershell -ExecutionPolicy Bypass -File .\up.ps1

# PowerShell-Skript: start-influxdb.ps1
$ErrorActionPreference = "Stop"

# Render influxdb.yaml aus der Vorlage mit .env
./render_influxdb_yaml.ps1

# Render contact-points.yaml aus der Vorlage mit .env
./render_contact_points_yaml.ps1

# Render render_power_imbalance_rule.yaml aus der Vorlage mit .env
./render_power_imbalance_rule.ps1

# Render power_sum_max_rule.yaml aus der Vorlage mit .env
./render_power_sum_max_rule.ps1

# Docker Compose mit allen übergebenen Argumenten starten
docker compose up @Args
