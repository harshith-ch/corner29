#!/usr/bin/env node
/**
 * Production build wrapper.
 *
 * SvelteKit 2.x has no config hook to conditionally exclude routes from the
 * route tree. To guarantee dev-only tools never ship in a prod build, we
 * physically move `src/routes/tools` out of the routes directory for the
 * duration of `vite build`, then restore it — even on failure — via finally.
 *
 * The destination uses an underscore prefix, which SvelteKit would ignore as
 * a private directory if it weren't outside `routes/` entirely.
 */

import { execSync } from 'node:child_process';
import { existsSync, renameSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');
const src = resolve(root, 'src/routes/tools');
const hidden = resolve(root, '.tools.dev-only');

// Recover from a prior aborted build that left the tree renamed. Safe because
// on a clean run `src/routes/tools` exists and `.tools.dev-only` does not.
if (!existsSync(src) && existsSync(hidden)) {
  renameSync(hidden, src);
  console.log('[build-prod] Recovered stale .tools.dev-only from prior run.');
}

let moved = false;
function restore() {
  if (moved && existsSync(hidden)) {
    renameSync(hidden, src);
    moved = false;
    console.log('[build-prod] Restored src/routes/tools.');
  }
}

// `finally` catches normal exits and thrown errors, but not signals delivered
// to the parent process (CI cancel, Ctrl+C on the wrapper itself). Signal
// handlers cover that; the flag-guarded `restore()` is idempotent so the
// overlap with `finally` is harmless.
for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) {
  process.on(sig, () => {
    restore();
    process.exit(1);
  });
}

try {
  if (existsSync(src)) {
    renameSync(src, hidden);
    moved = true;
    console.log('[build-prod] Hidden src/routes/tools for prod build.');
  }
  execSync('vite build', { stdio: 'inherit', cwd: root });
} finally {
  restore();
}
