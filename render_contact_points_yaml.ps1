# render_contact_points_yaml.ps1 - Render Grafana contact-points.yaml from template using .env variables.
# Usage: ./render_contact_points_yaml.ps1

$ErrorActionPreference = "Stop"

# Get script directory and .env path
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envPath = Join-Path $scriptDir ".env"

# Load .env variables
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

$template = Join-Path $scriptDir "grafana/provisioning/alerting/contact-points.yaml.template"
$output = Join-Path $scriptDir "grafana/provisioning/alerting/contact-points.yaml"

$recipient = [System.Environment]::GetEnvironmentVariable("ALERT_EMAIL_RECIPIENT")
$siteId    = [System.Environment]::GetEnvironmentVariable("SITE_ID")

if (-not $recipient) {
    Write-Error "ALERT_EMAIL_RECIPIENT is not set in .env!"
    exit 1
}
if (-not $siteId) {
    Write-Error "SITE_ID is not set in .env!"
    exit 1
}

(Get-Content $template) `
    -replace "{{ALERT_EMAIL_RECIPIENT}}", $recipient `
    -replace "{{SITE_ID}}", $siteId `
    | Set-Content $output

Write-Host "Rendered $output with ALERT_EMAIL_RECIPIENT=$recipient and SITE_ID=$siteId"
