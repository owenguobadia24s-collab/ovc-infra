/**
 * Phase 3 Control Panel - Read-Only Server
 *
 * READ-ONLY DATA SERVER
 *
 * This server:
 * - Serves the built Vite UI
 * - Exposes read-only GET endpoints for view data
 * - DENIES all non-GET requests
 * - Reads from PHASE3_REPO_ROOT environment variable
 *
 * NO WRITES. NO MUTATIONS. NO POST/PUT/PATCH/DELETE.
 */

import express, { Request, Response, NextFunction } from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { initializeSources, loadRunRegistry, loadOpStatusTable, loadExpectedVersions } from '../lib/sources';
import { determineHealthState } from '../lib/health_rules';

// ESM-compatible __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// =============================================================================
// Configuration
// =============================================================================

const PORT = process.env.PORT || 3311;
const REPO_ROOT = process.env.PHASE3_REPO_ROOT;

if (!REPO_ROOT) {
  console.error('ERROR: PHASE3_REPO_ROOT environment variable is required.');
  console.error('Set it to the path of your ovc-infra repository.');
  console.error('Example: PHASE3_REPO_ROOT=/path/to/ovc-infra npm run start');
  process.exit(1);
}

// Initialize sources with the repo root
console.log(`Initializing sources from: ${REPO_ROOT}`);
initializeSources(REPO_ROOT);

// =============================================================================
// Express App
// =============================================================================

const app = express();

// =============================================================================
// READ-ONLY ENFORCEMENT: Deny all non-GET requests
// =============================================================================

app.use((req: Request, res: Response, next: NextFunction) => {
  if (req.method !== 'GET' && req.method !== 'HEAD' && req.method !== 'OPTIONS') {
    console.warn(`BLOCKED: ${req.method} ${req.path} - Only GET requests allowed`);
    res.status(405).json({
      error: 'Method Not Allowed',
      message: 'This is a read-only control panel. Only GET requests are permitted.',
      method: req.method
    });
    return;
  }
  next();
});

// =============================================================================
// API Endpoints (GET-only)
// =============================================================================

// Health check
app.get('/api/health-check', (_req: Request, res: Response) => {
  res.json({ status: 'ok', readonly: true, repoRoot: REPO_ROOT });
});

// Runs view data
app.get('/api/runs', (_req: Request, res: Response) => {
  try {
    const result = loadRunRegistry();
    res.json({
      runs: result.data,
      trace: result.trace
    });
  } catch (err) {
    res.status(500).json({
      error: 'Failed to load run registry',
      message: err instanceof Error ? err.message : String(err)
    });
  }
});

// Failures view data
app.get('/api/failures', (_req: Request, res: Response) => {
  try {
    const opStatus = loadOpStatusTable();
    const runRegistry = loadRunRegistry();

    // Filter to failed runs only
    const failedRuns = (runRegistry.data as any[]).filter(r => r.status === 'FAIL');

    res.json({
      opStatusTable: opStatus.data,
      failedRuns: failedRuns,
      opStatusTrace: opStatus.trace,
      runRegistryTrace: runRegistry.trace
    });
  } catch (err) {
    res.status(500).json({
      error: 'Failed to load failure data',
      message: err instanceof Error ? err.message : String(err)
    });
  }
});

// Health view data
app.get('/api/health', (_req: Request, res: Response) => {
  try {
    // Build health evidence from available sources
    const healthResult = determineHealthState({
      pointers: null, // Would need loadActivePointers
      driftSignals: null,
      opStatusTable: [],
      sealValidationResults: [],
      governanceArtifactsReadable: true,
      filesystemAccessible: true,
      gitStateReadable: true
    });

    res.json({
      healthState: healthResult.state,
      traces: [healthResult.trace]
    });
  } catch (err) {
    res.status(500).json({
      error: 'Failed to compute health state',
      message: err instanceof Error ? err.message : String(err)
    });
  }
});

// Governance view data
app.get('/api/governance', (_req: Request, res: Response) => {
  try {
    const expectedVersions = loadExpectedVersions();

    res.json({
      expectedVersions: expectedVersions.data,
      enforcementLevels: [],
      knownGaps: [],
      sealedRegistries: [],
      traces: [expectedVersions.trace]
    });
  } catch (err) {
    res.status(500).json({
      error: 'Failed to load governance data',
      message: err instanceof Error ? err.message : String(err)
    });
  }
});

// Artifact detail
app.get('/api/artifacts/:runId', (req: Request, res: Response) => {
  try {
    const { runId } = req.params;
    // Would use loadRunEnvelope, loadManifest, loadManifestSeal
    res.json({
      runId,
      envelope: null,
      manifest: null,
      seal: null,
      note: 'Artifact detail endpoint - implementation pending'
    });
  } catch (err) {
    res.status(500).json({
      error: 'Failed to load artifact',
      message: err instanceof Error ? err.message : String(err)
    });
  }
});

// =============================================================================
// Static File Serving (built Vite app)
// =============================================================================

const clientDistPath = path.join(__dirname, '../../dist/client');

// Serve static files from the built client
app.use(express.static(clientDistPath));

// SPA fallback - serve index.html for all other routes
app.get('*', (_req: Request, res: Response) => {
  res.sendFile(path.join(clientDistPath, 'index.html'));
});

// =============================================================================
// Start Server
// =============================================================================

app.listen(PORT, () => {
  console.log('');
  console.log('═══════════════════════════════════════════════════════════════');
  console.log('  Phase 3 Control Panel - Read-Only Server');
  console.log('═══════════════════════════════════════════════════════════════');
  console.log(`  Status:    RUNNING`);
  console.log(`  Port:      ${PORT}`);
  console.log(`  Repo Root: ${REPO_ROOT}`);
  console.log(`  Mode:      READ-ONLY (GET requests only)`);
  console.log('');
  console.log('  "Sight without influence"');
  console.log('  No writes. No mutations. No triggers.');
  console.log('═══════════════════════════════════════════════════════════════');
  console.log('');
  console.log(`  Open: http://localhost:${PORT}`);
  console.log('');
});
