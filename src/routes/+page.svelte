<script lang="ts">
  import { listing } from '$lib/content';
  import { variants } from '$lib/variants';

  const palettes: Record<string, string[]> = {
    architectural: ['#0c0a09', '#f5f5f4', '#a8a29e'],
    boutique: ['#fef3c7', '#c2410c', '#7c2d12'],
    editorial: ['#1a3a2e', '#f5f1e8', '#8a9b7a']
  };
</script>

<svelte:head>
  <title>Corner29 — Design variants</title>
</svelte:head>

<main class="wrap">
  <section class="hero">
    <h1>Corner29</h1>
    <p class="sub">{listing.pitch}</p>
    <p class="meta">
      Three styles, with a top-bar (tabbed) alternative for two of them. Pick the combination that
      feels right.
    </p>
  </section>

  <section class="grid">
    {#each variants as v (v.slug)}
      <a href="/design/{v.slug}" class="card">
        <div class="swatches" aria-hidden="true">
          {#each palettes[v.style] as c}
            <span class="swatch" style="background: {c}"></span>
          {/each}
        </div>
        <div class="body">
          <div class="tag">{v.layout === 'tabs' ? 'Top-bar layout' : 'Single page layout'}</div>
          <h2>{v.label}</h2>
          <p>{v.hint}</p>
          <span class="link">Open preview →</span>
        </div>
      </a>
    {/each}
  </section>
</main>

<style>
  .wrap {
    max-width: 1100px;
    margin: 0 auto;
    padding: 3rem 1.5rem;
  }

  .hero {
    margin-bottom: 3rem;
    max-width: 38rem;
  }

  .hero h1 {
    font: 700 clamp(2.25rem, 6vw, 3.5rem) / 1 var(--font-sans);
    letter-spacing: -0.02em;
    margin: 0 0 1rem;
  }

  .hero .sub {
    font: 400 1.125rem / 1.55 var(--font-sans);
    opacity: 0.8;
    margin: 0 0 0.75rem;
  }

  .hero .meta {
    font: 500 0.9rem / 1.4 var(--font-sans);
    opacity: 0.55;
    margin: 0;
  }

  .grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }

  @media (min-width: 640px) {
    .grid {
      grid-template-columns: 1fr 1fr;
    }
  }

  @media (min-width: 960px) {
    .grid {
      grid-template-columns: 1fr 1fr 1fr;
    }
  }

  .card {
    display: block;
    text-decoration: none;
    color: inherit;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 1rem;
    overflow: hidden;
    background: color-mix(in oklab, currentColor 2%, transparent);
    transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
  }

  .card:hover {
    transform: translateY(-3px);
    border-color: rgba(0, 0, 0, 0.2);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.07);
  }

  :global(.dark) .card {
    border-color: rgba(255, 255, 255, 0.1);
  }

  :global(.dark) .card:hover {
    border-color: rgba(255, 255, 255, 0.3);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
  }

  .swatches {
    display: flex;
    height: 5rem;
  }

  .swatch {
    flex: 1;
  }

  .body {
    padding: 1.125rem 1.375rem 1.375rem;
  }

  .tag {
    font: 500 0.7rem var(--font-sans);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.55;
    margin-bottom: 0.5rem;
  }

  .body h2 {
    font: 700 1.25rem / 1.2 var(--font-sans);
    margin: 0 0 0.25rem;
    letter-spacing: -0.01em;
  }

  .body p {
    font: 400 0.85rem / 1.5 var(--font-sans);
    opacity: 0.65;
    margin: 0 0 1rem;
  }

  .link {
    font: 600 0.8rem var(--font-sans);
    opacity: 0.8;
  }
</style>
