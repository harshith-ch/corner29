<script lang="ts">
  import { listing, type FloorKey } from '$lib/content';
  import FloorSlider from '$lib/components/FloorSlider.svelte';
  import FloorPlanViewer from '$lib/components/FloorPlanViewer.svelte';
  import ContactForm from '$lib/components/ContactForm.svelte';
  import LocationMap from '$lib/components/LocationMap.svelte';
  import { page } from '$app/state';

  type Tab = 'overview' | 'location' | 'floors' | 'contact';

  const allTabs: { id: Tab; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'location', label: 'Location' },
    { id: 'floors', label: 'Floor plans' },
    { id: 'contact', label: 'Visit' }
  ];

  let active = $state<Tab>('overview');
  let selected = $state<FloorKey>('G');
  const current = $derived(listing.floors.find((f) => f.key === selected) ?? listing.floors[3]);
  const showContact = $derived(
    ['1', 'true'].includes(page.url.searchParams.get('contact') ?? '')
  );
  const tabs = $derived(allTabs.filter((t) => showContact || t.id !== 'contact'));
</script>

<svelte:head>
  <title>{listing.title} · Boutique (top-bar)</title>
</svelte:head>

<div class="variant">
  <nav class="section-nav" aria-label="Sections">
    <div class="nav-inner">
      {#each tabs as t}
        <button
          type="button"
          class="tab"
          class:active={active === t.id}
          onclick={() => (active = t.id)}
        >
          {t.label}
        </button>
      {/each}
    </div>
  </nav>

  <main class="content">
    {#if active === 'overview'}
      <section class="pane">
        <div class="badge">Now leasing · Kondapur</div>
        <h1>A corner office<br />with <em>room to breathe</em>.</h1>
        <p class="lede">{listing.pitch}</p>
        <div class="cta-row">
          {#if showContact}
            <button class="cta primary" onclick={() => (active = 'contact')}>Request a visit</button>
          {/if}
          <button class="cta soft" onclick={() => (active = 'floors')}>Tour the floors</button>
        </div>
        <div class="stat-cards">
          {#each listing.stats as s}
            <div class="stat-card">
              <div class="v">{s.value}</div>
              <div class="l">{s.label}</div>
            </div>
          {/each}
        </div>
      </section>
    {:else if active === 'location'}
      <section class="pane">
        <h2>Where you'll be</h2>
        <p class="sub">
          Right on Kondapur Main Road — easy access from Hi-Tec City, Gachibowli, and the metro
          corridor.
        </p>
        <div class="card">
          <LocationMap
            embedSrc={listing.location.mapsEmbedSrc}
            directionsUrl={listing.location.directionsUrl}
            label={listing.location.label}
            address={listing.location.address}
            plusCode={listing.location.plusCode}
          />
        </div>
      </section>
    {:else if active === 'floors'}
      <section class="pane">
        <h2>Walk the floors</h2>
        <p class="sub">
          Three basement parking levels, a ground-floor office with 13 meeting rooms, and four
          floors above.
        </p>
        <div class="card floor-card">
          <div class="floor-head">
            <div>
              <div class="floor-eyebrow">Currently viewing</div>
              <div class="floor-title">{current.title}</div>
            </div>
            {#if current.summary}<div class="floor-summary">{current.summary}</div>{/if}
          </div>
          <div class="slider-wrap slider-mobile">
            <FloorSlider floors={listing.floors} {selected} onSelect={(k) => (selected = k)} />
          </div>
          <div class="plan-layout">
            <div class="plan-body">
              <FloorPlanViewer src={current.svg} title={current.title} />
            </div>
            <div class="slider-desktop">
              <FloorSlider
                floors={listing.floors}
                {selected}
                onSelect={(k) => (selected = k)}
                orientation="vertical"
              />
            </div>
          </div>
          {#if current.rooms?.length}
            <div class="rooms">
              {#each current.rooms as r}
                <span class="pill">{r}</span>
              {/each}
            </div>
          {/if}
        </div>
      </section>
    {:else if active === 'contact'}
      <section class="pane">
        <h2>Come by for a tour</h2>
        <p class="sub">
          We'll walk you through every floor, answer your questions, and help you picture your team
          in the space.
        </p>
        <ContactForm />
      </section>
    {/if}
  </main>
</div>

<style>
  .variant {
    --accent: #c2410c;
    --accent-ring: rgba(194, 65, 12, 0.18);
    --btn-bg: #c2410c;
    --btn-fg: #fff7ed;
    --btn-bg-dark: #ea580c;
    --btn-fg-dark: #fff7ed;
    --btn-radius: 999px;
    --form-radius: 1.25rem;
    --form-bg: #fffbf5;
    --form-bg-dark: #1f1612;
    --form-border: rgba(194, 65, 12, 0.12);
    --form-border-dark: rgba(234, 88, 12, 0.2);
    --input-bg: #ffffff;
    --input-bg-dark: #2a1d17;
    --input-radius: 0.75rem;
  }

  :global(html:not(.dark)) .variant {
    background: linear-gradient(180deg, #fff8ed 0%, #fafaf9 30%);
  }

  :global(.dark) .variant {
    background: linear-gradient(180deg, #1a1210 0%, #0c0a09 30%);
  }

  .section-nav {
    position: sticky;
    top: 3.5rem;
    z-index: 10;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    background: color-mix(in oklab, currentColor 3%, transparent);
    border-bottom: 1px solid var(--form-border);
  }

  :global(.dark) .section-nav {
    border-bottom-color: var(--form-border-dark);
  }

  .nav-inner {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0.5rem 1.5rem;
    display: flex;
    gap: 0.25rem;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .nav-inner::-webkit-scrollbar {
    display: none;
  }

  .tab {
    flex: 0 0 auto;
    padding: 0.625rem 1.125rem;
    border: none;
    background: transparent;
    color: inherit;
    font: 600 0.875rem var(--font-sans);
    cursor: pointer;
    border-radius: 999px;
    opacity: 0.6;
    transition: opacity 120ms ease, background 120ms ease;
  }

  .tab:hover {
    opacity: 1;
    background: rgba(194, 65, 12, 0.08);
  }

  :global(.dark) .tab:hover {
    background: rgba(234, 88, 12, 0.15);
  }

  .tab.active {
    opacity: 1;
    background: var(--accent);
    color: var(--btn-fg);
  }

  :global(.dark) .tab.active {
    background: var(--btn-bg-dark);
  }

  .content {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2.5rem 1.5rem 4rem;
  }

  .pane {
    animation: fadeIn 220ms ease;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(4px);
    }
    to {
      opacity: 1;
      transform: none;
    }
  }

  .badge {
    display: inline-block;
    padding: 0.375rem 0.875rem;
    border-radius: 999px;
    background: rgba(194, 65, 12, 0.1);
    color: var(--accent);
    font: 600 0.75rem var(--font-sans);
    letter-spacing: 0.05em;
    margin-bottom: 1.25rem;
  }

  :global(.dark) .badge {
    background: rgba(234, 88, 12, 0.18);
    color: #fdba74;
  }

  h1 {
    font: 600 clamp(2.25rem, 5.5vw, 3.75rem) / 1.05 var(--font-sans);
    letter-spacing: -0.025em;
    margin: 0 0 1.25rem;
    max-width: 20ch;
  }

  h1 em {
    color: var(--accent);
    font-style: italic;
    font-weight: 500;
  }

  :global(.dark) h1 em {
    color: #fb923c;
  }

  h2 {
    font: 600 clamp(1.75rem, 3.5vw, 2.25rem) / 1.15 var(--font-sans);
    letter-spacing: -0.02em;
    margin: 0 0 0.5rem;
  }

  .lede {
    font: 400 1.1rem / 1.6 var(--font-sans);
    opacity: 0.75;
    margin: 0 0 2rem;
    max-width: 36rem;
  }

  .sub {
    font: 400 1rem / 1.55 var(--font-sans);
    opacity: 0.7;
    margin: 0 0 1.75rem;
    max-width: 42rem;
  }

  .cta-row {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 2.5rem;
  }

  .cta {
    padding: 0.875rem 1.5rem;
    border-radius: 999px;
    font: 600 0.9rem var(--font-sans);
    border: none;
    cursor: pointer;
    transition: transform 160ms ease;
  }

  .cta.primary {
    background: var(--btn-bg);
    color: var(--btn-fg);
    box-shadow: 0 6px 20px rgba(194, 65, 12, 0.25);
  }

  :global(.dark) .cta.primary {
    background: var(--btn-bg-dark);
    box-shadow: 0 6px 20px rgba(234, 88, 12, 0.35);
  }

  .cta.soft {
    background: rgba(194, 65, 12, 0.08);
    color: var(--accent);
  }

  :global(.dark) .cta.soft {
    background: rgba(234, 88, 12, 0.15);
    color: #fb923c;
  }

  .cta:hover {
    transform: translateY(-2px);
  }

  .stat-cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.875rem;
  }

  @media (min-width: 768px) {
    .stat-cards {
      grid-template-columns: repeat(4, 1fr);
    }
  }

  .stat-card {
    padding: 1.25rem;
    background: var(--form-bg);
    border: 1px solid var(--form-border);
    border-radius: 1rem;
  }

  :global(.dark) .stat-card {
    background: var(--form-bg-dark);
    border-color: var(--form-border-dark);
  }

  .stat-card .v {
    font: 700 1.5rem / 1.1 var(--font-sans);
    letter-spacing: -0.02em;
    color: var(--accent);
  }

  :global(.dark) .stat-card .v {
    color: #fb923c;
  }

  .stat-card .l {
    font: 500 0.8rem var(--font-sans);
    opacity: 0.65;
    margin-top: 0.25rem;
  }

  .card {
    padding: 1.5rem;
    background: var(--form-bg);
    border: 1px solid var(--form-border);
    border-radius: 1.25rem;
  }

  :global(.dark) .card {
    background: var(--form-bg-dark);
    border-color: var(--form-border-dark);
  }

  .floor-card {
    border-radius: 1.5rem;
  }

  .floor-head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }

  .floor-eyebrow {
    font: 600 0.7rem var(--font-sans);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.5;
  }

  .floor-title {
    font: 600 1.375rem var(--font-sans);
    letter-spacing: -0.01em;
  }

  .floor-summary {
    font: 500 0.875rem var(--font-sans);
    opacity: 0.7;
    text-align: right;
  }

  .slider-wrap {
    margin-bottom: 1rem;
    display: flex;
    justify-content: center;
  }

  .slider-desktop {
    display: none;
  }

  @media (min-width: 900px) {
    .slider-mobile {
      display: none;
    }
    .slider-desktop {
      display: flex;
      align-self: center;
    }
  }

  .plan-layout {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  @media (min-width: 900px) {
    .plan-layout {
      grid-template-columns: 1fr auto;
      align-items: stretch;
    }
  }

  .plan-body {
    height: clamp(400px, 65vh, 680px);
    border-radius: 1rem;
    overflow: hidden;
  }

  .rooms {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1.25rem;
  }

  .rooms .pill {
    padding: 0.375rem 0.875rem;
    background: rgba(194, 65, 12, 0.08);
    color: var(--accent);
    border-radius: 999px;
    font: 500 0.8rem var(--font-sans);
  }

  :global(.dark) .rooms .pill {
    background: rgba(234, 88, 12, 0.15);
    color: #fb923c;
  }
</style>
