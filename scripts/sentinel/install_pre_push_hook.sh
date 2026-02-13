#!/usr/bin/env bash
set -euo pipefail

BEGIN_MARKER="# BEGIN append-sentinel-verify"
END_MARKER="# END append-sentinel-verify"

force=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      force=true
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Usage: scripts/sentinel/install_pre_push_hook.sh [--force]

Installs a managed pre-push hook block that runs:
  python scripts/sentinel/append_sentinel.py --verify

Behavior:
- Existing managed block: no-op.
- Existing unmanaged pre-push hook: installer aborts unless --force is supplied.
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

hook_path=".git/hooks/pre-push"
mkdir -p ".git/hooks"

managed_block="$(cat <<EOF
$BEGIN_MARKER
if command -v python >/dev/null 2>&1; then
  _sentinel_python="python"
elif command -v python3 >/dev/null 2>&1; then
  _sentinel_python="python3"
else
  echo "append-sentinel: python/python3 not found in PATH" >&2
  exit 1
fi
"\${_sentinel_python}" scripts/sentinel/append_sentinel.py --verify
_sentinel_status=\$?
if [[ \$_sentinel_status -ne 0 ]]; then
  echo "append-sentinel verify failed with exit \${_sentinel_status}" >&2
  exit \$_sentinel_status
fi
$END_MARKER
EOF
)"

if [[ -f "$hook_path" ]]; then
  if grep -qF "$BEGIN_MARKER" "$hook_path"; then
    echo "Managed append-sentinel pre-push block already present. No changes made."
    exit 0
  fi
  if [[ "$force" != "true" ]]; then
    echo "Existing unmanaged pre-push hook detected. Re-run with --force to append managed block." >&2
    exit 1
  fi
fi

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
echo "Installed append-sentinel pre-push verify block at $hook_path"
