#!/usr/bin/env python3
"""
dxf-svg: Convert a DXF file into one or more SVG files, one per detected drawing.

The modelspace is scanned for natural gaps along the X axis (i.e. regions where
very few entities live) and each resulting "band" is rendered as its own SVG
file. This works well for architectural drawing sets that contain multiple
plans/sections arranged horizontally across a single modelspace.

Use --single to render the entire modelspace as one SVG instead.

BACKENDS
--------
native     (default) uses ezdxf's built-in SVG backend. Memory-light, compact
           output, groups geometry by layer. Recommended for all cases.

matplotlib uses the matplotlib backend. Materializes every primitive as a
           figure patch and one <path> per segment. High memory, very bloated
           SVGs. Only useful as a fallback if you hit a native-backend bug.
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import ezdxf
from ezdxf import bbox
from ezdxf.addons.drawing import Frontend, RenderContext


# --------------------------------------------------------------------------- #
# Entity indexing
# --------------------------------------------------------------------------- #
@dataclass
class IndexedEntity:
    entity: object
    emin_x: float
    emin_y: float
    emax_x: float
    emax_y: float

    @property
    def cx(self) -> float:
        return 0.5 * (self.emin_x + self.emax_x)

    @property
    def cy(self) -> float:
        return 0.5 * (self.emin_y + self.emax_y)


def build_entity_index(msp) -> list[IndexedEntity]:
    """Compute a bbox for every entity once, so we can slice them cheaply."""
    cache = bbox.Cache()
    out = []
    for e in msp:
        try:
            eb = bbox.extents([e], cache=cache)
        except Exception:
            continue
        if not eb.has_data:
            continue
        out.append(
            IndexedEntity(
                entity=e,
                emin_x=eb.extmin.x,
                emin_y=eb.extmin.y,
                emax_x=eb.extmax.x,
                emax_y=eb.extmax.y,
            )
        )
    return out


# --------------------------------------------------------------------------- #
# Automatic band detection (split a wide sheet into multiple drawings)
# --------------------------------------------------------------------------- #
def detect_bands(
    entities: list[IndexedEntity],
    *,
    bin_width: float = 1000.0,
    empty_thresh: int = 5,
    min_gap_width: float = 2000.0,
    edge_pad: float = 500.0,
) -> list[tuple[float, float]]:
    """Detect plan X-bands by finding low-density gaps in entity centers.

    bin_width      width of each density histogram bin (drawing units)
    empty_thresh   a bin is "empty" if it contains <= this many entity centers
    min_gap_width  reject gaps narrower than this (drawing units)
    edge_pad       ignore gaps that touch the overall left/right extents
    """
    if not entities:
        return []

    centers = sorted(e.cx for e in entities)
    xmin, xmax = centers[0], centers[-1]
    if xmax - xmin < 2 * bin_width:
        return [(xmin, xmax)]

    # Build histogram of entity-center X values
    n_bins = int((xmax - xmin) / bin_width) + 2
    hist = [0] * n_bins
    for x in centers:
        idx = int((x - xmin) / bin_width)
        if 0 <= idx < n_bins:
            hist[idx] += 1

    # Walk bins and record runs of empty bins
    gaps: list[tuple[float, float]] = []
    in_gap = False
    g_start = 0.0
    for i, h in enumerate(hist):
        b_start = xmin + i * bin_width
        if h <= empty_thresh:
            if not in_gap:
                g_start = b_start
                in_gap = True
        else:
            if in_gap:
                gaps.append((g_start, b_start))
                in_gap = False
    if in_gap:
        gaps.append((g_start, xmin + n_bins * bin_width))

    # Keep only gaps that are wide enough and not touching the outer edges
    real_gaps = [
        (s, e) for s, e in gaps
        if (e - s) >= min_gap_width
        and s > xmin + edge_pad
        and e < xmax - edge_pad
    ]

    # Turn the gap boundaries into inclusive bands
    bands: list[tuple[float, float]] = []
    cur = xmin
    for s, e in real_gaps:
        bands.append((cur, s))
        cur = e
    bands.append((cur, xmax))
    return bands


def merge_small_bands(
    bands: list[tuple[float, float]],
    entities: list[IndexedEntity],
    *,
    min_entities: int,
) -> list[tuple[float, float]]:
    """Merge bands that contain fewer than `min_entities` into their nearest
    neighbor, so we don't emit an SVG for a stray 5-entity sliver between
    real drawings. Bands below the threshold are folded into whichever
    adjacent band has more entities."""
    if min_entities <= 0 or len(bands) < 2:
        return bands

    # Count entities per band
    def count(b):
        bx0, bx1 = b
        return sum(1 for e in entities if bx0 <= e.cx <= bx1)

    # Iteratively fold small bands into neighbors until all bands pass
    bands = list(bands)
    counts = [count(b) for b in bands]
    changed = True
    while changed:
        changed = False
        for i, c in enumerate(counts):
            if c >= min_entities:
                continue
            if len(bands) == 1:
                break
            if i == 0:
                bands[1] = (bands[0][0], bands[1][1])
                bands.pop(0); counts.pop(0)
            elif i == len(bands) - 1:
                bands[-2] = (bands[-2][0], bands[-1][1])
                bands.pop(); counts.pop()
            else:
                # fold into the neighbor with more entities
                left, right = counts[i - 1], counts[i + 1]
                if left >= right:
                    bands[i - 1] = (bands[i - 1][0], bands[i][1])
                else:
                    bands[i + 1] = (bands[i][0], bands[i + 1][1])
                bands.pop(i); counts.pop(i)
            counts = [count(b) for b in bands]
            changed = True
            break
    return bands


def entities_in_band(
    entities: list[IndexedEntity],
    bx0: float,
    bx1: float,
    *,
    slack: float = 3000.0,
) -> list[IndexedEntity]:
    """Return entities whose center is in [bx0, bx1] AND whose extent stays
    within the band (plus some slack). The second condition filters out rogue
    drawing-wide entities that would otherwise blow up the tight bbox."""
    out = []
    for e in entities:
        if not (bx0 <= e.cx <= bx1):
            continue
        if e.emin_x < bx0 - slack or e.emax_x > bx1 + slack:
            continue
        out.append(e)
    return out


def tight_bbox(ents: list[IndexedEntity]) -> tuple[float, float, float, float]:
    xmin = min(e.emin_x for e in ents)
    ymin = min(e.emin_y for e in ents)
    xmax = max(e.emax_x for e in ents)
    ymax = max(e.emax_y for e in ents)
    return xmin, ymin, xmax, ymax


# --------------------------------------------------------------------------- #
# Backends
# --------------------------------------------------------------------------- #
def render_native(
    doc,
    entities: list[IndexedEntity],
    out_path: Path,
    *,
    bg: str = "white",
) -> None:
    """Render via ezdxf's native SVG backend. Fast, compact, layer-grouped.

    bg: "white" -> white background, dark strokes (suitable for web display)
        "dark"  -> ezdxf's default dark CAD-editor background
    """
    from ezdxf.addons.drawing import layout
    from ezdxf.addons.drawing.svg import SVGBackend
    from ezdxf.addons.drawing.config import (
        Configuration, BackgroundPolicy, ColorPolicy,
    )

    if bg == "white":
        config = Configuration(
            background_policy=BackgroundPolicy.WHITE,
            color_policy=ColorPolicy.COLOR_SWAP_BW,
        )
    else:
        config = Configuration()

    backend = SVGBackend()
    ctx = RenderContext(doc)
    Frontend(ctx, backend, config=config).draw_entities([e.entity for e in entities])

    # Auto-size the page to the content
    page = layout.Page(
        width=0,              # 0 => fit to content
        height=0,
        units=layout.Units.mm,
        margins=layout.Margins.all(5),
    )
    settings = layout.Settings(
        fit_page=True,
        scale=1.0,
        output_coordinate_space=1000,   # higher precision SVG coords
    )
    svg_text = backend.get_string(page, settings=settings)
    out_path.write_text(svg_text, encoding="utf-8")


def render_matplotlib(
    doc,
    entities: list[IndexedEntity],
    out_path: Path,
    *,
    margin: float = 1500.0,
    fig_width: float = 16.0,
) -> None:
    """Fallback: render via matplotlib. High memory, large SVGs."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    xmin, ymin, xmax, ymax = tight_bbox(entities)
    xmin -= margin; xmax += margin
    ymin -= margin; ymax += margin
    aspect = (xmax - xmin) / max(1.0, (ymax - ymin))
    fig_h = fig_width / aspect

    fig = plt.figure(figsize=(fig_width, fig_h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    ax.set_axis_off()
    ctx = RenderContext(doc)
    be = MatplotlibBackend(ax)
    Frontend(ctx, be).draw_entities([e.entity for e in entities])
    be.finalize()
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    fig.savefig(out_path, format="svg", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    gc.collect()


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Convert a DXF file into one SVG per detected drawing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("input", type=Path, help="Path to input .dxf file")
    ap.add_argument(
        "-o", "--output-dir", type=Path, default=Path("."),
        help="Directory to write SVGs into (default: current directory)",
    )
    ap.add_argument(
        "--prefix", default=None,
        help="Filename prefix. Default: derived from the input filename.",
    )
    ap.add_argument(
        "--names", type=Path, default=None,
        help="Optional JSON file with a list of names, one per detected band. "
             "Example: [\"ground\", \"floor_1\", \"floor_2\"]",
    )
    ap.add_argument(
        "--backend", choices=["native", "matplotlib"], default="native",
        help="Rendering backend (default: native)",
    )
    ap.add_argument(
        "--single", action="store_true",
        help="Render the whole modelspace as a single SVG instead of splitting.",
    )
    ap.add_argument(
        "--bands", type=Path, default=None,
        help="Optional JSON file with manual band boundaries, bypassing "
             "auto-detection. Format: [[xmin, xmax], [xmin, xmax], ...]. "
             "Entities are assigned to whichever band their center falls inside.",
    )
    ap.add_argument(
        "--bin-width", type=float, default=1000.0,
        help="Histogram bin width for gap detection (default: 1000)",
    )
    ap.add_argument(
        "--empty-thresh", type=int, default=5,
        help="Max entity centers in a bin for it to count as empty (default: 5)",
    )
    ap.add_argument(
        "--min-gap", type=float, default=2000.0,
        help="Minimum gap width to treat as an inter-plan separator (default: 2000)",
    )
    ap.add_argument(
        "--min-entities", type=int, default=50,
        help="Bands with fewer than this many entities are merged into their "
             "neighbor (default: 50). Set to 0 to disable merging.",
    )
    ap.add_argument(
        "--margin", type=float, default=1500.0,
        help="Extra drawing-unit margin around each cropped plan "
             "(matplotlib backend only; default: 1500)",
    )
    ap.add_argument(
        "--bg", choices=["white", "dark"], default="white",
        help="Background color scheme for the native backend. 'white' uses a "
             "white background with dark strokes (for web display). 'dark' "
             "uses ezdxf's default CAD-editor dark theme. Default: white.",
    )
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    if not args.input.exists():
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 2

    if args.prefix is None:
        prefix = args.input.stem.lower().replace(" ", "_") + "_"
    else:
        prefix = args.prefix
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading {args.input}", flush=True)
    doc = ezdxf.readfile(str(args.input))
    msp = doc.modelspace()

    print("Indexing entities...", flush=True)
    index = build_entity_index(msp)
    print(f"  {len(index)} entities with bboxes", flush=True)

    # Decide bands
    if args.single:
        xmin = min(e.emin_x for e in index)
        xmax = max(e.emax_x for e in index)
        bands = [(xmin, xmax)]
    elif args.bands:
        raw = json.loads(args.bands.read_text())
        bands = [(float(a), float(b)) for a, b in raw]
    else:
        bands = detect_bands(
            index,
            bin_width=args.bin_width,
            empty_thresh=args.empty_thresh,
            min_gap_width=args.min_gap,
        )
        if args.min_entities > 0:
            before = len(bands)
            bands = merge_small_bands(bands, index, min_entities=args.min_entities)
            if len(bands) != before:
                print(f"  merged small bands: {before} -> {len(bands)}", flush=True)
    print(f"Detected {len(bands)} band(s)", flush=True)
    for i, (a, b) in enumerate(bands, 1):
        print(f"  band {i}: x=[{a:.0f}, {b:.0f}]  width={b-a:.0f}", flush=True)

    # Build per-band name list
    if args.names:
        names = json.loads(args.names.read_text())
        if len(names) < len(bands):
            names += [f"part_{i+1:02d}" for i in range(len(names), len(bands))]
    else:
        names = [f"{i+1:02d}" for i in range(len(bands))]

    # Render each band
    for i, (bx0, bx1) in enumerate(bands):
        ents = entities_in_band(index, bx0, bx1)
        if not ents:
            print(f"  band {i+1}: no entities after containment filter — skipping")
            continue

        tag = names[i] if i < len(names) else f"{i+1:02d}"
        out = args.output_dir / f"{prefix}{tag}.svg"

        if args.verbose:
            xmin, ymin, xmax, ymax = tight_bbox(ents)
            print(f"  band {i+1}: {len(ents)} entities  "
                  f"x=[{xmin:.0f}, {xmax:.0f}] y=[{ymin:.0f}, {ymax:.0f}]",
                  flush=True)

        if args.backend == "native":
            render_native(doc, ents, out, bg=args.bg)
        else:
            render_matplotlib(doc, ents, out, margin=args.margin)

        size_kb = out.stat().st_size // 1024
        print(f"wrote {out}  ({len(ents)} entities, {size_kb} KB)", flush=True)
        gc.collect()

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
