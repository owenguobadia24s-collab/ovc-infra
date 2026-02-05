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

$success = $false

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

  $success = $true
}
finally {
  Pop-Location
  if ($success) {
    try {
      $createdUtc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
      $pySrc = Join-Path $repoRoot "src"
      $prevPythonPath = $env:PYTHONPATH
      if ($env:PYTHONPATH) {
        $env:PYTHONPATH = "$pySrc;$env:PYTHONPATH"
      } else {
        $env:PYTHONPATH = "$pySrc"
      }
      $env:OVC_RUN_DIR = $runDir
      $env:OVC_CREATED_UTC = $createdUtc
      $env:OVC_GRAPH_PATH = $graphPath
      $env:OVC_GRAPH_ROOT = $graphRoot

@'
from pathlib import Path
import os
from ovc_ops.run_envelope_v0_1 import get_git_state, seal_dir, write_run_json

run_dir = Path(os.environ["OVC_RUN_DIR"])
created_utc = os.environ.get("OVC_CREATED_UTC")
graph_path = os.environ.get("OVC_GRAPH_PATH") or ""
graph_root = os.environ.get("OVC_GRAPH_ROOT") or ""
git_commit, working_tree_state = get_git_state()

inputs = {}
if graph_path:
    inputs["graph_path"] = graph_path
if graph_root:
    inputs["graph_root"] = graph_root

outputs = [
    "tree_snapshot.txt",
    "rg_index.txt",
    "repo_files.txt",
    "legend_nodes.json",
    "graph_nodes.json",
    "coverage_report.md",
    "run.json",
    "manifest.json",
    "MANIFEST.sha256",
]

payload = {
    "run_id": run_dir.name,
    "created_utc": created_utc,
    "run_type": "op_run",
    "option": "QA",
    "operation_id": "OP-QA05",
    "git_commit": git_commit,
    "working_tree_state": working_tree_state,
    "outputs": outputs,
}
if inputs:
    payload["inputs"] = inputs

write_run_json(run_dir, payload)
seal_dir(run_dir, [
    "tree_snapshot.txt",
    "rg_index.txt",
    "repo_files.txt",
    "legend_nodes.json",
    "graph_nodes.json",
    "coverage_report.md",
    "run.json",
])
'@ | python -
      if ($null -ne $prevPythonPath) {
        $env:PYTHONPATH = $prevPythonPath
      } else {
        Remove-Item Env:\PYTHONPATH -ErrorAction SilentlyContinue
      }
    } catch {
      Write-Warning "run envelope write failed: $_"
    }
  }
}
