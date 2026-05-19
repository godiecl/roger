<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import { notificationsStore } from '$lib/stores/notifications';
  import { moderationService, type ContributionQueueItem, type ModerationStats, type PendingTag } from '$lib/services/moderationService';

  const REVIEWER_ROLES = ['curador', 'administrador', 'mesa_evaluadora'];
  const ATTR_LABELS: Record<string, string> = {
    chronology: 'Cronología',
    geographic: 'Geográfico',
    environmental: 'Ambiental',
    tag: 'Etiqueta',
  };
  const FIELD_LABELS: Record<string, string> = {
    precise_date: 'Fecha exacta', date_from: 'Desde', date_to: 'Hasta',
    date_hypothesis: 'Hipótesis', verification_source: 'Fuente',
    methodology: 'Metodología', visual_evidence_notes: 'Evidencia visual',
    geographic_location: 'Ubicación', latitude: 'Latitud', longitude: 'Longitud',
    location_radius_km: 'Radio km', signage_found: 'Señalética',
    architectural_landmarks: 'Hitos', landscape_features: 'Paisaje',
    specific_typology: 'Tipología', conservation_state: 'Conservación',
    human_env_relationship: 'Rel. humano-ambiente',
    tag_name: 'Etiqueta', tag_category: 'Categoría',
    setting_type: 'Tipo entorno',
  };

  type Tab = 'contributions' | 'tags';

  let tab: Tab = 'contributions';
  let stats: ModerationStats | null = null;
  let items: ContributionQueueItem[] = [];
  let tags: PendingTag[] = [];
  let total = 0;
  let totalTags = 0;
  let loading = true;
  let submitting = false;

  let filterType = '';
  let selected = new Set<number>();
  let rejectingId: number | null = null;
  let rejectReason = '';

  $: filteredItems = filterType ? items.filter((c) => c.attribute_type === filterType) : items;
  $: allSelected = filteredItems.length > 0 && filteredItems.every((c) => selected.has(c.id));

  onMount(async () => {
    if (!$isAuthenticated) { goto('/login'); return; }
    const role = $authStore.user?.role ?? '';
    if (!REVIEWER_ROLES.includes(role)) { goto('/'); return; }
    await loadAll();
  });

  async function loadAll() {
    loading = true;
    try {
      const [s, q, t] = await Promise.all([
        moderationService.getStats(),
        moderationService.getQueue({ limit: 200 }),
        moderationService.getPendingTags({ limit: 200 }),
      ]);
      stats = s;
      items = q.items;
      total = q.total;
      tags = t.items;
      totalTags = t.total;
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al cargar la cola.');
    } finally {
      loading = false;
    }
  }

  function toggleSelect(id: number) {
    if (selected.has(id)) selected.delete(id);
    else selected.add(id);
    selected = selected;
  }

  function toggleAll() {
    if (allSelected) filteredItems.forEach((c) => selected.delete(c.id));
    else filteredItems.forEach((c) => selected.add(c.id));
    selected = selected;
  }

  async function approveOne(id: number) {
    submitting = true;
    try {
      await moderationService.approve(id);
      items = items.filter((c) => c.id !== id);
      selected.delete(id);
      selected = selected;
      if (stats) stats = { ...stats, pending: stats.pending - 1, approved: stats.approved + 1 };
      notificationsStore.success('Aprobado.');
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
      items = items.filter((c) => c.id !== rejectingId);
      selected.delete(rejectingId);
      selected = selected;
      if (stats) stats = { ...stats, pending: stats.pending - 1, rejected: stats.rejected + 1 };
      notificationsStore.success('Rechazado.');
      rejectingId = null;
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error.');
    } finally { submitting = false; }
  }

  async function batchApprove() {
    if (selected.size === 0) return;
    submitting = true;
    try {
      const res = await moderationService.batchApprove([...selected]);
      notificationsStore.success(`${res.processed} aprobadas, ${res.failed} fallidas.`);
      await loadAll();
      selected = new Set();
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error en lote.');
    } finally { submitting = false; }
  }

  async function approveTag(id: number) {
    submitting = true;
    try {
      await moderationService.approveTag(id);
      tags = tags.filter((t) => t.photograph_tag_id !== id);
      if (stats) stats = { ...stats };
      notificationsStore.success('Tag aprobado.');
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error.');
    } finally { submitting = false; }
  }

  async function rejectTag(id: number) {
    submitting = true;
    try {
      await moderationService.rejectTag(id);
      tags = tags.filter((t) => t.photograph_tag_id !== id);
      notificationsStore.success('Tag eliminado.');
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error.');
    } finally { submitting = false; }
  }

  function fmt(iso: string) {
    return new Date(iso).toLocaleDateString('es-CL', { day: '2-digit', month: 'short', year: 'numeric' });
  }
</script>

<svelte:head><title>Moderación · ROGER</title></svelte:head>

<div class="container mx-auto px-4 py-8 max-w-5xl">
  <div class="flex items-center justify-between mb-6 flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-bold">Moderación</h1>
      <p class="text-base-content/60 text-sm mt-0.5">Cola de revisión — contribuciones y etiquetas IA</p>
    </div>
    <button class="btn btn-ghost btn-sm" on:click={loadAll} disabled={loading}>
      {#if loading}<span class="loading loading-spinner loading-xs"></span>{:else}Actualizar{/if}
    </button>
  </div>

  <!-- Stats -->
  {#if stats}
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      {#each [['Pendientes', stats.pending, 'warning'], ['Aprobadas', stats.approved, 'success'], ['Rechazadas', stats.rejected, 'error'], ['Total', stats.total, 'neutral']] as [label, val, color]}
        <div class="stat bg-base-100 border border-base-200 rounded-xl p-4">
          <div class="stat-title text-xs">{label}</div>
          <div class="stat-value text-2xl text-{color}">{val}</div>
        </div>
      {/each}
    </div>
  {:else if loading}
    <div class="grid grid-cols-4 gap-3 mb-6">
      {#each Array(4) as _}<div class="skeleton h-16 rounded-xl"></div>{/each}
    </div>
  {/if}

  <!-- Tabs -->
  <div role="tablist" class="tabs tabs-boxed mb-6">
    <button role="tab" class="tab {tab === 'contributions' ? 'tab-active' : ''}" on:click={() => (tab = 'contributions')}>
      Contribuciones {#if total > 0}<span class="badge badge-sm badge-warning ml-1">{total}</span>{/if}
    </button>
    <button role="tab" class="tab {tab === 'tags' ? 'tab-active' : ''}" on:click={() => (tab = 'tags')}>
      Tags IA {#if totalTags > 0}<span class="badge badge-sm badge-warning ml-1">{totalTags}</span>{/if}
    </button>
  </div>

  <!-- Contributions tab -->
  {#if tab === 'contributions'}
    {#if loading}
      <div class="space-y-3">
        {#each Array(4) as _}<div class="skeleton h-20 rounded-lg"></div>{/each}
      </div>
    {:else if items.length === 0}
      <div class="text-center py-16 text-base-content/40">
        <p class="text-lg font-semibold">No hay contribuciones pendientes</p>
      </div>
    {:else}
      <!-- Filter + batch bar -->
      <div class="flex flex-wrap items-center gap-2 mb-4">
        <button class="btn btn-sm {filterType === '' ? 'btn-primary' : 'btn-ghost'}" on:click={() => (filterType = '')}>
          Todos ({items.length})
        </button>
        {#each Object.entries(ATTR_LABELS) as [key, label]}
          {@const count = items.filter((c) => c.attribute_type === key).length}
          {#if count > 0}
            <button class="btn btn-sm {filterType === key ? 'btn-primary' : 'btn-ghost'}" on:click={() => (filterType = key)}>
              {label} ({count})
            </button>
          {/if}
        {/each}

        {#if selected.size > 0}
          <div class="ml-auto flex gap-2">
            <span class="text-sm text-base-content/60 self-center">{selected.size} seleccionadas</span>
            <button class="btn btn-success btn-sm" on:click={batchApprove} disabled={submitting}>
              Aprobar selección
            </button>
          </div>
        {/if}
      </div>

      <!-- Select all -->
      <label class="flex items-center gap-2 text-sm mb-3 cursor-pointer">
        <input type="checkbox" class="checkbox checkbox-sm" checked={allSelected} on:change={toggleAll} />
        Seleccionar todos
      </label>

      <div class="space-y-3">
        {#each filteredItems as c (c.id)}
          <div class="card bg-base-100 border border-base-300 shadow-sm">
            <div class="card-body p-4">
              <div class="flex items-start gap-3">
                <input type="checkbox" class="checkbox checkbox-sm mt-1 shrink-0"
                  checked={selected.has(c.id)} on:change={() => toggleSelect(c.id)} />

                <div class="flex-1 min-w-0">
                  <div class="flex flex-wrap items-center gap-2 mb-1">
                    <span class="badge badge-primary badge-sm">{ATTR_LABELS[c.attribute_type] ?? c.attribute_type}</span>
                    <span class="badge badge-ghost badge-sm">{FIELD_LABELS[c.field_name] ?? c.field_name}</span>
                    <span class="text-xs text-base-content/40">Foto #{c.photograph_id}</span>
                  </div>
                  <p class="text-sm"><span class="text-base-content/50">Propuesto: </span><strong class="break-all">{c.proposed_value}</strong></p>
                  {#if c.evidence_notes}
                    <p class="text-xs text-base-content/60 mt-1 italic">"{c.evidence_notes}"</p>
                  {/if}
                  <p class="text-xs text-base-content/40 mt-1">Usuario #{c.contributor_id} · {fmt(c.created_at)}</p>
                </div>

                <div class="flex gap-2 shrink-0">
                  <button class="btn btn-success btn-xs" on:click={() => approveOne(c.id)} disabled={submitting}>Aprobar</button>
                  <button class="btn btn-error btn-xs btn-outline" on:click={() => openReject(c.id)} disabled={submitting}>Rechazar</button>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}

  <!-- Tags tab -->
  {:else}
    {#if loading}
      <div class="space-y-3">
        {#each Array(4) as _}<div class="skeleton h-16 rounded-lg"></div>{/each}
      </div>
    {:else if tags.length === 0}
      <div class="text-center py-16 text-base-content/40">
        <p class="text-lg font-semibold">No hay tags IA pendientes</p>
      </div>
    {:else}
      <div class="space-y-3">
        {#each tags as tag (tag.photograph_tag_id)}
          <div class="card bg-base-100 border border-base-300 shadow-sm">
            <div class="card-body p-4">
              <div class="flex items-center justify-between gap-4 flex-wrap">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="badge badge-accent badge-sm">{tag.tag_category}</span>
                  <span class="font-medium text-sm">{tag.tag_name}</span>
                  <span class="text-xs text-base-content/40">Foto #{tag.photograph_id}</span>
                  {#if tag.confidence != null}
                    <span class="text-xs text-base-content/50">confianza {Math.round(tag.confidence * 100)}%</span>
                  {/if}
                </div>
                <div class="flex gap-2 shrink-0">
                  <button class="btn btn-success btn-xs" on:click={() => approveTag(tag.photograph_tag_id)} disabled={submitting}>Aprobar</button>
                  <button class="btn btn-error btn-xs btn-outline" on:click={() => rejectTag(tag.photograph_tag_id)} disabled={submitting}>Rechazar</button>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
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
