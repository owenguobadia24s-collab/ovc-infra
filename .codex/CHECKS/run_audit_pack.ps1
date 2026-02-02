param(
  [string]$Label = "auditpack",
  [string]$Graph = "",
  [string]$GraphDir = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function New-RunStamp {
  $ts = Get-Date -Format "yyyy-MM-dd__HHmmss"
  if ($Label -and $Label.Trim().Length -gt 0) { return "$ts`__$Label" }
  return $ts
}

$repoRoot = (Resolve-Path ".").Path
$runsRoot = Join-Path $repoRoot ".codex\RUNS"
$graphsRoot = "Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS"
$defaultGraphDir = "10_OPTION_FLOW"

$stamp = New-RunStamp
$runDir = Join-Path $runsRoot $stamp
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

Push-Location $repoRoot
try {
  $graphPath = ""
  $graphRoot = ""

  if ($Graph -and $Graph.Trim().Length -gt 0) {
    if (-not (Test-Path $Graph)) {
      throw "Graph file not found: $Graph"
    }
    $graphPath = $Graph
  } elseif ($GraphDir -and $GraphDir.Trim().Length -gt 0) {
    if (Test-Path $GraphDir) {
      $graphRoot = $GraphDir
    } else {
      $graphRoot = Join-Path $graphsRoot $GraphDir
      if (-not (Test-Path $graphRoot)) {
        throw "GraphDir not found: $GraphDir"
      }
    }
  } else {
    $graphRoot = Join-Path $graphsRoot $defaultGraphDir
    if (-not (Test-Path $graphRoot)) {
      throw "Default GraphDir not found: $graphRoot"
    }
  }

  # 1) Deterministic tree snapshot
  powershell -ExecutionPolicy Bypass -File .codex\CHECKS\snapshot_tree.ps1 -RunDir $runDir

  # 2) Evidence index (rg)
  if ($graphPath) {
    powershell -ExecutionPolicy Bypass -File .codex\CHECKS\rg_index.ps1 -RunDir $runDir -GraphPath $graphPath
  } else {
    powershell -ExecutionPolicy Bypass -File .codex\CHECKS\rg_index.ps1 -RunDir $runDir -GraphRoot $graphRoot
  }

  # 3) Coverage audit (repo <-> legend <-> graph)
  if ($graphPath) {
    python .codex\CHECKS\coverage_audit.py --run-dir $runDir --graph-file $graphPath --graphs-root $graphsRoot
  } else {
    python .codex\CHECKS\coverage_audit.py --run-dir $runDir --graphs-root $graphRoot
  }
}
finally {
  Pop-Location
}
