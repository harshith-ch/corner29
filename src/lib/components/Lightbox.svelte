<script lang="ts">
  import type { Camera } from '$lib/content';

  interface Props {
    camera: Camera | null;
    onClose: () => void;
  }

  let { camera, onClose }: Props = $props();

  let dialogEl: HTMLDivElement | undefined = $state();
  let closeBtn: HTMLButtonElement | undefined = $state();
  let previousFocus: HTMLElement | null = null;

  $effect(() => {
    if (!camera) return;
    previousFocus = document.activeElement as HTMLElement | null;
    // Focus the close button after the dialog renders so Esc/Enter/Tab land in-dialog.
    queueMicrotask(() => closeBtn?.focus());

    // Lock body scroll while the dialog is open. Preserve the previous value
    // so we don't clobber a lock set elsewhere (e.g. a parent modal).
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = prevOverflow;
      previousFocus?.focus?.();
      previousFocus = null;
    };
  });

  // Keep Tab focus cycling inside the dialog. Standard modal pattern: on Tab,
  // if focus is on the last focusable element, wrap to the first (and vice
  // versa for Shift+Tab).
  const FOCUSABLE =
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

  function trapTab(e: KeyboardEvent) {
    if (!dialogEl) return;
    const focusables = Array.from(
      dialogEl.querySelectorAll<HTMLElement>(FOCUSABLE)
    ).filter((el) => !el.hasAttribute('hidden'));
    if (focusables.length === 0) {
      e.preventDefault();
      return;
    }
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    const active = document.activeElement as HTMLElement | null;
    if (e.shiftKey && (active === first || !dialogEl.contains(active))) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && active === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    } else if (e.key === 'Tab') {
      trapTab(e);
    }
  }

  function onBackdrop(e: MouseEvent) {
    if (e.target === e.currentTarget) onClose();
  }
</script>

<svelte:window onkeydown={camera ? onKey : undefined} />

{#if camera}
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    bind:this={dialogEl}
    class="backdrop"
    role="dialog"
    aria-modal="true"
    aria-label={camera.title ?? 'Camera view'}
    tabindex="-1"
    onclick={onBackdrop}
  >
    <div class="panel">
      <button
        type="button"
        class="close"
        aria-label="Close"
        bind:this={closeBtn}
        onclick={onClose}
      >×</button>
      <figure>
        <img
          src={camera.image}
          alt={camera.title ?? `Camera ${camera.id}`}
          loading="lazy"
          decoding="async"
        />
        {#if camera.title || camera.caption}
          <figcaption>
            {#if camera.title}<strong>{camera.title}</strong>{/if}
            {#if camera.caption}<span>{camera.caption}</span>{/if}
          </figcaption>
        {/if}
      </figure>
    </div>
  </div>
{/if}

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.82);
    z-index: 1000;
    display: grid;
    place-items: center;
    padding: 1.5rem;
    backdrop-filter: blur(4px);
  }

  .panel {
    position: relative;
    max-width: min(90vw, 1600px);
    max-height: calc(100vh - 3rem);
    display: flex;
    flex-direction: column;
  }

  .close {
    position: absolute;
    top: -2.25rem;
    right: 0;
    width: 2rem;
    height: 2rem;
    border: 0;
    background: transparent;
    color: #fff;
    font-size: 1.5rem;
    line-height: 1;
    cursor: pointer;
    border-radius: 999px;
  }

  .close:hover {
    background: rgba(255, 255, 255, 0.15);
  }

  .close:focus-visible {
    outline: 2px solid #fff;
    outline-offset: 2px;
  }

  figure {
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  img {
    display: block;
    max-width: 100%;
    max-height: calc(100vh - 7rem);
    object-fit: contain;
    background: #111;
  }

  figcaption {
    color: #fafaf9;
    font: 400 0.9rem var(--font-sans);
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  figcaption strong {
    font-weight: 600;
  }

  figcaption span {
    opacity: 0.8;
  }
</style>
