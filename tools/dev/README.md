# Codex Unittest Runner

## Purpose

This runner mitigates Codex wrapper hangs by always emitting durable completion artifacts for unittest runs.

## Usage

```powershell
pwsh -NoProfile -NonInteractive -File tools/dev/codex_unittest.ps1
pwsh -NoProfile -NonInteractive -File tools/dev/codex_unittest.ps1 -Target tests.test_audit_interpreter_change_classification
```

## Artifacts

- `.codex/_unittest_last.txt`
- `.codex/_unittest_done.txt`
