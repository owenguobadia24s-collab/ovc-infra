/**
 * Phase 3 Control Panel - Governance Visibility View
 *
 * /governance - Versions, enforcement, gaps
 *
 * Requirements (per Phase 3 Architecture):
 * - Display active versions, enforcement levels, known gaps
 * - Sources: expected versions + enforcement matrix + scorecard
 * - No recalculation of enforcement
 *
 * READ-ONLY VIEW. NO WRITES.
 */

import React from 'react';
import { Layout, PageHeader } from '../../ui/Layout';
import { SourceTracePanel } from '../../ui/SourceBadge';
import { Table, Column } from '../../ui/Table';
import { ErrorPanel, DisplayError, LoadingState, InfoPanel } from '../../ui/ErrorPanel';
import { SealStatus } from '../../ui/SourceBadge';
import {
  ExpectedVersions,
  EnforcementLevel,
  GovernanceGap,
  SealedRegistryStatus
} from '../../lib/models';
import { SourceTrace } from '../../lib/trace';

// =============================================================================
// Page Component
// =============================================================================

interface GovernancePageProps {
  readonly expectedVersions: ExpectedVersions | null;
  readonly enforcementLevels: ReadonlyArray<EnforcementLevel>;
  readonly knownGaps: ReadonlyArray<GovernanceGap>;
  readonly sealedRegistries: ReadonlyArray<SealedRegistryStatus>;
  readonly traces: ReadonlyArray<SourceTrace>;
  readonly error?: DisplayError;
  readonly loading?: boolean;
}

export function GovernancePage({
  expectedVersions,
  enforcementLevels,
  knownGaps,
  sealedRegistries,
  traces,
  error,
  loading = false
}: GovernancePageProps): React.ReactElement {
  return (
    <Layout currentPath="/governance" title="Governance Visibility View">
      <PageHeader
        title="Governance Visibility"
        description="Active versions, enforcement levels, and known gaps. No recalculation - values are read from governance documents."
      />

      {/* Source traces - REQUIRED */}
      {traces.length > 0 && (
        <SourceTracePanel traces={traces} title="Governance Sources" />
      )}

      {/* Error display */}
      {error && <ErrorPanel error={error} />}

      {/* Loading state */}
      {loading && <LoadingState message="Loading governance data..." />}

      {!loading && !error && (
        <>
          {/* Expected Versions */}
          <Section title="Active Versions">
            {expectedVersions ? (
              <ExpectedVersionsView versions={expectedVersions} />
            ) : (
              <InfoPanel
                message="Expected versions not available"
                details="Could not load EXPECTED_VERSIONS_v0_1.json"
              />
            )}
          </Section>

          {/* Sealed Registries Status */}
          <Section title="Registry Seal Status">
            <SealedRegistriesTable registries={sealedRegistries} />
          </Section>

          {/* Enforcement Levels */}
          <Section title="Enforcement Levels">
            <EnforcementLevelsTable levels={enforcementLevels} />
          </Section>

          {/* Known Gaps */}
          <Section title="Known Governance Gaps">
            <KnownGapsTable gaps={knownGaps} />
          </Section>

          {/* Governance Summary */}
          <Section title="Governance Summary">
            <GovernanceSummary
              sealedRegistries={sealedRegistries}
              enforcementLevels={enforcementLevels}
              knownGaps={knownGaps}
            />
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
// Expected Versions View
// =============================================================================

interface ExpectedVersionsViewProps {
  readonly versions: ExpectedVersions;
}

function ExpectedVersionsView({ versions }: ExpectedVersionsViewProps): React.ReactElement {
  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '16px',
        fontFamily: 'monospace'
      }}
    >
      <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '12px 24px' }}>
        <span style={{ color: '#666' }}>Schema Version:</span>
        <span
          style={{
            color: '#4fc3f7',
            backgroundColor: '#16213e',
            padding: '2px 8px',
            borderRadius: '3px'
          }}
        >
          {versions.expected.schema_version}
        </span>

        <span style={{ color: '#666' }}>Threshold Pack Version:</span>
        <span
          style={{
            color: '#4fc3f7',
            backgroundColor: '#16213e',
            padding: '2px 8px',
            borderRadius: '3px'
          }}
        >
          {versions.expected.threshold_pack_version}
        </span>
      </div>
    </div>
  );
}

// =============================================================================
// Sealed Registries Table
// =============================================================================

interface SealedRegistriesTableProps {
  readonly registries: ReadonlyArray<SealedRegistryStatus>;
}

function SealedRegistriesTable({ registries }: SealedRegistriesTableProps): React.ReactElement {
  const columns: Column<SealedRegistryStatus>[] = [
    {
      key: 'registry_id',
      label: 'Registry ID',
      sortable: true
    },
    {
      key: 'sealed',
      label: 'Sealed',
      sortable: true,
      width: '100px',
      render: value => <SealStatus sealed={value as boolean} />
    },
    {
      key: 'pointer_known',
      label: 'Pointer Known',
      sortable: true,
      width: '120px',
      render: value => {
        if (value === true) return <span style={{ color: '#4caf50' }}>Yes</span>;
        if (value === false) return <span style={{ color: '#f44336' }}>No</span>;
        return <span style={{ color: '#ff9800' }}>Unknown</span>;
      }
    },
    {
      key: 'seal_source',
      label: 'Seal Source',
      sortable: false
    }
  ];

  return (
    <Table
      columns={columns}
      data={registries}
      keyField="registry_id"
      emptyMessage="No registry seal status available"
      initialSortKey="registry_id"
      initialSortDirection="asc"
    />
  );
}

// =============================================================================
// Enforcement Levels Table
// =============================================================================

interface EnforcementLevelsTableProps {
  readonly levels: ReadonlyArray<EnforcementLevel>;
}

function EnforcementLevelsTable({ levels }: EnforcementLevelsTableProps): React.ReactElement {
  const columns: Column<EnforcementLevel>[] = [
    {
      key: 'operation_id',
      label: 'Operation ID',
      sortable: true
    },
    {
      key: 'level',
      label: 'Level',
      sortable: true,
      width: '80px',
      render: value => <EnforcementLevelBadge level={String(value)} />
    },
    {
      key: 'description',
      label: 'Description',
      sortable: false
    }
  ];

  if (levels.length === 0) {
    return (
      <InfoPanel
        message="No enforcement levels loaded"
        details="Enforcement levels are sourced from OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.2.md"
      />
    );
  }

  return (
    <Table
      columns={columns}
      data={levels}
      keyField="operation_id"
      emptyMessage="No enforcement levels available"
      initialSortKey="level"
      initialSortDirection="desc"
    />
  );
}

// =============================================================================
// Enforcement Level Badge
// =============================================================================

interface EnforcementLevelBadgeProps {
  readonly level: string;
}

function EnforcementLevelBadge({ level }: EnforcementLevelBadgeProps): React.ReactElement {
  const colors: Record<string, { bg: string; fg: string }> = {
    C5: { bg: '#4caf50', fg: '#000' },
    C4: { bg: '#8bc34a', fg: '#000' },
    C3: { bg: '#ffeb3b', fg: '#000' },
    C2: { bg: '#ff9800', fg: '#000' },
    C1: { bg: '#ff5722', fg: '#fff' },
    C0: { bg: '#f44336', fg: '#fff' }
  };

  const color = colors[level] || { bg: '#666', fg: '#fff' };

  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '3px',
        backgroundColor: color.bg,
        color: color.fg,
        fontSize: '11px',
        fontWeight: 600,
        fontFamily: 'monospace'
      }}
    >
      {level}
    </span>
  );
}

// =============================================================================
// Known Gaps Table
// =============================================================================

interface KnownGapsTableProps {
  readonly gaps: ReadonlyArray<GovernanceGap>;
}

function KnownGapsTable({ gaps }: KnownGapsTableProps): React.ReactElement {
  const columns: Column<GovernanceGap>[] = [
    {
      key: 'gap_id',
      label: 'Gap ID',
      sortable: true,
      width: '120px'
    },
    {
      key: 'description',
      label: 'Description',
      sortable: false
    },
    {
      key: 'impact',
      label: 'Impact',
      sortable: false
    },
    {
      key: 'bounded',
      label: 'Bounded',
      sortable: true,
      width: '80px',
      render: value => (
        <span style={{ color: value ? '#4caf50' : '#f44336' }}>
          {value ? 'Yes' : 'No'}
        </span>
      )
    },
    {
      key: 'closable',
      label: 'Closable',
      sortable: true,
      width: '80px',
      render: value => (
        <span style={{ color: value ? '#4caf50' : '#ff9800' }}>
          {value ? 'Yes' : 'No'}
        </span>
      )
    }
  ];

  if (gaps.length === 0) {
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
        No known governance gaps
      </div>
    );
  }

  return (
    <Table
      columns={columns}
      data={gaps}
      keyField="gap_id"
      emptyMessage="No governance gaps"
      initialSortKey="bounded"
      initialSortDirection="asc"
    />
  );
}

// =============================================================================
// Governance Summary
// =============================================================================

interface GovernanceSummaryProps {
  readonly sealedRegistries: ReadonlyArray<SealedRegistryStatus>;
  readonly enforcementLevels: ReadonlyArray<EnforcementLevel>;
  readonly knownGaps: ReadonlyArray<GovernanceGap>;
}

function GovernanceSummary({
  sealedRegistries,
  enforcementLevels,
  knownGaps
}: GovernanceSummaryProps): React.ReactElement {
  const totalRegistries = sealedRegistries.length;
  const sealedCount = sealedRegistries.filter(r => r.sealed).length;
  const pointerKnownCount = sealedRegistries.filter(r => r.pointer_known === true).length;

  const c5Count = enforcementLevels.filter(l => l.level === 'C5').length;
  const c4Count = enforcementLevels.filter(l => l.level === 'C4').length;
  const c3Count = enforcementLevels.filter(l => l.level === 'C3').length;
  const c2Count = enforcementLevels.filter(l => l.level === 'C2').length;
  const c3PlusCount = c5Count + c4Count + c3Count;
  const totalOps = enforcementLevels.length;

  const boundedGaps = knownGaps.filter(g => g.bounded).length;
  const closableGaps = knownGaps.filter(g => g.closable).length;

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
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
        {/* Registry Stats */}
        <div>
          <h4 style={{ margin: '0 0 12px 0', color: '#888', fontSize: '11px', textTransform: 'uppercase' }}>
            Registry Seals
          </h4>
          <div style={{ color: '#e0e0e0' }}>
            <div>Sealed: <span style={{ color: '#4caf50' }}>{sealedCount}/{totalRegistries}</span></div>
            <div>Pointer Known: <span style={{ color: '#4caf50' }}>{pointerKnownCount}/{totalRegistries}</span></div>
          </div>
        </div>

        {/* Enforcement Stats */}
        <div>
          <h4 style={{ margin: '0 0 12px 0', color: '#888', fontSize: '11px', textTransform: 'uppercase' }}>
            Enforcement Coverage
          </h4>
          <div style={{ color: '#e0e0e0' }}>
            <div>C3+: <span style={{ color: '#4caf50' }}>{c3PlusCount}/{totalOps}</span> ({totalOps > 0 ? ((c3PlusCount / totalOps) * 100).toFixed(1) : 0}%)</div>
            <div>C2 (Weak): <span style={{ color: '#ff9800' }}>{c2Count}</span></div>
          </div>
        </div>

        {/* Gap Stats */}
        <div>
          <h4 style={{ margin: '0 0 12px 0', color: '#888', fontSize: '11px', textTransform: 'uppercase' }}>
            Known Gaps
          </h4>
          <div style={{ color: '#e0e0e0' }}>
            <div>Total: {knownGaps.length}</div>
            <div>Bounded: <span style={{ color: '#4caf50' }}>{boundedGaps}</span></div>
            <div>Closable: <span style={{ color: '#81c784' }}>{closableGaps}</span></div>
          </div>
        </div>
      </div>

      {/* No recalculation notice */}
      <div
        style={{
          marginTop: '16px',
          paddingTop: '12px',
          borderTop: '1px solid #333',
          color: '#666',
          fontSize: '11px',
          fontStyle: 'italic'
        }}
      >
        Values are read from governance documents. No recalculation performed by this panel.
      </div>
    </div>
  );
}

export default GovernancePage;
