# snapshot_tree.ps1
# READ-ONLY. Generates a deterministic tree snapshot for audit / drift diffing.

param(
  [string]$RepoRoot = (Resolve-Path ".").Path,
  [string]$OutDir   = (Join-Path (Resolve-Path ".").Path ".codex\RUNS"),
  [string]$Label    = "",
  [string]$RunDir   = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function New-RunStamp {
  $ts = Get-Date -Format "yyyy-MM-dd__HHmmss"
  if ($Label -and $Label.Trim().Length -gt 0) { return "$ts`__$Label" }
  return $ts
}

if ($RunDir -and $RunDir.Trim().Length -gt 0) {
  $runDir = $RunDir
  New-Item -ItemType Directory -Force -Path $runDir | Out-Null
} else {
  $stamp = New-RunStamp
  $runDir = Join-Path $OutDir $stamp
  New-Item -ItemType Directory -Force -Path $runDir | Out-Null
}

$outFile = Join-Path $runDir "tree_snapshot.txt"

# Exclusions: keep noise out of diffs
$excludeDirs = @(
  ".git", ".venv", "venv", "node_modules", ".next", "dist", "build",
  ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache",
  ".DS_Store"
)

# Build a stable file list (relative paths), directories + files
Push-Location $RepoRoot
try {
  $items = Get-ChildItem -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object {
      $p = $_.FullName.Substring($RepoRoot.Length).TrimStart('\','/')
      # Exclude if any path segment matches excludeDirs
      $segments = $p -split '[\\/]+'
      foreach ($seg in $segments) {
        if ($excludeDirs -contains $seg) { return $false }
      }
      return $true
    } |
    ForEach-Object {
      $_.FullName.Substring($RepoRoot.Length).TrimStart('\','/')
    } |
    Sort-Object

  @(
    "REPO_ROOT: $RepoRoot"
    "GENERATED_UTC: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
    "EXCLUDES: $($excludeDirs -join ', ')"
    ""
    "PATHS:"
  ) | Set-Content -Encoding UTF8 $outFile

  $items | Add-Content -Encoding UTF8 $outFile

  Write-Host "OK: tree snapshot written to $outFile"
}
finally {
  Pop-Location
}
