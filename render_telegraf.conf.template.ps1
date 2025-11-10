# render_telegraf.conf.template.ps1
# erzeugt telegraf.conf aus telegraf.conf.template + .env
# ersetzt ${VAR} durch die Werte aus .env oder Umgebung

# Pfade
$template = "telegraf/telegraf.conf.template"
$target   = "telegraf/telegraf.conf"
$envFile  = ".env"

# .env-Datei einlesen und als Umgebungsvariablen setzen
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $_.Trim() | Where-Object { $_ -and -not $_.StartsWith("#") } | ForEach-Object {
            $pair = $_ -split '=', 2
            if ($pair.Length -eq 2) {
                [System.Environment]::SetEnvironmentVariable($pair[0], $pair[1])
            }
        }
    }
    Write-Host ".env geladen und Umgebungsvariablen gesetzt."
} else {
    Write-Warning ".env Datei nicht gefunden: $envFile"
}

# Template einlesen
if (-Not (Test-Path $template)) {
    Write-Error "Template-Datei nicht gefunden: $template"
    exit 1
}
$content = Get-Content $template -Raw

# Variablen ersetzen
$missingVars = @()
$content = $content -replace '\$\{(\w+)\}', {
    param($m)
    $varName = $m.Groups[1].Value
    $envValue = [System.Environment]::GetEnvironmentVariable($varName)
    if ($envValue) {
        $envValue
    } else {
        $missingVars += $varName
        $m.Value  # Original-Text beibehalten
    }
}

# Ergebnis speichern
Set-Content -Path $target -Value $content -Encoding UTF8
Write-Host "Fertige telegraf.conf wurde erstellt: $target"

# Meldung für fehlende Variablen
if ($missingVars.Count -gt 0) {
    $missingVars = $missingVars | Sort-Object -Unique
    Write-Warning "Folgende Variablen wurden nicht gefunden und nicht ersetzt: $($missingVars -join ', ')"
}