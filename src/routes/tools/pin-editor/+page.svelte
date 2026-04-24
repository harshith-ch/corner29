<script lang="ts">
  import { listing, type Camera, type FloorKey } from '$lib/content';
  import FloorSlider from '$lib/components/FloorSlider.svelte';
  import FloorPlanViewer from '$lib/components/FloorPlanViewer.svelte';

  type DraftPin = Camera;

  let selected = $state<FloorKey>('G');
  const current = $derived(listing.floors.find((f) => f.key === selected) ?? listing.floors[3]);

  // Per-floor drafts seeded from content.ts so edits don't mutate the source.
  let byFloor = $state<Partial<Record<FloorKey, DraftPin[]>>>(
    Object.fromEntries(
      listing.floors.map((f) => [f.key, (f.cameras ?? []).map((c) => ({ ...c }))])
    ) as Partial<Record<FloorKey, DraftPin[]>>
  );

  const pins = $derived(byFloor[selected] ?? []);
  let selectedId = $state<string | null>(null);

  function nextId() {
    const prefix = selected.toLowerCase();
    let n = 1;
    const used = new Set((byFloor[selected] ?? []).map((p) => p.id));
    while (used.has(`${prefix}-cam-${n}`)) n++;
    return `${prefix}-cam-${n}`;
  }

  function onPlanClick(x: number, y: number) {
    const pin: DraftPin = {
      id: nextId(),
      x,
      y,
      heading: 0,
      fov: 60,
      image: ''
    };
    byFloor = { ...byFloor, [selected]: [...pins, pin] };
    selectedId = pin.id;
  }

  function update<K extends keyof Camera>(id: string, key: K, value: Camera[K]) {
    const next = pins.map((p) => (p.id === id ? { ...p, [key]: value } : p));
    byFloor = { ...byFloor, [selected]: next };
  }

  function remove(id: string) {
    byFloor = { ...byFloor, [selected]: pins.filter((p) => p.id !== id) };
    if (selectedId === id) selectedId = null;
  }

  function formatNumber(n: number) {
    return Math.abs(n) < 1e-3 ? '0' : n.toFixed(2);
  }

  function tsBlock() {
    if (!pins.length) return 'cameras: []';
    const lines = pins.map((p) => {
      const parts = [
        `      id: ${JSON.stringify(p.id)}`,
        `      x: ${formatNumber(p.x)}`,
        `      y: ${formatNumber(p.y)}`,
        `      heading: ${Math.round(p.heading)}`
      ];
      if (p.fov != null && p.fov !== 60) parts.push(`      fov: ${Math.round(p.fov)}`);
      parts.push(`      image: ${JSON.stringify(p.image)}`);
      if (p.title) parts.push(`      title: ${JSON.stringify(p.title)}`);
      if (p.caption) parts.push(`      caption: ${JSON.stringify(p.caption)}`);
      return `    {\n${parts.join(',\n')}\n    }`;
    });
    return `cameras: [\n${lines.join(',\n')}\n  ]`;
  }

  let copyState = $state<'idle' | 'copied' | 'error'>('idle');

  async function copyTs() {
    try {
      await navigator.clipboard.writeText(tsBlock());
      copyState = 'copied';
      setTimeout(() => (copyState = 'idle'), 1200);
    } catch {
      copyState = 'error';
      setTimeout(() => (copyState = 'idle'), 1800);
    }
  }

  // Heading handle drag: capture the pin's screen-space center at pointerdown,
  // then update heading from pointer position on every pointermove. We attach
  // the move/up listeners to window so the drag keeps tracking even if the
  // pointer leaves the small handle — the common UX for rotation handles.
  let drag = $state<{ id: string; cx: number; cy: number } | null>(null);

  function onHandleDown(e: PointerEvent, id: string) {
    e.stopPropagation();
    e.preventDefault();
    const btn = e.currentTarget as HTMLElement;
    const parent = btn.parentElement as HTMLElement | null;
    if (!parent) return;
    const r = parent.getBoundingClientRect();
    drag = { id, cx: r.left + r.width / 2, cy: r.top + r.height / 2 };
  }

  function onWindowMove(e: PointerEvent) {
    if (!drag) return;
    const dx = e.clientX - drag.cx;
    const dy = e.clientY - drag.cy;
    // 0° = screen-up; clockwise positive. Screen y grows downward so negate.
    const deg = (Math.atan2(dx, -dy) * 180) / Math.PI;
    update(drag.id, 'heading', ((deg % 360) + 360) % 360);
  }

  function onWindowUp() {
    drag = null;
  }

  function conePath(angle: number, radius: number) {
    const half = (angle / 2) * (Math.PI / 180);
    const x1 = -Math.sin(half) * radius;
    const y1 = -Math.cos(half) * radius;
    const x2 = Math.sin(half) * radius;
    const y2 = -Math.cos(half) * radius;
    const large = angle > 180 ? 1 : 0;
    return `M0 0 L${x1.toFixed(2)} ${y1.toFixed(2)} A${radius} ${radius} 0 ${large} 1 ${x2.toFixed(2)} ${y2.toFixed(2)} Z`;
  }

  function pct(value: number, origin: number, extent: number) {
    return ((value - origin) / extent) * 100;
  }
</script>

<svelte:head>
  <title>Pin editor · dev</title>
</svelte:head>

<svelte:window onpointermove={onWindowMove} onpointerup={onWindowUp} onpointercancel={onWindowUp} />

<div class="wrap">
  <header>
    <h1>Camera pin editor</h1>
    <p class="hint">
      Dev-only tool. Click the plan to drop a pin. Select a pin, then drag the blue handle to set its heading. Copy TS and paste into <code>src/lib/content.ts</code>.
    </p>
  </header>

  <div class="toolbar">
    <FloorSlider
      floors={listing.floors}
      {selected}
      onSelect={(k) => ((selected = k), (selectedId = null))}
    />
    <div class="spacer"></div>
    <button type="button" onclick={copyTs} class="copy">
      {copyState === 'copied'
        ? 'Copied'
        : copyState === 'error'
          ? 'Copy failed'
          : 'Copy TypeScript'}
    </button>
  </div>

  <div class="split">
    <div class="plan-col">
      <div class="plan-body">
        <FloorPlanViewer
          src={current.svg}
          title={current.title}
          editMode={true}
          onPlanClick={onPlanClick}
        >
          {#snippet overlay({ vbX, vbY, vbW, vbH, scale })}
            <div class="edit-layer">
              {#each pins as pin (pin.id)}
                {@const inv = scale > 0 ? 1 / scale : 1}
                {@const isSel = selectedId === pin.id}
                {@const fov = pin.fov ?? 60}
                <div
                  class="epin"
                  class:selected={isSel}
                  style="left: {pct(pin.x, vbX, vbW)}%; top: {pct(pin.y, vbY, vbH)}%;"
                >
                  <div class="epin-visual" style="transform: scale({inv});">
                    <svg
                      class="econe"
                      viewBox="-50 -50 100 100"
                      style="transform: translate(-50%, -50%) rotate({pin.heading}deg);"
                      aria-hidden="true"
                    >
                      <path
                        d={conePath(fov, 44)}
                        fill="currentColor"
                        fill-opacity="0.22"
                        stroke="currentColor"
                        stroke-opacity="0.65"
                        stroke-width="1.2"
                      />
                    </svg>
                    <button
                      type="button"
                      class="edot"
                      onclick={(e) => {
                        e.stopPropagation();
                        selectedId = pin.id;
                      }}
                      onpointerdown={(e) => e.stopPropagation()}
                      aria-label={`Select pin ${pin.id}`}
                    >{pin.id.split('-').pop()}</button>
                    {#if isSel}
                      <button
                        type="button"
                        class="ehandle"
                        style="transform: rotate({pin.heading}deg) translate(-50%, calc(-50% - 56px));"
                        onpointerdown={(e) => onHandleDown(e, pin.id)}
                        aria-label="Drag to set heading"
                      >↥</button>
                    {/if}
                  </div>
                </div>
              {/each}
            </div>
          {/snippet}
        </FloorPlanViewer>
      </div>
    </div>

    <aside class="side">
      <h2>Pins on {current.title}</h2>
      {#if pins.length === 0}
        <p class="empty">Click the plan to place the first camera.</p>
      {/if}
      <ul class="pin-list">
        {#each pins as pin (pin.id)}
          <li class:selected={selectedId === pin.id}>
            <button
              type="button"
              class="pin-row"
              onclick={() => (selectedId = pin.id)}
            >
              <span class="pin-id">{pin.id}</span>
              <span class="pin-coord">
                ({pin.x.toFixed(0)}, {pin.y.toFixed(0)}) · {Math.round(pin.heading)}°
              </span>
            </button>
            {#if selectedId === pin.id}
              <div class="fields">
                <label>
                  <span>id</span>
                  <input
                    type="text"
                    value={pin.id}
                    onchange={(e) =>
                      update(pin.id, 'id', (e.currentTarget as HTMLInputElement).value)}
                  />
                </label>
                <label>
                  <span>title</span>
                  <input
                    type="text"
                    value={pin.title ?? ''}
                    onchange={(e) =>
                      update(
                        pin.id,
                        'title',
                        (e.currentTarget as HTMLInputElement).value || undefined
                      )}
                  />
                </label>
                <label>
                  <span>caption</span>
                  <input
                    type="text"
                    value={pin.caption ?? ''}
                    onchange={(e) =>
                      update(
                        pin.id,
                        'caption',
                        (e.currentTarget as HTMLInputElement).value || undefined
                      )}
                  />
                </label>
                <label>
                  <span>image</span>
                  <input
                    type="text"
                    placeholder="/photos/ground/lobby-1.jpg"
                    value={pin.image}
                    onchange={(e) =>
                      update(pin.id, 'image', (e.currentTarget as HTMLInputElement).value)}
                  />
                </label>
                <label>
                  <span>heading</span>
                  <input
                    type="number"
                    min="0"
                    max="360"
                    step="1"
                    value={Math.round(pin.heading)}
                    onchange={(e) =>
                      update(
                        pin.id,
                        'heading',
                        Number((e.currentTarget as HTMLInputElement).value)
                      )}
                  />
                </label>
                <label>
                  <span>fov</span>
                  <input
                    type="number"
                    min="10"
                    max="180"
                    step="5"
                    value={Math.round(pin.fov ?? 60)}
                    onchange={(e) =>
                      update(
                        pin.id,
                        'fov',
                        Number((e.currentTarget as HTMLInputElement).value)
                      )}
                  />
                </label>
                <button type="button" class="danger" onclick={() => remove(pin.id)}>
                  Delete
                </button>
              </div>
            {/if}
          </li>
        {/each}
      </ul>

      <details open={pins.length > 0}>
        <summary>Preview output</summary>
        <pre>{tsBlock()}</pre>
      </details>
    </aside>
  </div>
</div>

<style>
  .wrap {
    max-width: 1400px;
    margin: 0 auto;
    padding: 1.25rem 1.25rem 4rem;
    font-family: var(--font-sans);
    color: inherit;
  }

  header h1 {
    font: 700 1.4rem var(--font-sans);
    margin: 0 0 0.25rem;
  }

  .hint {
    font: 400 0.85rem var(--font-sans);
    opacity: 0.7;
    margin: 0 0 1rem;
  }

  .hint code {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    background: rgba(0, 0, 0, 0.06);
    padding: 0.1rem 0.3rem;
    border-radius: 4px;
  }

  .toolbar {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    margin-bottom: 1rem;
  }

  .spacer {
    flex: 1;
  }

  .copy {
    padding: 0.5rem 0.9rem;
    font: 500 0.85rem var(--font-sans);
    border: 1px solid rgba(0, 0, 0, 0.2);
    background: #0c0a09;
    color: #fafaf9;
    cursor: pointer;
    border-radius: 4px;
  }

  .split {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  @media (min-width: 900px) {
    .split {
      grid-template-columns: 1fr 22rem;
    }
  }

  .plan-col {
    border: 1px solid rgba(0, 0, 0, 0.2);
    min-height: 520px;
  }

  :global(.dark) .plan-col {
    border-color: rgba(255, 255, 255, 0.2);
  }

  .plan-body {
    height: clamp(520px, 78vh, 820px);
  }

  .side {
    border: 1px solid rgba(0, 0, 0, 0.15);
    padding: 1rem;
    font-size: 0.9rem;
  }

  :global(.dark) .side {
    border-color: rgba(255, 255, 255, 0.15);
  }

  .side h2 {
    margin: 0 0 0.75rem;
    font-size: 1rem;
  }

  .empty {
    opacity: 0.6;
    font-size: 0.85rem;
  }

  .pin-list {
    list-style: none;
    padding: 0;
    margin: 0 0 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .pin-row {
    width: 100%;
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    padding: 0.5rem 0.6rem;
    background: rgba(0, 0, 0, 0.04);
    border: 1px solid transparent;
    border-radius: 4px;
    cursor: pointer;
    font: 500 0.8rem var(--font-mono);
    text-align: left;
    color: inherit;
  }

  .pin-list li.selected .pin-row {
    background: rgba(220, 38, 38, 0.12);
    border-color: rgba(220, 38, 38, 0.4);
  }

  .pin-id {
    font-weight: 600;
  }

  .pin-coord {
    opacity: 0.7;
    font-size: 0.72rem;
  }

  .fields {
    display: grid;
    gap: 0.4rem;
    padding: 0.6rem 0.5rem 0.75rem;
  }

  .fields label {
    display: grid;
    grid-template-columns: 5rem 1fr;
    gap: 0.5rem;
    align-items: center;
    font-size: 0.78rem;
  }

  .fields label > span {
    opacity: 0.65;
    font-family: var(--font-mono);
  }

  .fields input {
    padding: 0.3rem 0.4rem;
    font: 400 0.8rem var(--font-mono);
    border: 1px solid rgba(0, 0, 0, 0.25);
    background: transparent;
    color: inherit;
    border-radius: 3px;
  }

  :global(.dark) .fields input {
    border-color: rgba(255, 255, 255, 0.25);
  }

  .danger {
    justify-self: start;
    padding: 0.35rem 0.7rem;
    font: 500 0.78rem var(--font-sans);
    color: #b91c1c;
    background: transparent;
    border: 1px solid rgba(185, 28, 28, 0.5);
    border-radius: 4px;
    cursor: pointer;
  }

  details {
    margin-top: 0.5rem;
  }

  details summary {
    cursor: pointer;
    font-size: 0.8rem;
    opacity: 0.75;
    padding: 0.25rem 0;
  }

  pre {
    font: 400 0.72rem var(--font-mono);
    background: rgba(0, 0, 0, 0.05);
    padding: 0.6rem;
    border-radius: 4px;
    overflow: auto;
    max-height: 260px;
    margin: 0.4rem 0 0;
  }

  :global(.dark) pre {
    background: rgba(255, 255, 255, 0.06);
  }

  .edit-layer {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }

  .epin {
    position: absolute;
    color: #dc2626;
    pointer-events: none;
  }

  .epin.selected {
    color: #2563eb;
  }

  .epin-visual {
    position: absolute;
    left: 0;
    top: 0;
    transform-origin: 0 0;
    pointer-events: none;
  }

  .econe {
    position: absolute;
    left: 0;
    top: 0;
    width: 88px;
    height: 88px;
    pointer-events: none;
  }

  .edot {
    position: absolute;
    left: 0;
    top: 0;
    transform: translate(-50%, -50%);
    width: 26px;
    height: 26px;
    border-radius: 999px;
    background: currentColor;
    color: #fff;
    border: 2px solid rgba(255, 255, 255, 0.9);
    font: 600 0.7rem var(--font-mono);
    cursor: pointer;
    pointer-events: auto;
  }

  .ehandle {
    position: absolute;
    left: 0;
    top: 0;
    width: 22px;
    height: 22px;
    border-radius: 999px;
    background: #fff;
    color: #2563eb;
    border: 2px solid #2563eb;
    cursor: grab;
    font-size: 0.9rem;
    line-height: 1;
    pointer-events: auto;
  }

  .ehandle:active {
    cursor: grabbing;
  }
</style>
