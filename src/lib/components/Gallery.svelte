<script lang="ts">
  import type { GalleryImage } from '$lib/content';

  interface Props {
    images: GalleryImage[];
  }

  let { images }: Props = $props();

  let openIndex = $state<number | null>(null);
  let dialogEl: HTMLDivElement | undefined = $state();
  let closeBtn: HTMLButtonElement | undefined = $state();
  let previousFocus: HTMLElement | null = null;

  const current = $derived(openIndex !== null ? images[openIndex] : null);

  $effect(() => {
    if (openIndex === null) return;
    previousFocus = document.activeElement as HTMLElement | null;
    queueMicrotask(() => closeBtn?.focus());
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = prevOverflow;
      previousFocus?.focus?.();
      previousFocus = null;
    };
  });

  function close() {
    openIndex = null;
  }

  function next() {
    if (openIndex === null) return;
    openIndex = (openIndex + 1) % images.length;
  }

  function prev() {
    if (openIndex === null) return;
    openIndex = (openIndex - 1 + images.length) % images.length;
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      e.preventDefault();
      close();
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      next();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      prev();
    }
  }

  function onBackdrop(e: MouseEvent) {
    if (e.target === e.currentTarget) close();
  }
</script>

<svelte:window onkeydown={openIndex !== null ? onKey : undefined} />

<div class="grid">
  {#each images as img, i (img.src)}
    <button
      type="button"
      class="tile"
      onclick={() => (openIndex = i)}
      aria-label={`Open image: ${img.caption}`}
    >
      <img src={img.src} alt={img.caption} loading="lazy" decoding="async" />
      <span class="meta">
        <span class="cap">{img.caption}</span>
        <span class="floor">{img.floor}</span>
      </span>
    </button>
  {/each}
</div>

{#if current}
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    bind:this={dialogEl}
    class="backdrop"
    role="dialog"
    aria-modal="true"
    aria-label={current.caption}
    tabindex="-1"
    onclick={onBackdrop}
  >
    <div class="panel">
      <button
        type="button"
        class="icon-btn close"
        aria-label="Close"
        bind:this={closeBtn}
        onclick={close}
      >×</button>
      <button
        type="button"
        class="icon-btn nav prev"
        aria-label="Previous image"
        onclick={prev}
      >‹</button>
      <button
        type="button"
        class="icon-btn nav next"
        aria-label="Next image"
        onclick={next}
      >›</button>
      <figure>
        <img
          src={current.src}
          alt={current.caption}
          loading="eager"
          decoding="async"
        />
        <figcaption>
          <strong>{current.caption}</strong>
          <span>{current.floor} · {(openIndex ?? 0) + 1} / {images.length}</span>
        </figcaption>
      </figure>
    </div>
  </div>
{/if}

<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 0.625rem;
  }

  @media (min-width: 600px) {
    .grid {
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 0.875rem;
    }
  }

  .tile {
    position: relative;
    aspect-ratio: 4 / 3;
    padding: 0;
    margin: 0;
    border: 0;
    border-radius: var(--gallery-radius, 0.75rem);
    overflow: hidden;
    cursor: pointer;
    background: rgba(0, 0, 0, 0.05);
    display: block;
    color: inherit;
    transition: transform 200ms ease, box-shadow 200ms ease;
  }

  :global(.dark) .tile {
    background: rgba(255, 255, 255, 0.05);
  }

  .tile img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 320ms ease, filter 200ms ease;
  }

  .tile:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
  }

  .tile:hover img {
    transform: scale(1.04);
  }

  .tile:focus-visible {
    outline: 2px solid var(--accent, currentColor);
    outline-offset: 2px;
  }

  .meta {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 0.75rem 0.875rem 0.625rem;
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    background: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.7) 100%);
    color: #fff;
    text-align: left;
    pointer-events: none;
  }

  .cap {
    font: 600 0.85rem var(--font-sans);
    letter-spacing: -0.005em;
  }

  .floor {
    font: 500 0.7rem var(--font-sans);
    opacity: 0.85;
    letter-spacing: 0.02em;
  }

  .backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.88);
    z-index: 1000;
    display: grid;
    place-items: center;
    padding: 1.5rem;
    backdrop-filter: blur(4px);
  }

  .panel {
    position: relative;
    max-width: min(92vw, 1600px);
    max-height: calc(100vh - 3rem);
    display: flex;
    flex-direction: column;
  }

  .icon-btn {
    position: absolute;
    border: 0;
    background: rgba(255, 255, 255, 0.08);
    color: #fff;
    cursor: pointer;
    border-radius: 999px;
    display: grid;
    place-items: center;
    line-height: 1;
    font-family: var(--font-sans);
    transition: background 160ms ease, transform 160ms ease;
  }

  .icon-btn:hover {
    background: rgba(255, 255, 255, 0.18);
  }

  .icon-btn:focus-visible {
    outline: 2px solid #fff;
    outline-offset: 2px;
  }

  .close {
    top: -2.75rem;
    right: 0;
    width: 2.25rem;
    height: 2.25rem;
    font-size: 1.5rem;
  }

  .nav {
    top: 50%;
    transform: translateY(-50%);
    width: 2.75rem;
    height: 2.75rem;
    font-size: 2rem;
    font-weight: 300;
  }

  .nav:hover {
    transform: translateY(-50%) scale(1.08);
  }

  .prev {
    left: -3.5rem;
  }

  .next {
    right: -3.5rem;
  }

  @media (max-width: 900px) {
    .prev {
      left: 0.5rem;
    }
    .next {
      right: 0.5rem;
    }
  }

  figure {
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  figure img {
    display: block;
    max-width: 100%;
    max-height: calc(100vh - 7rem);
    object-fit: contain;
    background: #111;
    border-radius: 0.25rem;
  }

  figcaption {
    color: #fafaf9;
    font: 400 0.9rem var(--font-sans);
    display: flex;
    justify-content: space-between;
    gap: 0.75rem;
    align-items: baseline;
  }

  figcaption strong {
    font-weight: 600;
  }

  figcaption span {
    opacity: 0.7;
    font-size: 0.8rem;
  }
</style>
