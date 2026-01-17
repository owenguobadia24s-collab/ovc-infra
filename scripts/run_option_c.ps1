$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
  if (-not $env:DATABASE_URL) {
    Write-Host "DATABASE_URL is not set."
    Write-Host "Set it in this shell, for example:"
    Write-Host "  `$env:DATABASE_URL = 'postgresql://user:pass@host/db'"
    exit 1
  }

  $psql = Get-Command psql -ErrorAction SilentlyContinue
  if (-not $psql) {
    Write-Error "psql not found in PATH"
    exit 127
  }

  Write-Host "Applying Option C SQL..."
  & $psql.Path $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/option_c_v0_1.sql
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }

  Write-Host "Running Option C spotchecks..."
  & $psql.Path $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/option_c_spotchecks.sql
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }

  Write-Host ""
  Write-Host "Summary: If every spotcheck row shows status=PASS, treat this run as PASS."
  Write-Host "Summary: If any row shows status=WARN, investigate before proceeding."
} finally {
  Pop-Location
}
