<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore, isAuthenticated } from '$lib/stores/auth';
  import { notificationsStore } from '$lib/stores/notifications';
  import { contributionService } from '$lib/services';
  import type { Contribution, AttributeType } from '$lib/types';

  const REVIEWER_ROLES = ['curador', 'administrador', 'mesa_evaluadora'];

  let contributions: Contribution[] = [];
  let loading = true;
  let error: string | null = null;

  // Reject modal
  let rejectingId: number | null = null;
  let rejectReason = '';
  let submitting = false;

  // Filter
  let filterType: AttributeType | '' = '';

  $: filtered = filterType
    ? contributions.filter(c => c.attribute_type === filterType)
    : contributions;

  const ATTR_LABELS: Record<string, string> = {
    CHRONOLOGY: 'Cronología',
    GEOGRAPHIC: 'Geográfico',
    ENVIRONMENTAL: 'Ambiental',
    TAG: 'Etiqueta',
  };

  const FIELD_LABELS: Record<string, string> = {
    precise_date: 'Fecha exacta',
    date_from: 'Fecha desde',
    date_to: 'Fecha hasta',
    date_hypothesis: 'Hipótesis',
    verification_source: 'Fuente',
    methodology: 'Metodología',
    visual_evidence_notes: 'Evidencia visual',
    geographic_location: 'Ubicación',
    latitude: 'Latitud',
    longitude: 'Longitud',
    location_radius_km: 'Radio (km)',
    signage_found: 'Señalética',
    architectural_landmarks: 'Hitos',
    landscape_features: 'Paisaje',
    specific_typology: 'Tipología',
    conservation_state: 'Estado conservación',
    human_env_relationship: 'Rel. humano-ambiente',
    tag_name: 'Etiqueta',
    tag_category: 'Categoría de etiqueta',
    setting_type: 'Tipo de entorno',
  };

  onMount(async () => {
    if (!$isAuthenticated) {
      goto('/login');
      return;
    }
    const role = $authStore.user?.role ?? '';
    if (!REVIEWER_ROLES.includes(role)) {
      goto('/');
      return;
    }
    await loadPending();
  });

  async function loadPending() {
    loading = true; error = null;
    try {
      const resp = await contributionService.listPending({ limit: 200 });
      contributions = resp.contributions;
    } catch (e: any) {
      error = e.detail ?? 'No se pudo cargar la cola de revisión.';
    } finally {
      loading = false;
    }
  }

  async function approve(id: number) {
    submitting = true;
    try {
      await contributionService.approve(id);
      contributions = contributions.filter(c => c.id !== id);
      notificationsStore.success('Contribución aprobada.');
    } catch (e: any) {
      notificationsStore.error(e.detail ?? 'Error al aprobar.');
    } finally {
      submitting = false;
    }
  }

  function openReject(id: number) {
    rejectingId = id;
    rejectReason = '';
  }

  async function confirmReject() {
    if (!rejectingId) return;
    if (!rejectReason.trim()) {
      notificationsStore.error('Escribe el motivo del rechazo.');
      return;
    }
    submitting = true;
    try {
      await contributionService.reject(rejectingId, rejectReason.trim());
      contributions = contributions.filter(c => c.id !== rejectingId);
      notificationsStore.success('Contribución rechazada.');
      rejectingId = null;
    } catch (e: any) {
      notificationsStore.error(e.detail ?? 'Error al rechazar.');
    } finally {
      submitting = false;
    }
  }

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString('es-CL', {
      day: '2-digit', month: 'short', year: 'numeric',
    });
  }
</script>

<svelte:head>
  <title>Cola de revisión — ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-5xl">

  <!-- Header -->
  <div class="flex items-center justify-between mb-6 flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-bold">Cola de revisión</h1>
      <p class="text-base-content/60 text-sm mt-0.5">Contribuciones pendientes de aprobación</p>
    </div>
    <button class="btn btn-ghost btn-sm gap-2" on:click={loadPending} disabled={loading}>
      {#if loading}
        <span class="loading loading-spinner loading-xs"></span>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      {/if}
      Actualizar
    </button>
  </div>

  <!-- Error -->
  {#if error}
    <div class="alert alert-error mb-6">
      <span>{error}</span>
    </div>
  {/if}

  <!-- Filter bar -->
  {#if !loading && contributions.length > 0}
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        class="btn btn-sm {filterType === '' ? 'btn-primary' : 'btn-ghost'}"
        on:click={() => (filterType = '')}
      >
        Todos ({contributions.length})
      </button>
      {#each Object.entries(ATTR_LABELS) as [key, label]}
        {@const count = contributions.filter(c => c.attribute_type === key).length}
        {#if count > 0}
          <button
            class="btn btn-sm {filterType === key ? 'btn-primary' : 'btn-ghost'}"
            on:click={() => (filterType = key as AttributeType)}
          >
            {label} ({count})
          </button>
        {/if}
      {/each}
    </div>
  {/if}

  <!-- Loading -->
  {#if loading}
    <div class="flex justify-center py-20">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

  <!-- Empty -->
  {:else if filtered.length === 0}
    <div class="text-center py-20 text-base-content/40">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-lg font-semibold">
        {contributions.length === 0 ? 'No hay contribuciones pendientes' : 'No hay contribuciones de este tipo'}
      </p>
    </div>

  <!-- List -->
  {:else}
    <div class="space-y-4">
      {#each filtered as c (c.id)}
        <div class="card bg-base-100 border border-base-300 shadow-sm">
          <div class="card-body p-4">
            <div class="flex items-start justify-between gap-4 flex-wrap">
              <!-- Left: metadata -->
              <div class="flex-1 min-w-0">
                <div class="flex flex-wrap items-center gap-2 mb-2">
                  <span class="badge badge-primary badge-sm">{ATTR_LABELS[c.attribute_type] ?? c.attribute_type}</span>
                  <span class="badge badge-ghost badge-sm">{FIELD_LABELS[c.field_name] ?? c.field_name}</span>
                  <span class="text-xs text-base-content/40">Fotografía #{c.photograph_id}</span>
                </div>

                <p class="text-sm">
                  <span class="text-base-content/50">Valor propuesto: </span>
                  <strong class="break-all">{c.proposed_value}</strong>
                </p>

                {#if c.evidence_notes}
                  <p class="text-sm text-base-content/60 mt-1 italic">"{c.evidence_notes}"</p>
                {/if}

                <p class="text-xs text-base-content/40 mt-2">
                  Por usuario #{c.contributor_id} · {formatDate(c.created_at)}
                </p>
              </div>

              <!-- Right: actions -->
              <div class="flex gap-2 shrink-0">
                <button
                  class="btn btn-success btn-sm gap-1"
                  on:click={() => approve(c.id)}
                  disabled={submitting}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  Aprobar
                </button>
                <button
                  class="btn btn-error btn-sm btn-outline gap-1"
                  on:click={() => openReject(c.id)}
                  disabled={submitting}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Rechazar
                </button>
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Reject reason modal -->
{#if rejectingId !== null}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="modal modal-open" on:click|self={() => (rejectingId = null)}>
    <div class="modal-box">
      <button class="btn btn-sm btn-circle btn-ghost absolute right-3 top-3" on:click={() => (rejectingId = null)}>✕</button>
      <h3 class="text-lg font-bold mb-4">Motivo del rechazo</h3>
      <div class="form-control">
        <label class="label"><span class="label-text">Explicación para el colaborador</span></label>
        <textarea
          class="textarea textarea-bordered"
          rows="4"
          placeholder="Explica por qué se rechaza esta contribución..."
          bind:value={rejectReason}
        ></textarea>
      </div>
      <div class="modal-action">
        <button class="btn btn-ghost btn-sm" on:click={() => (rejectingId = null)}>Cancelar</button>
        <button class="btn btn-error btn-sm" on:click={confirmReject} disabled={submitting}>
          {#if submitting}
            <span class="loading loading-spinner loading-xs"></span>
          {/if}
          Confirmar rechazo
        </button>
      </div>
    </div>
  </div>
{/if}
