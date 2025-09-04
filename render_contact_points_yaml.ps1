# PowerShell-Skript: render_contact_points_yaml.ps1
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envPath = Join-Path $scriptDir ".env"

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
$siteId    = [System.Environment]::GetEnvironmentVariable("ALERT_EMAIL_SITE_ID")

if (-not $recipient) {
    Write-Error "ALERT_EMAIL_RECIPIENT is not set in .env!"
    exit 1
}
if (-not $siteId) {
    Write-Error "ALERT_EMAIL_SITE_ID is not set in .env!"
    exit 1
}
#test
# beide Platzhalter ersetzen
(Get-Content $template) `
    -replace "{{ALERT_EMAIL_RECIPIENT}}", $recipient `
    -replace "{{ALERT_EMAIL_SITE_ID}}", $siteId `
    | Set-Content $output

Write-Host "Rendered $output with ALERT_EMAIL_RECIPIENT=$recipient and ALERT_EMAIL_SITE_ID=$siteId"
