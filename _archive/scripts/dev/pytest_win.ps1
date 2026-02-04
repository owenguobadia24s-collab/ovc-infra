$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($env:TEMP)) {
    throw "TEMP environment variable is not set. Please set TEMP to a writable directory."
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\\..")
$baseTemp = Join-Path $env:TEMP "pytest-tmp-ovc"
$cacheDir = Join-Path $env:TEMP "pytest-cache-ovc"

New-Item -ItemType Directory -Force -Path $baseTemp | Out-Null
New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null

Write-Host "pytest_win: basetemp=$baseTemp cache_dir=$cacheDir"

Push-Location $repoRoot
try {
    & python -m pytest --basetemp "$baseTemp" -o "cache_dir=$cacheDir" @args
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
