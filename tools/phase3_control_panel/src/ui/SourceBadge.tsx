/**
 * Phase 3 Control Panel - Source Badge Component
 *
 * Displays the source trace for every table/data display.
 * Every page must show this trace per Phase 3 requirements.
 *
 * READ-ONLY DISPLAY COMPONENT.
 */

import React, { useState } from 'react';
import { SourceTrace } from '../lib/trace';

// =============================================================================
// Source Badge Component
// =============================================================================

interface SourceBadgeProps {
  readonly trace: SourceTrace;
  readonly compact?: boolean;
}

export function SourceBadge({ trace, compact = false }: SourceBadgeProps): React.ReactElement {
  const [expanded, setExpanded] = useState(false);

  const sealedColor = trace.sealed ? '#4caf50' : '#ff9800';
  const sealedText = trace.sealed ? 'SEALED' : 'UNSEALED';

  if (compact) {
    return (
      <span
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '2px 8px',
          backgroundColor: '#1a1a2e',
          borderRadius: '4px',
          fontSize: '11px',
          fontFamily: 'monospace',
          color: '#888'
        }}
      >
        <span style={{ color: sealedColor }}>{sealedText}</span>
        <span>{trace.registry_id}</span>
      </span>
    );
  }

  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '12px',
        marginBottom: '16px',
        fontFamily: 'monospace',
        fontSize: '12px'
      }}
    >
      {/* Header row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: expanded ? '12px' : 0
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span
            style={{
              backgroundColor: sealedColor,
              color: '#000',
              padding: '2px 6px',
              borderRadius: '3px',
              fontSize: '10px',
              fontWeight: 600
            }}
          >
            {sealedText}
          </span>
          <span style={{ color: '#e0e0e0' }}>Source: {trace.registry_id}</span>
        </div>

        {/* Expand/collapse button - navigation only, no action */}
        <button
          onClick={() => setExpanded(!expanded)}
          style={{
            background: 'none',
            border: 'none',
            color: '#4fc3f7',
            cursor: 'pointer',
            fontSize: '11px',
            fontFamily: 'monospace',
            padding: '4px 8px'
          }}
          aria-expanded={expanded}
          aria-label={expanded ? 'Collapse source details' : 'Expand source details'}
        >
          {expanded ? '\u25B2 Hide details' : '\u25BC Show details'}
        </button>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div style={{ color: '#888', lineHeight: 1.6 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '4px 12px' }}>
            {trace.pointer_file && (
              <>
                <span style={{ color: '#666' }}>Pointer:</span>
                <span>{trace.pointer_file}</span>
              </>
            )}
            {trace.active_run_id && (
              <>
                <span style={{ color: '#666' }}>Run ID:</span>
                <span>{trace.active_run_id}</span>
              </>
            )}
            {trace.artifact_path && (
              <>
                <span style={{ color: '#666' }}>Artifact:</span>
                <span>{trace.artifact_path}</span>
              </>
            )}
            {trace.notes && (
              <>
                <span style={{ color: '#666' }}>Notes:</span>
                <span>{trace.notes}</span>
              </>
            )}
            <span style={{ color: '#666' }}>Traced at:</span>
            <span style={{ color: '#555' }}>[{trace.traced_at} \u2014 non-canonical]</span>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Source Trace Panel (for page-level display)
// =============================================================================

interface SourceTracePanelProps {
  readonly traces: ReadonlyArray<SourceTrace>;
  readonly title?: string;
}

export function SourceTracePanel({
  traces,
  title = 'Data Sources'
}: SourceTracePanelProps): React.ReactElement {
  if (traces.length === 0) {
    return (
      <div
        style={{
          backgroundColor: '#1a1a2e',
          border: '1px solid #333',
          borderRadius: '4px',
          padding: '12px',
          marginBottom: '16px',
          fontFamily: 'monospace',
          fontSize: '12px',
          color: '#888'
        }}
      >
        No source traces available
      </div>
    );
  }

  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '12px',
        marginBottom: '16px'
      }}
    >
      <h4
        style={{
          margin: '0 0 12px 0',
          fontSize: '12px',
          fontWeight: 500,
          color: '#888',
          fontFamily: 'monospace',
          textTransform: 'uppercase',
          letterSpacing: '1px'
        }}
      >
        {title}
      </h4>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        {traces.map((trace, index) => (
          <SourceBadge key={`${trace.registry_id}-${index}`} trace={trace} compact />
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Seal Status Indicator
// =============================================================================

interface SealStatusProps {
  readonly sealed: boolean;
  readonly size?: 'small' | 'medium' | 'large';
}

export function SealStatus({ sealed, size = 'medium' }: SealStatusProps): React.ReactElement {
  const sizeStyles = {
    small: { fontSize: '10px', padding: '1px 4px' },
    medium: { fontSize: '11px', padding: '2px 6px' },
    large: { fontSize: '12px', padding: '3px 8px' }
  };

  return (
    <span
      style={{
        backgroundColor: sealed ? '#4caf50' : '#ff9800',
        color: '#000',
        borderRadius: '3px',
        fontWeight: 600,
        fontFamily: 'monospace',
        ...sizeStyles[size]
      }}
    >
      {sealed ? 'SEALED' : 'UNSEALED'}
    </span>
  );
}

export default SourceBadge;
