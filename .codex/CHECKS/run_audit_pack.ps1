param(
  [string]$Label = "auditpack"
)

$stamp = Get-Date -Format "yyyy-MM-dd__HHmmss"
$runLabel = "$stamp`__$Label"

powershell -ExecutionPolicy Bypass -File .codex\CHECKS\snapshot_tree.ps1 -Label $runLabel
powershell -ExecutionPolicy Bypass -File .codex\CHECKS\rg_index.ps1       -Label $runLabel
