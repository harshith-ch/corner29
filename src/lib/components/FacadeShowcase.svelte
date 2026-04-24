<script lang="ts">
  import type { GalleryImage } from '$lib/content';

  interface Props {
    images: GalleryImage[];
    intervalMs?: number;
    eyebrow?: string;
  }

  let { images, intervalMs = 5000, eyebrow = 'The building' }: Props = $props();

  let idx = $state(0);
  let paused = $state(false);

  // $effect (not onMount) so the interval re-subscribes if intervalMs changes.
  $effect(() => {
    if (images.length <= 1) return;
    const ms = intervalMs;
    const id = setInterval(() => {
      if (!paused) idx = (idx + 1) % images.length;
    }, ms);
    return () => clearInterval(id);
  });
</script>

<div
  class="showcase"
  onmouseenter={() => (paused = true)}
  onmouseleave={() => (paused = false)}
  onfocusin={() => (paused = true)}
  onfocusout={() => (paused = false)}
  role="group"
  aria-label="Building showcase"
>
  <div class="stage">
    {#each images as img, i (img.src)}
      <img
        class="slide"
        class:active={i === idx}
        src={img.src}
        alt={img.caption}
        loading={i === 0 ? 'eager' : 'lazy'}
        decoding="async"
      />
    {/each}
    <div class="scrim"></div>
    <div class="overlay">
      <span class="eyebrow">{eyebrow}</span>
      <span class="caption">{images[idx]?.caption ?? ''}</span>
    </div>
  </div>
  {#if images.length > 1}
    <div class="dots" aria-label="Choose image">
      {#each images as _img, i (i)}
        <button
          type="button"
          class="dot"
          class:active={i === idx}
          aria-label={`Show image ${i + 1}`}
          aria-current={i === idx ? 'true' : undefined}
          onclick={() => (idx = i)}
        ></button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .showcase {
    position: relative;
    border-radius: var(--facade-radius, 1.25rem);
    overflow: hidden;
    background: rgba(0, 0, 0, 0.04);
    box-shadow: 0 20px 60px -30px rgba(0, 0, 0, 0.45);
  }

  :global(.dark) .showcase {
    background: rgba(255, 255, 255, 0.04);
    box-shadow: 0 20px 60px -30px rgba(0, 0, 0, 0.8);
  }

  .stage {
    position: relative;
    aspect-ratio: 16 / 9;
    width: 100%;
    overflow: hidden;
  }

  @media (max-width: 600px) {
    .stage {
      aspect-ratio: 4 / 3;
    }
  }

  .slide {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0;
    transform: scale(1.04);
    transition: opacity 900ms ease, transform 6000ms ease;
    will-change: opacity, transform;
  }

  .slide.active {
    opacity: 1;
    transform: scale(1);
  }

  .scrim {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      180deg,
      rgba(0, 0, 0, 0) 40%,
      rgba(0, 0, 0, 0.55) 100%
    );
    pointer-events: none;
  }

  .overlay {
    position: absolute;
    left: 1.25rem;
    right: 1.25rem;
    bottom: 1.125rem;
    color: #fff;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    pointer-events: none;
  }

  .eyebrow {
    font: 600 0.7rem var(--font-sans);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    opacity: 0.85;
  }

  .caption {
    font: 600 1.05rem var(--font-sans);
    letter-spacing: -0.01em;
  }

  .dots {
    position: absolute;
    right: 1rem;
    top: 1rem;
    display: flex;
    gap: 0.375rem;
    padding: 0.375rem 0.5rem;
    background: rgba(0, 0, 0, 0.35);
    border-radius: 999px;
    backdrop-filter: blur(6px);
  }

  .dot {
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 999px;
    border: 0;
    padding: 0;
    background: rgba(255, 255, 255, 0.45);
    cursor: pointer;
    transition: background 160ms ease, transform 160ms ease;
  }

  .dot:hover {
    background: rgba(255, 255, 255, 0.75);
  }

  .dot.active {
    background: #fff;
    transform: scale(1.15);
  }

  .dot:focus-visible {
    outline: 2px solid #fff;
    outline-offset: 2px;
  }

  @media (prefers-reduced-motion: reduce) {
    .slide,
    .slide.active {
      transform: none;
      transition: opacity 150ms linear;
    }
  }
</style>
