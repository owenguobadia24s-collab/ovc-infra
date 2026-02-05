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
import {
  initializeSources,
  loadRunRegistrySafe,
  loadOpStatusTableSafe,
  loadExpectedVersionsSafe,
  loadRunEnvelopeSafe,
  loadManifestSafe,
  loadDeltaLogSafe,
  loadActivePointersSafe,
  ParseStatus,
  type LoadResultWithParse
} from '../lib/sources';
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
// Response Helper - Standardized ParseResult responses
// =============================================================================

interface ParseResultResponse {
  status: string;
  value: unknown;
  error: { status: string; path: string; message: string; detail?: string } | null;
  trace: unknown[];
}

/**
 * Respond with a standardized ParseResult shape.
 * Always returns HTTP 200 - the "state" is in the JSON body.
 * No interpretation. Just structured data.
 */
function respondParse<T>(
  res: Response,
  result: LoadResultWithParse<T>
): Response {
  const response: ParseResultResponse = {
    status: result.parseStatus,
    value: result.data ?? null,
    error: result.parseError ? {
      status: result.parseError.code,
      path: result.parseError.path,
      message: result.parseError.message,
      detail: result.parseError.detail
    } : null,
    trace: [result.trace]
  };
  return res.status(200).json(response);
}

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
  const result = loadRunRegistrySafe();
  return respondParse(res, result);
});

// Failures view data
app.get('/api/failures', (_req: Request, res: Response) => {
  const opStatus = loadOpStatusTableSafe();
  const runRegistry = loadRunRegistrySafe();

  // If either has a parse error, report the first error encountered
  if (opStatus.parseStatus !== ParseStatus.OK) {
    return respondParse(res, opStatus);
  }
  if (runRegistry.parseStatus !== ParseStatus.OK) {
    return respondParse(res, runRegistry);
  }

  // Filter to failed runs only
  const failedRuns = (runRegistry.data as ReadonlyArray<{ status?: string }>).filter(
    r => r.status === 'FAIL'
  );

  // Composite response - both OK
  return res.status(200).json({
    status: ParseStatus.OK,
    value: {
      opStatusTable: opStatus.data,
      failedRuns: failedRuns
    },
    error: null,
    trace: [opStatus.trace, runRegistry.trace]
  });
});

// Health view data
app.get('/api/health', (_req: Request, res: Response) => {
  // Load pointers safely for health evidence
  const pointersResult = loadActivePointersSafe();
  
  // Build health evidence from available sources
  const healthResult = determineHealthState({
    pointers: pointersResult.parseStatus === ParseStatus.OK ? pointersResult.data : null,
    driftSignals: null,
    opStatusTable: [],
    sealValidationResults: [],
    governanceArtifactsReadable: true,
    filesystemAccessible: true,
    gitStateReadable: true
  });

  return res.status(200).json({
    status: ParseStatus.OK,
    value: {
      healthState: healthResult.state
    },
    error: null,
    trace: [healthResult.trace, pointersResult.trace]
  });
});

// Governance view data
app.get('/api/governance', (_req: Request, res: Response) => {
  const result = loadExpectedVersionsSafe();
  
  // Return standardized shape with governance-specific value structure
  return res.status(200).json({
    status: result.parseStatus,
    value: result.parseStatus === ParseStatus.OK ? {
      expectedVersions: result.data,
      enforcementLevels: [],
      knownGaps: [],
      sealedRegistries: []
    } : null,
    error: result.parseError ? {
      status: result.parseError.code,
      path: result.parseError.path,
      message: result.parseError.message
    } : null,
    trace: [result.trace]
  });
});

// Diff view data
app.get('/api/diff', (_req: Request, res: Response) => {
  const result = loadDeltaLogSafe();
  return respondParse(res, result);
});

// Artifact detail
app.get('/api/artifacts/:runId', (req: Request, res: Response) => {
  const { runId } = req.params;
  
  const envelopeResult = loadRunEnvelopeSafe(runId);
  const manifestResult = loadManifestSafe(runId);

  // If envelope has a parse error, report it
  if (envelopeResult.parseStatus !== ParseStatus.OK && 
      envelopeResult.parseStatus !== ParseStatus.MISSING) {
    return respondParse(res, envelopeResult);
  }

  // If manifest has a parse error (other than missing), report it
  if (manifestResult.parseStatus !== ParseStatus.OK && 
      manifestResult.parseStatus !== ParseStatus.MISSING) {
    return respondParse(res, manifestResult);
  }

  // If both are missing, report MISSING status
  if (envelopeResult.parseStatus === ParseStatus.MISSING && 
      manifestResult.parseStatus === ParseStatus.MISSING) {
    return res.status(200).json({
      status: ParseStatus.MISSING,
      value: null,
      error: {
        status: ParseStatus.MISSING,
        path: runId,
        message: `Artifacts not found for run: ${runId}`
      },
      trace: [envelopeResult.trace, manifestResult.trace]
    });
  }

  // Return what we have
  return res.status(200).json({
    status: ParseStatus.OK,
    value: {
      runId,
      envelope: envelopeResult.data,
      manifest: manifestResult.data
    },
    error: null,
    trace: [envelopeResult.trace, manifestResult.trace]
  });
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
