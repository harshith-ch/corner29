<script lang="ts">
  import { onMount } from 'svelte';

  interface Section {
    id: string;
    label: string;
  }

  interface Props {
    sections: Section[];
  }

  let { sections }: Props = $props();

  let active = $state<string>(sections[0]?.id ?? '');
  let navEl: HTMLElement | undefined = $state();

  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]) active = (visible[0].target as HTMLElement).id;
      },
      { rootMargin: '-30% 0px -55% 0px', threshold: [0, 0.25, 0.5, 0.75, 1] }
    );

    const els = sections
      .map((s) => document.getElementById(s.id))
      .filter((el): el is HTMLElement => !!el);
    els.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  });

  function handleClick(e: MouseEvent, id: string) {
    e.preventDefault();
    const el = document.getElementById(id);
    if (!el) return;
    active = id;
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    history.replaceState(null, '', `#${id}`);
  }
</script>

<nav class="section-nav" aria-label="Sections" bind:this={navEl}>
  <div class="section-nav-inner">
    {#each sections as s (s.id)}
      <a
        href={`#${s.id}`}
        class="section-nav-link"
        class:active={active === s.id}
        onclick={(e) => handleClick(e, s.id)}
      >
        {s.label}
      </a>
    {/each}
  </div>
</nav>

<style>
  .section-nav {
    position: sticky;
    top: 3.5rem;
    z-index: 10;
    background: color-mix(in oklab, currentColor 3%, transparent);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  }

  :global(.dark) .section-nav {
    border-bottom-color: rgba(255, 255, 255, 0.08);
  }

  .section-nav-inner {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0.5rem 1.5rem;
    display: flex;
    gap: 0.25rem;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .section-nav-inner::-webkit-scrollbar {
    display: none;
  }

  .section-nav-link {
    flex: 0 0 auto;
    padding: 0.5rem 1rem;
    border-radius: 999px;
    color: inherit;
    text-decoration: none;
    font: 600 0.8rem var(--font-sans);
    opacity: 0.55;
    transition: opacity 120ms ease, background 120ms ease, color 120ms ease;
    white-space: nowrap;
  }

  .section-nav-link:hover {
    opacity: 1;
    background: rgba(0, 0, 0, 0.05);
  }

  :global(.dark) .section-nav-link:hover {
    background: rgba(255, 255, 255, 0.08);
  }

  .section-nav-link.active {
    opacity: 1;
    background: var(--section-nav-active-bg, rgba(0, 0, 0, 0.08));
    color: var(--section-nav-active-fg, inherit);
  }

  :global(.dark) .section-nav-link.active {
    background: var(--section-nav-active-bg-dark, rgba(255, 255, 255, 0.12));
    color: var(--section-nav-active-fg-dark, inherit);
  }
</style>
