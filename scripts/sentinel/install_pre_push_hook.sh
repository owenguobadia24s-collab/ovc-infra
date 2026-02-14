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

Installs a managed pre-push hook block that runs on maintenance/sentinel only:
  python scripts/sentinel/append_sentinel.py --verify

Behavior:
- Existing managed block: replaced in-place with current managed content.
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
_sentinel_branch="\$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
if [[ "\$_sentinel_branch" != "maintenance/sentinel" ]]; then
  exit 0
fi

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

has_managed=false
if [[ -f "$hook_path" ]] && grep -qF "$BEGIN_MARKER" "$hook_path"; then
  has_managed=true
fi

if [[ -f "$hook_path" && "$has_managed" != "true" && "$force" != "true" ]]; then
  echo "Existing unmanaged pre-push hook detected. Re-run with --force to append managed block." >&2
  exit 1
fi

if [[ "$force" == "true" ]]; then
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    echo
    echo "$managed_block"
    echo
  } > "$hook_path"
elif [[ ! -f "$hook_path" ]]; then
  {
    echo "#!/usr/bin/env bash"
    echo "set -euo pipefail"
    echo
    echo "$managed_block"
    echo
  } > "$hook_path"
elif [[ "$has_managed" == "true" ]]; then
  tmp_file="$(mktemp)"
  awk -v begin="$BEGIN_MARKER" -v end="$END_MARKER" '
    $0 == begin { in_block=1; next }
    $0 == end { in_block=0; next }
    !in_block { print }
  ' "$hook_path" > "$tmp_file"

  {
    cat "$tmp_file"
    echo
    echo "$managed_block"
    echo
  } > "$hook_path"
  rm -f "$tmp_file"
else
  {
    echo
    echo "$managed_block"
    echo
  } >> "$hook_path"
fi

if [[ ! -f "$hook_path" ]]; then
  echo "ERROR: failed to write $hook_path" >&2
  exit 1
fi

if ! grep -qF "$BEGIN_MARKER" "$hook_path" || ! grep -qF "$END_MARKER" "$hook_path"; then
  echo "ERROR: managed block markers missing after install" >&2
    exit 1
fi

chmod +x "$hook_path"
echo "Installed/updated append-sentinel pre-push verify block at $hook_path"
