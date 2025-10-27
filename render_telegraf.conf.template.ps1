# build_conf.ps1 (ungetestet)
# erzeugt telegraf.conf aus telegraf.conf.template + .env

# .env-Datei einlesen und als Umgebungsvariablen setzen
Get-Content .env | ForEach-Object {
    $_.Trim() | Where-Object { $_ -and -not $_.StartsWith("#") } | ForEach-Object {
        $pair = $_ -split '=', 2
        if ($pair.Length -eq 2) {
            [System.Environment]::SetEnvironmentVariable($pair[0], $pair[1])
        }
    }
}

# Template und Ziel
$template = "telegraf/telegraf.conf.template"
$target   = "telegraf/telegraf.conf"

# Template einlesen, Variablen ersetzen
$content = Get-Content $template -Raw
$content = $content -replace '\$\{(\w+)\}', { param($m) [System.Environment]::GetEnvironmentVariable($m.Groups[1].Value) }

# Ergebnis speichern
Set-Content -Path $target -Value $content -Encoding UTF8

Write-Host "Fertige telegraf.conf wurde erstellt: $target"
