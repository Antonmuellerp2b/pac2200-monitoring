# render_power_sum_max_rule.ps1 - Render Grafana power_sum_max_rule.yaml from template using .env variables.
# Usage: ./render_power_sum_max_rule.ps1

$ErrorActionPreference = "Stop"

# Load variables from .env file
Get-Content .env | ForEach-Object {
    if ($_ -match '^(.*?)=(.*)$') {
        Set-Variable -Name $matches[1] -Value $matches[2]
    }
}

$template = "grafana/provisioning/alerting/power_sum_max.yaml.template"
$output   = "grafana/provisioning/alerting/power_sum_max_rule.yaml"

# Create output directory if it does not exist
New-Item -ItemType Directory -Force -Path (Split-Path $output) | Out-Null

# Check required variables
if (-not $DATASOURCE_UID) { Write-Error "DATASOURCE_UID not set in .env!"; exit 1 }
if (-not $INFLUXDB_BUCKET) { Write-Error "INFLUXDB_BUCKET not set in .env!"; exit 1 }
if (-not $TOTAL_POWER_THRESHOLD_KW) { Write-Error "TOTAL_POWER_THRESHOLD_KW not set in .env!"; exit 1 }

# Replace placeholders in template with environment variables, skip comment lines
(Get-Content $template | Where-Object { $_ -notmatch '^\s*#' }) `
    -replace "{{DATASOURCE_UID}}", $DATASOURCE_UID `
    -replace "{{INFLUXDB_BUCKET}}", $INFLUXDB_BUCKET `
    -replace "{{TOTAL_POWER_THRESHOLD_KW}}", $TOTAL_POWER_THRESHOLD_KW `
    | Set-Content $output
