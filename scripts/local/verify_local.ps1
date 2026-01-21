param(
  [string]$ContractJson = "contracts/export_contract_v0.1.1_min.json",
  [string]$SampleExport = "tests/sample_exports/min_001.txt",
  [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    Write-Error "python not found in PATH"
    exit 127
  }

  Write-Host "Validating export contract..."
  & $python.Path -m tools.validate_contract $ContractJson $SampleExport
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }

  if (-not $SkipTests) {
    $testDir = Join-Path $repoRoot "tests"
    $testFiles = Get-ChildItem -Path $testDir -Filter "test_*.py" -ErrorAction SilentlyContinue
    if ($testFiles) {
      & $python.Path -c "import pytest" 2>$null
      if ($LASTEXITCODE -eq 0) {
        Write-Host "Running pytest..."
        & $python.Path -m pytest
        if ($LASTEXITCODE -ne 0) {
          exit $LASTEXITCODE
        }
      } else {
        Write-Host "pytest not available; skipping tests."
      }
    } else {
      Write-Host "No python tests found; skipping tests."
    }
  }

  $curlPath = $SampleExport -replace "\\", "/"
  Write-Host ""
  Write-Host "POST sample export (local worker):"
  Write-Host "curl.exe -X POST http://localhost:8787/tv --data-binary \"@$curlPath\""
} finally {
  Pop-Location
}
