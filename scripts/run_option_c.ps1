param(
  [string]$RunId,
  [switch]$Strict,
  [switch]$SpotchecksOnly
)

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

  if (-not $RunId) {
    if ($env:GITHUB_ACTIONS -eq "true" -or $env:CI -eq "true") {
      Write-Error "-RunId is required in CI."
      exit 1
    }
    $RunId = "local_{0}" -f (Get-Date -AsUTC -Format "yyyyMMddTHHmmssZ")
  }

  $evalVersion = "v0.1"
  $formulaHash = "6b328b4962b19a53e3a1c1f03f41d705"
  $horizonSpec = "K=1,2,6,12"
  $notes = "option_d_run"
  $strictValue = $Strict.IsPresent.ToString().ToLower()

  $reportsDir = "reports"
  New-Item -ItemType Directory -Path $reportsDir -Force | Out-Null

  $startedAt = (Get-Date -AsUTC).ToString("yyyy-MM-ddTHH:mm:ssZ")

  if (-not $SpotchecksOnly) {
    Write-Host "Applying Option C SQL..."
    & $psql.Path $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/option_c_v0_1.sql
    if ($LASTEXITCODE -ne 0) {
      exit 2
    }
  }

  Write-Host "Registering eval run..."
  $registerSql = @"
insert into derived.eval_runs (run_id, eval_version, formula_hash, horizon_spec, computed_at, notes)
values (:'run_id', :'eval_version', :'formula_hash', :'horizon_spec', now(), :'notes')
on conflict (run_id) do update
set eval_version = excluded.eval_version,
    formula_hash = excluded.formula_hash,
    horizon_spec = excluded.horizon_spec,
    computed_at = excluded.computed_at,
    notes = excluded.notes;
"@
  & $psql.Path $env:DATABASE_URL -v ON_ERROR_STOP=1 `
    -v run_id=$RunId `
    -v eval_version=$evalVersion `
    -v formula_hash=$formulaHash `
    -v horizon_spec=$horizonSpec `
    -v notes=$notes `
    -c $registerSql
  if ($LASTEXITCODE -ne 0) {
    exit 2
  }

  Write-Host "Running Option C spotchecks..."
  $spotcheckFile = Join-Path $reportsDir ("spotchecks_{0}.txt" -f $RunId)
  & $psql.Path $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/option_c_spotchecks.sql | Tee-Object -FilePath $spotcheckFile
  if ($LASTEXITCODE -ne 0) {
    exit 2
  }

  $spotcheckStatus = "PASS"
  $spotcheckReason = "All spotchecks PASS."
  if (Select-String -Path $spotcheckFile -Pattern "FAIL" -Quiet) {
    $spotcheckStatus = "FAIL"
    $spotcheckReason = "Spotcheck output contains FAIL."
  } elseif (Select-String -Path $spotcheckFile -Pattern "WARN" -Quiet) {
    $spotcheckStatus = "WARN"
    $spotcheckReason = "Spotcheck output contains WARN."
  }

  $finishedAt = (Get-Date -AsUTC).ToString("yyyy-MM-ddTHH:mm:ssZ")

  Write-Host "Generating run report..."
  $reportJson = Join-Path $reportsDir ("run_report_{0}.json" -f $RunId)
  $reportContent = & $psql.Path $env:DATABASE_URL -v ON_ERROR_STOP=1 `
    -v run_id=$RunId `
    -v started_at=$startedAt `
    -v finished_at=$finishedAt `
    -v spotcheck_status=$spotcheckStatus `
    -v spotcheck_reason=$spotcheckReason `
    -v strict=$strictValue `
    -t -A -f sql/option_c_run_report.sql
  if ($LASTEXITCODE -ne 0) {
    exit 2
  }
  $reportContent | Set-Content -Path $reportJson -Encoding ascii

  $reportMd = Join-Path $reportsDir ("run_report_{0}.md" -f $RunId)
@"
# Option C Run Report

- run_id: $RunId
- status: $spotcheckStatus
- started_at: $startedAt
- finished_at: $finishedAt
- eval_version: $evalVersion
- formula_hash: $formulaHash
- spotchecks: $spotcheckReason
"@ | Set-Content -Path $reportMd -Encoding ascii

  if ($spotcheckStatus -eq "FAIL") {
    exit 2
  }
  if ($spotcheckStatus -eq "WARN") {
    if ($Strict.IsPresent) {
      exit 2
    }
    exit 1
  }
} catch {
  Write-Error $_
  exit 2
} finally {
  Pop-Location
}
