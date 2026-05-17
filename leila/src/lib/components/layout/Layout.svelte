<script lang="ts">
  import Header from './Header.svelte';
  import Footer from './Footer.svelte';
  import SessionWarning from '$lib/components/common/SessionWarning.svelte';
  import DevPanel from '$lib/components/dev/DevPanel.svelte';
  import { page } from '$app/stores';

  $: isFullscreen = $page.url.pathname.includes('/viewer/');
  $: isMapPage = $page.url.pathname === '/mapa';
</script>

<a
  href="#main-content"
  class="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[9999] focus:rounded-md focus:bg-white focus:px-4 focus:py-2 focus:text-black focus:shadow-lg focus:outline-2 focus:outline-primary"
>
  Saltar al contenido principal
</a>

<div class="min-h-screen flex flex-col">
  {#if !isFullscreen}
    <Header />
  {/if}

  <main id="main-content" tabindex="-1" class="flex-1 min-h-0 w-full">
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
