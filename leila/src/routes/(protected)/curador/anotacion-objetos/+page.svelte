<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import { notificationsStore } from '$lib/stores/notifications';
  import { apiClient } from '$lib/services/apiClient';
  import {
    annotationService,
    type AnnotationVerdict,
    type ExpertDetectionAnnotation,
  } from '$lib/services/annotationService';

  const ALLOWED_ROLES = ['curador', 'administrador', 'mesa_evaluadora'];

  // Tipos locales basados en el schema del backend
  interface DetectedObject {
    id: number | null;
    label: string;
    category: string;
    confidence: number;
    description: string | null;
    bbox: number[] | null;
    mask_polygon: string | null;
  }

  interface DetectionItem {
    id: number | null;
    photograph_id: number;
    scene_description: string;
    provider: string;
    detection_time_ms: number;
    status: string;
    object_count: number;
    objects: DetectedObject[];
    created_at: string | null;
  }

  interface DetectionListResponse {
    total: number;
    skip: number;
    limit: number;
    detections: DetectionItem[];
  }

  // Estado principal
  let detections: DetectionItem[] = [];
  let selectedDetection: DetectionItem | null = null;
  let existingAnnotations: ExpertDetectionAnnotation[] = [];

  let loadingDetections = true;
  let loadingAnnotations = false;
  let submitting = false;
  let detectionsError: string | null = null;

  // Mapa de veredictos pendientes: detected_object_id → estado de anotación
  type ObjState = {
    verdict: AnnotationVerdict | null;
    corrected_label: string;
    notes: string;
    dirty: boolean;
  };
  let objStates: Record<string, ObjState> = {};

  $: annotationCount = Object.values(objStates).filter((s) => s.verdict !== null).length;

  onMount(async () => {
    if (!$isAuthenticated) { goto('/login'); return; }
    const role = $authStore.user?.role ?? '';
    if (!ALLOWED_ROLES.includes(role)) { goto('/curador'); return; }
    await loadDetections();
  });

  async function loadDetections() {
    loadingDetections = true;
    detectionsError = null;
    try {
      const res: DetectionListResponse = await apiClient.get('/detections', { skip: 0, limit: 100 });
      detections = res.detections.filter((d) => d.status === 'completed' && d.object_count > 0);
    } catch (e: any) {
      detectionsError = e?.detail ?? 'No se pudieron cargar las detecciones';
    } finally {
      loadingDetections = false;
    }
  }

  async function selectDetection(det: DetectionItem) {
    selectedDetection = det;
    objStates = {};
    for (const obj of det.objects) {
      const key = String(obj.id ?? `new_${obj.label}`);
      objStates[key] = { verdict: null, corrected_label: '', notes: '', dirty: false };
    }
    loadingAnnotations = true;
    try {
      if (det.id) {
        const res = await annotationService.getDetectionAnnotations(det.id);
        existingAnnotations = res.annotations;
        for (const ann of res.annotations) {
          const key = String(ann.detected_object_id);
          if (objStates[key]) {
            objStates[key].verdict = ann.verdict as AnnotationVerdict;
            objStates[key].corrected_label = ann.corrected_label ?? '';
            objStates[key].notes = ann.notes ?? '';
          }
        }
        objStates = { ...objStates };
      }
    } catch {
      existingAnnotations = [];
    } finally {
      loadingAnnotations = false;
    }
  }

  function setVerdict(objId: string, verdict: AnnotationVerdict) {
    objStates[objId] = { ...objStates[objId], verdict, dirty: true };
    objStates = { ...objStates };
  }

  async function submitAll() {
    if (!selectedDetection?.id) return;
    submitting = true;
    let saved = 0;
    let failed = 0;

    for (const [key, state] of Object.entries(objStates)) {
      if (state.verdict === null) continue;
      const objId = isNaN(Number(key)) ? null : Number(key);
      try {
        await annotationService.annotateDetection(selectedDetection.id, {
          detected_object_id: objId,
          verdict: state.verdict,
          corrected_label: state.corrected_label || null,
          notes: state.notes || null,
        });
        saved++;
      } catch {
        failed++;
      }
    }

    submitting = false;
    if (failed === 0) {
      notificationsStore.success(`${saved} anotación${saved !== 1 ? 'es' : ''} guardada${saved !== 1 ? 's' : ''}`);
      // Refrescar anotaciones existentes
      await selectDetection(selectedDetection);
    } else {
      notificationsStore.error(`${failed} anotación${failed !== 1 ? 'es' : ''} no se pudieron guardar`);
    }
  }

  function verdictClass(v: AnnotationVerdict | null): string {
    if (v === 'correct') return 'btn-success';
    if (v === 'incorrect') return 'btn-error';
    if (v === 'uncertain') return 'btn-warning';
    return 'btn-ghost';
  }

  function confidenceColor(c: number): string {
    if (c >= 0.8) return 'text-success';
    if (c >= 0.5) return 'text-warning';
    return 'text-error';
  }
</script>

<svelte:head>
  <title>Anotación de detecciones · ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-7xl">
  <header class="mb-6">
    <a href="/curador" class="text-sm text-base-content/60 hover:text-base-content inline-flex items-center gap-1 mb-3 min-h-[44px]">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Panel de curación
    </a>
    <h1 class="text-3xl font-bold">Anotación de detecciones de objetos</h1>
    <p class="text-base-content/60 text-sm mt-1">
      Valida las detecciones automáticas del modelo YOLO para construir el conjunto de evaluación (FONDEF ICa1/ICa2).
    </p>
  </header>

  <div class="flex flex-col lg:flex-row gap-6">

    <!-- Panel izquierdo: lista de detecciones -->
    <aside class="w-full lg:w-72 xl:w-80 flex-shrink-0" aria-label="Detecciones disponibles">
      <div class="card bg-base-100 shadow sticky top-4">
        <div class="card-body p-4">
          <h2 class="font-semibold text-sm mb-3">
            Detecciones completadas
            {#if !loadingDetections}
              <span class="badge badge-ghost badge-sm ml-1">{detections.length}</span>
            {/if}
          </h2>

          {#if loadingDetections}
            <div class="space-y-2" aria-busy="true">
              {#each Array(5) as _}
                <div class="skeleton h-12 w-full rounded-lg"></div>
              {/each}
            </div>
          {:else if detectionsError}
            <div class="alert alert-error text-xs" role="alert">
              <span>{detectionsError}</span>
            </div>
          {:else if detections.length === 0}
            <p class="text-sm text-base-content/50 text-center py-4">
              No hay detecciones completadas.
            </p>
          {:else}
            <ul class="space-y-1 max-h-[70vh] overflow-y-auto pr-1" role="listbox" aria-label="Lista de detecciones">
              {#each detections as det (det.id)}
                <li>
                  <button
                    role="option"
                    aria-selected={selectedDetection?.id === det.id}
                    class="w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors
                      {selectedDetection?.id === det.id
                        ? 'bg-primary text-primary-content'
                        : 'hover:bg-base-200'}"
                    on:click={() => selectDetection(det)}
                  >
                    <p class="font-medium">Foto #{det.photograph_id}</p>
                    <p class="text-xs opacity-70 mt-0.5">
                      {det.object_count} objeto{det.object_count !== 1 ? 's' : ''} · {det.provider}
                    </p>
                  </button>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>
    </aside>

    <!-- Panel principal: anotación -->
    <main class="flex-1 min-w-0">
      {#if !selectedDetection}
        <div class="card bg-base-100 shadow">
          <div class="card-body items-center text-center py-16">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-base-content/20 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p class="text-base-content/50 text-sm">Selecciona una detección del panel izquierdo para comenzar a anotar.</p>
          </div>
        </div>
      {:else}
        <div class="space-y-4">
          <!-- Cabecera de la detección -->
          <div class="card bg-base-100 shadow">
            <div class="card-body py-4">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 class="font-bold text-lg">Fotografía #{selectedDetection.photograph_id}</h2>
                  <p class="text-sm text-base-content/60 mt-0.5">
                    {selectedDetection.provider} · {selectedDetection.object_count} objetos detectados
                    {#if existingAnnotations.length > 0}
                      · <span class="text-success">{existingAnnotations.length} anotados previamente</span>
                    {/if}
                  </p>
                </div>
                <button
                  class="btn btn-primary min-h-[44px]"
                  disabled={annotationCount === 0 || submitting}
                  on:click={submitAll}
                  aria-label="Guardar todas las anotaciones"
                >
                  {#if submitting}
                    <span class="loading loading-spinner loading-sm" aria-hidden="true"></span>
                    Guardando…
                  {:else}
                    Guardar {annotationCount} anotación{annotationCount !== 1 ? 'es' : ''}
                  {/if}
                </button>
              </div>

              {#if selectedDetection.scene_description}
                <div class="mt-3 p-3 bg-base-200 rounded-lg text-sm text-base-content/70">
                  <span class="font-medium">Descripción IA: </span>{selectedDetection.scene_description}
                </div>
              {/if}
            </div>
          </div>

          <!-- Lista de objetos a anotar -->
          {#if loadingAnnotations}
            <div class="space-y-3" aria-busy="true">
              {#each Array(3) as _}
                <div class="skeleton h-24 w-full rounded-xl"></div>
              {/each}
            </div>
          {:else}
            <div class="space-y-3" role="list" aria-label="Objetos detectados para anotar">
              {#each selectedDetection.objects as obj (obj.id)}
                {@const key = String(obj.id ?? `new_${obj.label}`)}
                {@const state = objStates[key]}
                <article
                  class="card bg-base-100 shadow border-l-4
                    {state?.verdict === 'correct' ? 'border-success' :
                     state?.verdict === 'incorrect' ? 'border-error' :
                     state?.verdict === 'uncertain' ? 'border-warning' :
                     'border-base-200'}"
                  role="listitem"
                >
                  <div class="card-body py-4">
                    <div class="flex flex-wrap items-start gap-4">
                      <!-- Info del objeto -->
                      <div class="flex-1 min-w-0">
                        <div class="flex flex-wrap items-center gap-2 mb-1">
                          <span class="font-semibold">{obj.label}</span>
                          <span class="badge badge-outline badge-sm">{obj.category}</span>
                          <span class="text-xs {confidenceColor(obj.confidence)} font-mono">
                            {Math.round(obj.confidence * 100)}%
                          </span>
                        </div>
                        {#if obj.bbox}
                          <p class="text-xs text-base-content/40 font-mono">
                            bbox [{obj.bbox.map((v) => v.toFixed(3)).join(', ')}]
                          </p>
                        {/if}
                      </div>

                      <!-- Botones de veredicto -->
                      <div class="flex gap-2 flex-shrink-0" role="group" aria-label="Veredicto para {obj.label}">
                        <button
                          class="btn btn-sm min-h-[44px]
                            {state?.verdict === 'correct' ? 'btn-success' : 'btn-ghost border border-success/40 hover:btn-success'}"
                          on:click={() => setVerdict(key, 'correct')}
                          aria-pressed={state?.verdict === 'correct'}
                          title="Correcto"
                        >✓ Correcto</button>
                        <button
                          class="btn btn-sm min-h-[44px]
                            {state?.verdict === 'uncertain' ? 'btn-warning' : 'btn-ghost border border-warning/40 hover:btn-warning'}"
                          on:click={() => setVerdict(key, 'uncertain')}
                          aria-pressed={state?.verdict === 'uncertain'}
                          title="Incierto"
                        >? Incierto</button>
                        <button
                          class="btn btn-sm min-h-[44px]
                            {state?.verdict === 'incorrect' ? 'btn-error' : 'btn-ghost border border-error/40 hover:btn-error'}"
                          on:click={() => setVerdict(key, 'incorrect')}
                          aria-pressed={state?.verdict === 'incorrect'}
                          title="Incorrecto"
                        >✗ Incorrecto</button>
                      </div>
                    </div>

                    <!-- Campos adicionales cuando es incorrecto -->
                    {#if state?.verdict === 'incorrect'}
                      <div class="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div class="form-control">
                          <label class="label py-0.5" for="label-{key}">
                            <span class="label-text text-xs">Etiqueta correcta</span>
                          </label>
                          <input
                            id="label-{key}"
                            type="text"
                            class="input input-bordered input-sm"
                            placeholder="Ej: horse, building..."
                            bind:value={state.corrected_label}
                          />
                        </div>
                        <div class="form-control">
                          <label class="label py-0.5" for="notes-{key}">
                            <span class="label-text text-xs">Notas</span>
                          </label>
                          <input
                            id="notes-{key}"
                            type="text"
                            class="input input-bordered input-sm"
                            placeholder="Observación..."
                            bind:value={state.notes}
                          />
                        </div>
                      </div>
                    {:else if state?.verdict !== null}
                      <div class="mt-2">
                        <input
                          type="text"
                          class="input input-bordered input-xs w-full"
                          placeholder="Nota opcional..."
                          bind:value={state.notes}
                          aria-label="Nota para {obj.label}"
                        />
                      </div>
                    {/if}
                  </div>
                </article>
              {/each}
            </div>

            <!-- Instrucción sobre objetos no detectados -->
            <div class="alert alert-info text-sm" role="note">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>
                Si la IA no detectó un objeto que debería estar, registra la omisión desde la
                página de anotación de descripciones con una nota en la descripción de referencia.
              </span>
            </div>
          {/if}
        </div>
      {/if}
    </main>
  </div>
</div>
