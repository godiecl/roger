<script lang="ts">
  import { page } from '$app/stores';
</script>

<svelte:head>
  <title>{$page.status === 404 ? 'Página no encontrada' : 'Error'} — ROGER</title>
</svelte:head>

<div class="min-h-[80vh] flex items-center justify-center px-4">
  <div class="text-center max-w-lg">

    <!-- Número de error -->
    <div class="relative mb-6 select-none">
      <p class="text-[8rem] md:text-[10rem] font-black text-base-200 leading-none">
        {$page.status}
      </p>
      <div class="absolute inset-0 flex items-center justify-center">
        {#if $page.status === 404}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-base-content/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-base-content/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
        {/if}
      </div>
    </div>

    <!-- Mensaje -->
    <h1 class="text-2xl md:text-3xl font-bold text-base-content mb-3">
      {#if $page.status === 404}
        Página no encontrada
      {:else if $page.status === 403}
        Acceso denegado
      {:else}
        Algo salió mal
      {/if}
    </h1>

    <p class="text-base-content/60 text-sm leading-relaxed mb-8">
      {#if $page.status === 404}
        La dirección <code class="bg-base-200 px-1.5 py-0.5 rounded text-xs font-mono">{$page.url.pathname}</code>
        no existe en el archivo ROGER. Es posible que la URL esté mal escrita o que la página haya sido movida.
      {:else if $page.status === 403}
        No tienes permiso para acceder a esta sección. Si crees que es un error, inicia sesión o contacta al administrador.
      {:else}
        Ocurrió un error inesperado. El equipo ha sido notificado. Intenta recargar la página o vuelve al inicio.
      {/if}
    </p>

    <!-- Acciones -->
    <div class="flex gap-3 justify-center flex-wrap">
      <a href="/" class="btn btn-primary gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        Ir al inicio
      </a>
      <button class="btn btn-ghost gap-2" on:click={() => history.back()}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Volver atrás
      </button>
    </div>

    <!-- Links útiles -->
    <div class="mt-10 pt-8 border-t border-base-200">
      <p class="text-xs text-base-content/40 mb-3">Quizás buscabas alguna de estas secciones</p>
      <div class="flex flex-wrap gap-2 justify-center">
        {#each [
          { href: '/gallery', label: 'Colecciones' },
          { href: '/mapa', label: 'Mapa' },
          { href: '/investigacion', label: 'Investigación' },
          { href: '/sobre-roger', label: 'Acerca del Proyecto' },
          { href: '/contacto', label: 'Contacto' },
        ] as link}
          <a href={link.href} class="badge badge-outline hover:badge-primary transition-colors">
            {link.label}
          </a>
        {/each}
      </div>
    </div>

  </div>
</div>
