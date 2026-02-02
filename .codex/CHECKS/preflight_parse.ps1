param(
  [string]$ChecksDir = ".codex/CHECKS"
)

$ErrorActionPreference = "Stop"

$failures = @()
Get-ChildItem -Path $ChecksDir -Filter *.ps1 | ForEach-Object {
  $file = $_.FullName
  try {
    $null = [scriptblock]::Create((Get-Content -Raw $file))
    Write-Host "PARSE OK: $file"
  } catch {
    Write-Host "PARSE FAIL: $file"
    Write-Host $_.Exception.Message
    $failures += $file
  }
}

if ($failures.Count -gt 0) {
  Write-Host "\nFAILED PowerShell parse check on:" -ForegroundColor Red
  $failures | ForEach-Object { Write-Host $_ -ForegroundColor Red }
  exit 1
}
Write-Host "\nAll .ps1 scripts parsed successfully." -ForegroundColor Green