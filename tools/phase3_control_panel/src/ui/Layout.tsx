/**
 * Phase 3 Control Panel - Layout Component
 *
 * READ-ONLY CONTROL PANEL
 * "Sight without influence"
 *
 * This layout includes the mandatory Non-Authority Banner:
 * "Read-only Control Panel - no actions, no writes, no triggers."
 *
 * NO ACTION BUTTONS. NAVIGATION ONLY.
 */

import React from 'react';

// =============================================================================
// Non-Authority Banner (REQUIRED on all pages)
// =============================================================================

export const NON_AUTHORITY_BANNER_TEXT =
  'Read-only Control Panel \u2014 no actions, no writes, no triggers.';

interface NonAuthorityBannerProps {
  readonly className?: string;
}

export function NonAuthorityBanner({ className = '' }: NonAuthorityBannerProps): React.ReactElement {
  return (
    <div
      className={`non-authority-banner ${className}`}
      role="banner"
      aria-label="Read-only notice"
      style={{
        backgroundColor: '#1a1a2e',
        color: '#8b8b8b',
        padding: '8px 16px',
        textAlign: 'center',
        fontSize: '12px',
        fontFamily: 'monospace',
        borderBottom: '1px solid #333'
      }}
    >
      {NON_AUTHORITY_BANNER_TEXT}
    </div>
  );
}

// =============================================================================
// Navigation (READ-ONLY - navigation links only)
// =============================================================================

interface NavItem {
  readonly path: string;
  readonly label: string;
  readonly description: string;
}

const NAV_ITEMS: ReadonlyArray<NavItem> = Object.freeze([
  { path: '/runs', label: 'Runs', description: 'Timeline of all runs' },
  { path: '/failures', label: 'Failures', description: 'Aggregated failure view' },
  { path: '/artifacts', label: 'Artifacts', description: 'Drill-down to sealed artifacts' },
  { path: '/diff', label: 'Diff', description: 'Compare two runs' },
  { path: '/health', label: 'Health', description: 'System health state (H0-H9)' },
  { path: '/governance', label: 'Governance', description: 'Versions, enforcement, gaps' }
]);

interface NavigationProps {
  readonly currentPath: string;
}

export function Navigation({ currentPath }: NavigationProps): React.ReactElement {
  return (
    <nav
      role="navigation"
      aria-label="Main navigation"
      style={{
        backgroundColor: '#16213e',
        padding: '12px 16px',
        borderBottom: '1px solid #333'
      }}
    >
      <ul
        style={{
          listStyle: 'none',
          margin: 0,
          padding: 0,
          display: 'flex',
          gap: '24px'
        }}
      >
        {NAV_ITEMS.map(item => (
          <li key={item.path}>
            <a
              href={item.path}
              title={item.description}
              aria-current={currentPath === item.path ? 'page' : undefined}
              style={{
                color: currentPath === item.path ? '#4fc3f7' : '#e0e0e0',
                textDecoration: 'none',
                fontFamily: 'monospace',
                fontSize: '14px',
                padding: '4px 8px',
                borderRadius: '4px',
                backgroundColor: currentPath === item.path ? 'rgba(79, 195, 247, 0.1)' : 'transparent'
              }}
            >
              {item.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}

// =============================================================================
// Render Timestamp (Non-Canonical)
// =============================================================================

interface RenderTimestampProps {
  readonly timestamp: string;
}

export function RenderTimestamp({ timestamp }: RenderTimestampProps): React.ReactElement {
  return (
    <div
      style={{
        color: '#666',
        fontSize: '11px',
        fontFamily: 'monospace',
        padding: '4px 16px',
        textAlign: 'right'
      }}
    >
      [Rendered at: {timestamp} \u2014 non-canonical]
    </div>
  );
}

// =============================================================================
// Main Layout Component
// =============================================================================

interface LayoutProps {
  readonly children: React.ReactNode;
  readonly currentPath: string;
  readonly title: string;
}

export function Layout({ children, currentPath, title }: LayoutProps): React.ReactElement {
  const renderTimestamp = new Date().toISOString();

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#0f0f23',
        color: '#e0e0e0',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}
    >
      {/* Non-Authority Banner - REQUIRED */}
      <NonAuthorityBanner />

      {/* Header */}
      <header
        style={{
          backgroundColor: '#16213e',
          padding: '16px',
          borderBottom: '1px solid #333'
        }}
      >
        <h1
          style={{
            margin: 0,
            fontSize: '20px',
            fontWeight: 500,
            color: '#e0e0e0',
            fontFamily: 'monospace'
          }}
        >
          Phase 3 Control Panel
        </h1>
        <p
          style={{
            margin: '4px 0 0 0',
            fontSize: '12px',
            color: '#888',
            fontFamily: 'monospace'
          }}
        >
          {title}
        </p>
      </header>

      {/* Navigation */}
      <Navigation currentPath={currentPath} />

      {/* Main Content */}
      <main
        style={{
          padding: '24px',
          maxWidth: '1400px',
          margin: '0 auto'
        }}
      >
        {children}
      </main>

      {/* Footer with render timestamp */}
      <footer
        style={{
          borderTop: '1px solid #333',
          marginTop: '48px'
        }}
      >
        <RenderTimestamp timestamp={renderTimestamp} />
        <div
          style={{
            color: '#555',
            fontSize: '11px',
            fontFamily: 'monospace',
            padding: '8px 16px',
            textAlign: 'center'
          }}
        >
          Phase 3: Sight without influence. No write credentials exist.
        </div>
      </footer>
    </div>
  );
}

// =============================================================================
// Page Header Component
// =============================================================================

interface PageHeaderProps {
  readonly title: string;
  readonly description: string;
}

export function PageHeader({ title, description }: PageHeaderProps): React.ReactElement {
  return (
    <div style={{ marginBottom: '24px' }}>
      <h2
        style={{
          margin: 0,
          fontSize: '18px',
          fontWeight: 500,
          color: '#e0e0e0',
          fontFamily: 'monospace'
        }}
      >
        {title}
      </h2>
      <p
        style={{
          margin: '8px 0 0 0',
          fontSize: '13px',
          color: '#888',
          fontFamily: 'monospace'
        }}
      >
        {description}
      </p>
    </div>
  );
}

export default Layout;
