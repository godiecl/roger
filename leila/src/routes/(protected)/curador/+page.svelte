<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import { moderationService } from '$lib/services/moderationService';
  import { narrativeService } from '$lib/services/narrativeService';

  const REVIEWER_ROLES = ['curador', 'administrador', 'mesa_evaluadora'];

  let pendingContributions = 0;
  let pendingTags = 0;
  let pendingNarratives = 0;
  let loading = true;

  onMount(async () => {
    if (!$isAuthenticated) { goto('/login'); return; }
    const role = $authStore.user?.role ?? '';
    if (!REVIEWER_ROLES.includes(role)) { goto('/'); return; }

    try {
      const [stats, tagsRes, narrativesRes] = await Promise.all([
        moderationService.getStats(),
        moderationService.getPendingTags({ limit: 1 }),
        narrativeService.listNarratives(0, 1, false),
      ]);
      pendingContributions = stats.pending;
      pendingTags = tagsRes.total;
      pendingNarratives = narrativesRes.narratives.filter((n) => !n.is_approved).length > 0
        ? narrativesRes.total
        : 0;
    } catch {
      // counts are best-effort
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head><title>Curación · ROGER</title></svelte:head>

<div class="container mx-auto px-4 py-8 max-w-4xl">
  <h1 class="text-2xl font-bold mb-1">Panel de curación</h1>
  <p class="text-base-content/60 text-sm mb-8">Gestión de contenido y calidad del archivo</p>

  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">

    <!-- Moderación -->
    <a href="/curador/moderacion" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-warning/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          {#if !loading && (pendingContributions + pendingTags) > 0}
            <span class="badge badge-warning badge-sm">{pendingContributions + pendingTags} pendientes</span>
          {/if}
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Moderación</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">Revisión de contribuciones de usuarios y etiquetas sugeridas por IA.</p>
        <div class="mt-4 text-xs text-base-content/40 flex gap-3">
          {#if loading}
            <span class="loading loading-dots loading-xs"></span>
          {:else}
            <span>{pendingContributions} contribuciones</span>
            <span>{pendingTags} tags IA</span>
          {/if}
        </div>
      </div>
    </a>

    <!-- Metadatos -->
    <a href="/curador/metadatos" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-info/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Auditoría de metadatos</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">Vista completa de atributos taxonómicos 01–04 por fotografía.</p>
        <div class="mt-4 text-xs text-base-content/40">
          Técnicos · Cronología · Geográfico · Ambiental
        </div>
      </div>
    </a>

    <!-- Narrativas -->
    <a href="/curador/narrativas" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-success/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Narrativas IA</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">Revisar, aprobar y gestionar narrativas generadas por inteligencia artificial.</p>
        <div class="mt-4 text-xs text-base-content/40">
          VERAZ · VEROSÍMIL · confianza
        </div>
      </div>
    </a>

    <!-- Georeferencia -->
    <a href="/curador/georeferencia" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-primary/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Georeferencia</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">Validar, inferir y gestionar coordenadas geográficas de las fotografías.</p>
        <div class="mt-4 text-xs text-base-content/40">
          IA inferida · validación curador · mapa
        </div>
      </div>
    </a>

  </div>
</div>
