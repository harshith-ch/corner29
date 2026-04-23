<script lang="ts">
  import { listing, type FloorKey } from '$lib/content';
  import FloorSlider from '$lib/components/FloorSlider.svelte';
  import FloorPlanViewer from '$lib/components/FloorPlanViewer.svelte';
  import ContactForm from '$lib/components/ContactForm.svelte';
  import LocationMap from '$lib/components/LocationMap.svelte';
  import SectionNav from '$lib/components/SectionNav.svelte';
  import { page } from '$app/state';
  import { browser } from '$app/environment';

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
      { id: 'floors', label: 'Floor plans' },
      ...(showContact ? [{ id: 'contact', label: 'Visit' }] : [])
    ]
  );
</script>

<svelte:head>
  <title>{listing.title} · Boutique</title>
</svelte:head>

<div class="variant">
  <SectionNav {sections} />

  <!-- Hero -->
  <section class="hero" id="overview">
    <div class="badge">Now leasing · Kondapur</div>
    <h1>A corner office<br />with <em>room to breathe</em>.</h1>
    <p class="lede">{listing.pitch}</p>
    <div class="cta-row">
      {#if showContact}
        <a href="#contact" class="cta primary">Request a visit</a>
      {/if}
      <a href="#floors" class="cta soft">Tour the floors</a>
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

  <!-- Location -->
  <section class="section" id="location">
    <h2>Where you'll be</h2>
    <p class="sub">Right on Kondapur Main Road — easy access from Hi-Tec City, Gachibowli, and the metro corridor.</p>
    <div class="location-card">
      <LocationMap
        embedSrc={listing.location.mapsEmbedSrc}
        directionsUrl={listing.location.directionsUrl}
        label={listing.location.label}
        address={listing.location.address}
        plusCode={listing.location.plusCode}
      />
    </div>
  </section>

  <!-- Floors -->
  <section class="section" id="floors">
    <h2>Walk the floors</h2>
    <p class="sub">Swipe through eight levels — three basement parking levels, a ground-floor office with 13 meeting rooms, and four floors above.</p>

    <div class="floor-card">
      <div class="floor-head">
        <div>
          <div class="floor-eyebrow">Currently viewing</div>
          <div class="floor-title">{current.title}</div>
        </div>
        {#if current.summary}
          <div class="floor-summary">{current.summary}</div>
        {/if}
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

  <!-- Contact -->
  {#if showContact}
    <section class="section" id="contact">
      <div class="contact-wrap">
        <div class="contact-copy">
          <h2>Come by for a tour</h2>
          <p>We'll walk you through every floor, answer your questions, and help you picture your team in the space.</p>
          <div class="perks">
            <div class="perk">☕ Rooftop cafeteria</div>
            <div class="perk">🚗 3 parking levels</div>
            <div class="perk">🪴 Plug & play ready</div>
          </div>
        </div>
        <ContactForm />
      </div>
    </section>
  {/if}
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

    max-width: 1100px;
    margin: 0 auto;
    padding: 0 1.5rem;
    background: var(--page-bg, transparent);
  }

  :global(html:not(.dark)) .variant {
    background: linear-gradient(180deg, #fff8ed 0%, #fafaf9 40%);
  }

  :global(.dark) .variant {
    background: linear-gradient(180deg, #1a1210 0%, #0c0a09 40%);
  }

  .hero {
    padding: clamp(3rem, 8vw, 5.5rem) 0 3rem;
  }

  .variant :global(.section-nav) {
    margin: 0 -1.5rem;
  }

  .variant :global(.section-nav-inner) {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .hero,
  .section {
    scroll-margin-top: 7rem;
  }

  .badge {
    display: inline-block;
    padding: 0.375rem 0.875rem;
    border-radius: 999px;
    background: rgba(194, 65, 12, 0.1);
    color: var(--accent);
    font: 600 0.75rem var(--font-sans);
    letter-spacing: 0.05em;
    margin-bottom: 1.5rem;
  }

  :global(.dark) .badge {
    background: rgba(234, 88, 12, 0.18);
    color: #fdba74;
  }

  .hero h1 {
    font: 600 clamp(2.5rem, 6vw, 4rem) / 1.05 var(--font-sans);
    letter-spacing: -0.025em;
    margin: 0 0 1.25rem;
    max-width: 20ch;
  }

  .hero h1 em {
    color: var(--accent);
    font-style: italic;
    font-weight: 500;
  }

  :global(.dark) .hero h1 em {
    color: #fb923c;
  }

  .lede {
    font: 400 1.1rem / 1.6 var(--font-sans);
    opacity: 0.75;
    margin: 0 0 2rem;
    max-width: 36rem;
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
    text-decoration: none;
    transition: transform 160ms ease, box-shadow 160ms ease;
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
    transition: transform 160ms ease;
  }

  :global(.dark) .stat-card {
    background: var(--form-bg-dark);
    border-color: var(--form-border-dark);
  }

  .stat-card:hover {
    transform: translateY(-2px);
  }

  .stat-card .v {
    font: 700 1.5rem / 1.1 var(--font-sans);
    letter-spacing: -0.02em;
    color: inherit;
  }

  .stat-card .l {
    font: 500 0.8rem var(--font-sans);
    opacity: 0.65;
    margin-top: 0.25rem;
  }

  .section {
    padding: 4rem 0;
  }

  .section h2 {
    font: 600 clamp(1.75rem, 3.5vw, 2.375rem) / 1.15 var(--font-sans);
    letter-spacing: -0.02em;
    margin: 0 0 0.5rem;
  }

  .sub {
    font: 400 1rem / 1.55 var(--font-sans);
    opacity: 0.7;
    margin: 0 0 2rem;
    max-width: 42rem;
  }

  .location-card {
    padding: 1.5rem;
    background: var(--form-bg);
    border: 1px solid var(--form-border);
    border-radius: 1.25rem;
  }

  :global(.dark) .location-card {
    background: var(--form-bg-dark);
    border-color: var(--form-border-dark);
  }

  .floor-card {
    padding: 1.5rem;
    background: var(--form-bg);
    border: 1px solid var(--form-border);
    border-radius: 1.5rem;
  }

  :global(.dark) .floor-card {
    background: var(--form-bg-dark);
    border-color: var(--form-border-dark);
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
    height: clamp(380px, 60vh, 640px);
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
    background: rgba(120, 53, 15, 0.06);
    color: inherit;
    border: 1px solid var(--form-border);
    border-radius: 999px;
    font: 500 0.8rem var(--font-sans);
    opacity: 0.85;
  }

  :global(.dark) .rooms .pill {
    background: rgba(234, 88, 12, 0.06);
    border-color: var(--form-border-dark);
  }

  .contact-wrap {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
    align-items: start;
  }

  @media (min-width: 900px) {
    .contact-wrap {
      grid-template-columns: 1fr 1.2fr;
    }
  }

  .contact-copy h2 {
    margin-bottom: 1rem;
  }

  .contact-copy p {
    font: 400 1rem / 1.6 var(--font-sans);
    opacity: 0.75;
    margin: 0 0 1.5rem;
  }

  .perks {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .perk {
    font: 500 0.9rem var(--font-sans);
    opacity: 0.85;
  }
</style>
