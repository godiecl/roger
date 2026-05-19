<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import { notificationsStore } from '$lib/stores/notifications';
  import { georeferenceService, type GeoPin } from '$lib/services/georeferenceService';

  const CURATOR_ROLES = ['curador', 'administrador'];

  let pins: GeoPin[] = [];
  let loading = true;
  let submitting = false;
  let batchInferring = false;
  let deletingPin: GeoPin | null = null;

  $: validated = pins.filter((p) => p.validated);
  $: pending = pins.filter((p) => !p.validated && p.source === 'ai');
  $: fromMetadata = pins.filter((p) => p.source === 'metadata');

  onMount(async () => {
    if (!$isAuthenticated) { goto('/login'); return; }
    const role = $authStore.user?.role ?? '';
    if (!CURATOR_ROLES.includes(role)) { goto('/curador'); return; }
    await loadPins();
  });

  async function loadPins() {
    loading = true;
    try {
      const res = await georeferenceService.listPins();
      pins = res.pins;
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al cargar pins.');
    } finally {
      loading = false;
    }
  }

  async function validate(pin: GeoPin) {
    submitting = true;
    try {
      await georeferenceService.validateGeoreference(pin.photograph_id);
      notificationsStore.success('Referencia validada.');
      await loadPins();
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al validar.');
    } finally {
      submitting = false;
    }
  }

  async function confirmDelete() {
    if (!deletingPin) return;
    submitting = true;
    try {
      await georeferenceService.deleteGeoreference(deletingPin.attribute_id);
      notificationsStore.success('Referencia eliminada.');
      deletingPin = null;
      await loadPins();
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al eliminar.');
    } finally {
      submitting = false;
    }
  }

  async function runBatchInfer() {
    batchInferring = true;
    try {
      const result = await georeferenceService.batchInfer();
      notificationsStore.success(`Inferencia completada: ${result.inferred} coordenadas inferidas, ${result.errors} errores.`);
      await loadPins();
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error en inferencia masiva.');
    } finally {
      batchInferring = false;
    }
  }

  function sourceLabel(p: GeoPin) {
    if (p.validated || p.source === 'curator') return 'Validado';
    if (p.source === 'ai') return 'Inferido IA';
    return 'Metadato';
  }

  function sourceBadge(p: GeoPin) {
    if (p.validated || p.source === 'curator') return 'badge-success';
    if (p.source === 'ai') return 'badge-warning';
    return 'badge-ghost';
  }
</script>

<svelte:head><title>Georeferencia · ROGER</title></svelte:head>

<div class="container mx-auto px-4 py-8 max-w-5xl">
  <div class="flex items-center justify-between mb-6 flex-wrap gap-4">
    <div>
      <div class="flex items-center gap-2 mb-1">
        <a href="/curador" class="text-base-content/40 hover:text-base-content text-sm transition-colors">Curación</a>
        <span class="text-base-content/30">/</span>
        <span class="text-sm">Georeferencia</span>
      </div>
      <h1 class="text-2xl font-bold">Georeferencia</h1>
      <p class="text-base-content/60 text-sm mt-0.5">Gestión de coordenadas geográficas de las fotografías</p>
    </div>
    <div class="flex gap-2">
      <button
        class="btn btn-outline btn-sm"
        on:click={runBatchInfer}
        disabled={batchInferring}
        title="Infiere coordenadas con IA para las fotografías sin coordenadas"
      >
        {#if batchInferring}
          <span class="loading loading-spinner loading-xs"></span>
          Inferiendo…
        {:else}
          Inferir coordenadas IA
        {/if}
      </button>
      <button class="btn btn-ghost btn-sm" on:click={loadPins} disabled={loading}>
        {#if loading}<span class="loading loading-spinner loading-xs"></span>{:else}Actualizar{/if}
      </button>
    </div>
  </div>

  <!-- Stats -->
  <div class="grid grid-cols-3 gap-4 mb-6">
    <div class="stat bg-base-100 border border-base-200 rounded-xl py-3 px-4">
      <div class="stat-title text-xs">Total con coords</div>
      <div class="stat-value text-2xl">{pins.length}</div>
    </div>
    <div class="stat bg-base-100 border border-base-200 rounded-xl py-3 px-4">
      <div class="stat-title text-xs">Validados</div>
      <div class="stat-value text-2xl text-success">{validated.length}</div>
    </div>
    <div class="stat bg-base-100 border border-base-200 rounded-xl py-3 px-4">
      <div class="stat-title text-xs">Pendientes validación</div>
      <div class="stat-value text-2xl text-warning">{pending.length}</div>
    </div>
  </div>

  {#if loading}
    <div class="space-y-3">
      {#each Array(5) as _}<div class="skeleton h-20 rounded-lg"></div>{/each}
    </div>
  {:else if pins.length === 0}
    <div class="text-center py-20 text-base-content/40">
      <p class="text-lg font-semibold">Sin coordenadas en el archivo</p>
      <p class="text-sm mt-2">Usa "Inferir coordenadas IA" para generar pins desde las descripciones de ubicación.</p>
    </div>
  {:else}
    <div class="space-y-2">
      {#each pins as pin (pin.attribute_id)}
        <div class="card bg-base-100 border {pin.validated ? 'border-success/30' : pin.source === 'ai' ? 'border-warning/30' : 'border-base-200'} shadow-sm">
          <div class="card-body p-4">
            <div class="flex flex-wrap items-center gap-2">
              <span class="font-semibold text-sm truncate max-w-xs">{pin.title}</span>
              <span class="badge badge-xs {sourceBadge(pin)}">{sourceLabel(pin)}</span>
              {#if pin.confidence !== null && pin.confidence !== undefined}
                <span class="text-xs text-base-content/40">{Math.round(pin.confidence * 100)}% conf.</span>
              {/if}
              <span class="ml-auto text-xs text-base-content/40">
                {pin.year ?? '—'} · {pin.location}
              </span>
            </div>
            <div class="text-xs text-base-content/50 mt-1">
              {pin.lat.toFixed(4)}, {pin.lng.toFixed(4)}
            </div>
            <div class="flex gap-2 mt-2 flex-wrap">
              {#if !pin.validated && pin.source !== 'curator'}
                <button
                  class="btn btn-success btn-xs"
                  on:click={() => validate(pin)}
                  disabled={submitting}
                >
                  Validar
                </button>
              {:else}
                <span class="badge badge-xs badge-success gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                  </svg>
                  Ya fue validada
                </span>
              {/if}
              <a href="/colecciones?image={pin.photograph_id}" target="_blank" class="btn btn-ghost btn-xs">
                Ver foto
              </a>
              <button
                class="btn btn-error btn-xs btn-outline ml-auto"
                on:click={() => (deletingPin = pin)}
                disabled={submitting}
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Delete modal -->
{#if deletingPin !== null}
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
  <div class="modal modal-open" on:click|self={() => (deletingPin = null)}>
    <div class="modal-box">
      <button class="btn btn-sm btn-circle btn-ghost absolute right-3 top-3" on:click={() => (deletingPin = null)}>✕</button>
      <h3 class="text-lg font-bold mb-2">Eliminar referencia geográfica</h3>
      <p class="text-sm text-base-content/70 mb-1">
        <span class="font-semibold">{deletingPin.title}</span>
        {#if deletingPin.validated}<span class="badge badge-xs badge-success ml-1">validada</span>{/if}
      </p>
      <p class="text-sm text-base-content/70">Esta acción supersede el registro. La fotografía quedará sin coordenadas en el mapa.</p>
      <div class="modal-action">
        <button class="btn btn-ghost btn-sm" on:click={() => (deletingPin = null)}>Cancelar</button>
        <button class="btn btn-error btn-sm" on:click={confirmDelete} disabled={submitting}>
          {#if submitting}<span class="loading loading-spinner loading-xs"></span>{/if}
          Eliminar
        </button>
      </div>
    </div>
  </div>
{/if}
