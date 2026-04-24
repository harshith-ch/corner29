<script lang="ts">
  import type { Floor, FloorKey } from '$lib/content';

  interface Props {
    floors: Floor[];
    selected: FloorKey;
    onSelect: (key: FloorKey) => void;
    orientation?: 'horizontal' | 'vertical';
  }

  let { floors, selected, onSelect, orientation = 'horizontal' }: Props = $props();

  function onKey(e: KeyboardEvent, index: number) {
    if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
      e.preventDefault();
      const next = floors[Math.min(index + 1, floors.length - 1)];
      onSelect(next.key);
      const btn = document.querySelector<HTMLButtonElement>(
        `[data-floor-key="${next.key}"]`
      );
      btn?.focus();
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
      e.preventDefault();
      const prev = floors[Math.max(index - 1, 0)];
      onSelect(prev.key);
      const btn = document.querySelector<HTMLButtonElement>(
        `[data-floor-key="${prev.key}"]`
      );
      btn?.focus();
    }
  }
</script>

<div
  class="slider"
  class:vertical={orientation === 'vertical'}
  role="tablist"
  aria-label="Select floor"
  aria-orientation={orientation}
>
  {#each floors as f, i (f.key)}
    <button
      type="button"
      role="tab"
      aria-selected={selected === f.key}
      tabindex={selected === f.key ? 0 : -1}
      data-floor-key={f.key}
      class="chip"
      class:is-selected={selected === f.key}
      onclick={() => onSelect(f.key)}
      onkeydown={(e) => onKey(e, i)}
      title={f.title}
    >
      {f.key}
    </button>
  {/each}
</div>

<style>
  .slider {
    display: flex;
    gap: 0.375rem;
    overflow-x: auto;
    padding: 0.375rem;
    border-radius: 999px;
    background: var(--slider-bg, rgba(0, 0, 0, 0.05));
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }

  .slider.vertical {
    flex-direction: column-reverse;
    overflow-x: visible;
    overflow-y: auto;
    scroll-snap-type: y mandatory;
    border-radius: 999px;
    width: fit-content;
  }

  .slider::-webkit-scrollbar {
    display: none;
  }

  :global(.dark) .slider {
    background: var(--slider-bg-dark, rgba(255, 255, 255, 0.06));
  }

  .chip {
    flex: 0 0 auto;
    min-width: 2.75rem;
    height: 2.5rem;
    padding: 0 0.875rem;
    border: none;
    background: transparent;
    font: 600 0.875rem var(--font-sans);
    color: inherit;
    cursor: pointer;
    border-radius: 999px;
    scroll-snap-align: center;
    transition: background 120ms ease, color 120ms ease, transform 120ms ease;
  }

  .chip:hover {
    background: rgba(0, 0, 0, 0.05);
  }

  :global(.dark) .chip:hover {
    background: rgba(255, 255, 255, 0.08);
  }

  .chip.is-selected {
    background: var(--slider-active-bg, #0c0a09);
    color: var(--slider-active-fg, #fafaf9);
    transform: scale(1.02);
  }

  :global(.dark) .chip.is-selected {
    background: var(--slider-active-bg-dark, #fafaf9);
    color: var(--slider-active-fg-dark, #0c0a09);
  }

  .chip:focus-visible {
    outline: 2px solid currentColor;
    outline-offset: 2px;
  }
</style>
