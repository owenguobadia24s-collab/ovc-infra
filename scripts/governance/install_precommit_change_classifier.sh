#!/usr/bin/env bash
set -euo pipefail

BEGIN_MARKER="# BEGIN change-classifier"
END_MARKER="# END change-classifier"

force=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      force=true
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Usage: scripts/governance/install_precommit_change_classifier.sh [--force]

Installs a managed pre-commit hook block that runs:
  python scripts/governance/classify_change.py --staged

Behavior:
- Does not overwrite existing hook content.
- If an unmanaged pre-commit hook exists, installation bails unless --force is passed.
- If a managed block already exists, no change is made.
EOF
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$repo_root" ]]; then
  echo "ERROR: not inside a git repository" >&2
  exit 1
fi
cd "$repo_root"

hook_path=".git/hooks/pre-commit"
mkdir -p ".git/hooks"

managed_block="$(cat <<'EOF'
# BEGIN change-classifier
if command -v python >/dev/null 2>&1; then
  _classifier_python="python"
elif command -v python3 >/dev/null 2>&1; then
  _classifier_python="python3"
else
  echo "change-classifier: python/python3 not found in PATH" >&2
  exit 1
fi
"${_classifier_python}" scripts/governance/classify_change.py --staged
_classifier_status=$?
if [[ $_classifier_status -ne 0 ]]; then
  echo "change-classifier failed with exit ${_classifier_status}" >&2
  exit $_classifier_status
fi
# END change-classifier
EOF
)"

echo "Pre-commit change-classifier installer"
echo "Repository: $repo_root"
echo "Target hook: $hook_path"
echo "Action: install managed block for staged classification"
echo

if [[ -f "$hook_path" ]]; then
  if grep -qF "$BEGIN_MARKER" "$hook_path"; then
    echo "Managed change-classifier block already present. No changes made."
    exit 0
  fi

  if [[ "$force" != "true" ]]; then
    echo "Existing unmanaged pre-commit hook detected."
    echo "No changes made."
    echo "Re-run with --force to append the managed block safely."
    exit 1
  fi
fi

printf "Install managed pre-commit change-classifier block now? [y/N] "
read -r reply
case "${reply:-}" in
  y|Y|yes|YES)
    ;;
  *)
    echo "Cancelled. No changes made."
    exit 0
    ;;
esac

if [[ ! -f "$hook_path" ]]; then
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    echo
    echo "$managed_block"
    echo
  } > "$hook_path"
else
  {
    echo
    echo "$managed_block"
    echo
  } >> "$hook_path"
fi

chmod +x "$hook_path"
echo "Installed managed change-classifier block in $hook_path"
