import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  server: {
    fs: {
      // Allow serving files from the main repo's node_modules when running
      // the dev server from a git worktree (which shares node_modules via
      // symlink but resolves to the parent real path, outside the default
      // allow list).
      allow: ['..', '../..', '../../..']
    }
  }
});
