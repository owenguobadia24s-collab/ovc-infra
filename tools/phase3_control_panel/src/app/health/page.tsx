/**
 * Phase 3 Control Panel - System Health View
 *
 * /health - System health state (H0-H9)
 *
 * Requirements (per Phase 3 Architecture):
 * - Compute and display H0/H1/H2/H3/H9 exactly per Health Contracts v0.1
 * - Show which condition IDs triggered the state
 * - No custom heuristics
 *
 * Health Determination Ordering (MANDATORY):
 * 1. Check H9 (UNKNOWN) first
 * 2. Check H3 (RECOVERY_REQUIRED)
 * 3. Check H2 (DEGRADED_BLOCKING)
 * 4. Check H1 (DEGRADED_NON_BLOCKING)
 * 5. If none, state is H0 (HEALTHY)
 *
 * READ-ONLY VIEW. NO WRITES.
 */

import React from 'react';
import { Layout, PageHeader } from '../../ui/Layout';
import { SourceBadge, SourceTracePanel } from '../../ui/SourceBadge';
import { ErrorPanel, DisplayError, LoadingState, InfoPanel } from '../../ui/ErrorPanel';
import { HealthState, HealthCondition, HealthStateCode, HEALTH_STATE_NAMES, HEALTH_STATE_DESCRIPTIONS } from '../../lib/models';
import { SourceTrace } from '../../lib/trace';
import { getAllConditionDefinitions } from '../../lib/health_rules';

// =============================================================================
// Page Component
// =============================================================================

interface HealthPageProps {
  readonly healthState: HealthState | null;
  readonly traces: ReadonlyArray<SourceTrace>;
  readonly error?: DisplayError;
  readonly loading?: boolean;
}

export function HealthPage({
  healthState,
  traces,
  error,
  loading = false
}: HealthPageProps): React.ReactElement {
  return (
    <Layout currentPath="/health" title="System Health View">
      <PageHeader
        title="System Health State"
        description="Health state computed per Health Contracts v0.1. No custom heuristics."
      />

      {/* Compliance notice */}
      <InfoPanel
        message="Health computed per Health Contracts v0.1"
        details="Ordering: H9 (UNKNOWN) checked first, then H3 (RECOVERY_REQUIRED), H2 (DEGRADED_BLOCKING), H1 (DEGRADED_NON_BLOCKING), H0 (HEALTHY)."
      />

      {/* Source traces - REQUIRED */}
      {traces.length > 0 && (
        <SourceTracePanel traces={traces} title="Health Evidence Sources" />
      )}

      {/* Error display */}
      {error && <ErrorPanel error={error} />}

      {/* Loading state */}
      {loading && <LoadingState message="Computing health state..." />}

      {/* Health state display */}
      {!loading && !error && healthState && (
        <>
          {/* Primary health state banner */}
          <HealthStateBanner state={healthState} />

          {/* Triggered conditions */}
          <Section title="Triggered Conditions">
            <TriggeredConditionsTable conditions={healthState.triggeredConditions} />
          </Section>

          {/* All condition definitions */}
          <Section title="Condition Definitions (per Health Contracts v0.1)">
            <ConditionDefinitions />
          </Section>

          {/* Determination timestamp (non-canonical) */}
          <div
            style={{
              color: '#666',
              fontSize: '11px',
              fontFamily: 'monospace',
              marginTop: '24px'
            }}
          >
            [Determined at: {healthState.determinedAt} \u2014 non-canonical]
          </div>
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
// Health State Banner
// =============================================================================

interface HealthStateBannerProps {
  readonly state: HealthState;
}

function HealthStateBanner({ state }: HealthStateBannerProps): React.ReactElement {
  const colors: Record<HealthStateCode, { bg: string; border: string; text: string }> = {
    H0: { bg: '#1f2d1f', border: '#2e5c2e', text: '#4caf50' },
    H1: { bg: '#2d2a1f', border: '#5c5226', text: '#ff9800' },
    H2: { bg: '#2d1f1f', border: '#5c2626', text: '#f44336' },
    H3: { bg: '#2d1f2d', border: '#5c265c', text: '#e040fb' },
    H9: { bg: '#1f1f2d', border: '#26265c', text: '#9e9e9e' }
  };

  const color = colors[state.code];

  return (
    <div
      style={{
        backgroundColor: color.bg,
        border: `2px solid ${color.border}`,
        borderRadius: '8px',
        padding: '24px',
        marginBottom: '24px',
        textAlign: 'center'
      }}
    >
      {/* State code - large display */}
      <div
        style={{
          fontSize: '48px',
          fontWeight: 700,
          color: color.text,
          fontFamily: 'monospace',
          marginBottom: '8px'
        }}
      >
        {state.code}
      </div>

      {/* State name */}
      <div
        style={{
          fontSize: '20px',
          color: color.text,
          fontFamily: 'monospace',
          marginBottom: '12px'
        }}
      >
        {state.name}
      </div>

      {/* State description */}
      <div
        style={{
          fontSize: '14px',
          color: '#888',
          fontFamily: 'monospace'
        }}
      >
        {state.description}
      </div>

      {/* Degradation type */}
      <div
        style={{
          marginTop: '16px',
          padding: '8px 16px',
          backgroundColor: 'rgba(0,0,0,0.2)',
          borderRadius: '4px',
          display: 'inline-block'
        }}
      >
        <DegradationType code={state.code} />
      </div>
    </div>
  );
}

// =============================================================================
// Degradation Type Label
// =============================================================================

interface DegradationTypeProps {
  readonly code: HealthStateCode;
}

function DegradationType({ code }: DegradationTypeProps): React.ReactElement {
  const labels: Record<HealthStateCode, { text: string; color: string }> = {
    H0: { text: 'No degradation', color: '#4caf50' },
    H1: { text: 'Non-blocking degradation - core operations permitted', color: '#ff9800' },
    H2: { text: 'Blocking degradation - some operations blocked', color: '#f44336' },
    H3: { text: 'Recovery required - all operations blocked except recovery', color: '#e040fb' },
    H9: { text: 'Unknown - treat as RECOVERY_REQUIRED', color: '#9e9e9e' }
  };

  const label = labels[code];

  return (
    <span
      style={{
        color: label.color,
        fontSize: '12px',
        fontFamily: 'monospace'
      }}
    >
      {label.text}
    </span>
  );
}

// =============================================================================
// Triggered Conditions Table
// =============================================================================

interface TriggeredConditionsTableProps {
  readonly conditions: ReadonlyArray<HealthCondition>;
}

function TriggeredConditionsTable({ conditions }: TriggeredConditionsTableProps): React.ReactElement {
  const triggeredConditions = conditions.filter(c => c.triggered);

  if (triggeredConditions.length === 0) {
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
        No conditions triggered (HEALTHY state)
      </div>
    );
  }

  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        overflow: 'hidden'
      }}
    >
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontFamily: 'monospace',
          fontSize: '12px'
        }}
      >
        <thead>
          <tr>
            <th style={thStyle}>Condition ID</th>
            <th style={thStyle}>Description</th>
            <th style={thStyle}>Evidence</th>
          </tr>
        </thead>
        <tbody>
          {triggeredConditions.map(condition => (
            <tr key={condition.id}>
              <td style={{ ...tdStyle, width: '100px' }}>
                <span
                  style={{
                    backgroundColor: getConditionColor(condition.id),
                    color: '#fff',
                    padding: '2px 6px',
                    borderRadius: '3px',
                    fontSize: '11px'
                  }}
                >
                  {condition.id}
                </span>
              </td>
              <td style={tdStyle}>{condition.description}</td>
              <td style={{ ...tdStyle, color: '#888' }}>{condition.evidence || '\u2014'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const thStyle: React.CSSProperties = {
  textAlign: 'left',
  padding: '12px 16px',
  backgroundColor: '#16213e',
  borderBottom: '2px solid #333',
  color: '#e0e0e0',
  fontWeight: 500
};

const tdStyle: React.CSSProperties = {
  padding: '10px 16px',
  borderBottom: '1px solid #333',
  color: '#e0e0e0'
};

function getConditionColor(id: string): string {
  if (id.startsWith('H9')) return '#9e9e9e';
  if (id.startsWith('H3')) return '#e040fb';
  if (id.startsWith('H2')) return '#f44336';
  if (id.startsWith('H1')) return '#ff9800';
  if (id.startsWith('H0')) return '#4caf50';
  return '#666';
}

// =============================================================================
// Condition Definitions (from Health Contracts v0.1)
// =============================================================================

function ConditionDefinitions(): React.ReactElement {
  const definitions = getAllConditionDefinitions();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <ConditionGroup
        title="H9 - UNKNOWN (checked first)"
        conditions={definitions.h9}
        color="#9e9e9e"
      />
      <ConditionGroup
        title="H3 - RECOVERY_REQUIRED"
        conditions={definitions.h3}
        color="#e040fb"
      />
      <ConditionGroup
        title="H2 - DEGRADED_BLOCKING"
        conditions={definitions.h2}
        color="#f44336"
      />
      <ConditionGroup
        title="H1 - DEGRADED_NON_BLOCKING"
        conditions={definitions.h1}
        color="#ff9800"
      />
      <ConditionGroup
        title="H0 - HEALTHY (all must be true)"
        conditions={definitions.h0}
        color="#4caf50"
      />
    </div>
  );
}

interface ConditionGroupProps {
  readonly title: string;
  readonly conditions: ReadonlyArray<{ id: string; description: string }>;
  readonly color: string;
}

function ConditionGroup({ title, conditions, color }: ConditionGroupProps): React.ReactElement {
  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '16px'
      }}
    >
      <h4
        style={{
          margin: '0 0 12px 0',
          fontSize: '12px',
          fontWeight: 500,
          color,
          fontFamily: 'monospace'
        }}
      >
        {title}
      </h4>
      <ul
        style={{
          margin: 0,
          padding: 0,
          listStyle: 'none'
        }}
      >
        {conditions.map(condition => (
          <li
            key={condition.id}
            style={{
              padding: '6px 0',
              borderBottom: '1px solid #333',
              display: 'flex',
              gap: '12px',
              alignItems: 'baseline'
            }}
          >
            <span
              style={{
                color: '#666',
                fontSize: '11px',
                fontFamily: 'monospace',
                minWidth: '60px'
              }}
            >
              {condition.id}
            </span>
            <span style={{ color: '#888', fontSize: '12px' }}>{condition.description}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default HealthPage;
