#!/usr/bin/env node
// Optimize DXF-exported floor-plan SVGs for web delivery.
//
// The raw exports are 1.5–6 MB each (total ~33 MB) with 4–6 digits of decimal
// precision, a full-viewBox background <rect>, and occasional stray <path>
// elements spanning multiples of the authored viewBox. This script:
//   1. Drops the background rect and any stray-extent path (moved out of the
//      runtime viewer so the browser doesn't pay for it on every load).
//   2. Runs SVGO with precision 1 — coordinates are in the hundreds of
//      thousands, so one decimal is sub-millimeter and visually identical.
//   3. Writes back to static/svg/.
//
// Run manually: `node scripts/optimize-svgs.mjs`

import { readdir, readFile, writeFile, stat } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { optimize } from 'svgo';

const here = dirname(fileURLToPath(import.meta.url));
const svgDir = join(here, '..', 'static', 'svg');

// Walk an SVG path `d` attribute and return the bbox of every point it
// touches (endpoints + control points). Returns null if the path is
// malformed — caller should treat that as "don't drop it".
//
// Correctness notes for future maintainers:
//   - H/V take a single coordinate (not a pair).
//   - A takes 7 args where the 4th/5th are 0|1 flags, not coordinates.
//   - Lowercase commands are relative to the current point; for multi-pair
//     commands (C/S/Q/T/L), all pairs in a single batch are relative to the
//     current point *before* the batch — NOT cumulative within the batch.
//   - Numbers without a leading command implicitly repeat the previous one
//     (M→L, m→l after the first pair). The current point updates between
//     implicit repeats.
// The old version ignored all of this and diffed numeric pairs directly,
// which happened to work for the current DXF exports (M/L-heavy, no arcs)
// but would silently mis-measure any path with arcs or relative curves.
function pathExtent(d) {
  const ARGS = { M: 2, L: 2, H: 1, V: 1, C: 6, S: 4, Q: 4, T: 2, A: 7, Z: 0 };
  const tokens = [];
  const re = /([MmLlHhVvCcSsQqTtAaZz])|(-?\d*\.?\d+(?:[eE][-+]?\d+)?)/g;
  let m;
  while ((m = re.exec(d)) !== null) {
    tokens.push(m[1] ?? parseFloat(m[2]));
  }

  let x = 0, y = 0, sx = 0, sy = 0;
  let xMin = Infinity, xMax = -Infinity, yMin = Infinity, yMax = -Infinity;
  const hit = (px, py) => {
    if (px < xMin) xMin = px;
    if (px > xMax) xMax = px;
    if (py < yMin) yMin = py;
    if (py > yMax) yMax = py;
  };

  let cmd = null;
  let i = 0;
  while (i < tokens.length) {
    if (typeof tokens[i] === 'string') {
      cmd = tokens[i];
      i++;
    }
    if (cmd === null) return null;

    const abs = cmd.toUpperCase();
    const rel = cmd !== abs;
    const n = ARGS[abs];
    if (n === undefined) return null;

    if (n === 0) {
      x = sx;
      y = sy;
      continue;
    }

    const args = [];
    for (let k = 0; k < n; k++) {
      if (typeof tokens[i] !== 'number') return null;
      args.push(tokens[i]);
      i++;
    }

    if (abs === 'H') {
      x = rel ? x + args[0] : args[0];
      hit(x, y);
    } else if (abs === 'V') {
      y = rel ? y + args[0] : args[0];
      hit(x, y);
    } else if (abs === 'A') {
      x = rel ? x + args[5] : args[5];
      y = rel ? y + args[6] : args[6];
      hit(x, y);
    } else {
      const baseX = x, baseY = y;
      for (let k = 0; k < args.length; k += 2) {
        hit(rel ? baseX + args[k] : args[k], rel ? baseY + args[k + 1] : args[k + 1]);
      }
      x = rel ? baseX + args[args.length - 2] : args[args.length - 2];
      y = rel ? baseY + args[args.length - 1] : args[args.length - 1];
    }

    if (abs === 'M') {
      sx = x;
      sy = y;
      cmd = rel ? 'l' : 'L';
    }
  }

  if (xMin === Infinity) return null;
  return { xMin, xMax, yMin, yMax };
}

function preClean(text) {
  // Strip the xml decl so SVGO is happy, the full-viewBox white <rect>
  // background, and any <path> whose drawn extent exceeds 2× the viewBox
  // in either axis (the known stray path in floor 2, and any similar
  // artifact in other exports).
  let out = text.replace(/^<\?xml[^?]*\?>\s*/, '');
  out = out.replace(/<rect\b[^>]*fill\s*=\s*"white"[^>]*\/>/i, '');

  const vb = out.match(/viewBox\s*=\s*"([^"]+)"/);
  if (!vb) return out;
  const parts = vb[1].trim().split(/[\s,]+/).map(Number);
  if (parts.length !== 4 || !parts.every(Number.isFinite)) return out;
  const [, , vbW, vbH] = parts;
  const strayW = vbW * 2;
  const strayH = vbH * 2;

  return out.replace(/<path\b[^>]*\bd\s*=\s*"([^"]*)"[^>]*\/>/g, (match, d) => {
    const ext = pathExtent(d);
    if (!ext) return match;
    if (ext.xMax - ext.xMin > strayW || ext.yMax - ext.yMin > strayH) return '';
    return match;
  });
}

const svgoConfig = {
  multipass: true,
  floatPrecision: 1,
  plugins: [
    {
      name: 'preset-default',
      params: {
        overrides: {
          // Don't merge paths: the exports use per-path stroke widths/colors
          // in places, and merging can drop style distinctions.
          mergePaths: false,
          // Keep comments off; these files have QCAD export markers.
          removeComments: true
        }
      }
    },
    'removeDimensions'
  ]
};

async function run() {
  const entries = await readdir(svgDir);
  const svgs = entries.filter((f) => f.endsWith('.svg')).sort();

  let totalBefore = 0;
  let totalAfter = 0;

  for (const name of svgs) {
    const path = join(svgDir, name);
    const before = await readFile(path, 'utf8');
    const pre = preClean(before);
    const result = optimize(pre, { path, ...svgoConfig });
    if ('error' in result && result.error) {
      console.error(`  ! ${name}: ${result.error}`);
      continue;
    }
    const after = result.data;
    await writeFile(path, after);
    const sBefore = Buffer.byteLength(before);
    const sAfter = Buffer.byteLength(after);
    totalBefore += sBefore;
    totalAfter += sAfter;
    const pct = ((1 - sAfter / sBefore) * 100).toFixed(1);
    console.log(
      `  ${name.padEnd(26)} ${(sBefore / 1024).toFixed(0).padStart(6)} KB → ${(sAfter / 1024).toFixed(0).padStart(6)} KB  (−${pct}%)`
    );
  }

  const pct = ((1 - totalAfter / totalBefore) * 100).toFixed(1);
  console.log(
    `\n  total${' '.repeat(22)} ${(totalBefore / 1024).toFixed(0).padStart(6)} KB → ${(totalAfter / 1024).toFixed(0).padStart(6)} KB  (−${pct}%)`
  );
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
