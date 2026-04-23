<script lang="ts">
  import { page } from '$app/state';

  interface VariantItem {
    slug: string;
    label: string;
    hint: string;
  }

  interface Props {
    variants: VariantItem[];
  }

  let { variants }: Props = $props();

  let open = $state(false);
  let menuEl: HTMLDivElement | undefined = $state();

  const current = $derived.by(() => {
    const m = page.url.pathname.match(/^\/design\/([^/]+)/);
    return variants.find((v) => v.slug === m?.[1]) ?? null;
  });

  function close() {
    open = false;
  }

  function onDocClick(e: MouseEvent) {
    if (!menuEl) return;
    if (!menuEl.contains(e.target as Node)) close();
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') close();
  }

  $effect(() => {
    if (open) {
      document.addEventListener('click', onDocClick);
      document.addEventListener('keydown', onKey);
      return () => {
        document.removeEventListener('click', onDocClick);
        document.removeEventListener('keydown', onKey);
      };
    }
  });
</script>

<div class="wrap" bind:this={menuEl}>
  <button
    type="button"
    class="trigger"
    onclick={() => (open = !open)}
    aria-haspopup="menu"
    aria-expanded={open}
    aria-label="Change design variant"
    title="Change design variant"
  >
    <span class="label">{current?.label ?? 'Design'}</span>
    <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true" class:flip={open}>
      <path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
  </button>

  {#if open}
    <div role="menu" class="menu">
      <div class="menu-title">Design variants</div>
      <a href="/" role="menuitem" class="item" class:active={!current} onclick={close}>
        <span class="item-label">Overview</span>
        <span class="item-hint">Pick a variant</span>
      </a>
      {#each variants as v (v.slug)}
        <a
          href="/design/{v.slug}"
          role="menuitem"
          class="item"
          class:active={current?.slug === v.slug}
          onclick={close}
        >
          <span class="item-label">{v.label}</span>
          <span class="item-hint">{v.hint}</span>
        </a>
      {/each}
    </div>
  {/if}
</div>

<style>
  .wrap {
    position: relative;
  }

  .trigger {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    height: 2.25rem;
    padding: 0 0.75rem;
    border-radius: 999px;
    border: 1px solid rgba(0, 0, 0, 0.12);
    background: transparent;
    color: inherit;
    font: 500 0.8rem var(--font-sans);
    cursor: pointer;
    transition: background 120ms ease;
  }

  .trigger:hover {
    background: rgba(0, 0, 0, 0.05);
  }

  :global(.dark) .trigger {
    border-color: rgba(255, 255, 255, 0.15);
  }

  :global(.dark) .trigger:hover {
    background: rgba(255, 255, 255, 0.08);
  }

  .label {
    opacity: 0.85;
  }

  svg {
    transition: transform 160ms ease;
    opacity: 0.6;
  }

  svg.flip {
    transform: rotate(180deg);
  }

  .menu {
    position: absolute;
    top: calc(100% + 0.5rem);
    right: 0;
    min-width: 15rem;
    padding: 0.375rem;
    border-radius: 0.75rem;
    background: var(--menu-bg, #ffffff);
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.06);
    z-index: 30;
  }

  :global(.dark) .menu {
    background: #171717;
    border-color: rgba(255, 255, 255, 0.1);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
  }

  .menu-title {
    padding: 0.5rem 0.75rem 0.25rem;
    font: 600 0.7rem var(--font-sans);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    opacity: 0.5;
  }

  .item {
    display: flex;
    flex-direction: column;
    padding: 0.5rem 0.75rem;
    border-radius: 0.5rem;
    text-decoration: none;
    color: inherit;
    transition: background 100ms ease;
  }

  .item:hover {
    background: rgba(0, 0, 0, 0.05);
  }

  :global(.dark) .item:hover {
    background: rgba(255, 255, 255, 0.08);
  }

  .item.active {
    background: rgba(0, 0, 0, 0.08);
  }

  :global(.dark) .item.active {
    background: rgba(255, 255, 255, 0.1);
  }

  .item-label {
    font: 600 0.875rem var(--font-sans);
  }

  .item-hint {
    font: 400 0.75rem var(--font-sans);
    opacity: 0.6;
    margin-top: 0.125rem;
  }
</style>
