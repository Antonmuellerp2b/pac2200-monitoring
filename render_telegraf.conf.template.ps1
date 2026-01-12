# render_telegraf.conf.template.ps1
# Generates telegraf.conf from telegraf.conf.template + .env

$template = "telegraf/telegraf.conf.template"
$target = "telegraf/telegraf.conf"
$envFile = ".env"

# Load .env file
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $_.Trim() | Where-Object { $_ -and -not $_.StartsWith("#") } | ForEach-Object {
            $pair = $_ -split '=', 2
            if ($pair.Length -eq 2) {
                [System.Environment]::SetEnvironmentVariable($pair[0], $pair[1])
            }
        }
    }
    Write-Host ".env loaded."
} else {
    Write-Warning ".env file not found."
}

# Read template
$content = Get-Content $template -Raw

# Replace variables using a proper ScriptBlock
$missingVars = @()
$content = [regex]::Replace($content, '\$\{(\w+)\}', {
    param($m)
    $name = $m.Groups[1].Value
    $val = [System.Environment]::GetEnvironmentVariable($name)
    if ($val) { 
        return $val
    } else { 
        $missingVars += $name
        return $m.Value
    }
})

# Write the rendered file
Set-Content -Path $target -Value $content -Encoding UTF8

if ($missingVars.Count -gt 0) {
    $missingVars = $missingVars | Sort-Object -Unique
    Write-Warning "Missing variables: $($missingVars -join ', ')"
}