<script lang="ts">
  import Header from './Header.svelte';
  import Footer from './Footer.svelte';
  import SessionWarning from '$lib/components/common/SessionWarning.svelte';
  import DevPanel from '$lib/components/dev/DevPanel.svelte';
  import { page } from '$app/stores';

  $: isFullscreen = $page.url.pathname.includes('/viewer/');
  $: isMapPage = $page.url.pathname === '/mapa';
</script>

<div class="min-h-screen flex flex-col">
  {#if !isFullscreen}
    <Header />
  {/if}

  <main class="flex-1 min-h-0 w-full">
    <slot />
  </main>

  {#if !isFullscreen && !isMapPage}
    <Footer />
  {/if}

  <!-- Session expiration warning -->
  <SessionWarning />

  <!-- Developer panel (only in dev mode) -->
  <DevPanel />
</div>
