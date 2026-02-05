/**
 * Phase 3 Control Panel - Client Entry Point
 *
 * READ-ONLY VIEWER
 * This is the browser entry point that renders the read-only control panel.
 *
 * NO WRITES. NO MUTATIONS. NO ACTIONS.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './runtime/App';

const container = document.getElementById('root');
if (!container) {
  throw new Error('Root element not found');
}

const root = createRoot(container);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
