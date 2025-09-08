# up.ps1 - Start all services for PAC2200 monitoring stack (Windows)
# Renders all needed config files and starts docker compose.
# Usage: powershell -ExecutionPolicy Bypass -File .\up.ps1 -d

$ErrorActionPreference = "Stop"

# Render influxdb.yaml from template using .env
./render_influxdb_yaml.ps1

# Render contact-points.yaml from template using .env
./render_contact_points_yaml.ps1

# Render power_imbalance_rule.yaml from template using .env
./render_power_imbalance_rule.ps1

# Render power_sum_max_rule.yaml from template using .env
./render_power_sum_max_rule.ps1

# Start docker compose with any arguments passed to this script
docker compose up @Args
