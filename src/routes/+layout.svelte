<script lang="ts">
  import '../app.css';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import VariantMenu from '$lib/components/VariantMenu.svelte';
  import { variants } from '$lib/variants';

  interface Props {
    children?: import('svelte').Snippet;
  }

  let { children }: Props = $props();
</script>

<header class="topbar">
  <a href="/" class="brand">Corner29</a>
  <div class="spacer"></div>
  <VariantMenu {variants} />
  <ThemeToggle />
</header>

{@render children?.()}

<footer class="footer">
  <div>Corner29 · G+4 Office for Lease · Kondapur</div>
</footer>

<style>
  :global(body) {
    margin: 0;
    font-family: var(--font-sans);
  }

  .topbar {
    position: sticky;
    top: 0;
    z-index: 20;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1.25rem;
    background: color-mix(in oklab, currentColor 2%, transparent);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  }

  :global(.dark) .topbar {
    border-bottom-color: rgba(255, 255, 255, 0.08);
  }

  .brand {
    font: 700 1.05rem var(--font-sans);
    letter-spacing: -0.01em;
    color: inherit;
    text-decoration: none;
  }

  .spacer {
    flex: 1;
  }

  .footer {
    padding: 2.5rem 1.5rem 3rem;
    text-align: center;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    margin-top: 4rem;
    font: 500 0.85rem var(--font-sans);
  }

  :global(.dark) .footer {
    border-top-color: rgba(255, 255, 255, 0.08);
  }

  .footer .muted {
    opacity: 0.5;
    margin-top: 0.25rem;
    font-weight: 400;
  }
</style>
