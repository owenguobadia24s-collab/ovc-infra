/**
 * Phase 3 Control Panel - Table Component
 *
 * READ-ONLY DATA TABLE
 *
 * Allowed interactions (per validation report):
 * - Sorting (deterministic)
 * - Filtering
 * - Search
 * - Copy to clipboard
 *
 * Forbidden interactions:
 * - No action buttons
 * - No inline editing
 * - No form submissions
 *
 * NO WRITES. DISPLAY ONLY.
 */

import React, { useState, useMemo } from 'react';

// =============================================================================
// Table Types
// =============================================================================

export interface Column<T> {
  readonly key: keyof T | string;
  readonly label: string;
  readonly sortable?: boolean;
  readonly width?: string;
  readonly render?: (value: unknown, row: T) => React.ReactNode;
}

interface TableProps<T> {
  readonly columns: ReadonlyArray<Column<T>>;
  readonly data: ReadonlyArray<T>;
  readonly keyField: keyof T;
  readonly emptyMessage?: string;
  readonly onRowClick?: (row: T) => void; // Navigation only
  readonly initialSortKey?: string;
  readonly initialSortDirection?: 'asc' | 'desc';
}

// =============================================================================
// Sort and Filter Helpers
// =============================================================================

type SortDirection = 'asc' | 'desc' | null;

function sortData<T>(
  data: ReadonlyArray<T>,
  sortKey: string | null,
  sortDirection: SortDirection
): T[] {
  if (!sortKey || !sortDirection) {
    return [...data];
  }

  return [...data].sort((a, b) => {
    const aValue = (a as Record<string, unknown>)[sortKey];
    const bValue = (b as Record<string, unknown>)[sortKey];

    // Handle nulls
    if (aValue == null && bValue == null) return 0;
    if (aValue == null) return sortDirection === 'asc' ? -1 : 1;
    if (bValue == null) return sortDirection === 'asc' ? 1 : -1;

    // String comparison
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      const cmp = aValue.localeCompare(bValue);
      return sortDirection === 'asc' ? cmp : -cmp;
    }

    // Number comparison
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    }

    // Boolean comparison
    if (typeof aValue === 'boolean' && typeof bValue === 'boolean') {
      const cmp = aValue === bValue ? 0 : aValue ? 1 : -1;
      return sortDirection === 'asc' ? cmp : -cmp;
    }

    // Fallback to string comparison
    const cmp = String(aValue).localeCompare(String(bValue));
    return sortDirection === 'asc' ? cmp : -cmp;
  });
}

// =============================================================================
// Table Component
// =============================================================================

export function Table<T extends Record<string, unknown>>({
  columns,
  data,
  keyField,
  emptyMessage = 'No data available',
  onRowClick,
  initialSortKey = null,
  initialSortDirection = 'desc'
}: TableProps<T>): React.ReactElement {
  const [sortKey, setSortKey] = useState<string | null>(initialSortKey);
  const [sortDirection, setSortDirection] = useState<SortDirection>(
    initialSortKey ? initialSortDirection : null
  );
  const [filter, setFilter] = useState('');

  // Filter data
  const filteredData = useMemo(() => {
    if (!filter.trim()) {
      return data;
    }

    const lowerFilter = filter.toLowerCase();
    return data.filter(row => {
      return Object.values(row).some(value =>
        String(value).toLowerCase().includes(lowerFilter)
      );
    });
  }, [data, filter]);

  // Sort data (deterministic)
  const sortedData = useMemo(() => {
    return sortData(filteredData, sortKey, sortDirection);
  }, [filteredData, sortKey, sortDirection]);

  // Handle column header click for sorting
  const handleSort = (key: string, sortable?: boolean) => {
    if (!sortable) return;

    if (sortKey === key) {
      // Cycle: asc -> desc -> null -> asc
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortDirection(null);
        setSortKey(null);
      } else {
        setSortDirection('asc');
      }
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  // Get cell value
  const getCellValue = (row: T, column: Column<T>): React.ReactNode => {
    const key = column.key as string;
    const value = row[key as keyof T];

    if (column.render) {
      return column.render(value, row);
    }

    if (value === null || value === undefined) {
      return <span style={{ color: '#666' }}>\u2014</span>;
    }

    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    }

    return String(value);
  };

  return (
    <div>
      {/* Filter input - search only, no action */}
      <div style={{ marginBottom: '12px' }}>
        <input
          type="text"
          placeholder="Filter rows..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
          aria-label="Filter table rows"
          style={{
            width: '250px',
            padding: '8px 12px',
            backgroundColor: '#1a1a2e',
            border: '1px solid #333',
            borderRadius: '4px',
            color: '#e0e0e0',
            fontFamily: 'monospace',
            fontSize: '13px'
          }}
        />
        {filter && (
          <span style={{ marginLeft: '12px', color: '#888', fontSize: '12px' }}>
            Showing {sortedData.length} of {data.length} rows
          </span>
        )}
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontFamily: 'monospace',
            fontSize: '13px'
          }}
        >
          <thead>
            <tr>
              {columns.map(column => (
                <th
                  key={String(column.key)}
                  onClick={() => handleSort(String(column.key), column.sortable)}
                  style={{
                    textAlign: 'left',
                    padding: '12px 16px',
                    backgroundColor: '#16213e',
                    borderBottom: '2px solid #333',
                    color: '#e0e0e0',
                    fontWeight: 500,
                    cursor: column.sortable ? 'pointer' : 'default',
                    width: column.width,
                    userSelect: 'none'
                  }}
                  aria-sort={
                    sortKey === column.key
                      ? sortDirection === 'asc'
                        ? 'ascending'
                        : sortDirection === 'desc'
                          ? 'descending'
                          : 'none'
                      : undefined
                  }
                >
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {column.label}
                    {column.sortable && (
                      <span style={{ color: '#666' }}>
                        {sortKey === column.key
                          ? sortDirection === 'asc'
                            ? '\u25B2'
                            : sortDirection === 'desc'
                              ? '\u25BC'
                              : '\u25C6'
                          : '\u25C6'}
                      </span>
                    )}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length}
                  style={{
                    padding: '24px 16px',
                    textAlign: 'center',
                    color: '#666',
                    backgroundColor: '#1a1a2e'
                  }}
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              sortedData.map(row => (
                <tr
                  key={String(row[keyField])}
                  onClick={onRowClick ? () => onRowClick(row) : undefined}
                  style={{
                    cursor: onRowClick ? 'pointer' : 'default',
                    backgroundColor: '#1a1a2e'
                  }}
                  onMouseEnter={e => {
                    if (onRowClick) {
                      (e.currentTarget as HTMLElement).style.backgroundColor = '#222244';
                    }
                  }}
                  onMouseLeave={e => {
                    (e.currentTarget as HTMLElement).style.backgroundColor = '#1a1a2e';
                  }}
                >
                  {columns.map(column => (
                    <td
                      key={`${String(row[keyField])}-${String(column.key)}`}
                      style={{
                        padding: '10px 16px',
                        borderBottom: '1px solid #333',
                        color: '#e0e0e0'
                      }}
                    >
                      {getCellValue(row, column)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Row count */}
      <div
        style={{
          marginTop: '12px',
          color: '#666',
          fontSize: '11px',
          textAlign: 'right'
        }}
      >
        {sortedData.length} row{sortedData.length !== 1 ? 's' : ''}
        {sortKey && sortDirection && (
          <span>
            {' '}
            | Sorted by {sortKey} ({sortDirection})
          </span>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Status Cell Renderer
// =============================================================================

interface StatusCellProps {
  readonly status: string;
}

export function StatusCell({ status }: StatusCellProps): React.ReactElement {
  const colors: Record<string, { bg: string; fg: string }> = {
    PASS: { bg: '#4caf50', fg: '#000' },
    FAIL: { bg: '#f44336', fg: '#fff' },
    RUNNING: { bg: '#2196f3', fg: '#fff' },
    UNKNOWN: { bg: '#9e9e9e', fg: '#000' },
    HEALTHY: { bg: '#4caf50', fg: '#000' },
    DEGRADED: { bg: '#ff9800', fg: '#000' },
    BLOCKED: { bg: '#f44336', fg: '#fff' }
  };

  const color = colors[status] || { bg: '#666', fg: '#fff' };

  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '3px',
        backgroundColor: color.bg,
        color: color.fg,
        fontSize: '11px',
        fontWeight: 600
      }}
    >
      {status}
    </span>
  );
}

// =============================================================================
// Hash Cell Renderer (truncated with copy)
// =============================================================================

interface HashCellProps {
  readonly hash: string | null;
  readonly truncate?: number;
}

export function HashCell({ hash, truncate = 8 }: HashCellProps): React.ReactElement {
  if (!hash) {
    return <span style={{ color: '#666' }}>\u2014</span>;
  }

  const truncated = hash.substring(0, truncate);

  // Copy to clipboard on click (allowed per validation report)
  const handleCopy = () => {
    navigator.clipboard?.writeText(hash);
  };

  return (
    <span
      onClick={handleCopy}
      title={`${hash}\nClick to copy`}
      style={{
        cursor: 'pointer',
        fontFamily: 'monospace',
        color: '#4fc3f7'
      }}
    >
      {truncated}...
    </span>
  );
}

export default Table;
