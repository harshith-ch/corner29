<script lang="ts">
  import { listing, type FloorKey } from '$lib/content';
  import FloorSlider from '$lib/components/FloorSlider.svelte';
  import FloorPlanViewer from '$lib/components/FloorPlanViewer.svelte';
  import ContactForm from '$lib/components/ContactForm.svelte';
  import LocationMap from '$lib/components/LocationMap.svelte';
  import SectionNav from '$lib/components/SectionNav.svelte';
  import { page } from '$app/state';

  let selected = $state<FloorKey>('G');
  const current = $derived(listing.floors.find((f) => f.key === selected) ?? listing.floors[3]);
  const showContact = $derived(
    ['1', 'true'].includes(page.url.searchParams.get('contact') ?? '')
  );
  const sections = $derived(
    [
      { id: 'overview', label: 'Opening' },
      { id: 'location', label: 'Where' },
      { id: 'floors', label: 'Floor by floor' },
      ...(showContact ? [{ id: 'contact', label: 'To visit' }] : [])
    ]
  );
</script>

<svelte:head>
  <title>{listing.title} · Editorial</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
  <link
    href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,600;9..144,700&display=swap"
    rel="stylesheet"
  />
</svelte:head>

<div class="variant">
  <SectionNav {sections} />

  <!-- Hero -->
  <section class="hero" id="overview">
    <div class="kicker">
      <span>Corner29</span>
      <span>·</span>
      <span>Kondapur</span>
    </div>
    <h1 class="display">
      A corner building,<br />
      <em>quietly well-made.</em>
    </h1>
    <div class="dek">
      <p>{listing.pitch}</p>
    </div>

    <div class="pull-quote">
      <div class="pq-row">
        {#each listing.stats as s}
          <div class="pq-col">
            <div class="pq-v">{s.value}</div>
            <div class="pq-l">{s.label}</div>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Location -->
  <section class="section" id="location">
    <div class="section-head">
      <h2>Where</h2>
    </div>
    <p class="p">
      Anchored on Kondapur Main Road — a short walk from the metro corridor, flanked by Hi-Tec City
      and Gachibowli. You arrive by car, lift, or stair; the building is, in every sense, easy to
      reach.
    </p>
    <div class="map-wrap">
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
    <div class="section-head">
      <h2>Floor by floor</h2>
    </div>
    <p class="p">
      Eight levels: three of parking below, a ground-floor office with thirteen meeting rooms, and
      four upper floors — each a generous open plan punctuated by private cabins.
    </p>

    <div class="plan-spread">
      <aside class="plan-aside">
        <div class="floor-eyebrow">{current.key} — {current.title}</div>
        {#if current.summary}<div class="floor-summary">{current.summary}</div>{/if}
        {#if current.rooms?.length}
          <ul class="rooms">
            {#each current.rooms as r}
              <li>{r}</li>
            {/each}
          </ul>
        {/if}
      </aside>
      <div class="plan-main">
        <div class="slider-wrap slider-mobile">
          <FloorSlider floors={listing.floors} {selected} onSelect={(k) => (selected = k)} />
        </div>
        <div class="plan-layout">
          <div class="plan-frame">
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
      </div>
    </div>
  </section>

  <!-- Contact -->
  {#if showContact}
    <section class="section" id="contact">
      <div class="section-head">
        <h2>To visit</h2>
      </div>
      <p class="p">
        Leave a note — we'll respond within one working day and arrange a time for you to walk
        through in person.
      </p>
      <ContactForm />
    </section>
  {/if}
</div>

<style>
  .variant {
    --serif: 'Fraunces', var(--font-serif);
    --accent: #1a3a2e;
    --accent-ring: rgba(26, 58, 46, 0.18);
    --btn-bg: #1a3a2e;
    --btn-fg: #f5f1e8;
    --btn-bg-dark: #a8c5b5;
    --btn-fg-dark: #1a2e1a;
    --form-radius: 0.25rem;
    --input-radius: 0.25rem;
    --btn-radius: 0.25rem;
    --form-bg: #f5f1e8;
    --form-bg-dark: #1a2018;
    --form-border: rgba(26, 58, 46, 0.15);
    --form-border-dark: rgba(168, 197, 181, 0.2);
    --input-bg: #ffffff;
    --input-bg-dark: #0e1410;

    max-width: 920px;
    margin: 0 auto;
    padding: 0 1.5rem;
  }

  :global(html:not(.dark)) .variant {
    background: #faf7f0;
    color: #1a2018;
  }

  :global(.dark) .variant {
    background: #0e1410;
    color: #e8e3d6;
  }

  .hero {
    padding: clamp(3rem, 8vw, 6rem) 0 3rem;
    text-align: left;
  }

  .hero,
  .section {
    scroll-margin-top: 7rem;
  }

  .variant :global(.section-nav) {
    margin: 0 -1.5rem;
    border-bottom: 1px solid var(--form-border);
  }

  :global(.dark) .variant :global(.section-nav) {
    border-bottom-color: var(--form-border-dark);
  }

  .variant :global(.section-nav-inner) {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    max-width: 920px;
  }

  .variant :global(.section-nav-link) {
    font-family: var(--serif);
    font-weight: 400;
    font-size: 0.95rem;
    border-radius: 0.25rem;
  }

  .variant :global(.section-nav-link.active) {
    background: transparent;
    color: var(--accent);
    font-style: italic;
  }

  :global(.dark) .variant :global(.section-nav-link.active) {
    background: transparent;
    color: #a8c5b5;
  }

  .kicker {
    display: flex;
    gap: 0.625rem;
    font: 500 0.75rem var(--font-sans);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-bottom: 2rem;
    flex-wrap: wrap;
  }

  .display {
    font: 400 clamp(2.5rem, 8vw, 5rem) / 1 var(--serif);
    letter-spacing: -0.02em;
    margin: 0 0 2rem;
    font-optical-sizing: auto;
  }

  .display em {
    font-style: italic;
    color: var(--accent);
    font-weight: 300;
  }

  :global(.dark) .display em {
    color: #a8c5b5;
  }

  .dek {
    max-width: 32rem;
    margin: 0 0 3rem;
  }

  .dek p {
    font: 400 1.15rem / 1.7 var(--serif);
    opacity: 0.8;
    margin: 0;
  }

  .pull-quote {
    padding: 2rem 0;
    border-top: 1px solid var(--form-border);
    border-bottom: 1px solid var(--form-border);
  }

  :global(.dark) .pull-quote {
    border-color: var(--form-border-dark);
  }

  .pq-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem 1rem;
  }

  @media (min-width: 768px) {
    .pq-row {
      grid-template-columns: repeat(4, 1fr);
    }
  }

  .pq-v {
    font: 400 2rem / 1 var(--serif);
    letter-spacing: -0.02em;
    color: var(--accent);
  }

  :global(.dark) .pq-v {
    color: #a8c5b5;
  }

  .pq-l {
    font: 500 0.75rem var(--font-sans);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-top: 0.5rem;
  }

  .section {
    padding: 4rem 0;
  }

  .section-head {
    display: flex;
    align-items: baseline;
    gap: 1.25rem;
    margin-bottom: 1.5rem;
  }

  .number {
    font: 400 1rem var(--serif);
    font-style: italic;
    color: var(--accent);
    opacity: 0.7;
  }

  :global(.dark) .number {
    color: #a8c5b5;
  }

  .section h2 {
    font: 400 clamp(1.75rem, 4vw, 2.5rem) / 1.15 var(--serif);
    letter-spacing: -0.015em;
    margin: 0;
  }

  .p {
    font: 400 1.05rem / 1.75 var(--serif);
    opacity: 0.8;
    margin: 0 0 2rem;
    max-width: 38rem;
  }

  .map-wrap {
    border-top: 1px solid var(--form-border);
    padding-top: 1.5rem;
  }

  :global(.dark) .map-wrap {
    border-color: var(--form-border-dark);
  }

  .plan-spread {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  @media (min-width: 900px) {
    .plan-spread {
      grid-template-columns: 1fr 2.2fr;
      align-items: start;
    }
  }

  .plan-aside {
    padding: 1.25rem 0;
    border-top: 1px solid var(--form-border);
    border-bottom: 1px solid var(--form-border);
  }

  :global(.dark) .plan-aside {
    border-color: var(--form-border-dark);
  }

  .floor-eyebrow {
    font: 500 0.7rem var(--font-sans);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    opacity: 0.5;
    margin-bottom: 0.375rem;
  }

  .floor-summary {
    font: 400 1rem / 1.5 var(--serif);
    font-style: italic;
    opacity: 0.8;
    margin-bottom: 1rem;
  }

  .rooms {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .rooms li {
    font: 400 0.9rem / 1.6 var(--serif);
    opacity: 0.85;
    padding: 0.375rem 0;
    border-bottom: 1px dashed var(--form-border);
  }

  :global(.dark) .rooms li {
    border-color: var(--form-border-dark);
  }

  .slider-wrap {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 1rem;
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

  .plan-frame {
    height: clamp(400px, 65vh, 680px);
    border: 1px solid var(--form-border);
  }

  :global(.dark) .plan-frame {
    border-color: var(--form-border-dark);
  }
</style>
