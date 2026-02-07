param(
  [string]$Target = "tests.test_audit_interpreter_change_classification"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$defaultTarget = "tests.test_audit_interpreter_change_classification"
if ([string]::IsNullOrWhiteSpace($Target)) {
  $Target = $defaultTarget
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"
$codexDir = Join-Path $repoRoot ".codex"
$logPath = Join-Path $codexDir "_unittest_last.txt"
$donePath = Join-Path $codexDir "_unittest_done.txt"

$exitCode = 0
$didPushLocation = $false

try {
  New-Item -ItemType Directory -Force -Path $codexDir | Out-Null
  if (Test-Path -LiteralPath $donePath) {
    Remove-Item -LiteralPath $donePath -Force
  }

  Push-Location $repoRoot
  $didPushLocation = $true

  if (-not (Test-Path -LiteralPath $pythonPath)) {
    Set-Content -LiteralPath $logPath -Encoding utf8 -Value "ERROR: missing venv python at $pythonPath"
    $exitCode = 127
  } else {
    & $pythonPath -u -m unittest -v $Target *> $logPath
    $exitCode = [int]$LASTEXITCODE
  }
}
catch {
  try {
    New-Item -ItemType Directory -Force -Path $codexDir | Out-Null
    Add-Content -LiteralPath $logPath -Encoding utf8 -Value "ERROR: powershell_exception=$($_.Exception.Message)"
  } catch {
    # Intentionally swallow to keep sentinel write path alive.
  }
  if ($exitCode -eq 0) {
    $exitCode = 1
  }
}
finally {
  if ($didPushLocation) {
    try {
      Pop-Location
    } catch {
      # Ignore location stack errors to preserve deterministic sentinel write.
    }
  }

  New-Item -ItemType Directory -Force -Path $codexDir | Out-Null
  $utc = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
  $sentinel = "DONE target=$Target exit_code=$exitCode utc=$utc"
  Set-Content -LiteralPath $donePath -Encoding utf8 -Value $sentinel
}

exit $exitCode
