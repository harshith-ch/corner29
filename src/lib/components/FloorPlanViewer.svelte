<script lang="ts">
  import { loadSvgText } from '$lib/floor-prefetch';
  import type { Camera } from '$lib/content';
  import CameraPinLayer from './CameraPinLayer.svelte';

  interface Props {
    src: string;
    title: string;
    cameras?: Camera[];
    onCameraOpen?: (camera: Camera) => void;
    editMode?: boolean;
    onPlanClick?: (x: number, y: number) => void;
    overlay?: import('svelte').Snippet<[{ vbX: number; vbY: number; vbW: number; vbH: number; scale: number }]>;
  }

  let {
    src,
    title,
    cameras,
    onCameraOpen,
    editMode = false,
    onPlanClick,
    overlay
  }: Props = $props();

  let viewerEl: HTMLDivElement | undefined = $state();
  let viewport: HTMLDivElement | undefined = $state();
  let stageEl: HTMLDivElement | undefined = $state();
  let tx = $state(0);
  let ty = $state(0);
  let scale = $state(1);
  let loaded = $state(false);
  let isFullscreen = $state(false);
  let vbX = $state(0);
  let vbY = $state(0);
  let vbW = $state(1000);
  let vbH = $state(1000);
  // Content bbox in user coords — the authored viewBox tends to have empty
  // margin around the geometry, so we fit to the real extent instead.
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
    // Zero width/height happens during initial layout or when the element is
    // hidden (display:none ancestor, fullscreen transition). The ResizeObserver
    // will call fit again once the viewport has real dimensions.
    if (!rect.width || !rect.height) return;
    const s = Math.min(rect.width / contentW, rect.height / contentH) * 0.98;
    scale = s;
    tx = (rect.width - contentW * s) / 2 - (contentX - vbX) * s;
    ty = (rect.height - contentH * s) / 2 - (contentY - vbY) * s;
  }

  // Read the rendered geometry extent. Source SVGs are pre-cleaned offline
  // (background rect and stray paths removed), so a single getBBox gives a
  // tight content box without the intersection guards the old code needed.
  function measureContent() {
    const svg = stageEl?.querySelector('svg') as unknown as SVGGraphicsElement | null;
    if (!svg) return;
    try {
      const b = svg.getBBox();
      if (b.width > 0 && b.height > 0) {
        contentX = b.x;
        contentY = b.y;
        contentW = b.width;
        contentH = b.height;
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

  // Incremented on every load request. Any in-flight load whose token no
  // longer matches has been superseded by a newer src and must not commit —
  // otherwise an earlier slow fetch can overwrite a later fast one.
  let loadToken = 0;

  async function loadSvg(url: string) {
    const token = ++loadToken;
    loaded = false;
    svgMarkup = '';
    try {
      const text = await loadSvgText(url);
      if (token !== loadToken) return;
      const match = text.match(/viewBox\s*=\s*"([^"]+)"/);
      if (match) {
        const parts = match[1].trim().split(/[\s,]+/).map(Number);
        if (parts.length === 4 && parts.every((n) => Number.isFinite(n))) {
          vbX = parts[0];
          vbY = parts[1];
          vbW = parts[2];
          vbH = parts[3];
          contentX = vbX;
          contentY = vbY;
          contentW = vbW;
          contentH = vbH;
        }
      }
      svgMarkup = text;
      loaded = true;
      // setTimeout (not requestAnimationFrame) because rAF is paused in
      // background/hidden tabs — we want the plan sized correctly even when
      // the user opens the page in a background tab.
      setTimeout(() => {
        if (token !== loadToken) return;
        measureContent();
        fit();
      }, 0);
    } catch (e) {
      if (token !== loadToken) return;
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
  // Pointer-down origin in client coords for click vs drag detection.
  let downX = 0;
  let downY = 0;
  let moveDist = 0;

  function onPointerDown(e: PointerEvent) {
    if (e.button !== 0 && e.pointerType === 'mouse') return;
    dragging = true;
    lastX = e.clientX;
    lastY = e.clientY;
    downX = e.clientX;
    downY = e.clientY;
    moveDist = 0;
    (e.currentTarget as Element).setPointerCapture(e.pointerId);
  }

  function onPointerMove(e: PointerEvent) {
    if (!dragging) return;
    tx += e.clientX - lastX;
    ty += e.clientY - lastY;
    lastX = e.clientX;
    lastY = e.clientY;
    moveDist = Math.max(
      moveDist,
      Math.hypot(e.clientX - downX, e.clientY - downY)
    );
  }

  function onPointerUp(e: PointerEvent) {
    // 6px tolerates hand tremor on high-DPI trackpads; 4px suppressed taps
    // when users clicked at the moment of micro-drift.
    const wasClick = dragging && moveDist < 6;
    dragging = false;
    try {
      (e.currentTarget as Element).releasePointerCapture(e.pointerId);
    } catch {
      // Some browsers throw if the pointer was already released (e.g. when
      // pointercancel fires before pointerup). Safe to ignore.
    }
    if (wasClick && editMode && onPlanClick) {
      const svg = stageEl?.querySelector('svg') as SVGGraphicsElement | null;
      const ctm = svg?.getScreenCTM();
      if (svg && ctm && Number.isFinite(ctm.a) && ctm.a !== 0 && ctm.d !== 0) {
        try {
          // createSVGPoint lives on SVGSVGElement, not the generic graphics type.
          const pt = (svg as unknown as SVGSVGElement).createSVGPoint();
          pt.x = e.clientX;
          pt.y = e.clientY;
          const local = pt.matrixTransform(ctm.inverse());
          onPlanClick(local.x, local.y);
        } catch {
          // ctm.inverse() throws on singular matrices. Drop the click.
        }
      }
    }
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

  async function toggleFullscreen() {
    if (!viewerEl) return;
    try {
      // Only exit fullscreen if *our* viewer is the one in fullscreen.
      // Otherwise we'd yank another viewer (or unrelated element) out.
      if (document.fullscreenElement === viewerEl) {
        await document.exitFullscreen();
      } else if (!document.fullscreenElement) {
        await viewerEl.requestFullscreen();
      }
    } catch (e) {
      console.error('fullscreen toggle failed', e);
    }
  }

  function onFullscreenChange() {
    isFullscreen = document.fullscreenElement === viewerEl;
    setTimeout(fit, 0);
  }

  $effect(() => {
    loadSvg(src);
  });

  $effect(() => {
    document.addEventListener('fullscreenchange', onFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', onFullscreenChange);
  });

  // Re-fit when the viewport resizes (window resize, layout shift, mobile
  // browser chrome showing/hiding). Without this the plan stays scaled to
  // whatever the viewport was at initial load and overflows or under-fills.
  $effect(() => {
    if (!viewport) return;
    const ro = new ResizeObserver(() => fit());
    ro.observe(viewport);
    return () => ro.disconnect();
  });
</script>

<div class="viewer" bind:this={viewerEl} class:fullscreen={isFullscreen}>
  <!-- role="img" (not "application") because pan/zoom isn't keyboard-driven;
       screen-reader users can still reach the zoom/fit/fullscreen buttons. -->
  <div
    class="viewport"
    bind:this={viewport}
    onwheel={onWheel}
    onpointerdown={onPointerDown}
    onpointermove={onPointerMove}
    onpointerup={onPointerUp}
    onpointercancel={onPointerUp}
    role="img"
    aria-label="Floor plan — {title}"
  >
    <div
      class="stage"
      bind:this={stageEl}
      style="width: {vbW}px; height: {vbH}px; transform: translate({tx}px, {ty}px) scale({scale});"
    >
      {#if loaded}
        <!-- Inlined SVG is trusted: the only caller is FloorPlanViewer, and
             src is always a URL under /svg/ shipped with the build. If that
             directory ever serves user-supplied content this becomes XSS. -->
        <!-- eslint-disable-next-line svelte/no-at-html-tags -->
        {@html svgMarkup}
        {#if cameras && cameras.length && onCameraOpen}
          <CameraPinLayer
            {cameras}
            {vbX}
            {vbY}
            {vbW}
            {vbH}
            {scale}
            onOpen={onCameraOpen}
          />
        {/if}
        {#if overlay}
          {@render overlay({ vbX, vbY, vbW, vbH, scale })}
        {/if}
      {/if}
    </div>

    {#if !loaded}
      <div class="loading">Loading {title}…</div>
    {/if}

    <div class="controls">
      <button type="button" onclick={() => zoomBy(1.3)} aria-label="Zoom in">+</button>
      <button type="button" onclick={() => zoomBy(1 / 1.3)} aria-label="Zoom out">−</button>
      <button type="button" onclick={fit} aria-label="Fit to view" title="Fit to view">⤢</button>
      <button
        type="button"
        onclick={toggleFullscreen}
        aria-label={isFullscreen ? 'Exit full screen' : 'Enter full screen'}
        title={isFullscreen ? 'Exit full screen' : 'Full screen'}
      >
        {isFullscreen ? '×' : '⛶'}
      </button>
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

  .viewer.fullscreen {
    border-radius: 0;
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

  /* Style ONLY the injected plan SVG (direct child of .stage), not overlay
     SVGs such as camera pins. */
  .stage > :global(svg) {
    display: block;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }

  /* Force strokes to stay visible regardless of zoom level. The DXF-exported
     SVGs use huge coordinate systems (~60k units wide) with hairline strokes
     that would otherwise render as sub-pixel lines. */
  .stage > :global(svg path),
  .stage > :global(svg line),
  .stage > :global(svg polyline),
  .stage > :global(svg polygon),
  .stage > :global(svg rect),
  .stage > :global(svg circle) {
    vector-effect: non-scaling-stroke;
  }

  /* Invert strokes for dark mode so lines read as light-on-dark. */
  :global(.dark) .stage > :global(svg) {
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
