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

# Replace placeholders in template with environment variables
(Get-Content $template) `
    -replace "{{DATASOURCE_UID}}", $DATASOURCE_UID `
    -replace "{{INFLUXDB_BUCKET}}", $INFLUXDB_BUCKET `
    -replace "{{TOTAL_POWER_THRESHOLD_KW}}", $TOTAL_POWER_THRESHOLD_KW `
    | Set-Content $output

Write-Host "✅ Alert rule rendered to $output"
