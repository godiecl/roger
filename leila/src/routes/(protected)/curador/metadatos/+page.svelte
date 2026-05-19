<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import { notificationsStore } from '$lib/stores/notifications';
  import { metadataService, type PhotographMetadata, type AttributeRecord } from '$lib/services/metadataService';
  import { moderationService } from '$lib/services/moderationService';
  import { apiClient } from '$lib/services/apiClient';

  const REVIEWER_ROLES = ['curador', 'administrador', 'mesa_evaluadora'];

  // ── ISAD(G) ──────────────────────────────────────────────────────────────
  interface ISADGForm {
    reference_code:          string;
    level_of_description:    string;
    extent:                  string;
    archival_history:        string;
    scope_content:           string;
    access_conditions:       string;
    reproduction_conditions: string;
    language_material:       string;
  }
  const ISADG_LEVELS = ['', 'item', 'file', 'series', 'fonds'];
  let isadgForm: ISADGForm | null = null;
  let savingISADG = false;

  let photographId = '';
  let metadata: PhotographMetadata | null = null;
  let withPending: Array<{ photograph_id: number; pending_contributions: number }> = [];
  let loading = false;
  let loadingQueue = true;
  let includeSuperseded = false;
  let rejectingId: number | null = null;
  let rejectReason = '';
  let submitting = false;

  const ATTR_NAMES: Record<string, string> = {
    technical: 'Metadatos técnicos (01)',
    chronology: 'Cronología / Datación (02)',
    geographic: 'Referencia geográfica (03)',
    environmental: 'Contexto ambiental (04)',
  };

  const STATUS_BADGE: Record<string, string> = {
    active: 'badge-success',
    pending: 'badge-warning',
    superseded: 'badge-ghost',
  };

  onMount(async () => {
    if (!$isAuthenticated) { goto('/login'); return; }
    const role = $authStore.user?.role ?? '';
    if (!REVIEWER_ROLES.includes(role)) { goto('/'); return; }

    const qid = $page.url.searchParams.get('photo');
    if (qid) { photographId = qid; await search(); }

    try {
      withPending = await metadataService.listWithPending(0, 100);
    } finally {
      loadingQueue = false;
    }
  });

  async function search() {
    const id = parseInt(photographId);
    if (!id || id <= 0) { notificationsStore.error('Ingresa un ID válido.'); return; }
    loading = true;
    metadata = null;
    isadgForm = null;
    try {
      const [meta, photo] = await Promise.all([
        metadataService.getPhotographMetadata(id, includeSuperseded),
        apiClient.get<Record<string, unknown>>(`/archive/photographs/${id}`).catch(() => null),
      ]);
      metadata = meta;
      if (photo) {
        isadgForm = {
          reference_code:          (photo.reference_code          as string) ?? '',
          level_of_description:    (photo.level_of_description    as string) ?? '',
          extent:                  (photo.extent                  as string) ?? '',
          archival_history:        (photo.archival_history         as string) ?? '',
          scope_content:           (photo.scope_content           as string) ?? '',
          access_conditions:       (photo.access_conditions       as string) ?? '',
          reproduction_conditions: (photo.reproduction_conditions as string) ?? '',
          language_material:       (photo.language_material       as string) ?? '',
        };
      }
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al cargar metadatos.');
    } finally {
      loading = false;
    }
  }

  async function saveISADG() {
    const id = parseInt(photographId);
    if (!id || !isadgForm) return;
    savingISADG = true;
    try {
      const payload: Record<string, string | null> = {};
      (Object.keys(isadgForm) as (keyof ISADGForm)[]).forEach((k) => {
        payload[k] = (isadgForm![k] ?? '').trim() || null;
      });
      await apiClient.patch(`/archive/photographs/${id}`, payload);
      notificationsStore.success('Metadatos ISAD(G) guardados.');
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al guardar ISAD(G).');
    } finally {
      savingISADG = false;
    }
  }

  async function approveContribution(id: number) {
    submitting = true;
    try {
      await moderationService.approve(id);
      if (metadata) {
        metadata = {
          ...metadata,
          pending_contributions: metadata.pending_contributions.filter((c) => c.id !== id),
          pending_count: metadata.pending_count - 1,
        };
      }
      notificationsStore.success('Contribución aprobada.');
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error.');
    } finally { submitting = false; }
  }

  function openReject(id: number) { rejectingId = id; rejectReason = ''; }

  async function confirmReject() {
    if (!rejectingId) return;
    submitting = true;
    try {
      await moderationService.reject(rejectingId, rejectReason.trim() || undefined);
      if (metadata) {
        metadata = {
          ...metadata,
          pending_contributions: metadata.pending_contributions.filter((c) => c.id !== rejectingId),
          pending_count: metadata.pending_count - 1,
        };
      }
      notificationsStore.success('Rechazado.');
      rejectingId = null;
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error.');
    } finally { submitting = false; }
  }

  function formatValue(val: unknown): string {
    if (val === null || val === undefined) return '—';
    if (typeof val === 'boolean') return val ? 'Sí' : 'No';
    return String(val);
  }
</script>

<svelte:head><title>Auditoría de metadatos · ROGER</title></svelte:head>

<div class="container mx-auto px-4 py-8 max-w-5xl">
  <h1 class="text-2xl font-bold mb-1">Auditoría de metadatos</h1>
  <p class="text-base-content/60 text-sm mb-6">Vista completa de atributos taxonómicos por fotografía</p>

  <!-- Search bar -->
  <div class="card bg-base-100 border border-base-200 mb-6">
    <div class="card-body p-4">
      <div class="flex flex-wrap gap-3 items-end">
        <div class="form-control flex-1 min-w-[180px]">
          <label class="label pb-1" for="photo-id"><span class="label-text text-xs">ID de fotografía</span></label>
          <input id="photo-id" type="number" class="input input-bordered input-sm" placeholder="ej. 42"
            bind:value={photographId} on:keydown={(e) => e.key === 'Enter' && search()} />
        </div>
        <label class="flex items-center gap-2 text-sm cursor-pointer pb-1">
          <input type="checkbox" class="checkbox checkbox-sm" bind:checked={includeSuperseded} />
          Incluir historial
        </label>
        <button class="btn btn-primary btn-sm" on:click={search} disabled={loading}>
          {#if loading}<span class="loading loading-spinner loading-xs"></span>{/if}
          Buscar
        </button>
      </div>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Metadata detail -->
    <div class="lg:col-span-2 space-y-4">
      {#if loading}
        {#each Array(4) as _}
          <div class="skeleton h-24 rounded-lg"></div>
        {/each}

      {:else if metadata}
        <!-- Pending contributions first -->
        {#if metadata.pending_count > 0}
          <div class="card bg-warning/10 border border-warning/30">
            <div class="card-body p-4">
              <h2 class="font-semibold text-sm mb-3">
                Contribuciones pendientes ({metadata.pending_count})
              </h2>
              <div class="space-y-3">
                {#each metadata.pending_contributions as c (c.id)}
                  <div class="bg-base-100 rounded-lg p-3 border border-base-200">
                    <div class="flex items-start justify-between gap-2 flex-wrap">
                      <div>
                        <div class="flex flex-wrap gap-1 mb-1">
                          <span class="badge badge-warning badge-xs">{c.attribute_type}</span>
                          <span class="badge badge-ghost badge-xs">{c.field_name}</span>
                        </div>
                        <p class="text-sm"><strong>{c.proposed_value}</strong></p>
                        {#if c.evidence_notes}
                          <p class="text-xs text-base-content/60 italic mt-0.5">"{c.evidence_notes}"</p>
                        {/if}
                      </div>
                      <div class="flex gap-1 shrink-0">
                        <button class="btn btn-success btn-xs" on:click={() => approveContribution(c.id)} disabled={submitting}>Aprobar</button>
                        <button class="btn btn-error btn-xs btn-outline" on:click={() => openReject(c.id)} disabled={submitting}>Rechazar</button>
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            </div>
          </div>
        {/if}

        <!-- Taxonomy attributes -->
        {#each Object.entries(ATTR_NAMES) as [key, label]}
          {@const records = metadata[key as keyof PhotographMetadata] as AttributeRecord[]}
          <div class="card bg-base-100 border border-base-200">
            <div class="card-body p-4">
              <h2 class="font-semibold text-sm mb-3 flex items-center gap-2">
                {label}
                {#if records.length === 0}
                  <span class="badge badge-ghost badge-xs">Sin datos</span>
                {/if}
              </h2>

              {#if records.length > 0}
                <div class="space-y-3">
                  {#each records as rec (rec.id)}
                    <div class="border border-base-200 rounded-lg p-3 text-sm">
                      <div class="flex flex-wrap gap-2 mb-2 items-center">
                        <span class="badge badge-xs {STATUS_BADGE[rec.status] ?? 'badge-ghost'}">{rec.status}</span>
                        {#if rec.source_type}
                          <span class="badge badge-outline badge-xs">{rec.source_type}</span>
                        {/if}
                        {#if rec.analysis_provider}
                          <span class="text-xs text-base-content/40">{rec.analysis_provider}</span>
                        {/if}
                        {#if rec.confidence_level != null}
                          <span class="text-xs text-base-content/40">{Math.round(rec.confidence_level * 100)}% confianza</span>
                        {/if}
                      </div>
                      <dl class="grid grid-cols-2 gap-x-4 gap-y-1">
                        {#each Object.entries(rec.data) as [field, value]}
                          <dt class="text-base-content/50 text-xs">{field}</dt>
                          <dd class="text-xs break-all">{formatValue(value)}</dd>
                        {/each}
                      </dl>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
        {/each}

        <!-- ISAD(G) fields -->
        {#if isadgForm}
          <div class="card bg-base-100 border border-base-200">
            <div class="card-body p-4">
              <h2 class="font-semibold text-sm mb-3 flex items-center gap-2">
                Descripción archivística ISAD(G)
                <span class="badge badge-outline badge-xs">ISO 15489</span>
              </h2>

              <form on:submit|preventDefault={saveISADG} class="space-y-3" novalidate>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div class="form-control">
                    <label class="label py-0.5" for="isadg-ref"><span class="label-text text-xs">Código de referencia</span></label>
                    <input id="isadg-ref" type="text" class="input input-bordered input-xs"
                      placeholder="UCN/GER/001/001/0023" bind:value={isadgForm.reference_code} />
                  </div>
                  <div class="form-control">
                    <label class="label py-0.5" for="isadg-level"><span class="label-text text-xs">Nivel de descripción</span></label>
                    <select id="isadg-level" class="select select-bordered select-xs" bind:value={isadgForm.level_of_description}>
                      {#each ISADG_LEVELS as lvl}
                        <option value={lvl}>{lvl || '— sin especificar —'}</option>
                      {/each}
                    </select>
                  </div>
                </div>

                <div class="form-control">
                  <label class="label py-0.5" for="isadg-extent"><span class="label-text text-xs">Extensión y soporte</span></label>
                  <input id="isadg-extent" type="text" class="input input-bordered input-xs"
                    placeholder="1 fotografía; blanco y negro; 35mm" bind:value={isadgForm.extent} />
                </div>

                <div class="form-control">
                  <label class="label py-0.5" for="isadg-scope"><span class="label-text text-xs">Alcance y contenido</span></label>
                  <textarea id="isadg-scope" class="textarea textarea-bordered text-xs leading-relaxed" rows="2"
                    bind:value={isadgForm.scope_content}></textarea>
                </div>

                <div class="form-control">
                  <label class="label py-0.5" for="isadg-history"><span class="label-text text-xs">Historia archivística</span></label>
                  <textarea id="isadg-history" class="textarea textarea-bordered text-xs leading-relaxed" rows="2"
                    bind:value={isadgForm.archival_history}></textarea>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div class="form-control">
                    <label class="label py-0.5" for="isadg-access"><span class="label-text text-xs">Condiciones de acceso</span></label>
                    <input id="isadg-access" type="text" class="input input-bordered input-xs"
                      placeholder="Acceso libre" bind:value={isadgForm.access_conditions} />
                  </div>
                  <div class="form-control">
                    <label class="label py-0.5" for="isadg-repro"><span class="label-text text-xs">Condiciones de reproducción</span></label>
                    <input id="isadg-repro" type="text" class="input input-bordered input-xs"
                      placeholder="CC-BY / Reservados" bind:value={isadgForm.reproduction_conditions} />
                  </div>
                  <div class="form-control">
                    <label class="label py-0.5" for="isadg-lang"><span class="label-text text-xs">Idioma del material</span></label>
                    <input id="isadg-lang" type="text" class="input input-bordered input-xs"
                      placeholder="spa / deu" bind:value={isadgForm.language_material} />
                  </div>
                </div>

                <div class="flex justify-end pt-1">
                  <button type="submit" class="btn btn-sm btn-outline min-h-[36px]" disabled={savingISADG}>
                    {#if savingISADG}<span class="loading loading-spinner loading-xs" aria-hidden="true"></span>{/if}
                    Guardar ISAD(G)
                  </button>
                </div>
              </form>
            </div>
          </div>
        {/if}

      {:else}
        <div class="text-center py-16 text-base-content/30">
          <p>Ingresa un ID de fotografía para ver sus metadatos</p>
        </div>
      {/if}
    </div>

    <!-- Queue sidebar -->
    <div>
      <div class="card bg-base-100 border border-base-200 sticky top-4">
        <div class="card-body p-4">
          <h2 class="font-semibold text-sm mb-3">Fotos con pendientes</h2>
          {#if loadingQueue}
            <div class="space-y-2">
              {#each Array(5) as _}<div class="skeleton h-8 rounded"></div>{/each}
            </div>
          {:else if withPending.length === 0}
            <p class="text-xs text-base-content/40">Sin pendientes en cola</p>
          {:else}
            <ul class="space-y-1 max-h-96 overflow-y-auto">
              {#each withPending as item (item.photograph_id)}
                <li>
                  <button
                    class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm hover:bg-base-200 transition-colors
                      {metadata?.photograph_id === item.photograph_id ? 'bg-primary/10 text-primary font-medium' : ''}"
                    on:click={() => { photographId = String(item.photograph_id); search(); }}
                  >
                    <span>Foto #{item.photograph_id}</span>
                    <span class="badge badge-warning badge-xs">{item.pending_contributions}</span>
                  </button>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Reject modal -->
{#if rejectingId !== null}
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
  <div class="modal modal-open" on:click|self={() => (rejectingId = null)}>
    <div class="modal-box">
      <button class="btn btn-sm btn-circle btn-ghost absolute right-3 top-3" on:click={() => (rejectingId = null)}>✕</button>
      <h3 class="text-lg font-bold mb-4">Motivo del rechazo</h3>
      <div class="form-control">
        <label class="label" for="reject-reason"><span class="label-text">Explicación (opcional)</span></label>
        <textarea id="reject-reason" class="textarea textarea-bordered" rows="3"
          placeholder="Explica por qué se rechaza..." bind:value={rejectReason}></textarea>
      </div>
      <div class="modal-action">
        <button class="btn btn-ghost btn-sm" on:click={() => (rejectingId = null)}>Cancelar</button>
        <button class="btn btn-error btn-sm" on:click={confirmReject} disabled={submitting}>
          {#if submitting}<span class="loading loading-spinner loading-xs"></span>{/if}
          Confirmar rechazo
        </button>
      </div>
    </div>
  </div>
{/if}
