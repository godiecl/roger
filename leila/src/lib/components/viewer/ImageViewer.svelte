<script lang="ts">
  import type { Image, Narrative } from '$lib/types';
  import { createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/services/apiClient';
  import LikeReportBar from '$lib/components/viewer/LikeReportBar.svelte';

  export let image: Image;
  export let narratives: Narrative[] = [];

  const dispatch = createEventDispatcher();

  type Tab = 'visualization' | 'narrative' | 'timeline';
  let activeTab: Tab = 'visualization';

  // --- Context state ---
  interface ContextResponse {
    id: number;
    image_id: number;
    text: string;
    provider: string;
    is_anchored: boolean;
    like_count: number;
    report_count: number;
    created_at?: string;
  }

  let freshContext: ContextResponse | null = null;
  let freshContextLoading = false;
  let anchoredContexts: ContextResponse[] = [];
  let anchoredLoading = false;
  let narrativeTabChecked = false;

  // --- Timeline state ---
  interface TimelineEvent {
    id?: number;
    date_label: string;
    year?: number;
    title: string;
    description: string;
    axis: string;
    source_type: string;
  }
  interface TimelineData {
    id?: number;
    photograph_id: number;
    context_summary: string;
    events: TimelineEvent[];
    is_approved: boolean;
  }

  let timeline: TimelineData | null = null;
  let timelineLoading = false;
  let timelineError: string | null = null;
  let timelineChecked = false;

  const axisLabel: Record<string, string> = {
    biographical: 'Biográfico',
    historical: 'Histórico',
    expedition: 'Expedición',
  };

  const axisColor: Record<string, string> = {
    biographical: 'badge-primary',
    historical: 'badge-secondary',
    expedition: 'badge-accent',
  };

  $: groupedEvents = timeline?.events.reduce(
    (acc, ev) => {
      if (!acc[ev.axis]) acc[ev.axis] = [];
      acc[ev.axis].push(ev);
      return acc;
    },
    {} as Record<string, TimelineEvent[]>
  ) ?? {};

  function handleClose() {
    dispatch('close');
  }

  function selectTab(tab: Tab) {
    activeTab = tab;
    if (tab === 'narrative' && !narrativeTabChecked) {
      loadNarrativeTab();
    }
    if (tab === 'timeline' && !timelineChecked) {
      loadTimeline();
    }
  }

  async function loadNarrativeTab() {
    narrativeTabChecked = true;
    freshContextLoading = true;
    anchoredLoading = true;

    // Fire both in parallel
    const [contextResult, anchoredResult] = await Promise.allSettled([
      apiClient.post<ContextResponse>(`/context/generate/${image.id}`, {}),
      apiClient.get<ContextResponse[]>(`/context/image/${image.id}/anchored`),
    ]);

    if (contextResult.status === 'fulfilled') {
      freshContext = contextResult.value;
    }
    freshContextLoading = false;

    if (anchoredResult.status === 'fulfilled') {
      anchoredContexts = anchoredResult.value;
    }
    anchoredLoading = false;
  }

  async function loadTimeline() {
    timelineLoading = true;
    timelineError = null;
    try {
      timeline = await apiClient.get<TimelineData>(`/timelines/photograph/${image.id}`);
    } catch (e: any) {
      if (e.status !== 404) {
        timelineError = e.detail || 'Error al cargar la línea de tiempo';
      }
    } finally {
      timelineLoading = false;
      timelineChecked = true;
    }
  }

  async function generateTimeline() {
    timelineLoading = true;
    timelineError = null;
    try {
      timeline = await apiClient.post<TimelineData>('/timelines', {
        photograph_id: image.id,
        photograph_date: image.year ? String(image.year) : undefined,
        photograph_location: image.location ?? undefined,
        photograph_description: image.description ?? undefined,
      });
      timelineChecked = true;
    } catch (e: any) {
      timelineError = e.detail || 'Error al generar la línea de tiempo';
    } finally {
      timelineLoading = false;
    }
  }
</script>

<!-- Backdrop -->
<div
  class="fixed inset-0 bg-black/80 z-50 flex items-start justify-center p-4 overflow-y-auto"
  on:click|self={handleClose}
  on:keydown={(e) => e.key === 'Escape' && handleClose()}
  role="presentation"
>
  <div
    class="bg-base-100 rounded-xl w-full max-w-7xl my-4 flex flex-col shadow-2xl"
    role="dialog"
    aria-modal="true"
    aria-labelledby="viewer-title"
    tabindex="-1"
  >

    <!-- Header -->
    <div class="flex items-start justify-between px-6 py-5 border-b border-base-300">
      <div class="flex-1 min-w-0 pr-4">
        <h2 id="viewer-title" class="text-xl font-bold leading-tight">{image.title}</h2>
        <div class="flex flex-wrap items-center gap-4 mt-1.5 text-sm text-base-content/55">
          {#if image.year}
            <span class="flex items-center gap-1.5">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {image.year}
            </span>
          {/if}
          {#if image.location}
            <span class="flex items-center gap-1.5">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {image.location}
            </span>
          {/if}
          {#if image.tags?.length > 0}
            <span class="flex items-center gap-1.5">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-5 5a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              {image.tags.length} {image.tags.length === 1 ? 'etiqueta' : 'etiquetas'}
            </span>
          {/if}
        </div>
      </div>
      <div class="flex items-center gap-2 flex-shrink-0">
        <a
          href={image.file_path}
          download
          class="btn btn-sm btn-outline gap-1.5"
          aria-label="Descargar imagen"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Descargar
        </a>
        <button
          class="btn btn-ghost btn-circle btn-sm"
          on:click={handleClose}
          aria-label="Cerrar visor"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Body: content + sidebar -->
    <div class="flex flex-col lg:flex-row min-h-0">

      <!-- Left: tabs + content -->
      <div class="flex-1 flex flex-col min-w-0">
        <!-- Tab bar -->
        <div class="flex border-b border-base-300 px-6" role="tablist">
          {#each [
            { id: 'visualization', label: 'Visualización' },
            { id: 'narrative', label: 'Narrativa IA' },
            { id: 'timeline', label: 'Línea de Tiempo' },
          ] as tab (tab.id)}
            <button
              role="tab"
              aria-selected={activeTab === tab.id}
              class="px-4 py-3 text-sm font-medium border-b-2 transition-colors
                {activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-base-content/55 hover:text-base-content'}"
              on:click={() => selectTab(tab.id as Tab)}
            >
              {tab.label}
            </button>
          {/each}
        </div>

        <!-- Tab content -->
        <div class="p-6 overflow-y-auto">

          {#if activeTab === 'visualization'}
            <!-- Imagen -->
            <div
              class="flex items-center justify-center bg-base-200 rounded-xl overflow-hidden"
              style="min-height: 16rem;"
            >
              <img
                src={image.file_path}
                alt={image.title}
                class="max-w-full object-contain"
                style="max-height: 65vh;"
                loading="lazy"
              />
            </div>
            {#if image.description}
              <p class="mt-4 text-sm text-base-content/65 leading-relaxed">{image.description}</p>
            {/if}

          {:else if activeTab === 'narrative'}
            <!-- Narrativa IA -->
            <div class="space-y-6">

              <!-- Contexto generado por IA -->
              <div>
                <h3 class="text-xs font-semibold uppercase tracking-wider text-base-content/50 mb-3">
                  Contexto Histórico
                </h3>
                {#if freshContextLoading}
                  <!-- Skeleton 4 líneas -->
                  <div class="card bg-base-200 p-5 animate-pulse">
                    <div class="flex items-center gap-2 mb-3">
                      <div class="h-4 bg-base-300 rounded w-16"></div>
                      <div class="h-4 bg-base-300 rounded w-24 ml-auto"></div>
                    </div>
                    <div class="space-y-2">
                      <div class="h-3 bg-base-300 rounded w-full"></div>
                      <div class="h-3 bg-base-300 rounded w-11/12"></div>
                      <div class="h-3 bg-base-300 rounded w-4/5"></div>
                      <div class="h-3 bg-base-300 rounded w-3/4"></div>
                    </div>
                  </div>
                {:else if freshContext}
                  <div class="card bg-base-200 p-5">
                    <div class="flex flex-wrap items-center gap-2 mb-3">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/40 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      <span class="text-xs font-medium text-base-content/55">Generado por IA</span>
                      <span class="badge badge-sm badge-warning ml-auto">Verosímil</span>
                    </div>
                    <p class="text-sm leading-relaxed text-base-content/85">{freshContext.text}</p>
                    <div class="mt-4 pt-3 border-t border-base-300">
                      <LikeReportBar
                        contentType="context"
                        contentId={freshContext.id}
                        likeCount={freshContext.like_count}
                      />
                    </div>
                  </div>
                {:else}
                  <p class="text-sm text-base-content/40 text-center py-6">
                    No se pudo generar el contexto para esta imagen.
                  </p>
                {/if}
              </div>

              <!-- Contextos anclados por curadores -->
              <div>
                <h3 class="text-xs font-semibold uppercase tracking-wider text-base-content/50 mb-3">
                  Contextos Verificados
                </h3>
                {#if anchoredLoading}
                  <!-- Skeleton tarjeta -->
                  <div class="card bg-base-200 p-5 animate-pulse">
                    <div class="flex items-center gap-2 mb-3">
                      <div class="h-4 bg-base-300 rounded w-20"></div>
                      <div class="h-4 bg-base-300 rounded w-16 ml-auto"></div>
                    </div>
                    <div class="space-y-2">
                      <div class="h-3 bg-base-300 rounded w-full"></div>
                      <div class="h-3 bg-base-300 rounded w-5/6"></div>
                      <div class="h-3 bg-base-300 rounded w-2/3"></div>
                    </div>
                  </div>
                {:else if anchoredContexts.length > 0}
                  <div class="space-y-4">
                    {#each anchoredContexts as ctx (ctx.id)}
                      <div class="card bg-base-200 p-5">
                        <div class="flex flex-wrap items-center gap-2 mb-3">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-success flex-shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                          </svg>
                          <span class="text-xs font-medium text-base-content/55">Anclado por curador</span>
                          <span class="badge badge-sm badge-warning ml-auto">Verosímil</span>
                        </div>
                        <p class="text-sm leading-relaxed text-base-content/85">{ctx.text}</p>
                        <div class="mt-4 pt-3 border-t border-base-300">
                          <LikeReportBar
                            contentType="context"
                            contentId={ctx.id}
                            likeCount={ctx.like_count}
                          />
                        </div>
                      </div>
                    {/each}
                  </div>
                {:else}
                  <p class="text-sm text-base-content/40 text-center py-4">
                    Ningún curador ha anclado un contexto para esta imagen aún.
                  </p>
                {/if}
              </div>

              <!-- Narrativas aprobadas (contenido de curadores) -->
              {#if narratives.length > 0}
                <div>
                  <h3 class="text-xs font-semibold uppercase tracking-wider text-base-content/50 mb-3">
                    Narrativas del Curador
                  </h3>
                  <div class="space-y-4">
                    {#each narratives as narrative (narrative.id)}
                      <div class="card bg-base-200 p-5">
                        <div class="flex flex-wrap items-center gap-2 mb-3">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-warning flex-shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                          <span class="font-semibold text-sm">Narrativa</span>
                          <div class="flex gap-1.5 ml-auto">
                            <span class="badge badge-sm {narrative.is_manual ? 'badge-success' : 'badge-warning'}">
                              {narrative.is_manual ? 'Veraz' : 'Verosímil'}
                            </span>
                            {#if narrative.trazabilidad?.confidence_score != null}
                              <span class="badge badge-sm badge-outline">
                                {Math.round(narrative.trazabilidad.confidence_score * 100)}% confianza
                              </span>
                            {/if}
                          </div>
                        </div>
                        <p class="text-sm leading-relaxed text-base-content/85">{narrative.text}</p>
                        <div class="mt-4 pt-3 border-t border-base-300">
                          <LikeReportBar
                            contentType="narrative"
                            contentId={narrative.id}
                            likeCount={narrative.like_count}
                          />
                        </div>
                      </div>
                    {/each}
                  </div>
                </div>
              {/if}

            </div>

          {:else if activeTab === 'timeline'}
            <!-- Línea de Tiempo -->
            {#if timelineLoading}
              <div class="flex flex-col items-center justify-center py-16 gap-3">
                <span class="loading loading-spinner loading-lg"></span>
                <p class="text-sm text-base-content/55">Generando línea de tiempo con IA...</p>
              </div>
            {:else if timelineError}
              <div class="alert alert-error">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span class="text-sm">{timelineError}</span>
                <button class="btn btn-xs btn-ghost ml-auto" on:click={generateTimeline}>Reintentar</button>
              </div>
            {:else if !timeline}
              <div class="flex flex-col items-center justify-center py-12 gap-4 text-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-base-content/25" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="text-sm text-base-content/55">No hay línea de tiempo generada para esta imagen.</p>
                <button class="btn btn-primary btn-sm" on:click={generateTimeline}>
                  Generar con IA
                </button>
              </div>
            {:else}
              <div class="space-y-6">
                {#if timeline.context_summary}
                  <div class="card bg-base-200 p-4">
                    <p class="text-sm text-base-content/70 leading-relaxed">{timeline.context_summary}</p>
                  </div>
                {/if}

                {#each Object.entries(groupedEvents) as [axis, events] (axis)}
                  <div>
                    <div class="flex items-center gap-2 mb-3">
                      <span class="badge {axisColor[axis] ?? 'badge-ghost'} badge-sm">
                        {axisLabel[axis] ?? axis}
                      </span>
                      <div class="flex-1 h-px bg-base-300"></div>
                    </div>
                    <div class="space-y-0">
                      {#each events as event (event.id ?? event.title)}
                        <div class="flex gap-4 pb-4">
                          <div class="w-20 flex-shrink-0 text-right pt-0.5">
                            <span class="text-xs font-medium text-primary leading-tight">{event.date_label}</span>
                          </div>
                          <div class="flex-shrink-0 flex flex-col items-center">
                            <div class="w-2.5 h-2.5 rounded-full bg-primary mt-0.5 flex-shrink-0"></div>
                            <div class="w-px flex-1 bg-base-300 mt-1"></div>
                          </div>
                          <div class="flex-1 pb-1">
                            <p class="font-medium text-sm leading-snug">{event.title}</p>
                            <p class="text-xs text-base-content/60 mt-0.5 leading-relaxed">{event.description}</p>
                            <span class="badge badge-xs mt-1.5 {event.source_type === 'veraz' ? 'badge-success' : 'badge-warning'}">
                              {event.source_type === 'veraz' ? 'Fuente verificada' : 'Verosímil'}
                            </span>
                          </div>
                        </div>
                      {/each}
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          {/if}

        </div>
      </div>

      <!-- Right sidebar -->
      <aside
        class="w-full lg:w-72 xl:w-80 flex-shrink-0 border-t lg:border-t-0 lg:border-l border-base-300 p-6 space-y-5 overflow-y-auto"
        aria-label="Metadatos"
      >
        <div>
          <h3 class="text-xs font-semibold uppercase tracking-wider text-base-content/50 mb-3">
            Metadatos de la Imagen
          </h3>
          <dl class="space-y-3">
            {#if image.year}
              <div>
                <dt class="text-xs text-base-content/45">Fecha</dt>
                <dd class="text-sm font-medium mt-0.5">{image.year}</dd>
              </div>
            {/if}
            {#if image.location}
              <div>
                <dt class="text-xs text-base-content/45">Ubicación</dt>
                <dd class="text-sm font-medium mt-0.5">{image.location}</dd>
              </div>
            {/if}
            {#if image.author}
              <div>
                <dt class="text-xs text-base-content/45">Autor</dt>
                <dd class="text-sm font-medium mt-0.5">{image.author}</dd>
              </div>
            {/if}
            {#if image.metadata?.technique}
              <div>
                <dt class="text-xs text-base-content/45">Técnica</dt>
                <dd class="text-sm font-medium mt-0.5">{image.metadata.technique}</dd>
              </div>
            {/if}
            {#if image.metadata?.width_px && image.metadata?.height_px}
              <div>
                <dt class="text-xs text-base-content/45">Dimensiones</dt>
                <dd class="text-sm font-medium mt-0.5">{image.metadata.width_px} × {image.metadata.height_px} px</dd>
              </div>
            {/if}
          </dl>
        </div>

        {#if image.description}
          <div>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-base-content/50 mb-2">
              Descripción
            </h3>
            <p class="text-xs text-base-content/65 leading-relaxed">{image.description}</p>
          </div>
        {/if}

        {#if image.tags?.length > 0}
          <div>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-base-content/50 mb-2">
              Etiquetas
            </h3>
            <div class="flex flex-wrap gap-1.5">
              {#each image.tags as tag (tag)}
                <span class="badge badge-sm badge-outline">{tag}</span>
              {/each}
            </div>
          </div>
        {/if}
      </aside>
    </div>

  </div>
</div>

<svelte:window
  on:keydown={(e) => {
    if (e.key === 'Escape') handleClose();
  }}
/>
