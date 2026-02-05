/**
 * Phase 3 Control Panel - Artifact Drill-Down View
 *
 * /artifacts/[run_id] - Sealed artifact details
 *
 * Requirements (per Phase 3 Architecture):
 * - Show run.json, manifest.json, MANIFEST.sha256 links/view
 * - Show hashes and file list
 * - No editing, no upload
 *
 * READ-ONLY VIEW. NO WRITES.
 */

import React from 'react';
import { Layout, PageHeader } from '../../../ui/Layout';
import { SourceBadge } from '../../../ui/SourceBadge';
import { Table, Column, HashCell } from '../../../ui/Table';
import { ErrorPanel, DisplayError, LoadingState, InfoPanel } from '../../../ui/ErrorPanel';
import { SealStatus } from '../../../ui/SourceBadge';
import { RunEnvelope, Manifest, ManifestSeal, ManifestEntry } from '../../../lib/models';
import { SourceTrace } from '../../../lib/trace';

// =============================================================================
// Page Component
// =============================================================================

interface ArtifactPageProps {
  readonly runId: string;
  readonly envelope: RunEnvelope | null;
  readonly manifest: Manifest | null;
  readonly seal: ManifestSeal | null;
  readonly trace: SourceTrace;
  readonly error?: DisplayError;
  readonly loading?: boolean;
}

export function ArtifactPage({
  runId,
  envelope,
  manifest,
  seal,
  trace,
  error,
  loading = false
}: ArtifactPageProps): React.ReactElement {
  const isSealed = manifest !== null && seal !== null;

  return (
    <Layout currentPath="/artifacts" title={`Artifact: ${runId}`}>
      <PageHeader
        title="Artifact Drill-Down"
        description={`Viewing sealed artifacts for run: ${runId}`}
      />

      {/* Source trace - REQUIRED */}
      <SourceBadge trace={trace} />

      {/* Error display */}
      {error && <ErrorPanel error={error} />}

      {/* Loading state */}
      {loading && <LoadingState message="Loading artifact data..." />}

      {!loading && !error && (
        <>
          {/* Seal Status Banner */}
          <SealStatusBanner isSealed={isSealed} seal={seal} />

          {/* Run Envelope Section */}
          <Section title="run.json">
            {envelope ? (
              <RunEnvelopeView envelope={envelope} />
            ) : (
              <InfoPanel
                message="run.json not found"
                details="This run folder does not contain a run.json envelope."
              />
            )}
          </Section>

          {/* Manifest Section */}
          <Section title="manifest.json">
            {manifest ? (
              <ManifestView manifest={manifest} />
            ) : (
              <InfoPanel
                message="manifest.json not found"
                details="This run folder does not contain a manifest."
              />
            )}
          </Section>

          {/* Seal Section */}
          <Section title="MANIFEST.sha256">
            {seal ? (
              <SealView seal={seal} />
            ) : (
              <InfoPanel
                message="MANIFEST.sha256 not found"
                details="This run folder is not sealed."
              />
            )}
          </Section>

          {/* File List Section */}
          <Section title="File List">
            {manifest && manifest.files.length > 0 ? (
              <FileListTable files={manifest.files} />
            ) : (
              <InfoPanel
                message="No files in manifest"
                details="The manifest contains no file entries."
              />
            )}
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
// Seal Status Banner
// =============================================================================

interface SealStatusBannerProps {
  readonly isSealed: boolean;
  readonly seal: ManifestSeal | null;
}

function SealStatusBanner({ isSealed, seal }: SealStatusBannerProps): React.ReactElement {
  return (
    <div
      style={{
        backgroundColor: isSealed ? '#1f2d1f' : '#2d2a1f',
        border: `1px solid ${isSealed ? '#2e5c2e' : '#5c5226'}`,
        borderRadius: '4px',
        padding: '16px',
        marginBottom: '24px',
        fontFamily: 'monospace',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <SealStatus sealed={isSealed} size="large" />
        <span style={{ color: '#e0e0e0', fontSize: '14px' }}>
          {isSealed ? 'This artifact is sealed' : 'This artifact is not sealed'}
        </span>
      </div>
      {seal && (
        <div style={{ color: '#888', fontSize: '12px' }}>
          ROOT_SHA256: <span style={{ color: '#4fc3f7' }}>{seal.root_sha256.substring(0, 16)}...</span>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Run Envelope View
// =============================================================================

interface RunEnvelopeViewProps {
  readonly envelope: RunEnvelope;
}

function RunEnvelopeView({ envelope }: RunEnvelopeViewProps): React.ReactElement {
  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '16px',
        fontFamily: 'monospace',
        fontSize: '12px'
      }}
    >
      <PropertyGrid>
        <Property label="Run ID" value={envelope.run_id} />
        <Property label="Operation ID" value={envelope.operation_id} />
        <Property label="Status" value={envelope.status} highlight />
        <Property label="Started At" value={envelope.started_at} />
        <Property label="Completed At" value={envelope.completed_at || 'N/A'} />
        <Property label="Run Root" value={envelope.run_root} />
        <Property
          label="Manifest SHA256"
          value={envelope.manifest_sha256 ? `${envelope.manifest_sha256.substring(0, 16)}...` : 'N/A'}
        />
      </PropertyGrid>

      {/* Inputs */}
      {envelope.inputs.length > 0 && (
        <SubSection title="Inputs">
          {envelope.inputs.map((input, i) => (
            <div key={i} style={{ marginBottom: '4px', color: '#888' }}>
              <span style={{ color: '#4fc3f7' }}>{input.name}</span>: {input.path}
              {input.sha256 && <span style={{ color: '#666' }}> ({input.sha256.substring(0, 8)}...)</span>}
            </div>
          ))}
        </SubSection>
      )}

      {/* Outputs */}
      {envelope.outputs.length > 0 && (
        <SubSection title="Outputs">
          {envelope.outputs.map((output, i) => (
            <div key={i} style={{ marginBottom: '4px', color: '#888' }}>
              <span style={{ color: '#4fc3f7' }}>{output.name}</span>: {output.path}
              {output.sha256 && <span style={{ color: '#666' }}> ({output.sha256.substring(0, 8)}...)</span>}
            </div>
          ))}
        </SubSection>
      )}

      {/* Reasons */}
      {envelope.reasons.length > 0 && (
        <SubSection title="Reasons (from canon)">
          <ul style={{ margin: 0, paddingLeft: '16px', color: '#ff8a80' }}>
            {envelope.reasons.map((reason, i) => (
              <li key={i}>{reason}</li>
            ))}
          </ul>
        </SubSection>
      )}
    </div>
  );
}

// =============================================================================
// Manifest View
// =============================================================================

interface ManifestViewProps {
  readonly manifest: Manifest;
}

function ManifestView({ manifest }: ManifestViewProps): React.ReactElement {
  const totalBytes = manifest.files.reduce((sum, f) => sum + f.bytes, 0);

  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '16px',
        fontFamily: 'monospace',
        fontSize: '12px'
      }}
    >
      <PropertyGrid>
        <Property label="Manifest Version" value={manifest.manifest_version} />
        <Property label="Run ID" value={manifest.run_id} />
        <Property label="Created At" value={manifest.created_at} />
        <Property label="File Count" value={String(manifest.files.length)} />
        <Property label="Total Size" value={formatBytes(totalBytes)} />
      </PropertyGrid>
    </div>
  );
}

// =============================================================================
// Seal View
// =============================================================================

interface SealViewProps {
  readonly seal: ManifestSeal;
}

function SealView({ seal }: SealViewProps): React.ReactElement {
  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '16px',
        fontFamily: 'monospace',
        fontSize: '12px'
      }}
    >
      <PropertyGrid>
        <Property
          label="ROOT_SHA256"
          value={seal.root_sha256}
          monospace
          copyable
        />
        <Property label="Created At" value={seal.created_at} />
      </PropertyGrid>
    </div>
  );
}

// =============================================================================
// File List Table
// =============================================================================

interface FileListTableProps {
  readonly files: ReadonlyArray<ManifestEntry>;
}

function FileListTable({ files }: FileListTableProps): React.ReactElement {
  const columns: Column<ManifestEntry>[] = [
    {
      key: 'relpath',
      label: 'File Path',
      sortable: true
    },
    {
      key: 'bytes',
      label: 'Size',
      sortable: true,
      width: '100px',
      render: value => formatBytes(value as number)
    },
    {
      key: 'sha256',
      label: 'SHA256',
      sortable: false,
      width: '150px',
      render: value => <HashCell hash={value as string} truncate={12} />
    }
  ];

  return (
    <Table
      columns={columns}
      data={files}
      keyField="relpath"
      emptyMessage="No files in manifest"
      initialSortKey="relpath"
      initialSortDirection="asc"
    />
  );
}

// =============================================================================
// Helper Components
// =============================================================================

function PropertyGrid({ children }: { children: React.ReactNode }): React.ReactElement {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '8px 16px' }}>
      {children}
    </div>
  );
}

interface PropertyProps {
  readonly label: string;
  readonly value: string;
  readonly highlight?: boolean;
  readonly monospace?: boolean;
  readonly copyable?: boolean;
}

function Property({ label, value, highlight, monospace, copyable }: PropertyProps): React.ReactElement {
  const handleCopy = () => {
    if (copyable) {
      navigator.clipboard?.writeText(value);
    }
  };

  return (
    <>
      <span style={{ color: '#666' }}>{label}:</span>
      <span
        style={{
          color: highlight ? '#4caf50' : '#e0e0e0',
          fontFamily: monospace ? 'monospace' : 'inherit',
          cursor: copyable ? 'pointer' : 'default',
          wordBreak: 'break-all'
        }}
        onClick={handleCopy}
        title={copyable ? 'Click to copy' : undefined}
      >
        {value}
      </span>
    </>
  );
}

function SubSection({ title, children }: { title: string; children: React.ReactNode }): React.ReactElement {
  return (
    <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #333' }}>
      <div style={{ color: '#888', fontSize: '11px', marginBottom: '8px', textTransform: 'uppercase' }}>
        {title}
      </div>
      {children}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default ArtifactPage;
