# dxf-svg

Converts a DXF file into one SVG per detected drawing. Useful when an
architect hands you a single DXF that contains several plans/sections
arranged horizontally across the same modelspace (a common way CAD sheets
are packed).

## Why a separate tool

1. **Memory.** DXFs with many `INSERT` (block) references, e.g. furniture
   plans with hundreds of chairs and desks, explode into tens of thousands
   of primitives when rendered. The matplotlib-backed render path in
   `ezdxf` holds all of those in memory and can easily exhaust a few GB
   just for one drawing. This script defaults to `ezdxf`'s native SVG
   backend, which streams geometry directly to disk and uses far less RAM.
2. **File size.** The native backend groups geometry by layer and avoids
   one-`<path>`-per-segment bloat. Output is typically 5–10× smaller than
   matplotlib's for the same drawing.
3. **Multi-drawing splits.** Auto-detects horizontal gaps in the
   modelspace and writes one SVG per drawing, so you don't have to crop
   manually.

## Install

### With `uv` (recommended)

```sh
cd dxf-svg
uv sync
uv run ./convert.py --help
```

Or run the script directly without installing:

```sh
uv run --with "ezdxf>=1.3.0" ./convert.py path/to/plan.dxf
```

### With `pip`

```sh
cd dxf-svg
python -m venv .venv
source .venv/bin/activate
pip install -e .
./convert.py --help
```

## Usage

### Auto-split a multi-drawing DXF

```sh
./convert.py "OFFICE FURNITURE PLANS.dxf" -o ./out
```

Output:

```
Reading OFFICE FURNITURE PLANS.dxf
Indexing entities...
  3472 entities with bboxes
Detected 5 band(s)
  band 1: x=[1804, 34804]    width=33000
  band 2: x=[48804, 79804]   width=31000
  band 3: x=[93804, 124804]  width=31000
  band 4: x=[138804, 169804] width=31000
  band 5: x=[184804, 217336] width=32532
wrote out/office_furniture_plans_01.svg  (631 entities, 312 KB)
wrote out/office_furniture_plans_02.svg  (688 entities, 389 KB)
wrote out/office_furniture_plans_03.svg  (720 entities, 401 KB)
...
```

### Custom filenames

Pass a JSON file mapping band index → name:

```sh
cat > names.json <<EOF
["ground", "floor_1", "floor_2", "floor_3", "floor_4"]
EOF

./convert.py "OFFICE FURNITURE PLANS.dxf" -o ./out --names names.json
```

produces `office_furniture_plans_ground.svg`, `…_floor_1.svg`, etc.

Or override the filename prefix:

```sh
./convert.py plans.dxf -o ./out --prefix office_
```

### Render the whole modelspace as one SVG

```sh
./convert.py plans.dxf -o ./out --single
```

### Use the matplotlib fallback

Only useful if the native backend misrenders something for your file.
Prepare for big files and high memory:

```sh
./convert.py plans.dxf -o ./out --backend matplotlib
```

### Tuning the gap detection

If your DXF has tighter or wider spacing than the defaults assume:

```sh
./convert.py plans.dxf \
  --bin-width 500 \          # finer histogram
  --empty-thresh 2 \         # stricter "empty" bin
  --min-gap 1000 \           # smaller minimum gap
  --min-entities 100         # merge bands smaller than this into neighbors
```

Pass `--verbose` to see each band's entity count and tight bbox.

### When auto-detection misses

Some DXFs have thin slivers of entities between drawings (title-block seams,
dimension lines, legend text) that confuse the gap detector. If `-v` output
shows bands in the wrong places, you have two options:

**Option A — tune auto-detection.**

```sh
./convert.py plans.dxf -v \
  --empty-thresh 20 \   # allow up to 20 centers per "empty" bin
  --min-gap 3000 \      # require wider gaps to count as a split
  --min-entities 100    # drop bands smaller than this
```

**Option B — specify bands manually.**

```sh
cat > bands.json <<EOF
[
  [4562270, 4635000],
  [4635000, 4710000],
  [4710000, 4785000],
  [4713000, 4790000],
  [4790000, 4844950]
]
EOF

./convert.py plans.dxf --bands bands.json --names names.json -o ./out
```

Entity centers are assigned to whichever band they fall inside. Bands may
overlap — useful for vertically-stacked drawings that share X range.

## How it works

1. Read the DXF with `ezdxf`.
2. For every entity in the modelspace, compute its bbox (cached).
3. Build a 1D histogram of entity-center X values.
4. Find runs of near-empty bins — these are the inter-drawing gaps.
5. The bands between gaps become separate drawings.
6. For each band, keep only entities whose bbox stays roughly inside the
   band (prevents stray drawing-wide entities, e.g. a border, from
   inflating one band's bbox).
7. Render each band's entities with the chosen backend.

## Limitations

- Assumes drawings are separated horizontally. For vertically-stacked
  drawings you'd want a symmetric Y-axis split (easy change — the band
  detector is independent).
- `--backend matplotlib` produces SVGs 5–10× larger than the native
  backend. Only keep matplotlib installed if you need it.
- The native SVG backend is young; a few exotic DXF features (complex
  hatches, gradient-filled polys, specific MTEXT formatting) may render
  slightly differently than in matplotlib. File an issue or fall back
  to matplotlib for those specific plans if needed.

## Troubleshooting

**"Only 1 band detected when there should be more"** — lower
`--empty-thresh` or `--min-gap` or `--bin-width`. Run with `-v` to see
the per-band bboxes.

**"Bands overlap or look wrong"** — the entity clustering is fooled by a
drawing-wide entity. Check `-v` output; if one band's bbox covers the
whole drawing, that band has a rogue entity. You can file a follow-up
issue or split manually with `--single` per pre-cropped file.

**"Out of memory with --backend matplotlib"** — use the native backend
(the default). Matplotlib is not a realistic choice for furniture-heavy
plans.

**"Native backend rendering looks incomplete"** — try the matplotlib
backend on a single plan to compare. If you find something ezdxf's
native backend misrenders, that is a good bug report to file upstream.
