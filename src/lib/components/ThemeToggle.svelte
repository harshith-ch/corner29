<script lang="ts">
  import { onMount } from 'svelte';

  let dark = $state(false);

  onMount(() => {
    dark = document.documentElement.classList.contains('dark');
  });

  function toggle() {
    dark = !dark;
    const root = document.documentElement;
    if (dark) root.classList.add('dark');
    else root.classList.remove('dark');
    try {
      localStorage.setItem('theme', dark ? 'dark' : 'light');
    } catch {}
  }
</script>

<button
  type="button"
  class="toggle"
  onclick={toggle}
  aria-label="Toggle dark mode"
  aria-pressed={dark}
  title="Toggle theme"
>
  {#if dark}
    <!-- sun -->
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
    </svg>
  {:else}
    <!-- moon -->
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  {/if}
</button>

<style>
  .toggle {
    display: inline-grid;
    place-items: center;
    width: 2.25rem;
    height: 2.25rem;
    border-radius: 999px;
    border: 1px solid rgba(0, 0, 0, 0.12);
    background: transparent;
    color: inherit;
    cursor: pointer;
    transition: background 120ms ease, transform 120ms ease;
  }

  .toggle:hover {
    background: rgba(0, 0, 0, 0.05);
    transform: scale(1.05);
  }

  :global(.dark) .toggle {
    border-color: rgba(255, 255, 255, 0.15);
  }

  :global(.dark) .toggle:hover {
    background: rgba(255, 255, 255, 0.08);
  }
</style>
