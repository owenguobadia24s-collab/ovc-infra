param(
  [string]$RunDir = ".codex\RUNS\2026-02-02__194924__family"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path ".").Path
$runDirPath = (Resolve-Path $RunDir).Path

if (-not (Test-Path $runDirPath)) {
  throw "Run dir not found: $runDirPath"
}

Push-Location $repoRoot
try {
  python .codex\CHECKS\plan_graph_nodeid_renames.py --run-dir "$runDirPath"
  python .codex\CHECKS\apply_graph_nodeid_renames.py --run-dir "$runDirPath" --repo-root . | Out-File -FilePath (Join-Path $runDirPath "rename_dryrun.diff") -Encoding UTF8
}
finally {
  Pop-Location
}

$planJson = Join-Path $runDirPath "rename_plan.json"
$planMd = Join-Path $runDirPath "rename_plan.md"
$dryRun = Join-Path $runDirPath "rename_dryrun.diff"

Write-Host ("RUN_DIR: {0}" -f $runDirPath)
Write-Host ("- {0}" -f $planJson)
Write-Host ("- {0}" -f $planMd)
Write-Host ("- {0}" -f $dryRun)
