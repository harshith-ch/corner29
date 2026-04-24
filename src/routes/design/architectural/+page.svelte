<script lang="ts">
  import { listing, type FloorKey } from '$lib/content';
  import FloorSlider from '$lib/components/FloorSlider.svelte';
  import FloorPlanViewer from '$lib/components/FloorPlanViewer.svelte';
  import ContactForm from '$lib/components/ContactForm.svelte';
  import LocationMap from '$lib/components/LocationMap.svelte';
  import SectionNav from '$lib/components/SectionNav.svelte';
  import { prefetchSvgs } from '$lib/floor-prefetch';
  import { page } from '$app/state';
  import { browser } from '$app/environment';
  import { onMount } from 'svelte';

  onMount(() => prefetchSvgs(listing.floors.map((f) => f.svg)));

  let selected = $state<FloorKey>('G');
  const current = $derived(listing.floors.find((f) => f.key === selected) ?? listing.floors[3]);
  // Guard with `browser` — searchParams can't be read during prerender.
  const showContact = $derived(
    browser && ['1', 'true'].includes(page.url.searchParams.get('contact') ?? '')
  );
  const sections = $derived(
    [
      { id: 'overview', label: 'Overview' },
      { id: 'location', label: 'Location' },
      { id: 'floors', label: 'Plans' },
      ...(showContact ? [{ id: 'contact', label: 'Enquiry' }] : [])
    ]
  );
</script>

<svelte:head>
  <title>{listing.title} · Architectural</title>
</svelte:head>

<div class="variant">
  <SectionNav {sections} />

  <!-- Hero -->
  <section class="hero grid" id="overview">
    <div class="col-meta">
      <div class="ref">01 — Corner29</div>
      <div class="coords">17.4637° N · 78.3636° E</div>
    </div>
    <div class="col-main">
      <h1>
        <span class="mono">G + 4</span><br />Standalone<br />Office
      </h1>
    </div>
    <div class="col-side">
      <p class="lede">{listing.pitch}</p>
      <div class="stats">
        {#each listing.stats as s, i}
          <div class="stat">
            <span class="num mono">{String(i + 1).padStart(2, '0')}</span>
            <span class="v">{s.value}</span>
            <span class="l">{s.label}</span>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Location -->
  <section class="section grid" id="location">
    <div class="col-meta">
      <div class="ref mono">02 — Site</div>
    </div>
    <div class="col-span">
      <h2>Location</h2>
      <LocationMap
        embedSrc={listing.location.mapsEmbedSrc}
        directionsUrl={listing.location.directionsUrl}
        label={listing.location.label}
        address={listing.location.address}
        plusCode={listing.location.plusCode}
      />
    </div>
  </section>

  <!-- Floor plans -->
  <section class="section grid" id="floors">
    <div class="col-meta">
      <div class="ref mono">03 — Plans</div>
      <div class="floor-count">
        {listing.floors.length} levels
      </div>
    </div>
    <div class="col-span">
      <h2>Floor plans</h2>
      <div class="slider-row slider-mobile">
        <FloorSlider floors={listing.floors} {selected} onSelect={(k) => (selected = k)} />
      </div>
      <div class="plan-layout">
        <div class="slider-desktop">
          <FloorSlider
            floors={listing.floors}
            {selected}
            onSelect={(k) => (selected = k)}
            orientation="vertical"
          />
        </div>
        <div class="plan">
          <div class="plan-head">
            <span class="mono tiny">{current.key}</span>
            <span class="ttl">{current.title}</span>
            {#if current.summary}<span class="sum">— {current.summary}</span>{/if}
          </div>
          <div class="plan-body">
            <FloorPlanViewer src={current.svg} title={current.title} />
          </div>
        </div>
        {#if current.rooms?.length}
          <ul class="rooms">
            {#each current.rooms as r}
              <li>{r}</li>
            {/each}
          </ul>
        {/if}
      </div>
    </div>
  </section>

  <!-- Contact -->
  {#if showContact}
    <section class="section grid" id="contact">
      <div class="col-meta">
        <div class="ref mono">04 — Enquiry</div>
      </div>
      <div class="col-span contact-col">
        <h2>Visit the site</h2>
        <p class="sub">Leave your details. We respond within one business day.</p>
        <ContactForm variant="plain" />
      </div>
    </section>
  {/if}
</div>

<style>
  .variant {
    --accent: #0c0a09;
    --accent-ring: rgba(12, 10, 9, 0.15);
    --btn-bg: #0c0a09;
    --btn-fg: #fafaf9;
    --btn-bg-dark: #fafaf9;
    --btn-fg-dark: #0c0a09;
    --btn-radius: 0;
    --form-radius: 0;
    --input-radius: 0;
    --form-bg: transparent;
    --form-bg-dark: transparent;

    max-width: 1280px;
    margin: 0 auto;
    padding: 0 1.5rem;
  }

  .mono,
  .variant :global(.rooms),
  .variant :global(.hint) {
    font-family: var(--font-mono);
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 1.5rem;
  }

  .col-meta {
    grid-column: span 12;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding-top: 0.5rem;
  }

  @media (min-width: 900px) {
    .col-meta {
      grid-column: span 2;
    }
  }

  .col-main {
    grid-column: span 12;
  }

  @media (min-width: 900px) {
    .col-main {
      grid-column: span 6;
    }
  }

  .col-side {
    grid-column: span 12;
  }

  @media (min-width: 900px) {
    .col-side {
      grid-column: span 4;
    }
  }

  .col-span {
    grid-column: span 12;
  }

  @media (min-width: 900px) {
    .col-span {
      grid-column: span 10;
    }
  }

  .hero {
    padding: clamp(3rem, 8vw, 6rem) 0 4rem;
    align-items: start;
  }

  .hero,
  .section {
    scroll-margin-top: 7rem;
  }

  .variant :global(.section-nav) {
    margin: 0 -1.5rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.15);
  }

  :global(.dark) .variant :global(.section-nav) {
    border-bottom-color: rgba(255, 255, 255, 0.15);
  }

  .variant :global(.section-nav-inner) {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    max-width: 1280px;
  }

  .variant :global(.section-nav-link) {
    border-radius: 0;
    font-family: var(--font-mono);
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-size: 0.72rem;
  }

  .variant :global(.section-nav-link.active) {
    background: var(--btn-bg);
    color: var(--btn-fg);
  }

  :global(.dark) .variant :global(.section-nav-link.active) {
    background: var(--btn-bg-dark);
    color: var(--btn-fg-dark);
  }

  .ref {
    font: 500 0.75rem var(--font-mono);
    letter-spacing: 0.05em;
    opacity: 0.6;
  }

  .coords {
    font: 400 0.7rem var(--font-mono);
    opacity: 0.4;
  }

  .hero h1 {
    font: 700 clamp(3rem, 10vw, 6.5rem) / 0.95 var(--font-sans);
    letter-spacing: -0.03em;
    margin: 0;
  }

  .hero h1 .mono {
    font-weight: 400;
    letter-spacing: 0;
  }

  .lede {
    font: 400 0.95rem / 1.65 var(--font-sans);
    opacity: 0.8;
    margin: 0 0 2rem;
  }

  .stats {
    display: flex;
    flex-direction: column;
  }

  .stat {
    display: grid;
    grid-template-columns: 2.5rem 1fr auto;
    align-items: baseline;
    padding: 0.75rem 0;
    border-top: 1px solid rgba(0, 0, 0, 0.15);
    font: 500 0.9rem var(--font-sans);
  }

  :global(.dark) .stat {
    border-top-color: rgba(255, 255, 255, 0.18);
  }

  .stat:last-child {
    border-bottom: 1px solid rgba(0, 0, 0, 0.15);
  }

  :global(.dark) .stat:last-child {
    border-bottom-color: rgba(255, 255, 255, 0.18);
  }

  .stat .num {
    font-size: 0.7rem;
    opacity: 0.5;
  }

  .stat .v {
    font-weight: 600;
  }

  .stat .l {
    opacity: 0.6;
    font-size: 0.8rem;
  }

  .section {
    padding: 5rem 0;
    border-top: 1px solid rgba(0, 0, 0, 0.15);
  }

  :global(.dark) .section {
    border-top-color: rgba(255, 255, 255, 0.15);
  }

  .section h2 {
    font: 700 clamp(1.75rem, 4vw, 2.75rem) / 1.05 var(--font-sans);
    letter-spacing: -0.02em;
    margin: 0 0 2rem;
  }

  .floor-count {
    font: 400 0.7rem var(--font-mono);
    opacity: 0.5;
  }

  .slider-row {
    margin-bottom: 1.5rem;
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
      align-self: start;
    }
  }

  .plan-layout {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  @media (min-width: 900px) {
    .plan-layout {
      grid-template-columns: auto 1fr 14rem;
      align-items: start;
      gap: 1.25rem;
    }
  }

  .plan {
    border: 1px solid rgba(0, 0, 0, 0.2);
  }

  :global(.dark) .plan {
    border-color: rgba(255, 255, 255, 0.2);
  }

  .plan-head {
    padding: 0.75rem 1rem;
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.15);
    font: 500 0.875rem var(--font-sans);
  }

  :global(.dark) .plan-head {
    border-bottom-color: rgba(255, 255, 255, 0.15);
  }

  .plan-head .tiny {
    font-size: 0.75rem;
    letter-spacing: 0.08em;
  }

  .plan-head .ttl {
    font-weight: 600;
  }

  .plan-head .sum {
    opacity: 0.6;
    font-size: 0.8rem;
  }

  .plan-body {
    height: clamp(420px, 70vh, 720px);
  }

  .rooms {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0 1rem;
    font: 500 0.8rem var(--font-mono);
  }

  @media (min-width: 900px) {
    .rooms {
      grid-template-columns: 1fr;
    }
  }

  .rooms li {
    padding: 0.625rem 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  }

  :global(.dark) .rooms li {
    border-bottom-color: rgba(255, 255, 255, 0.12);
  }

  .contact-col .sub {
    font: 400 0.95rem var(--font-sans);
    opacity: 0.7;
    margin: -0.5rem 0 1.5rem;
  }
</style>
