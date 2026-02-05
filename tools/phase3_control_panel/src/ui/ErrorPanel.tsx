/**
 * Phase 3 Control Panel - Error Panel Component
 *
 * READ-ONLY ERROR DISPLAY
 *
 * Displays errors from data loading without any recovery actions.
 * No "Fix" buttons. No "Retry" buttons. Display only.
 *
 * NO WRITES. NO ACTIONS.
 */

import React from 'react';

// =============================================================================
// Error Types
// =============================================================================

export interface DisplayError {
  readonly code: string;
  readonly message: string;
  readonly details?: string;
  readonly source?: string;
  readonly timestamp: string;
}

// =============================================================================
// Error Panel Component
// =============================================================================

interface ErrorPanelProps {
  readonly error: DisplayError;
}

export function ErrorPanel({ error }: ErrorPanelProps): React.ReactElement {
  return (
    <div
      role="alert"
      style={{
        backgroundColor: '#2d1f1f',
        border: '1px solid #5c2626',
        borderRadius: '4px',
        padding: '16px',
        marginBottom: '16px',
        fontFamily: 'monospace'
      }}
    >
      {/* Error header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '12px'
        }}
      >
        <span
          style={{
            backgroundColor: '#f44336',
            color: '#fff',
            padding: '2px 8px',
            borderRadius: '3px',
            fontSize: '11px',
            fontWeight: 600
          }}
        >
          ERROR
        </span>
        <span style={{ color: '#e0e0e0', fontSize: '14px' }}>{error.code}</span>
      </div>

      {/* Error message */}
      <div
        style={{
          color: '#ff8a80',
          fontSize: '13px',
          marginBottom: error.details ? '12px' : 0
        }}
      >
        {error.message}
      </div>

      {/* Details (if present) */}
      {error.details && (
        <div
          style={{
            backgroundColor: '#1a1111',
            padding: '12px',
            borderRadius: '4px',
            fontSize: '12px',
            color: '#888',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word'
          }}
        >
          {error.details}
        </div>
      )}

      {/* Metadata footer */}
      <div
        style={{
          marginTop: '12px',
          fontSize: '11px',
          color: '#666',
          display: 'flex',
          justifyContent: 'space-between'
        }}
      >
        {error.source && <span>Source: {error.source}</span>}
        <span>[{error.timestamp} \u2014 non-canonical]</span>
      </div>

      {/* No action notice */}
      <div
        style={{
          marginTop: '12px',
          paddingTop: '12px',
          borderTop: '1px solid #5c2626',
          fontSize: '11px',
          color: '#666',
          fontStyle: 'italic'
        }}
      >
        Read-only display. No recovery actions available from this panel.
      </div>
    </div>
  );
}

// =============================================================================
// Error List Component
// =============================================================================

interface ErrorListProps {
  readonly errors: ReadonlyArray<DisplayError>;
  readonly title?: string;
}

export function ErrorList({
  errors,
  title = 'Errors'
}: ErrorListProps): React.ReactElement {
  if (errors.length === 0) {
    return (
      <div
        style={{
          backgroundColor: '#1f2d1f',
          border: '1px solid #2e5c2e',
          borderRadius: '4px',
          padding: '12px',
          fontFamily: 'monospace',
          fontSize: '12px',
          color: '#81c784'
        }}
      >
        No errors detected
      </div>
    );
  }

  return (
    <div>
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
        {title} ({errors.length})
      </h4>
      {errors.map((error, index) => (
        <ErrorPanel key={`${error.code}-${index}`} error={error} />
      ))}
    </div>
  );
}

// =============================================================================
// Warning Panel Component
// =============================================================================

interface WarningPanelProps {
  readonly message: string;
  readonly details?: string;
}

export function WarningPanel({ message, details }: WarningPanelProps): React.ReactElement {
  return (
    <div
      role="alert"
      style={{
        backgroundColor: '#2d2a1f',
        border: '1px solid #5c5226',
        borderRadius: '4px',
        padding: '12px',
        marginBottom: '16px',
        fontFamily: 'monospace'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span
          style={{
            backgroundColor: '#ff9800',
            color: '#000',
            padding: '2px 8px',
            borderRadius: '3px',
            fontSize: '11px',
            fontWeight: 600
          }}
        >
          WARNING
        </span>
        <span style={{ color: '#ffcc80', fontSize: '13px' }}>{message}</span>
      </div>
      {details && (
        <div
          style={{
            marginTop: '8px',
            fontSize: '12px',
            color: '#888'
          }}
        >
          {details}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Info Panel Component
// =============================================================================

interface InfoPanelProps {
  readonly message: string;
  readonly details?: string;
}

export function InfoPanel({ message, details }: InfoPanelProps): React.ReactElement {
  return (
    <div
      style={{
        backgroundColor: '#1f2a2d',
        border: '1px solid #26525c',
        borderRadius: '4px',
        padding: '12px',
        marginBottom: '16px',
        fontFamily: 'monospace'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span
          style={{
            backgroundColor: '#2196f3',
            color: '#fff',
            padding: '2px 8px',
            borderRadius: '3px',
            fontSize: '11px',
            fontWeight: 600
          }}
        >
          INFO
        </span>
        <span style={{ color: '#80d4ff', fontSize: '13px' }}>{message}</span>
      </div>
      {details && (
        <div
          style={{
            marginTop: '8px',
            fontSize: '12px',
            color: '#888'
          }}
        >
          {details}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Loading State Component
// =============================================================================

interface LoadingStateProps {
  readonly message?: string;
}

export function LoadingState({
  message = 'Loading data...'
}: LoadingStateProps): React.ReactElement {
  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '24px',
        textAlign: 'center',
        fontFamily: 'monospace'
      }}
    >
      <div
        style={{
          color: '#888',
          fontSize: '14px',
          marginBottom: '8px'
        }}
      >
        {message}
      </div>
      <div style={{ color: '#555', fontSize: '12px' }}>
        Read-only data loading in progress...
      </div>
    </div>
  );
}

// =============================================================================
// Empty State Component
// =============================================================================

interface EmptyStateProps {
  readonly title: string;
  readonly message: string;
}

export function EmptyState({ title, message }: EmptyStateProps): React.ReactElement {
  return (
    <div
      style={{
        backgroundColor: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: '4px',
        padding: '48px 24px',
        textAlign: 'center',
        fontFamily: 'monospace'
      }}
    >
      <div
        style={{
          color: '#e0e0e0',
          fontSize: '16px',
          marginBottom: '8px'
        }}
      >
        {title}
      </div>
      <div style={{ color: '#666', fontSize: '13px' }}>{message}</div>
    </div>
  );
}

export default ErrorPanel;
