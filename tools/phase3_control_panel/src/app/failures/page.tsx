/**
 * Phase 3 Control Panel - Failures View
 *
 * /failures - Aggregated failure view
 *
 * Requirements (per Phase 3 Architecture):
 * - Aggregations from canon fields only
 * - No inferred "cause" language
 * - Trace must include: op_status_table source
 * - No action buttons except navigation/filter/sort/search
 *
 * READ-ONLY VIEW. NO WRITES.
 */

import React from 'react';
import { Layout, PageHeader } from '../../ui/Layout';
import { SourceBadge, SourceTracePanel } from '../../ui/SourceBadge';
import { Table, Column, StatusCell } from '../../ui/Table';
import { ErrorPanel, DisplayError, LoadingState, WarningPanel } from '../../ui/ErrorPanel';
import { OperationStatusEntry, RunRegistryEntry, FailureAggregate } from '../../lib/models';
import { SourceTrace } from '../../lib/trace';

// =============================================================================
// Page Component
// =============================================================================

interface FailuresPageProps {
  readonly opStatusTable: ReadonlyArray<OperationStatusEntry>;
  readonly failedRuns: ReadonlyArray<RunRegistryEntry>;
  readonly opStatusTrace: SourceTrace;
  readonly runRegistryTrace: SourceTrace;
  readonly error?: DisplayError;
  readonly loading?: boolean;
}

export function FailuresPage({
  opStatusTable,
  failedRuns,
  opStatusTrace,
  runRegistryTrace,
  error,
  loading = false
}: FailuresPageProps): React.ReactElement {
  // Aggregate failures by operation
  const aggregates = aggregateFailures(failedRuns);

  // Find operations with FAIL status in op_status_table
  const failedOps = opStatusTable.filter(op => op.last_run_status === 'FAIL');

  return (
    <Layout currentPath="/failures" title="Failures View">
      <PageHeader
        title="Failure Aggregations"
        description="Aggregated failures from canonical sources. No inferred causes - only observed reasons from run.json."
      />

      {/* Source traces - REQUIRED */}
      <SourceTracePanel
        traces={[opStatusTrace, runRegistryTrace]}
        title="Data Sources"
      />

      {/* Warning about interpretation */}
      <WarningPanel
        message="Failure reasons shown are from canonical fields only"
        details="This view does not infer causes. Reasons are extracted directly from the 'reasons' field in run.json outputs."
      />

      {/* Error display */}
      {error && <ErrorPanel error={error} />}

      {/* Loading state */}
      {loading && <LoadingState message="Loading failure data..." />}

      {/* Operations with failures */}
      {!loading && !error && (
        <>
          <Section title="Operations with Failed Runs">
            <FailedOperationsTable operations={failedOps} />
          </Section>

          <Section title="Failure Aggregations by Operation">
            <FailureAggregatesTable aggregates={aggregates} />
          </Section>

          <Section title="Recent Failed Runs">
            <FailedRunsTable runs={failedRuns.slice(0, 20)} />
          </Section>
        </>
      )}
    </Layout>
  );
}

// =============================================================================
// Section Component
// =============================================================================

interface SectionProps {
  readonly title: string;
  readonly children: React.ReactNode;
}

function Section({ title, children }: SectionProps): React.ReactElement {
  return (
    <div style={{ marginBottom: '32px' }}>
      <h3
        style={{
          margin: '0 0 16px 0',
          fontSize: '14px',
          fontWeight: 500,
          color: '#e0e0e0',
          fontFamily: 'monospace',
          paddingBottom: '8px',
          borderBottom: '1px solid #333'
        }}
      >
        {title}
      </h3>
      {children}
    </div>
  );
}

// =============================================================================
// Failed Operations Table
// =============================================================================

interface FailedOperationsTableProps {
  readonly operations: ReadonlyArray<OperationStatusEntry>;
}

function FailedOperationsTable({ operations }: FailedOperationsTableProps): React.ReactElement {
  const columns: Column<OperationStatusEntry>[] = [
    {
      key: 'operation_id',
      label: 'Operation ID',
      sortable: true
    },
    {
      key: 'operation_name',
      label: 'Name',
      sortable: true
    },
    {
      key: 'last_run_status',
      label: 'Status',
      sortable: true,
      width: '100px',
      render: value => <StatusCell status={String(value)} />
    },
    {
      key: 'last_run_at',
      label: 'Last Run At',
      sortable: true,
      render: value => formatTimestamp(value as string | null)
    },
    {
      key: 'enforcement_level',
      label: 'Enforcement',
      sortable: true,
      width: '100px'
    },
    {
      key: 'last_run_id',
      label: 'Run ID',
      sortable: false,
      render: (value, row) => (
        <a
          href={`/artifacts/${row.last_run_id}`}
          style={{ color: '#4fc3f7', textDecoration: 'none' }}
        >
          {truncateRunId(value as string | null)}
        </a>
      )
    }
  ];

  if (operations.length === 0) {
    return (
      <div
        style={{
          backgroundColor: '#1f2d1f',
          border: '1px solid #2e5c2e',
          borderRadius: '4px',
          padding: '16px',
          fontFamily: 'monospace',
          fontSize: '13px',
          color: '#81c784'
        }}
      >
        No operations with FAIL status
      </div>
    );
  }

  return (
    <Table
      columns={columns}
      data={operations}
      keyField="operation_id"
      emptyMessage="No failed operations"
      initialSortKey="last_run_at"
      initialSortDirection="desc"
    />
  );
}

// =============================================================================
// Failure Aggregates Table
// =============================================================================

interface FailureAggregatesTableProps {
  readonly aggregates: ReadonlyArray<FailureAggregate>;
}

function FailureAggregatesTable({ aggregates }: FailureAggregatesTableProps): React.ReactElement {
  const columns: Column<FailureAggregate>[] = [
    {
      key: 'operation_id',
      label: 'Operation ID',
      sortable: true
    },
    {
      key: 'failure_count',
      label: 'Failure Count',
      sortable: true,
      width: '120px',
      render: value => (
        <span style={{ color: value as number > 0 ? '#ff8a80' : '#81c784' }}>
          {String(value)}
        </span>
      )
    },
    {
      key: 'last_failure_at',
      label: 'Last Failure',
      sortable: true,
      render: value => formatTimestamp(value as string | null)
    },
    {
      key: 'reasons',
      label: 'Observed Reasons (from canon)',
      sortable: false,
      render: value => {
        const reasons = value as string[];
        if (!reasons || reasons.length === 0) {
          return <span style={{ color: '#666' }}>No reasons recorded</span>;
        }
        return (
          <ul style={{ margin: 0, paddingLeft: '16px', color: '#888' }}>
            {reasons.slice(0, 3).map((reason, i) => (
              <li key={i} style={{ fontSize: '11px' }}>
                {reason}
              </li>
            ))}
            {reasons.length > 3 && (
              <li style={{ fontSize: '11px', color: '#666' }}>
                +{reasons.length - 3} more reasons
              </li>
            )}
          </ul>
        );
      }
    }
  ];

  if (aggregates.length === 0) {
    return (
      <div
        style={{
          backgroundColor: '#1f2d1f',
          border: '1px solid #2e5c2e',
          borderRadius: '4px',
          padding: '16px',
          fontFamily: 'monospace',
          fontSize: '13px',
          color: '#81c784'
        }}
      >
        No failures to aggregate
      </div>
    );
  }

  return (
    <Table
      columns={columns}
      data={aggregates}
      keyField="operation_id"
      emptyMessage="No failure aggregates"
      initialSortKey="failure_count"
      initialSortDirection="desc"
    />
  );
}

// =============================================================================
// Failed Runs Table
// =============================================================================

interface FailedRunsTableProps {
  readonly runs: ReadonlyArray<RunRegistryEntry>;
}

function FailedRunsTable({ runs }: FailedRunsTableProps): React.ReactElement {
  const columns: Column<RunRegistryEntry>[] = [
    {
      key: 'run_id',
      label: 'Run ID',
      sortable: true,
      render: (value, row) => (
        <a
          href={`/artifacts/${row.run_id}`}
          style={{ color: '#4fc3f7', textDecoration: 'none' }}
        >
          {truncateRunId(String(value))}
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
      sortable: false,
      width: '80px',
      render: value => <StatusCell status={String(value)} />
    },
    {
      key: 'indexed_at',
      label: 'Indexed At',
      sortable: true,
      render: value => formatTimestamp(String(value))
    }
  ];

  return (
    <Table
      columns={columns}
      data={runs}
      keyField="run_id"
      emptyMessage="No failed runs"
      initialSortKey="indexed_at"
      initialSortDirection="desc"
    />
  );
}

// =============================================================================
// Helpers
// =============================================================================

function aggregateFailures(runs: ReadonlyArray<RunRegistryEntry>): FailureAggregate[] {
  const aggregateMap = new Map<string, FailureAggregate>();

  for (const run of runs) {
    if (run.status !== 'FAIL') continue;

    const existing = aggregateMap.get(run.operation_id);
    if (existing) {
      aggregateMap.set(run.operation_id, {
        ...existing,
        failure_count: existing.failure_count + 1,
        last_failure_at:
          run.indexed_at > (existing.last_failure_at || '')
            ? run.indexed_at
            : existing.last_failure_at
      });
    } else {
      aggregateMap.set(run.operation_id, {
        operation_id: run.operation_id,
        failure_count: 1,
        last_failure_at: run.indexed_at,
        reasons: [] // Would need to load run.json for reasons
      });
    }
  }

  return Array.from(aggregateMap.values()).sort((a, b) => b.failure_count - a.failure_count);
}

function formatTimestamp(iso: string | null): string {
  if (!iso) return '\u2014';
  try {
    const date = new Date(iso);
    return date.toISOString().replace('T', ' ').substring(0, 19);
  } catch {
    return iso;
  }
}

function truncateRunId(runId: string | null): string {
  if (!runId) return '\u2014';
  if (runId.length <= 40) return runId;
  return runId.substring(0, 37) + '...';
}

export default FailuresPage;
