param(
    [Parameter(Mandatory = $true)]
    [string]$DateNy,
    [string]$Symbol = "GBPUSD",
    [string]$TvCsv
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

Push-Location $RepoRoot
try {
    $argsList = @("src/validate_day.py", "--date_ny", $DateNy, "--symbol", $Symbol)
    if ($TvCsv) {
        $argsList += @("--tv-csv", $TvCsv)
    }

    Write-Host "Running validate_day.py for $Symbol on $DateNy"
    Write-Host "python $($argsList -join ' ')"
    & python @argsList
} finally {
    Pop-Location
}
