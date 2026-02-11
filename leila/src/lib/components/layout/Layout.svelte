<script lang="ts">
  import Header from './Header.svelte';
  import Footer from './Footer.svelte';
  import SessionWarning from '$lib/components/common/SessionWarning.svelte';
  import DevPanel from '$lib/components/dev/DevPanel.svelte';
  import { page } from '$app/stores';

  // Check if current page should hide header/footer
  $: isFullscreen = $page.url.pathname.includes('/viewer/');
</script>

<div class="min-h-screen flex flex-col">
  {#if !isFullscreen}
    <Header />
  {/if}

  <main class="flex-1 {isFullscreen ? '' : 'container mx-auto px-4 py-8'}">
    <slot />
  </main>

  {#if !isFullscreen}
    <Footer />
  {/if}

  <!-- Session expiration warning -->
  <SessionWarning />

  <!-- Developer panel (only in dev mode) -->
  <DevPanel />
</div>
