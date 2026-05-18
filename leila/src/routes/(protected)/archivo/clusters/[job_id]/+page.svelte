<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { clusterService, type ClusteringJob } from '$lib/services/clusterService';
  import { notificationsStore } from '$lib/stores/notifications';

  $: jobId = Number($page.params.job_id);

  let job: ClusteringJob | null = null;
  let loading = true;
  let error: string | null = null;
  let justifying = false;
  let justified = false;

  onMount(async () => {
    try {
      job = await clusterService.get(jobId);
      // Si los clusters aún no tienen justificación, generarla automáticamente
      const hasAnyJustification = job.clusters.some((c) => c.justification);
      if (!hasAnyJustification && job.clusters.length > 0) {
        await regenerateJustifications(false);
      } else {
        justified = hasAnyJustification;
      }
    } catch (e: any) {
      error = e?.detail || e?.message || 'No se pudo cargar la agrupación';
    } finally {
      loading = false;
    }
  });

  async function regenerateJustifications(showToast: boolean = true) {
    if (!job) return;
    justifying = true;
    try {
      job = await clusterService.justify(jobId);
      justified = true;
      if (showToast) notificationsStore.success('Justificaciones regeneradas');
    } catch (e: any) {
      notificationsStore.error(e?.detail || 'No se pudieron generar las justificaciones');
    } finally {
      justifying = false;
    }
  }
</script>

<svelte:head>
  <title>Agrupación #{jobId} · ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-5xl">
  <header class="mb-6">
    <a href="/archivo" class="text-sm text-base-content/60 hover:text-base-content inline-flex items-center gap-1 mb-3">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Volver al archivo
    </a>
    <h1 class="text-3xl font-bold">Agrupación #{jobId}</h1>
    {#if job}
      <div class="flex flex-wrap items-center gap-3 text-sm text-base-content/60 mt-1">
        <span>{job.algorithm.toUpperCase()}</span>
        <span>·</span>
        <span>{job.n_clusters} cluster{job.n_clusters !== 1 ? 's' : ''}</span>
        <span>·</span>
        <span>{job.photograph_ids.length} fotografías</span>
        {#if job.noise_count > 0}
          <span>·</span>
          <span>{job.noise_count} fuera de cluster</span>
        {/if}
        <span>·</span>
        <span>{job.processing_time_ms} ms</span>
      </div>
    {/if}
  </header>

  {#if loading}
    <div class="flex items-center justify-center py-16">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if error}
    <div class="alert alert-error">
      <span>{error}</span>
    </div>
  {:else if job}
    <div class="flex items-center justify-between mb-4">
      <p class="text-sm text-base-content/60">
        {#if justifying}
          Generando justificaciones con el LLM…
        {:else if justified}
          Justificaciones generadas automáticamente
        {:else}
          Sin justificación aún
        {/if}
      </p>
      <button
        class="btn btn-sm btn-ghost"
        on:click={() => regenerateJustifications(true)}
        disabled={justifying}
      >
        {#if justifying}<span class="loading loading-spinner loading-xs"></span>{/if}
        Regenerar
      </button>
    </div>

    <div class="space-y-4">
      {#each job.clusters as cluster (cluster.id)}
        <article class="card bg-base-100 shadow-md">
          <div class="card-body">
            <header class="flex items-start justify-between gap-3">
              <div>
                <h2 class="card-title">{cluster.label}</h2>
                <p class="text-sm text-base-content/60">
                  {cluster.member_count} fotografía{cluster.member_count !== 1 ? 's' : ''}
                  {#if cluster.centroid_photograph_id} · centroide #{cluster.centroid_photograph_id}{/if}
                </p>
              </div>
              <span class="badge badge-secondary">{cluster.algorithm}</span>
            </header>

            {#if cluster.justification}
              <div class="mt-3 p-4 bg-base-200 rounded-lg border-l-4 border-secondary">
                <p class="text-sm font-medium text-base-content/70 mb-1">Justificación del LLM</p>
                <p class="text-sm whitespace-pre-line">{cluster.justification}</p>
              </div>
            {:else if justifying}
              <div class="mt-3 flex items-center gap-2 text-sm text-base-content/60">
                <span class="loading loading-dots loading-sm"></span>
                Generando justificación…
              </div>
            {/if}

            <details class="mt-3">
              <summary class="text-sm text-base-content/60 cursor-pointer">
                IDs ({cluster.photograph_ids.length})
              </summary>
              <p class="text-xs font-mono mt-2 text-base-content/50 break-all">
                {cluster.photograph_ids.join(', ')}
              </p>
            </details>
          </div>
        </article>
      {/each}
    </div>
  {/if}
</div>
