$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $repoRoot "skills"
$target = Join-Path $env:USERPROFILE ".codex\skills"

if (-not (Test-Path -Path $source)) {
    throw "Cannot find skills directory: $source"
}

New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item -Path (Join-Path $source "*") -Destination $target -Recurse -Force

Write-Host "Installed paper-check skills to $target"
