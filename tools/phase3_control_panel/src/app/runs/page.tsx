/**
 * Phase 3 Control Panel - Runs View
 *
 * /runs - Timeline of all runs
 *
 * Requirements (per Phase 3 Architecture):
 * - Timeline list with links to drill-down
 * - Deterministic ordering
 * - Trace must include: run_registry pointer source
 * - No action buttons except navigation/filter/sort/search
 *
 * READ-ONLY VIEW. NO WRITES.
 */

import React from 'react';
import { Layout, PageHeader } from '../../ui/Layout';
import { SourceBadge } from '../../ui/SourceBadge';
import { Table, Column, StatusCell, HashCell } from '../../ui/Table';
import { ErrorPanel, DisplayError, LoadingState } from '../../ui/ErrorPanel';
import { RunRegistryEntry } from '../../lib/models';
import { SourceTrace } from '../../lib/trace';

// =============================================================================
// Page Component
// =============================================================================

interface RunsPageProps {
  readonly runs: ReadonlyArray<RunRegistryEntry>;
  readonly trace: SourceTrace;
  readonly error?: DisplayError;
  readonly loading?: boolean;
}

export function RunsPage({
  runs,
  trace,
  error,
  loading = false
}: RunsPageProps): React.ReactElement {
  // Define table columns
  const columns: Column<RunRegistryEntry>[] = [
    {
      key: 'run_id',
      label: 'Run ID',
      sortable: true,
      render: (value, row) => (
        <a
          href={`/artifacts/${row.run_id}`}
          style={{ color: '#4fc3f7', textDecoration: 'none' }}
          title="View artifact details"
        >
          {String(value)}
        </a>
      )
    },
    {
      key: 'operation_id',
      label: 'Operation',
      sortable: true
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      width: '100px',
      render: value => <StatusCell status={String(value)} />
    },
    {
      key: 'indexed_at',
      label: 'Indexed At',
      sortable: true,
      render: value => formatTimestamp(String(value))
    },
    {
      key: 'manifest_sha256',
      label: 'Seal Hash',
      sortable: false,
      width: '120px',
      render: value => <HashCell hash={value as string | null} />
    }
  ];

  // Handle row click - navigation only
  const handleRowClick = (row: RunRegistryEntry): void => {
    window.location.href = `/artifacts/${row.run_id}`;
  };

  return (
    <Layout currentPath="/runs" title="Runs View">
      <PageHeader
        title="Runs Timeline"
        description="All runs indexed in the run registry. Click a row to view artifact details."
      />

      {/* Source trace - REQUIRED */}
      <SourceBadge trace={trace} />

      {/* Error display */}
      {error && <ErrorPanel error={error} />}

      {/* Loading state */}
      {loading && <LoadingState message="Loading run registry..." />}

      {/* Data table */}
      {!loading && !error && (
        <Table
          columns={columns}
          data={runs}
          keyField="run_id"
          emptyMessage="No runs found in registry"
          onRowClick={handleRowClick}
          initialSortKey="indexed_at"
          initialSortDirection="desc"
        />
      )}

      {/* Summary stats */}
      {!loading && !error && runs.length > 0 && (
        <RunsSummary runs={runs} />
      )}
    </Layout>
  );
}

// =============================================================================
// Summary Component
// =============================================================================

interface RunsSummaryProps {
  readonly runs: ReadonlyArray<RunRegistryEntry>;
}

function RunsSummary({ runs }: RunsSummaryProps): React.ReactElement {
  const passCount = runs.filter(r => r.status === 'PASS').length;
  const failCount = runs.filter(r => r.status === 'FAIL').length;
  const otherCount = runs.length - passCount - failCount;

  const operationCounts = new Map<string, number>();
  for (const run of runs) {
    const count = operationCounts.get(run.operation_id) || 0;
    operationCounts.set(run.operation_id, count + 1);
  }

  return (
    <div
      style={{
        marginTop: '24px',
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '16px',
        fontFamily: 'monospace',
        fontSize: '12px'
      }}
    >
      <h4
        style={{
          margin: '0 0 12px 0',
          fontSize: '12px',
          fontWeight: 500,
          color: '#888',
          textTransform: 'uppercase',
          letterSpacing: '1px'
        }}
      >
        Summary
      </h4>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        <SummaryCard label="Total Runs" value={runs.length} />
        <SummaryCard label="Passed" value={passCount} color="#4caf50" />
        <SummaryCard label="Failed" value={failCount} color="#f44336" />
        <SummaryCard label="Other" value={otherCount} color="#9e9e9e" />
      </div>

      <div style={{ marginTop: '16px', color: '#666' }}>
        <span>Operations: </span>
        {Array.from(operationCounts.entries())
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5)
          .map(([op, count], i) => (
            <span key={op}>
              {i > 0 && ', '}
              {op} ({count})
            </span>
          ))}
        {operationCounts.size > 5 && <span> +{operationCounts.size - 5} more</span>}
      </div>
    </div>
  );
}

// =============================================================================
// Summary Card Component
// =============================================================================

interface SummaryCardProps {
  readonly label: string;
  readonly value: number;
  readonly color?: string;
}

function SummaryCard({ label, value, color = '#e0e0e0' }: SummaryCardProps): React.ReactElement {
  return (
    <div>
      <div style={{ color: '#666', fontSize: '11px', marginBottom: '4px' }}>{label}</div>
      <div style={{ color, fontSize: '24px', fontWeight: 500 }}>{value}</div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatTimestamp(iso: string): string {
  try {
    const date = new Date(iso);
    return date.toISOString().replace('T', ' ').substring(0, 19);
  } catch {
    return iso;
  }
}

export default RunsPage;
