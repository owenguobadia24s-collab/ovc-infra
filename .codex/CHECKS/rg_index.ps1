# rg_index.ps1
# READ-ONLY. Builds a deterministic "evidence index" using ripgrep.
# Requires: rg (ripgrep) on PATH.

param(
  [string]$RepoRoot = (Resolve-Path ".").Path,
  [string]$OutDir   = (Join-Path (Resolve-Path ".").Path ".codex\RUNS"),
  [string]$Label    = "",
  [string]$RunDir   = "",
  [string]$GraphPath = "",
  [string]$GraphRoot = "Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function New-RunStamp {
  $ts = Get-Date -Format "yyyy-MM-dd__HHmmss"
  if ($Label -and $Label.Trim().Length -gt 0) { return "$ts`__$Label" }
  return $ts
}

# Check ripgrep exists
if (-not (Get-Command rg -ErrorAction SilentlyContinue)) {
  throw "ripgrep (rg) not found on PATH. Install ripgrep first."
}

if ($RunDir -and $RunDir.Trim().Length -gt 0) {
  $runDir = $RunDir
  New-Item -ItemType Directory -Force -Path $runDir | Out-Null
} else {
  $stamp = New-RunStamp
  $runDir = Join-Path $OutDir $stamp
  New-Item -ItemType Directory -Force -Path $runDir | Out-Null
}

$outFile = Join-Path $runDir "rg_index.txt"

# Stable rg options:
# --no-heading: keeps output minimal
# -n: line numbers
# -S: smart case
# --hidden: include dotfiles (but we exclude .git)
# --glob: exclude noisy dirs
$rgBase = @(
  "rg","--no-heading","-n","-S","--hidden",
  "--glob","!.git/**",
  "--glob","!.venv/**","--glob","!venv/**",
  "--glob","!node_modules/**",
  "--glob","!dist/**","--glob","!build/**",
  "--glob","!.pytest_cache/**","--glob","!__pycache__/**"
)

$legendScope = "Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/**/*.md"

Push-Location $RepoRoot
try {
  if ($GraphPath -and -not (Test-Path $GraphPath)) {
    throw "GraphPath not found: $GraphPath"
  }
  if (-not $GraphPath -and $GraphRoot -and -not (Test-Path $GraphRoot)) {
    throw "GraphRoot not found: $GraphRoot"
  }

  # Index queries: tune these as OVC grows.
  # Kept broad enough to help Pass 1/2/3 prove objects/flows.
  $queries = @(
    @{ name='LEGEND_NODE_IDS'; pattern='^\|\s*[A-Z0-9_\-]+\s*\|'; scope=$legendScope }
  )

  if ($GraphPath) {
    $queries += @(
      @{ name='WORKFLOWS';       pattern='.github/workflows|uses:|run:|python|node|bash|pwsh'; scope='.github/workflows/**/*' },
      @{ name='SQL_DEFS';        pattern='CREATE\s+(TABLE|VIEW|MATERIALIZED\s+VIEW)\s+'; scope='sql/**/*.sql' },
      @{ name='SQL_REFS';        pattern='\bFROM\b|\bJOIN\b|\bREFERENCES\b'; scope='sql/**/*.sql' },
      @{ name='PY_IMPORTS';      pattern='^\s*(from\s+\S+\s+import|import\s+\S+)'; scope='**/*.py' },
      @{ name='SCRIPTS_ENTRY';   pattern='if\s+__name__\s*==\s*[''\"'']__main__[''\"'']|argparse|click\.'; scope='**/*.py' },
      @{ name='GRAPH_TARGET';    pattern='.'; scope=$GraphPath } # dumps file content with line numbers via rg (cheap "open")
    )
  } else {
    $graphScope = "$GraphRoot/**/*.md"
    $queries += @(
      @{ name='GRAPH_MERMAID';   pattern='```mermaid|graph\s+|flowchart\s+'; scope=$graphScope },
      @{ name='GRAPH_NODE_IDS';  pattern='^\s*[A-Za-z0-9][A-Za-z0-9_\-]*\s*(\[|\(|\{\{|\{|\")'; scope=$graphScope }
    )
  }

  @(
    "REPO_ROOT: $RepoRoot"
    "GENERATED_UTC: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
    "GRAPH_PATH: $GraphPath"
    "GRAPH_ROOT: $GraphRoot"
    ""
    "FORMAT: <file>:<line>:<match>"
    ""
  ) | Set-Content -Encoding UTF8 $outFile

  foreach ($q in $queries) {
    Add-Content -Encoding UTF8 $outFile ("==== QUERY: {0} ====" -f $q.name)
    Add-Content -Encoding UTF8 $outFile ("SCOPE: {0}" -f $q.scope)
    Add-Content -Encoding UTF8 $outFile ("PATTERN: {0}" -f $q.pattern)
    Add-Content -Encoding UTF8 $outFile ""

    # For GRAPH_TARGET we want to print the file with line numbers.
    if ($q.name -eq "GRAPH_TARGET") {
      # rg "." prints every line with file:line:...
      & $rgBase $q.pattern $q.scope | Add-Content -Encoding UTF8 $outFile
    } else {
      & $rgBase $q.pattern $q.scope | Add-Content -Encoding UTF8 $outFile
    }

    Add-Content -Encoding UTF8 $outFile ""
  }

  Write-Host "OK: rg index written to $outFile"
}
finally {
  Pop-Location
}
