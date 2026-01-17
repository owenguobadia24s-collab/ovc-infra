# Secrets and Environment

## Required
- `DATABASE_URL`
  - GitHub Actions secret: `DATABASE_URL`
  - Local environment variable: `DATABASE_URL`

## Optional (Future)
- R2 credentials (for artifact mirroring)
- Notification webhook URL

## Local Execution

Mac/Linux:

```bash
export DATABASE_URL='postgresql://user:pass@host/db'
./scripts/run_option_c.sh --run-id test_local
```

Windows (PowerShell):

```powershell
$env:DATABASE_URL = 'postgresql://user:pass@host/db'
.\scripts\run_option_c.ps1 -RunId test_local
```
