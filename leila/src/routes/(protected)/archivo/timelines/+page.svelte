<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { timelineService, type Timeline } from '$lib/services/timelineService';
  import { notificationsStore } from '$lib/stores/notifications';

  let photographIds: number[] = [];
  let timelines: Array<{ photograph_id: number; timeline?: Timeline; error?: string }> = [];
  let loading = true;
  let progress = 0;

  onMount(async () => {
    const params = $page.url.searchParams.getAll('id');
    photographIds = params.map((p) => Number(p)).filter((n) => !Number.isNaN(n));

    if (photographIds.length === 0) {
      loading = false;
      return;
    }

    timelines = photographIds.map((id) => ({ photograph_id: id }));

    // Generate timelines in parallel, updating progress
    await Promise.all(
      photographIds.map(async (id, i) => {
        try {
          const t = await timelineService.generate({ photograph_id: id });
          timelines[i] = { photograph_id: id, timeline: t };
          timelines = timelines;
        } catch (e: any) {
          timelines[i] = { photograph_id: id, error: e?.detail || 'Error al generar' };
          timelines = timelines;
        } finally {
          progress++;
        }
      }),
    );

    loading = false;
    const failures = timelines.filter((t) => t.error).length;
    if (failures > 0) {
      notificationsStore.error(`${failures} línea${failures !== 1 ? 's' : ''} de tiempo fallaron`);
    }
  });

  $: axisLabel = (axis: string) =>
    axis === 'biographical' ? 'Biográfico' :
    axis === 'historical' ? 'Histórico' :
    axis === 'expedition' ? 'Expedición' :
    axis;

  $: axisColor = (axis: string) =>
    axis === 'biographical' ? 'border-primary' :
    axis === 'historical' ? 'border-info' :
    axis === 'expedition' ? 'border-warning' :
    'border-base-content';
</script>

<svelte:head>
  <title>Líneas de tiempo · ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-5xl">
  <header class="mb-6">
    <a href="/archivo" class="text-sm text-base-content/60 hover:text-base-content inline-flex items-center gap-1 mb-3 min-h-[44px]">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Volver al archivo
    </a>
    <h1 class="text-3xl font-bold">Líneas de tiempo</h1>
    <p class="text-base-content/60 mt-1">
      Contexto biográfico, histórico y de expedición para {photographIds.length} fotografía{photographIds.length !== 1 ? 's' : ''}.
    </p>
  </header>

  {#if photographIds.length === 0}
    <div class="alert alert-warning">
      <span>No se especificaron fotografías. Vuelve al archivo y selecciona al menos dos.</span>
    </div>
  {:else if loading}
    <div class="card bg-base-100 shadow" role="status" aria-live="polite">
      <div class="card-body items-center text-center">
        <span class="loading loading-spinner loading-lg text-primary" aria-hidden="true"></span>
        <p class="text-sm text-base-content/60">
          Generando {Math.min(progress + 1, photographIds.length)} de {photographIds.length}…
        </p>
        <progress
          class="progress progress-primary w-full max-w-xs"
          value={progress}
          max={photographIds.length}
          aria-label="Progreso de generación de líneas de tiempo"
        ></progress>
      </div>
    </div>
  {:else}
    <div class="space-y-6">
      {#each timelines as item (item.photograph_id)}
        <article class="card bg-base-100 shadow-md">
          <div class="card-body">
            <header class="border-b border-base-200 pb-3 mb-3">
              <h2 class="card-title">Fotografía #{item.photograph_id}</h2>
              {#if item.timeline}
                <p class="text-sm text-base-content/60 mt-1">
                  {item.timeline.event_count} evento{item.timeline.event_count !== 1 ? 's' : ''} ·
                  {item.timeline.provider} · {item.timeline.generation_time_ms} ms
                </p>
              {/if}
            </header>

            {#if item.error}
              <div class="alert alert-error text-sm">
                <span>{item.error}</span>
              </div>
            {:else if item.timeline}
              {#if item.timeline.context_summary}
                <div class="p-4 bg-base-200 rounded-lg mb-3 border-l-4 border-secondary">
                  <p class="text-sm font-medium text-base-content/70 mb-1">Razonamiento del LLM</p>
                  <p class="text-sm whitespace-pre-line">{item.timeline.context_summary}</p>
                </div>
              {/if}

              <div class="space-y-2">
                {#each item.timeline.events as event}
                  <div class="border-l-4 pl-3 py-1 {axisColor(event.axis)}">
                    <div class="flex flex-wrap items-baseline gap-2">
                      <span class="badge badge-sm">{axisLabel(event.axis)}</span>
                      <span class="font-medium text-sm">{event.date_label}</span>
                      <span class="text-sm font-semibold">{event.title}</span>
                      <span class="badge badge-xs badge-ghost">{event.source_type}</span>
                    </div>
                    <p class="text-sm text-base-content/70 mt-1">{event.description}</p>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        </article>
      {/each}
    </div>
  {/if}
</div>
