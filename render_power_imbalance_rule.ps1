$ErrorActionPreference = "Stop"

# Pfade
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envPath = Join-Path $scriptDir ".env"
$template = Join-Path $scriptDir "grafana/provisioning/alerting/power_imbalance_rule.yaml.template"
$output = Join-Path $scriptDir "grafana/provisioning/alerting/power_imbalance_rule.yaml"

# .env laden
if (Test-Path $envPath) {
    Get-Content $envPath | ForEach-Object {
        if ($_ -match '^([\w]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            [System.Environment]::SetEnvironmentVariable($name, $value)
        }
    }
} else {
    Write-Error ".env file not found at $envPath"
    exit 1
}

# Variablen prüfen
$PHASE_IMBALANCE_RATIO_THRESHOLD = [System.Environment]::GetEnvironmentVariable("PHASE_IMBALANCE_RATIO_THRESHOLD")
$minPhase = [System.Environment]::GetEnvironmentVariable("PHASE_IMBALANCE_MIN_KW")
$datasource = [System.Environment]::GetEnvironmentVariable("DATASOURCE_UID")
$bucket = [System.Environment]::GetEnvironmentVariable("INFLUXDB_BUCKET")

if (-not $PHASE_IMBALANCE_RATIO_THRESHOLD) { Write-Error "PHASE_IMBALANCE_RATIO_THRESHOLD not set in .env!"; exit 1 }
if (-not $minPhase) { Write-Error "PHASE_IMBALANCE_MIN_KW not set in .env!"; exit 1 }
if (-not $datasource) { Write-Error "DATASOURCE_UID not set in .env!"; exit 1 }
if (-not $bucket) { Write-Error "INFLUXDB_BUCKET not set in .env!"; exit 1 }

# Template ersetzen
(Get-Content $template) `
    -replace "{{PHASE_IMBALANCE_RATIO_THRESHOLD}}", $PHASE_IMBALANCE_RATIO_THRESHOLD `
    -replace "{{PHASE_IMBALANCE_MIN_KW}}", $minPhase `
    -replace "{{DATASOURCE_UID}}", $datasource `
    -replace "{{INFLUXDB_BUCKET}}", $bucket `
    | Set-Content $output

Write-Host "Rendered $output with PHASE_IMBALANCE_RATIO_THRESHOLD=$PHASE_IMBALANCE_RATIO_THRESHOLD, PHASE_IMBALANCE_MIN_KW=$minPhase, DATASOURCE_UID=$datasource, INFLUXDB_BUCKET=$bucket"
