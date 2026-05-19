<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import { notificationsStore } from '$lib/stores/notifications';
  import { apiClient } from '$lib/services/apiClient';
  import {
    narrativeCompareService,
    type LLMProviderResult,
    type LLMCompareResponse,
  } from '$lib/services/narrativeService';

  const ALLOWED_ROLES = ['curador', 'administrador', 'investigador'];

  interface DetectionItem {
    id: number | null;
    photograph_id: number;
    scene_description: string;
    provider: string;
    status: string;
    object_count: number;
    created_at: string | null;
  }

  let detections: DetectionItem[] = [];
  let selectedPhotographId: number | null = null;
  let customSystemPrompt = '';
  let customUserPrompt = '';
  let loadingDetections = true;
  let comparing = false;
  let result: LLMCompareResponse | null = null;
  let error: string | null = null;

  onMount(async () => {
    if (!$isAuthenticated) { goto('/login'); return; }
    const role = $authStore.user?.role ?? '';
    if (!ALLOWED_ROLES.includes(role)) { goto('/curador'); return; }
    await loadDetections();
  });

  async function loadDetections() {
    loadingDetections = true;
    try {
      const res = await apiClient.get<{ detections: DetectionItem[] }>('/detections', { skip: 0, limit: 200 });
      detections = res.detections.filter((d) => d.status === 'completed');
    } catch {
      detections = [];
    } finally {
      loadingDetections = false;
    }
  }

  async function compare() {
    if (!selectedPhotographId) return;
    comparing = true;
    error = null;
    result = null;
    try {
      result = await narrativeCompareService.compare({
        photograph_id: selectedPhotographId,
        system_prompt: customSystemPrompt.trim() || undefined,
        user_prompt: customUserPrompt.trim() || undefined,
      });
    } catch (e: any) {
      error = e?.detail ?? 'Error al comparar los modelos';
      notificationsStore.error(error!);
    } finally {
      comparing = false;
    }
  }

  function providerBadgeClass(r: LLMProviderResult): string {
    if (r.error) return 'badge-error';
    const p = r.provider.toLowerCase();
    if (p.startsWith('groq'))       return 'badge-warning';
    if (p.startsWith('openai'))     return 'badge-success';
    if (p.startsWith('anthropic'))  return 'badge-info';
    return 'badge-ghost';
  }

  function speedLabel(ms: number): string {
    if (ms < 1000) return `${ms} ms`;
    return `${(ms / 1000).toFixed(1)} s`;
  }
</script>

<svelte:head><title>Comparación LLM · ROGER</title></svelte:head>

<div class="container mx-auto px-4 py-8 max-w-6xl">
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
    <h1 class="text-3xl font-bold">Comparación multi-LLM</h1>
    <p class="text-base-content/60 text-sm mt-1">
      Envía el mismo contexto fotográfico a todos los proveedores LLM configurados y compara sus respuestas en paralelo.
    </p>
  </header>

  <div class="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6">
    <!-- Sidebar: selector de fotografía -->
    <aside class="space-y-3">
      <h2 class="font-semibold text-sm text-base-content/70 uppercase tracking-wide">
        Fotografías analizadas
      </h2>

      {#if loadingDetections}
        <div class="space-y-2" aria-busy="true" aria-label="Cargando fotografías">
          {#each Array(6) as _}
            <div class="skeleton h-12 w-full rounded-lg"></div>
          {/each}
        </div>
      {:else if detections.length === 0}
        <p class="text-sm text-base-content/50">
          No hay fotografías con análisis completado.
          Ejecuta detecciones primero desde el visualizador.
        </p>
      {:else}
        <div class="space-y-1 max-h-[60vh] overflow-y-auto pr-1" role="listbox" aria-label="Lista de fotografías">
          {#each detections as det}
            <button
              class="w-full text-left px-3 py-2.5 rounded-lg border text-sm transition-all min-h-[44px]
                     {selectedPhotographId === det.photograph_id
                       ? 'bg-primary text-primary-content border-primary'
                       : 'bg-base-100 border-base-200 hover:border-primary/40 hover:bg-base-200'}"
              on:click={() => { selectedPhotographId = det.photograph_id; result = null; error = null; }}
              role="option"
              aria-selected={selectedPhotographId === det.photograph_id}
            >
              <span class="font-medium block">Foto #{det.photograph_id}</span>
              <span class="text-xs opacity-70 block truncate">{det.scene_description || 'Sin descripción'}</span>
            </button>
          {/each}
        </div>
      {/if}
    </aside>

    <!-- Área principal -->
    <main class="space-y-5">
      <!-- Prompts opcionales -->
      <details class="collapse collapse-arrow border border-base-200 bg-base-100 rounded-box">
        <summary class="collapse-title text-sm font-medium min-h-[44px] flex items-center">
          Personalizar prompts (opcional)
        </summary>
        <div class="collapse-content space-y-3 pt-0">
          <div>
            <label class="label label-text text-xs" for="sys-prompt">System prompt</label>
            <textarea
              id="sys-prompt"
              class="textarea textarea-bordered w-full text-sm leading-relaxed"
              rows="3"
              placeholder="Deja vacío para usar el prompt estándar ROGER (historiador patrimonial)."
              bind:value={customSystemPrompt}
            ></textarea>
          </div>
          <div>
            <label class="label label-text text-xs" for="user-prompt">User prompt / contexto adicional</label>
            <textarea
              id="user-prompt"
              class="textarea textarea-bordered w-full text-sm leading-relaxed"
              rows="3"
              placeholder="Deja vacío para construir el contexto automáticamente desde los metadatos de la fotografía."
              bind:value={customUserPrompt}
            ></textarea>
          </div>
        </div>
      </details>

      <!-- Botón comparar -->
      <button
        class="btn btn-primary w-full sm:w-auto min-h-[44px]"
        on:click={compare}
        disabled={!selectedPhotographId || comparing}
        aria-label="Comparar modelos LLM"
      >
        {#if comparing}
          <span class="loading loading-spinner loading-sm" aria-hidden="true"></span>
          Comparando modelos…
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Comparar modelos
        {/if}
      </button>

      {#if !selectedPhotographId && !comparing && !result}
        <p class="text-sm text-base-content/40">Selecciona una fotografía para comenzar la comparación.</p>
      {/if}

      <!-- Error global -->
      {#if error}
        <div class="alert alert-error text-sm" role="alert">
          <span>{error}</span>
        </div>
      {/if}

      <!-- Skeleton mientras compara -->
      {#if comparing}
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4" aria-busy="true" aria-label="Generando respuestas">
          {#each Array(3) as _}
            <div class="card bg-base-100 border border-base-200 shadow">
              <div class="card-body space-y-3">
                <div class="skeleton h-4 w-1/2 rounded"></div>
                <div class="skeleton h-3 w-full rounded"></div>
                <div class="skeleton h-3 w-full rounded"></div>
                <div class="skeleton h-3 w-4/5 rounded"></div>
                <div class="skeleton h-3 w-3/4 rounded"></div>
                <div class="skeleton h-3 w-full rounded"></div>
              </div>
            </div>
          {/each}
        </div>
      {/if}

      <!-- Resultados -->
      {#if result}
        <!-- Contexto enviado -->
        <details class="collapse collapse-arrow border border-base-200 bg-base-50 rounded-box">
          <summary class="collapse-title text-xs text-base-content/50 min-h-[40px] flex items-center">
            Ver contexto enviado a los modelos
          </summary>
          <div class="collapse-content text-xs text-base-content/70 space-y-2 pt-0">
            <div>
              <span class="font-semibold">System:</span>
              <p class="whitespace-pre-wrap mt-0.5">{result.system_prompt}</p>
            </div>
            <div>
              <span class="font-semibold">User:</span>
              <p class="whitespace-pre-wrap mt-0.5">{result.user_prompt}</p>
            </div>
          </div>
        </details>

        <!-- Tarjetas de respuesta -->
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {#each result.results as r}
            <article
              class="card bg-base-100 border shadow
                     {r.error ? 'border-error/30' : 'border-base-200'}"
            >
              <div class="card-body p-4">
                <div class="flex items-center justify-between gap-2 mb-3">
                  <span class="badge badge-sm font-mono {providerBadgeClass(r)}">{r.provider}</span>
                  <span class="text-xs text-base-content/40">{speedLabel(r.time_ms)}</span>
                </div>

                {#if r.error}
                  <div class="alert alert-error alert-sm text-xs p-2" role="alert">
                    <span class="line-clamp-3">{r.error}</span>
                  </div>
                {:else}
                  <p class="text-sm leading-relaxed text-base-content/90 whitespace-pre-wrap">
                    {r.response}
                  </p>
                {/if}
              </div>
            </article>
          {/each}
        </div>

        <p class="text-xs text-base-content/30 text-right mt-2">
          Calculado: {new Date(result.computed_at).toLocaleString('es-CL')}
        </p>
      {/if}
    </main>
  </div>
</div>
