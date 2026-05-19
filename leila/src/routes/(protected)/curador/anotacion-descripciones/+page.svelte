<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import { notificationsStore } from '$lib/stores/notifications';
  import { apiClient } from '$lib/services/apiClient';
  import {
    annotationService,
    type ExpertDescriptionAnnotation,
  } from '$lib/services/annotationService';

  const ALLOWED_ROLES = ['curador', 'administrador', 'mesa_evaluadora', 'investigador'];

  interface DetectionItem {
    id: number | null;
    photograph_id: number;
    scene_description: string;
    provider: string;
    object_count: number;
    status: string;
  }

  interface DetectionListResponse {
    total: number;
    skip: number;
    limit: number;
    detections: DetectionItem[];
  }

  // Estado
  let detections: DetectionItem[] = [];
  let loadingDetections = true;
  let detectionsError: string | null = null;

  // Mapa photograph_id → estado del formulario
  type FormState = {
    reference_description: string;
    ai_rating: number | null;
    notes: string;
    submitting: boolean;
    saved: boolean;
    existing: ExpertDescriptionAnnotation | null;
  };
  let forms: Record<number, FormState> = {};

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
      detections = res.detections.filter((d) => d.status === 'completed');

      // Inicializar formularios y cargar anotaciones existentes en paralelo
      for (const det of detections) {
        forms[det.photograph_id] = {
          reference_description: '',
          ai_rating: null,
          notes: '',
          submitting: false,
          saved: false,
          existing: null,
        };
      }
      forms = { ...forms };

      await Promise.allSettled(
        detections.map(async (det) => {
          try {
            const anns = await annotationService.getDescriptionAnnotations(det.photograph_id);
            if (anns.length > 0) {
              const latest = anns[anns.length - 1];
              forms[det.photograph_id] = {
                reference_description: latest.reference_description,
                ai_rating: latest.ai_rating,
                notes: latest.notes ?? '',
                submitting: false,
                saved: true,
                existing: latest,
              };
            }
          } catch {
            // sin anotación previa — ok
          }
        }),
      );
      forms = { ...forms };
    } catch (e: any) {
      detectionsError = e?.detail ?? 'No se pudieron cargar las detecciones';
    } finally {
      loadingDetections = false;
    }
  }

  async function submit(photographId: number) {
    const form = forms[photographId];
    if (!form || !form.reference_description.trim()) {
      notificationsStore.error('La descripción de referencia es obligatoria');
      return;
    }
    forms[photographId] = { ...form, submitting: true };

    try {
      const saved = await annotationService.annotateDescription(photographId, {
        ai_rating: form.ai_rating,
        reference_description: form.reference_description.trim(),
        notes: form.notes.trim() || null,
      });
      forms[photographId] = {
        ...forms[photographId],
        submitting: false,
        saved: true,
        existing: saved,
      };
      forms = { ...forms };
      notificationsStore.success('Descripción de referencia guardada');
    } catch (e: any) {
      forms[photographId] = { ...forms[photographId], submitting: false };
      forms = { ...forms };
      notificationsStore.error(e?.detail ?? 'Error al guardar');
    }
  }

  function ratingLabel(r: number | null): string {
    if (r === null) return 'Sin calificar';
    return ['', 'Muy mala', 'Mala', 'Aceptable', 'Buena', 'Excelente'][r] ?? '';
  }

  function ratingColor(r: number | null): string {
    if (!r) return 'text-base-content/40';
    if (r <= 2) return 'text-error';
    if (r === 3) return 'text-warning';
    return 'text-success';
  }
</script>

<svelte:head>
  <title>Anotación de descripciones · ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-4xl">
  <header class="mb-8">
    <a href="/curador" class="text-sm text-base-content/60 hover:text-base-content inline-flex items-center gap-1 mb-3 min-h-[44px]">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Panel de curación
    </a>
    <h1 class="text-3xl font-bold">Anotación de descripciones</h1>
    <p class="text-base-content/60 text-sm mt-1">
      Escribe la descripción de referencia (ground truth) para cada fotografía y evalúa la calidad de la descripción generada por IA (FONDEF ICa3, umbral 0.7).
    </p>
  </header>

  {#if loadingDetections}
    <div class="space-y-4" aria-busy="true" aria-label="Cargando fotografías">
      {#each Array(4) as _}
        <div class="card bg-base-100 shadow">
          <div class="card-body space-y-3">
            <div class="skeleton h-5 w-1/3 rounded"></div>
            <div class="skeleton h-16 w-full rounded"></div>
            <div class="skeleton h-24 w-full rounded"></div>
          </div>
        </div>
      {/each}
    </div>
  {:else if detectionsError}
    <div class="alert alert-error" role="alert">
      <span>{detectionsError}</span>
      <button class="btn btn-sm btn-ghost ml-auto" on:click={loadDetections}>Reintentar</button>
    </div>
  {:else if detections.length === 0}
    <div class="alert alert-warning" role="status">
      <span>
        No hay detecciones completadas.
        Ejecuta primero el análisis de objetos desde el
        <a href="/archivo" class="link font-medium">archivo</a>.
      </span>
    </div>
  {:else}
    <!-- Estadística rápida -->
    {@const annotated = Object.values(forms).filter((f) => f.saved).length}
    <div class="flex items-center gap-4 mb-6 text-sm">
      <span class="text-base-content/60">{detections.length} fotografías</span>
      <span class="badge badge-success">{annotated} anotadas</span>
      <span class="badge badge-ghost">{detections.length - annotated} pendientes</span>
    </div>

    <div class="space-y-5" role="list" aria-label="Fotografías para anotar">
      {#each detections as det (det.photograph_id)}
        {@const form = forms[det.photograph_id]}
        {#if form}
          <article
            class="card bg-base-100 shadow border-l-4
              {form.saved ? 'border-success' : 'border-base-200'}"
            role="listitem"
          >
            <div class="card-body">
              <!-- Cabecera -->
              <header class="flex flex-wrap items-start justify-between gap-3 mb-3">
                <div>
                  <h2 class="font-semibold">
                    Fotografía #{det.photograph_id}
                    {#if form.saved}
                      <span class="badge badge-success badge-sm ml-2">Anotada</span>
                    {/if}
                  </h2>
                  <p class="text-xs text-base-content/50 mt-0.5">
                    {det.object_count} objeto{det.object_count !== 1 ? 's' : ''} detectados · {det.provider}
                  </p>
                </div>
              </header>

              <!-- Descripción IA (referencia) -->
              {#if det.scene_description}
                <div class="p-3 bg-base-200 rounded-lg mb-4">
                  <p class="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-1">
                    Descripción generada por IA
                    <span class="badge badge-warning badge-xs ml-1">Verosímil</span>
                  </p>
                  <p class="text-sm text-base-content/80 leading-relaxed">{det.scene_description}</p>
                </div>
              {/if}

              <!-- Calificación de la IA -->
              <div class="mb-4">
                <p class="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-2">
                  Calidad de la descripción IA
                </p>
                <div class="flex flex-wrap gap-2" role="radiogroup" aria-label="Calificación de la descripción IA">
                  {#each [1, 2, 3, 4, 5] as rating}
                    <button
                      role="radio"
                      aria-checked={form.ai_rating === rating}
                      class="btn btn-sm min-h-[44px] w-11
                        {form.ai_rating === rating
                          ? rating <= 2 ? 'btn-error' : rating === 3 ? 'btn-warning' : 'btn-success'
                          : 'btn-ghost border border-base-300'}"
                      on:click={() => { forms[det.photograph_id] = { ...form, ai_rating: form.ai_rating === rating ? null : rating }; forms = { ...forms }; }}
                      title={ratingLabel(rating)}
                    >
                      {rating}
                    </button>
                  {/each}
                  <span class="text-sm self-center {ratingColor(form.ai_rating)}">
                    {ratingLabel(form.ai_rating)}
                  </span>
                </div>
              </div>

              <!-- Descripción de referencia -->
              <div class="form-control mb-3">
                <label class="label py-0.5" for="desc-{det.photograph_id}">
                  <span class="label-text text-xs font-semibold uppercase tracking-wider text-base-content/50">
                    Descripción de referencia (ground truth)
                    <span class="text-error ml-1">*</span>
                  </span>
                </label>
                <textarea
                  id="desc-{det.photograph_id}"
                  class="textarea textarea-bordered text-sm leading-relaxed"
                  rows="4"
                  placeholder="Describe con precisión qué se ve en la fotografía: objetos, personas, paisaje, época estimada, contexto histórico visible..."
                  bind:value={form.reference_description}
                  aria-required="true"
                ></textarea>
              </div>

              <!-- Notas -->
              <div class="form-control mb-4">
                <label class="label py-0.5" for="notes-{det.photograph_id}">
                  <span class="label-text text-xs text-base-content/50">Notas adicionales (opcional)</span>
                </label>
                <input
                  id="notes-{det.photograph_id}"
                  type="text"
                  class="input input-bordered input-sm"
                  placeholder="Observaciones sobre la calidad de la detección, contexto especial..."
                  bind:value={form.notes}
                />
              </div>

              <!-- Botón guardar -->
              <div class="flex justify-end">
                <button
                  class="btn btn-primary btn-sm min-h-[44px]"
                  disabled={form.submitting || !form.reference_description.trim()}
                  on:click={() => submit(det.photograph_id)}
                  aria-label="Guardar anotación para fotografía #{det.photograph_id}"
                >
                  {#if form.submitting}
                    <span class="loading loading-spinner loading-xs" aria-hidden="true"></span>
                    Guardando…
                  {:else if form.saved}
                    Actualizar anotación
                  {:else}
                    Guardar anotación
                  {/if}
                </button>
              </div>
            </div>
          </article>
        {/if}
      {/each}
    </div>
  {/if}
</div>
