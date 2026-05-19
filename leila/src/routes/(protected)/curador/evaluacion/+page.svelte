<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import { notificationsStore } from '$lib/stores/notifications';
  import {
    annotationService,
    type EvaluationMetrics,
    type MetricResult,
  } from '$lib/services/annotationService';

  const ALLOWED_ROLES = ['curador', 'administrador', 'mesa_evaluadora', 'investigador'];

  let metrics: EvaluationMetrics | null = null;
  let loading = true;
  let error: string | null = null;
  let refreshing = false;

  onMount(async () => {
    if (!$isAuthenticated) { goto('/login'); return; }
    const role = $authStore.user?.role ?? '';
    if (!ALLOWED_ROLES.includes(role)) { goto('/curador'); return; }
    await load();
  });

  async function load(showToast = false) {
    if (metrics) refreshing = true; else loading = true;
    error = null;
    try {
      metrics = await annotationService.getMetrics();
      if (showToast) notificationsStore.success('Métricas actualizadas');
    } catch (e: any) {
      error = e?.detail ?? 'Error al cargar las métricas';
    } finally {
      loading = false;
      refreshing = false;
    }
  }

  function pct(v: number | null): string {
    if (v === null) return '—';
    return (v * 100).toFixed(1) + '%';
  }

  function progressPct(v: number | null, target: number): number {
    if (v === null) return 0;
    return Math.min(100, Math.round((v / target) * 100));
  }

  function statusClass(m: MetricResult): string {
    if (m.passes === null) return 'badge-ghost';
    return m.passes ? 'badge-success' : 'badge-error';
  }

  function statusLabel(m: MetricResult): string {
    if (m.passes === null) return 'Datos insuficientes';
    return m.passes ? 'CUMPLE' : 'NO CUMPLE';
  }

  function progressClass(m: MetricResult): string {
    if (m.passes === null) return 'progress-ghost';
    return m.passes ? 'progress-success' : 'progress-error';
  }

  function valueColor(m: MetricResult): string {
    if (m.passes === null) return 'text-base-content/40';
    return m.passes ? 'text-success' : 'text-error';
  }

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString('es-CL', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }
</script>

<svelte:head>
  <title>Evaluación FONDEF · ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-5xl">
  <header class="mb-8">
    <a href="/curador" class="text-sm text-base-content/60 hover:text-base-content inline-flex items-center gap-1 mb-3 min-h-[44px]">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Panel de curación
    </a>
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold">Métricas de evaluación FONDEF</h1>
        <p class="text-base-content/60 text-sm mt-1">
          Indicadores de cumplimiento ICa1–ICa4 calculados desde las anotaciones de expertos.
        </p>
      </div>
      <button
        class="btn btn-outline btn-sm min-h-[44px]"
        on:click={() => load(true)}
        disabled={loading || refreshing}
        aria-label="Recalcular métricas"
      >
        {#if refreshing}
          <span class="loading loading-spinner loading-xs" aria-hidden="true"></span>
          Recalculando…
        {:else}
          Recalcular
        {/if}
      </button>
    </div>
  </header>

  {#if loading}
    <!-- Skeleton inicial -->
    <div class="space-y-4" aria-busy="true" aria-label="Cargando métricas">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {#each Array(4) as _}
          <div class="card bg-base-100 shadow">
            <div class="card-body space-y-3">
              <div class="skeleton h-5 w-2/3 rounded"></div>
              <div class="skeleton h-12 w-1/3 rounded"></div>
              <div class="skeleton h-3 w-full rounded-full"></div>
              <div class="skeleton h-3 w-4/5 rounded"></div>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {:else if error}
    <div class="alert alert-error" role="alert">
      <span>{error}</span>
      <button class="btn btn-sm btn-ghost ml-auto" on:click={() => load()}>Reintentar</button>
    </div>
  {:else if metrics}
    <!-- Alerta de datos insuficientes -->
    {#if !metrics.sufficient_data}
      <div class="alert alert-warning mb-6 text-sm" role="status">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>
          Datos insuficientes para calcular todas las métricas. Se necesitan al menos
          <strong>10 anotaciones de objetos</strong> y <strong>5 evaluaciones de descripción</strong>.
          Completa las anotaciones desde
          <a href="/curador/anotacion-objetos" class="link">anotación de objetos</a> y
          <a href="/curador/anotacion-descripciones" class="link">anotación de descripciones</a>.
        </span>
      </div>
    {/if}

    <!-- Tarjetas de métricas -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-8">
      {#each [metrics.ica1, metrics.ica2, metrics.ica3, metrics.ica4] as metric}
        <article class="card bg-base-100 shadow">
          <div class="card-body">
            <!-- Encabezado -->
            <div class="flex items-start justify-between gap-2 mb-1">
              <h2 class="font-semibold text-sm leading-snug">{metric.label}</h2>
              <span class="badge badge-sm flex-shrink-0 {statusClass(metric)}">
                {statusLabel(metric)}
              </span>
            </div>
            <p class="text-xs text-base-content/50 mb-4 leading-relaxed">{metric.description}</p>

            <!-- Valor principal -->
            <div class="flex items-end gap-3 mb-3">
              <span class="text-4xl font-bold tabular-nums {valueColor(metric)}">
                {pct(metric.value)}
              </span>
              <span class="text-sm text-base-content/50 pb-1">
                objetivo: {pct(metric.target)}
              </span>
            </div>

            <!-- Barra de progreso -->
            <progress
              class="progress w-full {progressClass(metric)}"
              value={progressPct(metric.value, metric.target)}
              max="100"
              aria-label="{metric.label}: {pct(metric.value)} de objetivo {pct(metric.target)}"
            ></progress>

            <!-- Detalles colapsables -->
            <details class="mt-3">
              <summary class="text-xs text-base-content/40 cursor-pointer select-none">
                Ver detalles
              </summary>
              <dl class="mt-2 space-y-1">
                {#each Object.entries(metric.detail) as [k, v]}
                  {#if !Array.isArray(v)}
                    <div class="flex items-center justify-between text-xs">
                      <dt class="text-base-content/50">{k.replaceAll('_', ' ')}</dt>
                      <dd class="font-mono font-medium">{v}</dd>
                    </div>
                  {:else}
                    <div class="text-xs">
                      <dt class="text-base-content/50 mb-1">{k.replaceAll('_', ' ')}</dt>
                      <dd class="flex flex-wrap gap-1">
                        {#each v as item}
                          <span class="badge badge-xs badge-ghost">{item}</span>
                        {/each}
                      </dd>
                    </div>
                  {/if}
                {/each}
              </dl>
            </details>
          </div>
        </article>
      {/each}
    </div>

    <!-- Cobertura de anotaciones -->
    <section class="card bg-base-100 shadow mb-6" aria-label="Cobertura de anotaciones">
      <div class="card-body">
        <h2 class="font-semibold mb-4">Cobertura de anotaciones</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">

          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-base-content/60">Detecciones anotadas</span>
              <span class="font-medium">
                {metrics.coverage.detections_annotated} / {metrics.coverage.detections_total}
              </span>
            </div>
            <progress
              class="progress progress-primary w-full"
              value={metrics.coverage.detection_coverage_pct}
              max="100"
              aria-label="Cobertura de detecciones: {metrics.coverage.detection_coverage_pct}%"
            ></progress>
            <p class="text-xs text-base-content/40 mt-0.5 text-right">
              {metrics.coverage.detection_coverage_pct}% · {metrics.coverage.total_detection_annotations} anotaciones totales
            </p>
          </div>

          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-base-content/60">Descripciones de referencia</span>
              <span class="font-medium">
                {metrics.coverage.descriptions_annotated} / {metrics.coverage.descriptions_total}
              </span>
            </div>
            <progress
              class="progress progress-secondary w-full"
              value={metrics.coverage.description_coverage_pct}
              max="100"
              aria-label="Cobertura de descripciones: {metrics.coverage.description_coverage_pct}%"
            ></progress>
            <p class="text-xs text-base-content/40 mt-0.5 text-right">
              {metrics.coverage.description_coverage_pct}% · {metrics.coverage.total_description_annotations} evaluaciones
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Acciones rápidas -->
    <section class="card bg-base-200" aria-label="Próximos pasos">
      <div class="card-body py-4">
        <h2 class="font-semibold text-sm mb-3">Próximos pasos para mejorar los indicadores</h2>
        <div class="flex flex-wrap gap-3">
          <a href="/curador/anotacion-objetos" class="btn btn-sm btn-outline min-h-[44px]">
            Anotar más objetos → ICa1/ICa2
          </a>
          <a href="/curador/anotacion-descripciones" class="btn btn-sm btn-outline min-h-[44px]">
            Evaluar descripciones → ICa3
          </a>
        </div>
      </div>
    </section>

    <!-- Pie: fecha de cálculo -->
    <p class="text-xs text-base-content/30 text-right mt-4">
      Calculado: {formatDate(metrics.computed_at)}
    </p>
  {/if}
</div>
