<script lang="ts">
  interface Props {
    src: string;
    title: string;
  }

  let { src, title }: Props = $props();

  let viewport: HTMLDivElement | undefined = $state();
  let stageEl: HTMLDivElement | undefined = $state();
  let tx = $state(0);
  let ty = $state(0);
  let scale = $state(1);
  let loaded = $state(false);
  let vbX = $state(0);
  let vbY = $state(0);
  let vbW = $state(1000);
  let vbH = $state(1000);
  // Fit only on the very first floor load; preserve the user's zoom/pan when
  // they switch floors so the view stays consistent.
  let hasFitOnce = false;
  // Tight content bounding box (excludes the background rect). These default
  // to the viewBox and get refined to the geometry's real extent after mount.
  let contentX = $state(0);
  let contentY = $state(0);
  let contentW = $state(1000);
  let contentH = $state(1000);
  let svgMarkup = $state('');

  function clamp(v: number, min: number, max: number) {
    return Math.max(min, Math.min(max, v));
  }

  function fit() {
    if (!viewport) return;
    const rect = viewport.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    // Fit the content bbox (not the full viewBox) so empty margins are trimmed.
    const s = Math.min(rect.width / contentW, rect.height / contentH) * 0.98;
    scale = s;
    // The stage is sized to the full viewBox and starts at (0, 0) in viewBox
    // coords. We translate so the content bbox ends up centered in the viewport.
    tx = (rect.width - contentW * s) / 2 - (contentX - vbX) * s;
    ty = (rect.height - contentH * s) / 2 - (contentY - vbY) * s;
  }

  // After render, measure the real geometry extent (skipping the bg <rect>)
  // by querying the first content <g> and taking its getBBox.
  // getBBox on the <svg> returns the union bbox of all children in viewBox
  // coords, accounting for any child transforms (including the DXF exporter's
  // scale(1,-1) flip). Because we strip the full-viewBox background <rect>
  // during parse, this bbox is tight to the actual geometry.
  function measureContent() {
    if (!stageEl) return;
    const svg = stageEl.querySelector('svg') as unknown as SVGGraphicsElement | null;
    if (!svg) return;
    try {
      const bbox = svg.getBBox();
      if (bbox.width > 0 && bbox.height > 0) {
        contentX = bbox.x;
        contentY = bbox.y;
        contentW = bbox.width;
        contentH = bbox.height;
        return;
      }
    } catch {
      // getBBox can throw on detached elements; fall through to viewBox.
    }
    contentX = vbX;
    contentY = vbY;
    contentW = vbW;
    contentH = vbH;
  }

  // Load SVG as text, extract viewBox, render inline.
  async function loadSvg(url: string) {
    loaded = false;
    svgMarkup = '';
    try {
      const res = await fetch(url);
      const text = await res.text();
      const match = text.match(/viewBox\s*=\s*"([^"]+)"/);
      if (match) {
        const parts = match[1].trim().split(/[\s,]+/).map(Number);
        if (parts.length === 4 && parts.every((n) => Number.isFinite(n))) {
          vbX = parts[0];
          vbY = parts[1];
          vbW = parts[2];
          vbH = parts[3];
          // Seed content bbox with viewBox as a safe fallback.
          contentX = vbX;
          contentY = vbY;
          contentW = vbW;
          contentH = vbH;
        }
      }
      // Strip the outer <?xml ... ?> declaration so we can embed, and remove the
      // full-viewBox background <rect> the DXF exporter inserts as the first
      // child — otherwise getBBox() on the svg would return the viewBox bounds
      // (with all its empty margin) instead of the real geometry bbox.
      svgMarkup = text
        .replace(/^<\?xml[^?]*\?>\s*/, '')
        .replace(/<rect\b[^>]*fill\s*=\s*"white"[^>]*\/>/i, '');
      loaded = true;
      // Wait for the DOM to mount the SVG, then measure. Only fit on first
      // load — subsequent floor switches keep the current zoom/pan.
      await new Promise(requestAnimationFrame);
      measureContent();
      if (!hasFitOnce) {
        fit();
        hasFitOnce = true;
      }
    } catch (e) {
      console.error('failed to load floor plan', url, e);
    }
  }

  function onWheel(e: WheelEvent) {
    if (!viewport) return;
    e.preventDefault();
    const rect = viewport.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    const next = clamp(scale * factor, 0.0001, 1000);
    const ratio = next / scale;
    tx = mx - (mx - tx) * ratio;
    ty = my - (my - ty) * ratio;
    scale = next;
  }

  let dragging = false;
  let lastX = 0;
  let lastY = 0;

  function onPointerDown(e: PointerEvent) {
    if (e.button !== 0 && e.pointerType === 'mouse') return;
    dragging = true;
    lastX = e.clientX;
    lastY = e.clientY;
    (e.currentTarget as Element).setPointerCapture(e.pointerId);
  }

  function onPointerMove(e: PointerEvent) {
    if (!dragging) return;
    tx += e.clientX - lastX;
    ty += e.clientY - lastY;
    lastX = e.clientX;
    lastY = e.clientY;
  }

  function onPointerUp(e: PointerEvent) {
    dragging = false;
    try {
      (e.currentTarget as Element).releasePointerCapture(e.pointerId);
    } catch {}
  }

  function zoomBy(factor: number) {
    if (!viewport) return;
    const rect = viewport.getBoundingClientRect();
    const mx = rect.width / 2;
    const my = rect.height / 2;
    const next = clamp(scale * factor, 0.0001, 1000);
    const ratio = next / scale;
    tx = mx - (mx - tx) * ratio;
    ty = my - (my - ty) * ratio;
    scale = next;
  }

  $effect(() => {
    loadSvg(src);
  });

  // Don't auto-fit on resize — preserves the user's zoom/pan across viewport
  // changes too. They can tap the Fit button if things go off-screen.
</script>

<div class="viewer">
  <div
    class="viewport"
    bind:this={viewport}
    onwheel={onWheel}
    onpointerdown={onPointerDown}
    onpointermove={onPointerMove}
    onpointerup={onPointerUp}
    onpointercancel={onPointerUp}
    role="application"
    aria-label="Floor plan viewer — {title}"
  >
    <div
      class="stage"
      bind:this={stageEl}
      style="width: {vbW}px; height: {vbH}px; transform: translate({tx}px, {ty}px) scale({scale});"
    >
      {#if loaded}
        <!-- eslint-disable-next-line svelte/no-at-html-tags -->
        {@html svgMarkup}
      {/if}
    </div>

    {#if !loaded}
      <div class="loading">Loading {title}…</div>
    {/if}

    <div class="controls">
      <button type="button" onclick={() => zoomBy(1.3)} aria-label="Zoom in">+</button>
      <button type="button" onclick={() => zoomBy(1 / 1.3)} aria-label="Zoom out">−</button>
      <button type="button" onclick={fit} aria-label="Fit to view" title="Fit to view">⤢</button>
    </div>

    <div class="hint">drag to pan · scroll to zoom</div>
  </div>
</div>

<style>
  .viewer {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
    border-radius: inherit;
    background: var(--viewer-bg, #f5f5f4);
  }

  :global(.dark) .viewer {
    background: var(--viewer-bg-dark, #171717);
  }

  .viewport {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
    touch-action: none;
    cursor: grab;
    user-select: none;
  }

  .viewport:active {
    cursor: grabbing;
  }

  .stage {
    position: absolute;
    top: 0;
    left: 0;
    transform-origin: 0 0;
    will-change: transform;
  }

  .stage :global(svg) {
    display: block;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }

  /* Force strokes to stay visible regardless of zoom level. The DXF-exported
     SVGs use huge coordinate systems (~60k units wide) with hairline strokes
     that would otherwise render as sub-pixel lines. */
  .stage :global(svg path),
  .stage :global(svg line),
  .stage :global(svg polyline),
  .stage :global(svg polygon),
  .stage :global(svg rect),
  .stage :global(svg circle) {
    vector-effect: non-scaling-stroke;
  }

  /* Invert strokes for dark mode so lines read as light-on-dark. */
  :global(.dark) .stage :global(svg) {
    filter: invert(0.95) hue-rotate(180deg);
  }

  .loading {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    font: 500 0.875rem var(--font-sans);
    color: currentColor;
    opacity: 0.5;
  }

  .controls {
    position: absolute;
    top: 12px;
    right: 12px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(6px);
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    padding: 3px;
  }

  :global(.dark) .controls {
    background: rgba(30, 30, 30, 0.9);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
  }

  .controls button {
    width: 34px;
    height: 34px;
    border: none;
    background: transparent;
    font-size: 16px;
    cursor: pointer;
    border-radius: 6px;
    color: currentColor;
  }

  .controls button:hover {
    background: rgba(0, 0, 0, 0.06);
  }

  :global(.dark) .controls button:hover {
    background: rgba(255, 255, 255, 0.08);
  }

  .hint {
    position: absolute;
    bottom: 10px;
    left: 12px;
    font: 400 0.7rem var(--font-sans);
    opacity: 0.5;
    pointer-events: none;
  }
</style>
