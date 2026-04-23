<script lang="ts">
  interface Props {
    embedSrc: string;
    directionsUrl: string;
    label: string;
    address: string;
    plusCode: string;
  }

  let { embedSrc, directionsUrl, label, address, plusCode }: Props = $props();
</script>

<div class="wrap">
  <div class="map">
    <iframe
      src={embedSrc}
      title="Map showing {label}"
      loading="lazy"
      referrerpolicy="no-referrer-when-downgrade"
      allowfullscreen
    ></iframe>
  </div>
  <div class="meta">
    <div class="line label">{label}</div>
    <div class="line">{address}</div>
    <div class="line mono">Plus code · {plusCode}</div>
    <a href={directionsUrl} target="_blank" rel="noopener" class="btn">
      Get directions →
    </a>
  </div>
</div>

<style>
  .wrap {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }

  @media (min-width: 768px) {
    .wrap {
      grid-template-columns: 3fr 2fr;
      align-items: stretch;
    }
  }

  .map {
    aspect-ratio: 16 / 10;
    width: 100%;
    overflow: hidden;
    border-radius: var(--map-radius, 0.75rem);
    background: rgba(0, 0, 0, 0.05);
  }

  :global(.dark) .map {
    background: rgba(255, 255, 255, 0.06);
  }

  .map iframe {
    width: 100%;
    height: 100%;
    border: 0;
    display: block;
  }

  .meta {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
    justify-content: center;
  }

  .line {
    font: 400 0.95rem var(--font-sans);
    opacity: 0.9;
  }

  .line.label {
    font-size: 1.25rem;
    font-weight: 600;
    opacity: 1;
    margin-bottom: 0.25rem;
  }

  .line.mono {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    opacity: 0.6;
  }

  .btn {
    margin-top: 0.75rem;
    align-self: flex-start;
    padding: 0.625rem 1.125rem;
    border-radius: var(--btn-radius, 999px);
    background: var(--btn-bg, #0c0a09);
    color: var(--btn-fg, #fafaf9);
    font: 600 0.875rem var(--font-sans);
    text-decoration: none;
    transition: opacity 120ms ease, transform 120ms ease;
  }

  .btn:hover {
    opacity: 0.9;
    transform: translateY(-1px);
  }

  :global(.dark) .btn {
    background: var(--btn-bg-dark, #fafaf9);
    color: var(--btn-fg-dark, #0c0a09);
  }
</style>
