<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import { notificationsStore } from '$lib/stores/notifications';
  import { clusterService, type ClusteringJob } from '$lib/services/clusterService';
  import {
    timelineService,
    type CollectionNarrative,
    type CollectionClusterSummary,
  } from '$lib/services/timelineService';

  const ALLOWED_ROLES = ['curador', 'administrador', 'investigador'];

  let jobs: ClusteringJob[] = [];
  let selectedJobId: number | null = null;
  let narrative: CollectionNarrative | null = null;

  let loadingJobs = true;
  let generating = false;
  let jobsError: string | null = null;
  let narrativeError: string | null = null;

  $: selectedJob = jobs.find((j) => j.id === selectedJobId) ?? null;

  onMount(async () => {
    if (!$isAuthenticated) { goto('/login'); return; }
    const role = $authStore.user?.role ?? '';
    if (!ALLOWED_ROLES.includes(role)) { goto('/curador'); return; }
    await loadJobs();
  });

  async function loadJobs() {
    loadingJobs = true;
    jobsError = null;
    try {
      const res = await clusterService.list({ limit: 50 });
      jobs = res.jobs.filter((j) => j.status === 'completed' && j.clusters.length > 0);
    } catch (e: any) {
      jobsError = e?.detail ?? 'No se pudieron cargar las agrupaciones';
    } finally {
      loadingJobs = false;
    }
  }

  async function generate() {
    if (!selectedJobId) return;
    generating = true;
    narrative = null;
    narrativeError = null;
    try {
      narrative = await timelineService.generateCollectionNarrative(selectedJobId);
    } catch (e: any) {
      narrativeError = e?.detail ?? 'Error al generar la narrativa. Intenta nuevamente.';
      notificationsStore.error(narrativeError ?? 'Error');
    } finally {
      generating = false;
    }
  }

  function yearSpan(n: CollectionNarrative): string {
    if (n.year_min && n.year_max) {
      return n.year_min === n.year_max ? `${n.year_min}` : `${n.year_min} – ${n.year_max}`;
    }
    return 'período no determinado';
  }

  function clusterDateLabel(c: CollectionClusterSummary): string {
    if (!c.year_representative) return 'Fecha no determinada';
    if (c.year_min && c.year_max && c.year_min !== c.year_max) {
      return `ca. ${c.year_representative} (${c.year_min}–${c.year_max})`;
    }
    return String(c.year_representative);
  }
</script>

<svelte:head>
  <title>Narrativa temporal de colección · ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-5xl">
  <!-- Encabezado -->
  <header class="mb-8">
    <a
      href="/curador"
      class="text-sm text-base-content/60 hover:text-base-content inline-flex items-center gap-1 mb-3 min-h-[44px]"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Panel de curación
    </a>
    <h1 class="text-3xl font-bold">Narrativa temporal de colección</h1>
    <p class="text-base-content/60 mt-1 text-sm">
      Genera una narrativa cohesiva del corpus completo a partir de una agrupación visual,
      ordenando los clusters cronológicamente con contexto histórico.
    </p>
  </header>

  <!-- Selector de agrupación -->
  <section class="card bg-base-100 shadow mb-6" aria-label="Selección de agrupación">
    <div class="card-body">
      <h2 class="card-title text-base mb-4">1. Selecciona una agrupación visual</h2>

      {#if loadingJobs}
        <div class="space-y-3" aria-busy="true" aria-label="Cargando agrupaciones">
          {#each Array(3) as _}
            <div class="skeleton h-16 w-full rounded-lg"></div>
          {/each}
        </div>
      {:else if jobsError}
        <div class="alert alert-error text-sm" role="alert">
          <span>{jobsError}</span>
          <button class="btn btn-sm btn-ghost ml-auto" on:click={loadJobs}>Reintentar</button>
        </div>
      {:else if jobs.length === 0}
        <div class="alert alert-warning text-sm" role="status">
          <span>
            No hay agrupaciones completadas.
            <a href="/archivo" class="link font-medium">Ve al archivo</a>
            para crear una.
          </span>
        </div>
      {:else}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3" role="listbox" aria-label="Agrupaciones disponibles">
          {#each jobs as job (job.id)}
            <button
              role="option"
              aria-selected={selectedJobId === job.id}
              class="text-left p-4 rounded-lg border-2 transition-all min-h-[44px]
                {selectedJobId === job.id
                  ? 'border-primary bg-primary/5'
                  : 'border-base-200 hover:border-primary/40 bg-base-100'}"
              on:click={() => { selectedJobId = job.id; narrative = null; narrativeError = null; }}
            >
              <p class="font-semibold text-sm">Agrupación #{job.id}</p>
              <p class="text-xs text-base-content/60 mt-1">
                {job.n_clusters} cluster{job.n_clusters !== 1 ? 's' : ''} ·
                {job.photograph_ids.length} fotografías
              </p>
              <p class="text-xs text-base-content/50 mt-0.5">
                {job.algorithm.toUpperCase()} · {job.embedding_model}
              </p>
            </button>
          {/each}
        </div>

        <div class="flex items-center justify-between mt-4">
          {#if selectedJob}
            <p class="text-sm text-base-content/60">
              Agrupación #{selectedJob.id} seleccionada ·
              {selectedJob.n_clusters} clusters ·
              {selectedJob.photograph_ids.length} fotografías
            </p>
          {:else}
            <p class="text-sm text-base-content/40">Ninguna agrupación seleccionada</p>
          {/if}

          <button
            class="btn btn-primary min-h-[44px]"
            disabled={!selectedJobId || generating}
            on:click={generate}
            aria-label="Generar narrativa temporal de la colección"
          >
            {#if generating}
              <span class="loading loading-spinner loading-sm" aria-hidden="true"></span>
              Generando…
            {:else}
              Generar narrativa
            {/if}
          </button>
        </div>
      {/if}
    </div>
  </section>

  <!-- Estado de generación -->
  {#if generating}
    <section class="card bg-base-100 shadow mb-6" aria-live="polite" aria-busy="true" aria-label="Generando narrativa">
      <div class="card-body space-y-4">
        <h2 class="card-title text-base">2. Narrativa de la colección</h2>
        <div class="skeleton h-6 w-2/3 rounded"></div>
        <div class="skeleton h-4 w-full rounded"></div>
        <div class="skeleton h-4 w-full rounded"></div>
        <div class="skeleton h-4 w-5/6 rounded"></div>
        <div class="skeleton h-4 w-full rounded mt-2"></div>
        <div class="skeleton h-4 w-4/5 rounded"></div>
        <p class="text-xs text-base-content/50 text-center pt-2">El LLM está generando la narrativa temporal…</p>
      </div>
    </section>
  {/if}

  <!-- Error al generar -->
  {#if narrativeError && !generating}
    <div class="alert alert-error mb-6" role="alert">
      <span>{narrativeError}</span>
    </div>
  {/if}

  <!-- Resultado -->
  {#if narrative && !generating}
    <section aria-label="Narrativa temporal generada">
      <!-- Cabecera del resultado -->
      <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
        <h2 class="text-xl font-bold">2. Narrativa de la colección</h2>
        <div class="flex flex-wrap gap-2 text-xs text-base-content/60">
          <span class="badge badge-ghost">{narrative.cluster_count} clusters</span>
          <span class="badge badge-ghost">{narrative.photograph_count} fotografías</span>
          {#if narrative.year_min}
            <span class="badge badge-ghost">{yearSpan(narrative)}</span>
          {/if}
          <span class="badge badge-ghost">{narrative.provider}</span>
          <span class="badge badge-ghost">{narrative.generation_time_ms} ms</span>
        </div>
      </div>

      <!-- Arco temporal -->
      <div class="card bg-primary/5 border border-primary/20 shadow-sm mb-4">
        <div class="card-body py-4">
          <p class="text-xs font-semibold text-primary uppercase tracking-wider mb-1">Arco temporal</p>
          <p class="text-sm leading-relaxed">{narrative.temporal_arc}</p>
        </div>
      </div>

      <!-- Narrativa principal -->
      <div class="card bg-base-100 shadow mb-4">
        <div class="card-body">
          <h3 class="font-semibold text-base mb-3">Narrativa del corpus</h3>
          <div class="prose prose-sm max-w-none text-base-content/90 leading-relaxed whitespace-pre-line">
            {narrative.collection_narrative}
          </div>
        </div>
      </div>

      <!-- Hilos temáticos + significado histórico en columnas -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div class="card bg-base-100 shadow">
          <div class="card-body">
            <h3 class="font-semibold text-sm mb-3">Hilos temáticos</h3>
            <div class="flex flex-wrap gap-2">
              {#each narrative.thematic_threads as thread}
                <span class="badge badge-secondary badge-outline">{thread}</span>
              {/each}
            </div>
          </div>
        </div>

        <div class="card bg-base-100 shadow">
          <div class="card-body">
            <h3 class="font-semibold text-sm mb-3">Significado histórico</h3>
            <p class="text-sm text-base-content/80 leading-relaxed">{narrative.historical_significance}</p>
          </div>
        </div>
      </div>

      <!-- Clusters ordenados cronológicamente -->
      <div class="card bg-base-100 shadow">
        <div class="card-body">
          <h3 class="font-semibold text-base mb-4">Clusters en orden cronológico</h3>

          <ol class="relative border-l border-base-300 ml-3 space-y-5">
            {#each narrative.ordered_clusters as cluster, i (cluster.cluster_id)}
              <li class="ml-6">
                <!-- Círculo en la línea de tiempo -->
                <span
                  class="absolute -left-3 flex items-center justify-center w-6 h-6 rounded-full
                    {cluster.year_representative ? 'bg-primary text-primary-content' : 'bg-base-300 text-base-content/50'}
                    text-xs font-bold"
                  aria-hidden="true"
                >
                  {i + 1}
                </span>

                <article class="p-4 bg-base-200 rounded-lg">
                  <header class="flex flex-wrap items-start justify-between gap-2 mb-2">
                    <div>
                      <h4 class="font-semibold text-sm">{cluster.label}</h4>
                      <p class="text-xs text-base-content/60 mt-0.5">
                        {cluster.photograph_count} fotografía{cluster.photograph_count !== 1 ? 's' : ''}
                        {#if cluster.centroid_photograph_id}
                          · centroide #{cluster.centroid_photograph_id}
                        {/if}
                      </p>
                    </div>
                    <div class="flex flex-col items-end gap-1">
                      <span
                        class="badge badge-sm {cluster.year_representative ? 'badge-primary' : 'badge-ghost'}"
                      >
                        {clusterDateLabel(cluster)}
                      </span>
                      {#if cluster.date_source !== 'none'}
                        <span class="text-xs text-base-content/40">fuente: {cluster.date_source}</span>
                      {/if}
                    </div>
                  </header>

                  <a
                    href="/archivo/clusters/{cluster.cluster_id}"
                    class="text-xs text-primary hover:underline min-h-[44px] inline-flex items-center"
                    aria-label="Ver detalle del cluster {cluster.label}"
                  >
                    Ver agrupación →
                  </a>
                </article>
              </li>
            {/each}
          </ol>
        </div>
      </div>

      <!-- Acción para regenerar -->
      <div class="flex justify-end mt-6">
        <button
          class="btn btn-outline btn-sm min-h-[44px]"
          on:click={generate}
          disabled={generating}
          aria-label="Regenerar narrativa temporal"
        >
          Regenerar narrativa
        </button>
      </div>
    </section>
  {/if}
</div>
