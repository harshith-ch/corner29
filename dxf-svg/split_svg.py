#!/usr/bin/env python3
"""
split_svg.py: Split a wide CAD-exported SVG (from QCAD's dwg2svg, etc.) into
one file per drawing using X-axis bands.

Each input SVG is assumed to contain several plans/sections side by side in
DXF world coordinates, wrapped in a single outermost <g transform="scale(1,-1)">.
The band boundaries are provided as [xmin, xmax] pairs in that coordinate space.

Per-band output is web-ready:
  - white background rect
  - <style> injecting vector-effect:non-scaling-stroke so strokes are visible
    at any zoom in a browser
  - viewBox cropped to the band (keeping the full Y range of the source)
  - only elements whose center X lies in the band

Usage:
  ./split_svg.py input.svg --bands bands.json --names names.json -o out/
  ./split_svg.py input.svg -o out/            # auto bands (uses defaults)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# --------------------------------------------------------------------------- #
# Simple SVG path "d" parser — returns (min_x, max_x) of all coordinate
# references. Handles the commands QCAD emits (M/L/C/Z/A all absolute) plus
# a broader set for robustness.
# --------------------------------------------------------------------------- #
_TOKEN_RE = re.compile(r'[A-Za-z]|-?\d+\.?\d*(?:[eE][-+]?\d+)?')


def path_xy_extent(d: str):
    """Return (min_x, max_x, min_y, max_y) of all coordinate refs, or None."""
    tokens = _TOKEN_RE.findall(d)
    xs: list[float] = []
    ys: list[float] = []
    i = 0
    n = len(tokens)
    cmd = None
    while i < n:
        t = tokens[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in ("Z", "z"):
                continue
        if cmd in ("M", "L", "T", "m", "l", "t"):
            xs.append(float(tokens[i])); ys.append(float(tokens[i + 1])); i += 2
        elif cmd in ("H", "h"):
            xs.append(float(tokens[i])); i += 1
        elif cmd in ("V", "v"):
            ys.append(float(tokens[i])); i += 1
        elif cmd in ("C", "c"):
            xs.append(float(tokens[i])); ys.append(float(tokens[i + 1]))
            xs.append(float(tokens[i + 2])); ys.append(float(tokens[i + 3]))
            xs.append(float(tokens[i + 4])); ys.append(float(tokens[i + 5]))
            i += 6
        elif cmd in ("S", "s", "Q", "q"):
            xs.append(float(tokens[i])); ys.append(float(tokens[i + 1]))
            xs.append(float(tokens[i + 2])); ys.append(float(tokens[i + 3]))
            i += 4
        elif cmd in ("A", "a"):
            # rx ry angle large sweep x y
            xs.append(float(tokens[i + 5])); ys.append(float(tokens[i + 6]))
            i += 7
        else:
            i += 1
    if not xs or not ys:
        return None
    return min(xs), max(xs), min(ys), max(ys)


def path_x_extent(d: str):
    r = path_xy_extent(d)
    return None if r is None else (r[0], r[1])


# --------------------------------------------------------------------------- #
# Element scanner. Finds every self-closing <path .../>, <circle .../> and
# <ellipse .../> at any nesting depth and returns (start, end, elem_str, center_x).
# --------------------------------------------------------------------------- #
_PATH_RE = re.compile(r'<path\b[^/>]*/\s*>')
_CIRCLE_RE = re.compile(r'<circle\b[^/>]*/\s*>')
_ELLIPSE_RE = re.compile(r'<ellipse\b[^/>]*/\s*>')
_LINE_RE = re.compile(r'<line\b[^/>]*/\s*>')
_RECT_RE = re.compile(r'<rect\b[^/>]*/\s*>')


def find_elements(svg_text: str):
    """Yield (elem_str, center_x, x_ext, center_y, y_ext) for every geometric
    element in the SVG. (Kept compatible with older callers: they use the first
    three values via `for elem, cx, ext in find_elements(...)`.)"""
    for m in _PATH_RE.finditer(svg_text):
        elem = m.group(0)
        dm = re.search(r' d="([^"]*)"', elem)
        if not dm:
            continue
        ext = path_xy_extent(dm.group(1))
        if ext is None:
            continue
        x0, x1, y0, y1 = ext
        yield elem, 0.5 * (x0 + x1), (x0, x1), 0.5 * (y0 + y1), (y0, y1)

    for m in _CIRCLE_RE.finditer(svg_text):
        elem = m.group(0)
        cx = re.search(r' cx="(-?\d+\.?\d*)"', elem)
        cy = re.search(r' cy="(-?\d+\.?\d*)"', elem)
        r = re.search(r' r="(-?\d+\.?\d*)"', elem)
        if not cx:
            continue
        cxv = float(cx.group(1))
        cyv = float(cy.group(1)) if cy else 0.0
        rv = float(r.group(1)) if r else 0.0
        yield elem, cxv, (cxv - rv, cxv + rv), cyv, (cyv - rv, cyv + rv)

    for m in _ELLIPSE_RE.finditer(svg_text):
        elem = m.group(0)
        cx = re.search(r' cx="(-?\d+\.?\d*)"', elem)
        cy = re.search(r' cy="(-?\d+\.?\d*)"', elem)
        rx = re.search(r' rx="(-?\d+\.?\d*)"', elem)
        ry = re.search(r' ry="(-?\d+\.?\d*)"', elem)
        if not cx:
            continue
        cxv = float(cx.group(1))
        cyv = float(cy.group(1)) if cy else 0.0
        rxv = float(rx.group(1)) if rx else 0.0
        ryv = float(ry.group(1)) if ry else 0.0
        yield elem, cxv, (cxv - rxv, cxv + rxv), cyv, (cyv - ryv, cyv + ryv)

    for m in _LINE_RE.finditer(svg_text):
        elem = m.group(0)
        x1 = re.search(r' x1="(-?\d+\.?\d*)"', elem)
        x2 = re.search(r' x2="(-?\d+\.?\d*)"', elem)
        y1 = re.search(r' y1="(-?\d+\.?\d*)"', elem)
        y2 = re.search(r' y2="(-?\d+\.?\d*)"', elem)
        if not (x1 and x2):
            continue
        xa = float(x1.group(1)); xb = float(x2.group(1))
        ya = float(y1.group(1)) if y1 else 0.0
        yb = float(y2.group(1)) if y2 else 0.0
        yield (elem, 0.5 * (xa + xb), (min(xa, xb), max(xa, xb)),
               0.5 * (ya + yb), (min(ya, yb), max(ya, yb)))

    for m in _RECT_RE.finditer(svg_text):
        elem = m.group(0)
        x = re.search(r' x="(-?\d+\.?\d*)"', elem)
        y = re.search(r' y="(-?\d+\.?\d*)"', elem)
        w = re.search(r' width="(-?\d+\.?\d*)"', elem)
        h = re.search(r' height="(-?\d+\.?\d*)"', elem)
        if not x:
            continue
        xv = float(x.group(1))
        yv = float(y.group(1)) if y else 0.0
        wv = float(w.group(1)) if w else 0.0
        hv = float(h.group(1)) if h else 0.0
        yield (elem, xv + 0.5 * wv, (xv, xv + wv),
               yv + 0.5 * hv, (yv, yv + hv))


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
DEFAULT_OFFICE_BANDS = [
    [1804, 34804],
    [48804, 79804],
    [93804, 124804],
    [138804, 169804],
    [184804, 217336],
]
DEFAULT_OFFICE_NAMES = [
    "ground_floor", "first_floor", "second_floor", "third_floor", "fourth_floor",
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output-dir", type=Path, default=Path("."))
    ap.add_argument("--bands", type=Path, default=None,
                    help="JSON [[xmin, xmax], ...]")
    ap.add_argument("--names", type=Path, default=None,
                    help="JSON list of names, one per band")
    ap.add_argument("--stroke-width", type=float, default=8.0,
                    help="Hard-force inline stroke-width in drawing units. "
                         "Drawing is in mm, so 8 = 8mm. Default 8. Set to 0 to "
                         "disable and rely on non-scaling-stroke CSS only.")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    if not args.input.exists():
        print(f"error: {args.input} not found", file=sys.stderr)
        return 2

    # Bands + names
    if args.bands:
        bands = json.loads(args.bands.read_text())
    else:
        bands = DEFAULT_OFFICE_BANDS
    if args.names:
        names = json.loads(args.names.read_text())
    else:
        names = DEFAULT_OFFICE_NAMES
    while len(names) < len(bands):
        names.append(f"band_{len(names) + 1:02d}")

    print(f"Reading {args.input} ({args.input.stat().st_size // 1024 // 1024} MB)", flush=True)
    txt = args.input.read_text()

    # Extract the source viewBox to determine Y range and outer SVG style.
    svg_open = re.search(r'<svg\b[^>]*>', txt)
    if not svg_open:
        print("error: no <svg> opening tag found", file=sys.stderr)
        return 2
    vb = re.search(r'viewBox="([^"]+)"', svg_open.group(0))
    if not vb:
        print("error: source SVG has no viewBox", file=sys.stderr)
        return 2
    vb_x, vb_y, vb_w, vb_h = [float(s) for s in vb.group(1).split()]
    print(f"source viewBox: x={vb_x:.1f} y={vb_y:.1f} w={vb_w:.1f} h={vb_h:.1f}")

    # Normalize bands: accept [x0,x1] or [x0,x1,y0,y1]. Pre-flip y, so "above"
    # in the displayed page has MORE-POSITIVE path-y (less-negative).
    norm_bands = []
    for b in bands:
        if len(b) == 2:
            norm_bands.append((b[0], b[1], -float("inf"), float("inf")))
        elif len(b) == 4:
            norm_bands.append((b[0], b[1], b[2], b[3]))
        else:
            print(f"error: band must have 2 or 4 values, got {b}", file=sys.stderr)
            return 2
    bands = norm_bands

    # Bucket elements by band. Also track tight content bbox per band so the
    # emitted viewBox hugs the drawing instead of reusing the full source frame.
    buckets: list[list[str]] = [[] for _ in bands]
    content_bbox = [None] * len(bands)  # each: [xmin, xmax, ymin, ymax]
    assigned = skipped = 0
    sw_pattern = re.compile(r'stroke-width:[0-9.]+\s*;?')
    for elem, cx, x_ext, cy, y_ext in find_elements(txt):
        placed = False
        for i, (bx0, bx1, by0, by1) in enumerate(bands):
            if bx0 <= cx <= bx1 and by0 <= cy <= by1:
                if args.stroke_width > 0:
                    new_attr = f'stroke-width:{args.stroke_width};'
                    if sw_pattern.search(elem):
                        elem = sw_pattern.sub(new_attr, elem)
                    else:
                        elem = re.sub(r'style="([^"]*)"',
                                      lambda m: f'style="{m.group(1).rstrip(";")};{new_attr}"',
                                      elem, count=1)
                buckets[i].append(elem)
                # Track extents, but CLAMP to the band bounds. A few stray
                # elements have their center in this band yet extend far into
                # neighboring bands (e.g., a horizontal sheet divider); without
                # clamping they blow up the computed viewBox.
                clamped_x0 = max(x_ext[0], bx0)
                clamped_x1 = min(x_ext[1], bx1)
                clamped_y0 = max(y_ext[0], by0) if by0 != -float("inf") else y_ext[0]
                clamped_y1 = min(y_ext[1], by1) if by1 !=  float("inf") else y_ext[1]
                if content_bbox[i] is None:
                    content_bbox[i] = [clamped_x0, clamped_x1, clamped_y0, clamped_y1]
                else:
                    cb = content_bbox[i]
                    if clamped_x0 < cb[0]: cb[0] = clamped_x0
                    if clamped_x1 > cb[1]: cb[1] = clamped_x1
                    if clamped_y0 < cb[2]: cb[2] = clamped_y0
                    if clamped_y1 > cb[3]: cb[3] = clamped_y1
                placed = True
                assigned += 1
                break
        if not placed:
            skipped += 1
    print(f"{assigned} elements placed, {skipped} discarded (outside all bands)")

    # Emit
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for i, (bx0, bx1, by0, by1) in enumerate(bands):
        cb = content_bbox[i]
        if cb is None:
            print(f"  warning: band {names[i]!r} is empty, skipping")
            continue
        # Tight viewBox around content + small padding. Path coords are in the
        # pre-flip space (y negative); the outer <g transform="scale(1,-1)">
        # flips them, so display-y = -path-y. Thus the viewBox in display coords
        # has y = -cb[3] (because +y in display corresponds to -y in path space).
        pad = 0.01 * max(cb[1] - cb[0], cb[3] - cb[2])
        vb_x0 = cb[0] - pad
        vb_w = (cb[1] - cb[0]) + 2 * pad
        # post-flip y range
        vb_y0 = -cb[3] - pad
        vb_h = (cb[3] - cb[2]) + 2 * pad
        new_vb = f"{vb_x0:.2f} {vb_y0:.2f} {vb_w:.2f} {vb_h:.2f}"
        body = "".join(buckets[i])
        # CSS: non-scaling-stroke keeps strokes at fixed pixel width in browsers
        # No physical units on width/height: gigantic mm values (33000mm = ~125k
        # CSS pixels) break image renderers and cause weird browser behavior.
        # Unitless dimensions let the container size the display; viewBox keeps
        # coordinates in drawing units.
        svg_out = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!-- Split from QCAD export -->\n'
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
            f'viewBox="{new_vb}" preserveAspectRatio="xMidYMid meet" '
            'style="stroke-linecap:round;stroke-linejoin:round;fill:none;'
            'stroke:#111;background:#fff">\n'
            f'<rect x="{vb_x0:.2f}" y="{vb_y0:.2f}" width="{vb_w:.2f}" '
            f'height="{vb_h:.2f}" fill="white" stroke="none"/>\n'
            '<g transform="scale(1,-1)">'
            f'{body}'
            '</g>\n'
            '</svg>\n'
        )
        out_path = args.output_dir / f"{names[i]}.svg"
        out_path.write_text(svg_out)
        kb = out_path.stat().st_size // 1024
        print(f"  {names[i]:16} -> {out_path.name}  ({len(buckets[i])} elems, {kb} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
