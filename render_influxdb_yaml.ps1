$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envPath = Join-Path $scriptDir ".env"

if (Test-Path $envPath) {
    Get-Content $envPath | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+?)=(.*)') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim().Trim("'`"")

            [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
} else {
    Write-Error ".env file not found at $envPath"
    exit 1
}

$templatePath = Join-Path $scriptDir "influxdb.yaml.template"
$outputPath = Join-Path $scriptDir "grafana/provisioning/datasources/influxdb.yaml"
$outputDir = Split-Path $outputPath -Parent

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$template = Get-Content $templatePath -Raw

$templateReplaced = [regex]::Replace($template, '\$\{?(\w+)\}?', {
    param($match)
    $varName = $match.Groups[1].Value
    $returnVal = [System.Environment]::GetEnvironmentVariable($varName, "Process")
    if ([string]::IsNullOrEmpty($returnVal)) { return "" }
    else { return $returnVal }
})

$templateReplaced | Set-Content -Encoding UTF8 $outputPath
