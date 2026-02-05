/**
 * Phase 3 Control Panel - Diff View
 *
 * /diff - Compare two runs
 *
 * Requirements (per Phase 3 Architecture):
 * - Compare two user-selected run_ids (GET params only)
 * - Show manifest diffs + registry delta record if exists
 * - Explicitly state: "Delta log is explanatory only."
 *
 * READ-ONLY VIEW. NO WRITES.
 */

import React, { useState } from 'react';
import { Layout, PageHeader } from '../../ui/Layout';
import { SourceBadge, SourceTracePanel } from '../../ui/SourceBadge';
import { Table, Column, HashCell } from '../../ui/Table';
import { ErrorPanel, DisplayError, LoadingState, InfoPanel, WarningPanel } from '../../ui/ErrorPanel';
import { ManifestDiff, ManifestEntry, ManifestEntryChange, DeltaLogEntry } from '../../lib/models';
import { SourceTrace } from '../../lib/trace';

// =============================================================================
// Page Component
// =============================================================================

interface DiffPageProps {
  readonly leftRunId: string | null;
  readonly rightRunId: string | null;
  readonly diff: ManifestDiff | null;
  readonly deltaLogEntry: DeltaLogEntry | null;
  readonly traces: ReadonlyArray<SourceTrace>;
  readonly availableRunIds: ReadonlyArray<string>;
  readonly error?: DisplayError;
  readonly loading?: boolean;
  readonly onSelectRuns?: (leftId: string, rightId: string) => void;
}

export function DiffPage({
  leftRunId,
  rightRunId,
  diff,
  deltaLogEntry,
  traces,
  availableRunIds,
  error,
  loading = false,
  onSelectRuns
}: DiffPageProps): React.ReactElement {
  const [selectedLeft, setSelectedLeft] = useState(leftRunId || '');
  const [selectedRight, setSelectedRight] = useState(rightRunId || '');

  // Handle compare - navigation only (GET params)
  const handleCompare = () => {
    if (selectedLeft && selectedRight && onSelectRuns) {
      onSelectRuns(selectedLeft, selectedRight);
    } else if (selectedLeft && selectedRight) {
      // Fallback: navigate via GET params
      window.location.href = `/diff?left=${encodeURIComponent(selectedLeft)}&right=${encodeURIComponent(selectedRight)}`;
    }
  };

  return (
    <Layout currentPath="/diff" title="Diff View">
      <PageHeader
        title="Run Diff Comparison"
        description="Compare two sealed runs. Shows manifest structural diffs and delta log records."
      />

      {/* MANDATORY Warning */}
      <WarningPanel
        message="Delta log is explanatory only"
        details="The delta log explains what changed between snapshots. It does NOT drive control, trigger actions, or update pointers."
      />

      {/* Run Selection */}
      <RunSelector
        availableRunIds={availableRunIds}
        selectedLeft={selectedLeft}
        selectedRight={selectedRight}
        onLeftChange={setSelectedLeft}
        onRightChange={setSelectedRight}
        onCompare={handleCompare}
      />

      {/* Source traces - REQUIRED */}
      {traces.length > 0 && (
        <SourceTracePanel traces={traces} title="Comparison Sources" />
      )}

      {/* Error display */}
      {error && <ErrorPanel error={error} />}

      {/* Loading state */}
      {loading && <LoadingState message="Computing diff..." />}

      {/* Diff results */}
      {!loading && !error && diff && leftRunId && rightRunId && (
        <>
          {/* Diff Summary */}
          <DiffSummary
            leftRunId={leftRunId}
            rightRunId={rightRunId}
            diff={diff}
          />

          {/* Delta Log Entry (if exists) */}
          {deltaLogEntry && (
            <Section title="Delta Log Record (Explanatory Only)">
              <DeltaLogView entry={deltaLogEntry} />
            </Section>
          )}

          {/* Added Files */}
          <Section title={`Added Files (${diff.added.length})`}>
            {diff.added.length > 0 ? (
              <AddedFilesTable files={diff.added} />
            ) : (
              <InfoPanel message="No files added" />
            )}
          </Section>

          {/* Removed Files */}
          <Section title={`Removed Files (${diff.removed.length})`}>
            {diff.removed.length > 0 ? (
              <RemovedFilesTable files={diff.removed} />
            ) : (
              <InfoPanel message="No files removed" />
            )}
          </Section>

          {/* Changed Files */}
          <Section title={`Changed Files (${diff.changed.length})`}>
            {diff.changed.length > 0 ? (
              <ChangedFilesTable changes={diff.changed} />
            ) : (
              <InfoPanel message="No files changed" />
            )}
          </Section>
        </>
      )}

      {/* No comparison yet */}
      {!loading && !error && !diff && (
        <InfoPanel
          message="Select two runs to compare"
          details="Choose a left and right run ID from the dropdowns above, then click Compare."
        />
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
// Run Selector
// =============================================================================

interface RunSelectorProps {
  readonly availableRunIds: ReadonlyArray<string>;
  readonly selectedLeft: string;
  readonly selectedRight: string;
  readonly onLeftChange: (id: string) => void;
  readonly onRightChange: (id: string) => void;
  readonly onCompare: () => void;
}

function RunSelector({
  availableRunIds,
  selectedLeft,
  selectedRight,
  onLeftChange,
  onRightChange,
  onCompare
}: RunSelectorProps): React.ReactElement {
  const selectStyle: React.CSSProperties = {
    padding: '8px 12px',
    backgroundColor: '#1a1a2e',
    border: '1px solid #333',
    borderRadius: '4px',
    color: '#e0e0e0',
    fontFamily: 'monospace',
    fontSize: '12px',
    minWidth: '300px'
  };

  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '16px',
        marginBottom: '24px'
      }}
    >
      <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
        <div>
          <label
            style={{
              display: 'block',
              color: '#888',
              fontSize: '11px',
              marginBottom: '4px',
              fontFamily: 'monospace',
              textTransform: 'uppercase'
            }}
          >
            Left Run (older)
          </label>
          <select
            value={selectedLeft}
            onChange={e => onLeftChange(e.target.value)}
            style={selectStyle}
            aria-label="Select left run for comparison"
          >
            <option value="">Select run...</option>
            {availableRunIds.map(id => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            style={{
              display: 'block',
              color: '#888',
              fontSize: '11px',
              marginBottom: '4px',
              fontFamily: 'monospace',
              textTransform: 'uppercase'
            }}
          >
            Right Run (newer)
          </label>
          <select
            value={selectedRight}
            onChange={e => onRightChange(e.target.value)}
            style={selectStyle}
            aria-label="Select right run for comparison"
          >
            <option value="">Select run...</option>
            {availableRunIds.map(id => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
        </div>

        {/* Navigation button only - triggers GET request */}
        <a
          href={
            selectedLeft && selectedRight
              ? `/diff?left=${encodeURIComponent(selectedLeft)}&right=${encodeURIComponent(selectedRight)}`
              : '#'
          }
          style={{
            padding: '8px 16px',
            backgroundColor: selectedLeft && selectedRight ? '#4fc3f7' : '#333',
            color: selectedLeft && selectedRight ? '#000' : '#666',
            border: 'none',
            borderRadius: '4px',
            fontFamily: 'monospace',
            fontSize: '12px',
            textDecoration: 'none',
            cursor: selectedLeft && selectedRight ? 'pointer' : 'not-allowed'
          }}
          aria-disabled={!selectedLeft || !selectedRight}
        >
          Compare
        </a>
      </div>

      <div style={{ marginTop: '8px', color: '#666', fontSize: '11px' }}>
        Comparison uses GET parameters only. No state mutation.
      </div>
    </div>
  );
}

// =============================================================================
// Diff Summary
// =============================================================================

interface DiffSummaryProps {
  readonly leftRunId: string;
  readonly rightRunId: string;
  readonly diff: ManifestDiff;
}

function DiffSummary({ leftRunId, rightRunId, diff }: DiffSummaryProps): React.ReactElement {
  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '16px',
        marginBottom: '24px',
        fontFamily: 'monospace'
      }}
    >
      <div style={{ display: 'flex', gap: '24px', marginBottom: '16px' }}>
        <div>
          <div style={{ color: '#666', fontSize: '11px' }}>Left (older)</div>
          <div style={{ color: '#e0e0e0', fontSize: '12px' }}>{leftRunId}</div>
        </div>
        <div style={{ color: '#666', fontSize: '20px' }}>\u2192</div>
        <div>
          <div style={{ color: '#666', fontSize: '11px' }}>Right (newer)</div>
          <div style={{ color: '#e0e0e0', fontSize: '12px' }}>{rightRunId}</div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '32px' }}>
        <StatBox label="Added" value={diff.added.length} color="#4caf50" />
        <StatBox label="Removed" value={diff.removed.length} color="#f44336" />
        <StatBox label="Changed" value={diff.changed.length} color="#ff9800" />
      </div>
    </div>
  );
}

interface StatBoxProps {
  readonly label: string;
  readonly value: number;
  readonly color: string;
}

function StatBox({ label, value, color }: StatBoxProps): React.ReactElement {
  return (
    <div>
      <div style={{ color: '#666', fontSize: '11px' }}>{label}</div>
      <div style={{ color, fontSize: '24px', fontWeight: 500 }}>{value}</div>
    </div>
  );
}

// =============================================================================
// Delta Log View
// =============================================================================

interface DeltaLogViewProps {
  readonly entry: DeltaLogEntry;
}

function DeltaLogView({ entry }: DeltaLogViewProps): React.ReactElement {
  return (
    <div
      style={{
        backgroundColor: '#1a2a1a',
        border: '1px solid #2e5c2e',
        borderRadius: '4px',
        padding: '16px',
        fontFamily: 'monospace',
        fontSize: '12px'
      }}
    >
      {/* Explanatory notice */}
      <div
        style={{
          backgroundColor: '#0f1a0f',
          padding: '8px',
          borderRadius: '4px',
          marginBottom: '12px',
          color: '#888',
          fontSize: '11px',
          fontStyle: 'italic'
        }}
      >
        Delta log is explanatory only \u2014 it does not drive control.
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '6px 16px', color: '#e0e0e0' }}>
        <span style={{ color: '#666' }}>Delta Version:</span>
        <span>{entry.delta_version}</span>

        <span style={{ color: '#666' }}>Registry:</span>
        <span>{entry.registry_id}</span>

        <span style={{ color: '#666' }}>Delta Basis:</span>
        <span>{entry.delta_basis}</span>

        <span style={{ color: '#666' }}>From Run:</span>
        <span>{entry.from_ref?.run_id || 'N/A (bootstrap)'}</span>

        <span style={{ color: '#666' }}>To Run:</span>
        <span>{entry.to_ref.run_id}</span>

        <span style={{ color: '#666' }}>Created:</span>
        <span>{entry.created_utc}</span>
      </div>

      {/* Diff summary from delta log */}
      <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #2e5c2e' }}>
        <div style={{ color: '#888', fontSize: '11px', marginBottom: '8px' }}>
          Delta Summary:
        </div>
        <div style={{ color: '#81c784' }}>
          +{entry.counts.added} added,{' '}
          <span style={{ color: '#ff8a80' }}>
            -{entry.counts.removed} removed,{' '}
          </span>
          <span style={{ color: '#ffcc80' }}>
            ~{entry.counts.modified} changed
          </span>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// File Tables
// =============================================================================

function AddedFilesTable({ files }: { files: ReadonlyArray<ManifestEntry> }): React.ReactElement {
  const columns: Column<ManifestEntry>[] = [
    { key: 'relpath', label: 'File Path', sortable: true },
    { key: 'bytes', label: 'Size', sortable: true, width: '100px', render: v => formatBytes(v as number) },
    { key: 'sha256', label: 'SHA256', sortable: false, width: '120px', render: v => <HashCell hash={v as string} /> }
  ];

  return <Table columns={columns} data={files} keyField="relpath" initialSortKey="relpath" />;
}

function RemovedFilesTable({ files }: { files: ReadonlyArray<ManifestEntry> }): React.ReactElement {
  const columns: Column<ManifestEntry>[] = [
    { key: 'relpath', label: 'File Path', sortable: true },
    { key: 'bytes', label: 'Size', sortable: true, width: '100px', render: v => formatBytes(v as number) },
    { key: 'sha256', label: 'SHA256', sortable: false, width: '120px', render: v => <HashCell hash={v as string} /> }
  ];

  return <Table columns={columns} data={files} keyField="relpath" initialSortKey="relpath" />;
}

function ChangedFilesTable({ changes }: { changes: ReadonlyArray<ManifestEntryChange> }): React.ReactElement {
  const columns: Column<ManifestEntryChange>[] = [
    { key: 'relpath', label: 'File Path', sortable: true },
    {
      key: 'left',
      label: 'Left Hash',
      sortable: false,
      width: '120px',
      render: (_, row) => <HashCell hash={row.left.sha256} />
    },
    {
      key: 'right',
      label: 'Right Hash',
      sortable: false,
      width: '120px',
      render: (_, row) => <HashCell hash={row.right.sha256} />
    },
    {
      key: 'bytes_diff',
      label: 'Size Change',
      sortable: false,
      width: '100px',
      render: (_, row) => {
        const diff = row.right.bytes - row.left.bytes;
        const sign = diff >= 0 ? '+' : '';
        return <span style={{ color: diff >= 0 ? '#81c784' : '#ff8a80' }}>{sign}{formatBytes(Math.abs(diff))}</span>;
      }
    }
  ];

  return <Table columns={columns} data={changes} keyField="relpath" initialSortKey="relpath" />;
}

// =============================================================================
// Helpers
// =============================================================================

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(Math.abs(bytes)) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default DiffPage;
