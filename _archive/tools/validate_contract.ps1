param(
  [string]$ContractJson = "contracts/export_contract_v0.1.1_min.json",
  [string]$SampleExport
)

if (-not $SampleExport) {
  Write-Error "Usage: .\\tools\\validate_contract.ps1 -SampleExport <path> [-ContractJson <path>]"
  exit 2
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  Write-Error "python not found in PATH"
  exit 127
}

$contractPath = Resolve-Path (Join-Path $repoRoot $ContractJson)
$samplePath = Resolve-Path (Join-Path $repoRoot $SampleExport)

& $python.Path (Join-Path $repoRoot "tools\\validate_contract.py") $contractPath $samplePath
exit $LASTEXITCODE
