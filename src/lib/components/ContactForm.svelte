<script lang="ts">
  interface Props {
    variant?: 'card' | 'plain';
  }

  let { variant = 'card' }: Props = $props();

  let name = $state('');
  let email = $state('');
  let phone = $state('');
  let visitDate = $state('');
  let message = $state('');
  let sending = $state(false);
  let status = $state<'idle' | 'ok' | 'error'>('idle');

  // Placeholder: simulates a submission client-side. Wire up Formspree / Web3Forms
  // (or a serverless function) later by replacing this with a real fetch().
  async function onSubmit(e: SubmitEvent) {
    e.preventDefault();
    sending = true;
    status = 'idle';
    const payload = { name, email, phone, visitDate, message };
    console.log('[contact]', payload);
    await new Promise((r) => setTimeout(r, 600));
    status = 'ok';
    name = '';
    email = '';
    phone = '';
    visitDate = '';
    message = '';
    sending = false;
  }
</script>

<form class="form" class:plain={variant === 'plain'} onsubmit={onSubmit}>
  <div class="row">
    <label>
      <span>Name</span>
      <input type="text" bind:value={name} required autocomplete="name" />
    </label>
    <label>
      <span>Email</span>
      <input type="email" bind:value={email} required autocomplete="email" />
    </label>
  </div>
  <div class="row">
    <label>
      <span>Phone</span>
      <input type="tel" bind:value={phone} autocomplete="tel" />
    </label>
    <label>
      <span>Preferred visit date</span>
      <input type="date" bind:value={visitDate} />
    </label>
  </div>
  <label>
    <span>Message</span>
    <textarea
      bind:value={message}
      rows="4"
      placeholder="Tell us about your team size, timelines, any questions…"
    ></textarea>
  </label>
  <div class="actions">
    <button type="submit" disabled={sending}>
      {sending ? 'Sending…' : 'Request a visit'}
    </button>
    {#if status === 'ok'}
      <span class="msg ok">Thanks — we'll be in touch shortly.</span>
    {:else if status === 'error'}
      <span class="msg err">Something went wrong. Try again or email us directly.</span>
    {/if}
  </div>
</form>

<style>
  .form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1.5rem;
    border-radius: var(--form-radius, 1rem);
    background: var(--form-bg, #ffffff);
    border: 1px solid var(--form-border, rgba(0, 0, 0, 0.08));
  }

  :global(.dark) .form {
    background: var(--form-bg-dark, #171717);
    border-color: var(--form-border-dark, rgba(255, 255, 255, 0.1));
  }

  .form.plain {
    padding: 0;
    background: transparent;
    border: none;
  }

  .row {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  @media (min-width: 640px) {
    .row {
      grid-template-columns: 1fr 1fr;
    }
  }

  label {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
    font: 500 0.8rem var(--font-sans);
  }

  label span {
    opacity: 0.7;
    letter-spacing: 0.01em;
  }

  input,
  textarea {
    width: 100%;
    padding: 0.625rem 0.75rem;
    border: 1px solid var(--input-border, rgba(0, 0, 0, 0.15));
    background: var(--input-bg, #fafaf9);
    color: inherit;
    border-radius: var(--input-radius, 0.5rem);
    font: 400 0.95rem var(--font-sans);
    transition: border-color 120ms ease, box-shadow 120ms ease;
  }

  :global(.dark) input,
  :global(.dark) textarea {
    background: var(--input-bg-dark, #0c0a09);
    border-color: var(--input-border-dark, rgba(255, 255, 255, 0.15));
  }

  input:focus,
  textarea:focus {
    outline: none;
    border-color: var(--accent, #0c0a09);
    box-shadow: 0 0 0 3px var(--accent-ring, rgba(12, 10, 9, 0.12));
  }

  textarea {
    resize: vertical;
    min-height: 5.5rem;
    font-family: var(--font-sans);
  }

  .actions {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  button[type='submit'] {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: var(--btn-radius, 999px);
    background: var(--btn-bg, #0c0a09);
    color: var(--btn-fg, #fafaf9);
    font: 600 0.9rem var(--font-sans);
    cursor: pointer;
    transition: opacity 120ms ease, transform 120ms ease;
  }

  :global(.dark) button[type='submit'] {
    background: var(--btn-bg-dark, #fafaf9);
    color: var(--btn-fg-dark, #0c0a09);
  }

  button[type='submit']:hover:not(:disabled) {
    transform: translateY(-1px);
  }

  button[type='submit']:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .msg {
    font: 500 0.85rem var(--font-sans);
  }

  .msg.ok {
    color: #059669;
  }

  .msg.err {
    color: #dc2626;
  }
</style>
