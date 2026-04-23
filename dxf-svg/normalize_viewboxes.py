#!/usr/bin/env python3
"""Rewrite each SVG's viewBox to a common size, centered on the existing
viewBox's center. Used after split_svg.py so all floor plans render at the
same apparent scale in a browser (no jarring zoom shift between drawings).

The input SVGs are expected to already have viewBoxes that tightly wrap their
content (as produced by the updated split_svg.py).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


VB_RE = re.compile(r'viewBox="(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)"')
BG_RE = re.compile(
    r'<rect\s+x="(-?[\d.]+)"\s+y="(-?[\d.]+)"\s+width="(-?[\d.]+)"\s+'
    r'height="(-?[\d.]+)"\s+fill="white"\s+stroke="none"/>'
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("svgs", nargs="+", type=Path,
                    help="SVG files to normalize (edits in place)")
    ap.add_argument("--pad", type=float, default=0.03,
                    help="Extra fractional padding around the largest drawing "
                         "(default 3%% = 0.03)")
    args = ap.parse_args(argv)

    # Pass 1: read each file's viewBox, figure out the target (max W, max H).
    info = []
    for p in args.svgs:
        if not p.exists():
            print(f"error: {p} not found", file=sys.stderr); return 2
        text = p.read_text()
        m = VB_RE.search(text)
        if not m:
            print(f"error: {p} has no viewBox", file=sys.stderr); return 2
        x, y, w, h = map(float, m.groups())
        info.append((p, text, x, y, w, h))

    target_w = max(w for _, _, _, _, w, _ in info) * (1 + args.pad)
    target_h = max(h for _, _, _, _, _, h in info) * (1 + args.pad)
    print(f"target viewBox size: {target_w:.2f} x {target_h:.2f}")

    # Pass 2: rewrite each viewBox to (target_w, target_h) centered on the
    # existing viewBox center. Also rewrite the white background <rect> to
    # cover the full new viewBox, and drop explicit width/height so the SVG
    # fills its container.
    for p, text, x, y, w, h in info:
        cx = x + 0.5 * w
        cy = y + 0.5 * h
        new_x = cx - 0.5 * target_w
        new_y = cy - 0.5 * target_h
        new_vb = f'viewBox="{new_x:.2f} {new_y:.2f} {target_w:.2f} {target_h:.2f}"'
        text = VB_RE.sub(new_vb, text, count=1)

        new_bg = (f'<rect x="{new_x:.2f}" y="{new_y:.2f}" '
                  f'width="{target_w:.2f}" height="{target_h:.2f}" '
                  'fill="white" stroke="none"/>')
        text, n = BG_RE.subn(new_bg, text, count=1)
        if n == 0:
            print(f"  warn: {p.name} missing white-bg rect")

        p.write_text(text)
        print(f"  {p.name:24} was {w:.0f}x{h:.0f}  ->  centered in {target_w:.0f}x{target_h:.0f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
