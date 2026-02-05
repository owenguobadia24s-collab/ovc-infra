/**
 * Phase 3 Control Panel - Runtime App Component
 *
 * READ-ONLY CONTROL PANEL ROUTER
 *
 * Routes to six read-only views:
 * - /runs - Timeline of all runs
 * - /failures - Aggregated failure view
 * - /artifacts - Artifact drill-down (also /artifacts/:runId)
 * - /diff - Compare two runs
 * - /health - System health state (H0-H9)
 * - /governance - Versions, enforcement, gaps
 *
 * NO WRITES. NO MUTATIONS. NO ACTIONS.
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';

// Import page components
import { RunsPage } from '../app/runs/page';
import { FailuresPage } from '../app/failures/page';
import { HealthPage } from '../app/health/page';
import { GovernancePage } from '../app/governance/page';

// Import types
import { DisplayError } from '../ui/ErrorPanel';
import { SourceTrace } from '../lib/trace';

// =============================================================================
// API Client (GET-only, read-only)
// =============================================================================

async function fetchApi<T>(endpoint: string): Promise<{ data: T | null; error?: DisplayError }> {
  try {
    const response = await fetch(`/api${endpoint}`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });

    if (!response.ok) {
      return {
        data: null,
        error: {
          code: `HTTP_${response.status}`,
          message: `Failed to fetch ${endpoint}`,
          details: response.statusText,
          timestamp: new Date().toISOString()
        }
      };
    }

    const json = await response.json();
    return { data: json };
  } catch (err) {
    return {
      data: null,
      error: {
        code: 'FETCH_ERROR',
        message: 'Failed to connect to server',
        details: err instanceof Error ? err.message : String(err),
        timestamp: new Date().toISOString()
      }
    };
  }
}

// =============================================================================
// Default Trace (for loading/error states)
// =============================================================================

function createDefaultTrace(registryId: string): SourceTrace {
  return {
    registry_id: registryId,
    pointer_file: null,
    active_run_id: null,
    artifact_path: null,
    sealed: false,
    notes: 'Loading...',
    traced_at: new Date().toISOString()
  };
}

// =============================================================================
// View Wrappers (fetch data and render page components)
// =============================================================================

function RunsView(): React.ReactElement {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<DisplayError | undefined>();

  useEffect(() => {
    fetchApi('/runs').then(result => {
      setLoading(false);
      if (result.error) {
        setError(result.error);
      } else {
        setData(result.data);
      }
    });
  }, []);

  return (
    <RunsPage
      runs={data?.runs ?? []}
      trace={data?.trace ?? createDefaultTrace('run_registry')}
      error={error}
      loading={loading}
    />
  );
}

function FailuresView(): React.ReactElement {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<DisplayError | undefined>();

  useEffect(() => {
    fetchApi('/failures').then(result => {
      setLoading(false);
      if (result.error) {
        setError(result.error);
      } else {
        setData(result.data);
      }
    });
  }, []);

  return (
    <FailuresPage
      opStatusTable={data?.opStatusTable ?? []}
      failedRuns={data?.failedRuns ?? []}
      opStatusTrace={data?.opStatusTrace ?? createDefaultTrace('op_status_table')}
      runRegistryTrace={data?.runRegistryTrace ?? createDefaultTrace('run_registry')}
      error={error}
      loading={loading}
    />
  );
}

function HealthView(): React.ReactElement {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<DisplayError | undefined>();

  useEffect(() => {
    fetchApi('/health').then(result => {
      setLoading(false);
      if (result.error) {
        setError(result.error);
      } else {
        setData(result.data);
      }
    });
  }, []);

  return (
    <HealthPage
      healthState={data?.healthState ?? null}
      traces={data?.traces ?? []}
      error={error}
      loading={loading}
    />
  );
}

function GovernanceView(): React.ReactElement {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<DisplayError | undefined>();

  useEffect(() => {
    fetchApi('/governance').then(result => {
      setLoading(false);
      if (result.error) {
        setError(result.error);
      } else {
        setData(result.data);
      }
    });
  }, []);

  return (
    <GovernancePage
      expectedVersions={data?.expectedVersions ?? null}
      enforcementLevels={data?.enforcementLevels ?? []}
      knownGaps={data?.knownGaps ?? []}
      sealedRegistries={data?.sealedRegistries ?? []}
      traces={data?.traces ?? []}
      error={error}
      loading={loading}
    />
  );
}

// Placeholder views for artifacts and diff (require more complex props)
function ArtifactsView(): React.ReactElement {
  return (
    <div style={{ padding: '24px', fontFamily: 'monospace' }}>
      <h1 style={{ color: '#e0e0e0' }}>Artifacts View</h1>
      <p style={{ color: '#888' }}>Select a run from the Runs view to see artifact details.</p>
    </div>
  );
}

function ArtifactDetailView(): React.ReactElement {
  const { runId } = useParams<{ runId: string }>();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<DisplayError | undefined>();

  useEffect(() => {
    if (runId) {
      fetchApi(`/artifacts/${encodeURIComponent(runId)}`).then(result => {
        setLoading(false);
        if (result.error) {
          setError(result.error);
        } else {
          setData(result.data);
        }
      });
    }
  }, [runId]);

  if (loading) {
    return (
      <div style={{ padding: '24px', fontFamily: 'monospace', color: '#888' }}>
        Loading artifact details for {runId}...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '24px', fontFamily: 'monospace' }}>
        <h1 style={{ color: '#f44336' }}>Error Loading Artifact</h1>
        <p style={{ color: '#888' }}>{error.message}</p>
        <pre style={{ color: '#666' }}>{error.details}</pre>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', fontFamily: 'monospace' }}>
      <h1 style={{ color: '#e0e0e0' }}>Artifact: {runId}</h1>
      <pre style={{ color: '#888', whiteSpace: 'pre-wrap' }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}

function DiffView(): React.ReactElement {
  return (
    <div style={{ padding: '24px', fontFamily: 'monospace' }}>
      <h1 style={{ color: '#e0e0e0' }}>Diff View</h1>
      <p style={{ color: '#888' }}>
        Use query parameters to compare runs: /diff?left=RUN_ID_1&amp;right=RUN_ID_2
      </p>
    </div>
  );
}

// =============================================================================
// App Component
// =============================================================================

export function App(): React.ReactElement {
  return (
    <BrowserRouter>
      <Routes>
        {/* Default redirect to runs */}
        <Route path="/" element={<Navigate to="/runs" replace />} />

        {/* Six read-only views */}
        <Route path="/runs" element={<RunsView />} />
        <Route path="/failures" element={<FailuresView />} />
        <Route path="/artifacts" element={<ArtifactsView />} />
        <Route path="/artifacts/:runId" element={<ArtifactDetailView />} />
        <Route path="/diff" element={<DiffView />} />
        <Route path="/health" element={<HealthView />} />
        <Route path="/governance" element={<GovernanceView />} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/runs" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
