<script lang="ts">
  import type { Camera } from '$lib/content';

  interface Props {
    cameras: Camera[];
    vbX: number;
    vbY: number;
    vbW: number;
    vbH: number;
    scale: number;
    onOpen: (camera: Camera) => void;
  }

  let { cameras, vbX, vbY, vbW, vbH, scale, onOpen }: Props = $props();

  const inv = $derived(scale > 0 ? 1 / scale : 1);

  function pct(value: number, origin: number, extent: number) {
    return ((value - origin) / extent) * 100;
  }

  // Pie-slice path centered at 0,0, pointing up (screen -Y). Outer rotation
  // handles heading. Drawn in viewBox "-50 -50 100 100".
  function conePath(angle: number, radius: number) {
    const half = (angle / 2) * (Math.PI / 180);
    const x1 = -Math.sin(half) * radius;
    const y1 = -Math.cos(half) * radius;
    const x2 = Math.sin(half) * radius;
    const y2 = -Math.cos(half) * radius;
    const large = angle > 180 ? 1 : 0;
    return `M0 0 L${x1.toFixed(2)} ${y1.toFixed(2)} A${radius} ${radius} 0 ${large} 1 ${x2.toFixed(2)} ${y2.toFixed(2)} Z`;
  }
</script>

<div class="pin-layer">
  {#each cameras as cam (cam.id)}
    {@const fov = cam.fov ?? 75}
    {@const gradId = `cone-grad-${cam.id}`}
    <button
      type="button"
      class="pin"
      style="left: {pct(cam.x, vbX, vbW)}%; top: {pct(cam.y, vbY, vbH)}%;"
      aria-label={`Camera view: ${cam.title ?? cam.id}`}
      onclick={(e) => {
        e.stopPropagation();
        onOpen(cam);
      }}
      onpointerdown={(e) => e.stopPropagation()}
    >
      <span class="pin-visual" style="transform: translate(-50%, -50%) scale({inv});">
        <span class="cone-wrap" style="transform: rotate({cam.heading}deg);" aria-hidden="true">
          <svg class="cone" viewBox="-50 -50 100 100" preserveAspectRatio="xMidYMid meet">
            <defs>
              <radialGradient id={gradId} cx="0" cy="0" r="38" gradientUnits="userSpaceOnUse">
                <stop offset="0" stop-color="currentColor" stop-opacity="0.85" />
                <stop offset="0.55" stop-color="currentColor" stop-opacity="0.4" />
                <stop offset="1" stop-color="currentColor" stop-opacity="0.05" />
              </radialGradient>
            </defs>
            <path d={conePath(fov, 38)} fill="url(#{gradId})" />
            <path
              d={conePath(fov, 38)}
              fill="none"
              stroke="currentColor"
              stroke-opacity="0.95"
              stroke-width="1.6"
              stroke-linejoin="round"
              stroke-linecap="round"
            />
          </svg>
        </span>

        <span class="glyph-wrap" aria-hidden="true">
          <!-- Outlined camera for light mode -->
          <svg
            class="glyph glyph-light"
            viewBox="0 0 24 24"
            preserveAspectRatio="xMidYMid meet"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linejoin="round"
            stroke-linecap="round"
          >
            <path
              d="M3.5 7.5h3.25l1.5-2h7.5l1.5 2h3.25a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1h-17a1 1 0 0 1-1-1v-10a1 1 0 0 1 1-1z"
            />
            <circle cx="12" cy="13" r="3.75" />
          </svg>

          <!-- Filled camera for dark mode -->
          <svg
            class="glyph glyph-dark"
            viewBox="0 0 24 24"
            preserveAspectRatio="xMidYMid meet"
          >
            <path
              fill="currentColor"
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M9 4 7.5 6H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-3.5L15 4H9Zm3 4.5a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z"
            />
            <circle cx="12" cy="12.5" r="1.6" fill="currentColor" />
          </svg>
        </span>
      </span>
    </button>
  {/each}
</div>

<style>
  .pin-layer {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }

  .pin {
    --accent: #1d4ed8;
    --halo: rgba(255, 255, 255, 0.92);
    --ink: #0f172a;
    position: absolute;
    width: 0;
    height: 0;
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--accent);
    pointer-events: auto;
    cursor: pointer;
  }

  :global(.dark) .pin {
    --accent: #93c5fd;
    --halo: rgba(10, 15, 25, 0.85);
    --ink: #f8fafc;
  }

  .pin-visual {
    position: absolute;
    left: 0;
    top: 0;
    display: block;
    width: 0;
    height: 0;
    transform-origin: 0 0;
    pointer-events: none;
  }

  .cone-wrap {
    position: absolute;
    left: -55px;
    top: -55px;
    width: 110px;
    height: 110px;
    transform-origin: center;
    pointer-events: none;
    display: block;
    opacity: 0;
    transition: opacity 140ms ease;
  }

  .pin:hover .cone-wrap,
  .pin:focus-visible .cone-wrap {
    opacity: 1;
  }

  .cone {
    display: block;
    overflow: visible;
  }

  .glyph-wrap {
    position: absolute;
    left: -8px;
    top: -8px;
    width: 16px;
    height: 16px;
    display: block;
    pointer-events: auto;
    color: var(--ink);
    filter: drop-shadow(0 0 1.5px var(--halo)) drop-shadow(0 0 1.5px var(--halo));
    transition: transform 120ms ease, color 120ms ease;
    transform-origin: center;
  }

  .pin:hover .glyph-wrap,
  .pin:focus-visible .glyph-wrap {
    color: var(--accent);
    transform: scale(1.15);
  }

  .glyph {
    display: block;
    width: 100%;
    height: 100%;
  }

  .glyph-dark {
    display: none;
  }

  :global(.dark) .glyph-light {
    display: none;
  }

  :global(.dark) .glyph-dark {
    display: block;
  }

  .pin:focus-visible .glyph-wrap {
    outline: 2px solid var(--accent);
    outline-offset: 3px;
    border-radius: 3px;
  }
</style>
