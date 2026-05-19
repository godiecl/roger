<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import { notificationsStore } from '$lib/stores/notifications';
  import { narrativeService } from '$lib/services/narrativeService';
  import type { Narrative } from '$lib/types';

  const CURATOR_ROLES = ['curador', 'administrador'];
  const CONFIDENCE_BADGE: Record<string, string> = {
    high: 'badge-success',
    medium: 'badge-warning',
    low: 'badge-error',
  };
  const CONFIDENCE_LABEL: Record<string, string> = {
    high: 'Alta',
    medium: 'Media',
    low: 'Baja',
  };

  type Tab = 'all' | 'pending' | 'approved';

  let tab: Tab = 'pending';
  let narratives: Narrative[] = [];
  let total = 0;
  let loading = true;
  let submitting = false;
  let deletingId: number | null = null;
  let expandedId: number | null = null;
  let isCurator = false;

  $: filtered = narratives.filter((n) => {
    if (tab === 'pending') return !n.is_approved;
    if (tab === 'approved') return n.is_approved;
    return true;
  });

  $: pendingCount = narratives.filter((n) => !n.is_approved).length;
  $: approvedCount = narratives.filter((n) => n.is_approved).length;

  onMount(async () => {
    if (!$isAuthenticated) { goto('/login'); return; }
    const role = $authStore.user?.role ?? '';
    if (!CURATOR_ROLES.includes(role)) { goto('/curador'); return; }
    isCurator = true;
    await load();
  });

  async function load() {
    loading = true;
    try {
      const res = await narrativeService.listNarratives(0, 500, false);
      narratives = res.narratives;
      total = res.total;
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al cargar narrativas.');
    } finally {
      loading = false;
    }
  }

  async function approve(n: Narrative) {
    submitting = true;
    try {
      const updated = await narrativeService.approveNarrative(n.id, $authStore.user!.id);
      narratives = narratives.map((x) => (x.id === n.id ? updated : x));
      notificationsStore.success('Narrativa aprobada.');
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error.');
    } finally {
      submitting = false;
    }
  }

  async function unapprove(n: Narrative) {
    submitting = true;
    try {
      const updated = await narrativeService.unapproveNarrative(n.id);
      narratives = narratives.map((x) => (x.id === n.id ? updated : x));
      notificationsStore.success('Aprobación retirada.');
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error.');
    } finally {
      submitting = false;
    }
  }

  async function confirmDelete() {
    if (!deletingId) return;
    submitting = true;
    try {
      await narrativeService.deleteNarrative(deletingId);
      narratives = narratives.filter((n) => n.id !== deletingId);
      notificationsStore.success('Narrativa eliminada.');
      deletingId = null;
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error.');
    } finally {
      submitting = false;
    }
  }

  function fmt(iso: string) {
    return new Date(iso).toLocaleDateString('es-CL', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  function excerpt(text: string, maxLen = 200) {
    return text.length > maxLen ? text.slice(0, maxLen) + '…' : text;
  }
</script>

<svelte:head><title>Narrativas IA · ROGER</title></svelte:head>

<div class="container mx-auto px-4 py-8 max-w-5xl">
  <div class="flex items-center justify-between mb-6 flex-wrap gap-4">
    <div>
      <div class="flex items-center gap-2 mb-1">
        <a href="/curador" class="text-base-content/40 hover:text-base-content text-sm transition-colors">Curación</a>
        <span class="text-base-content/30">/</span>
        <span class="text-sm">Narrativas IA</span>
      </div>
      <h1 class="text-2xl font-bold">Narrativas IA</h1>
      <p class="text-base-content/60 text-sm mt-0.5">Revisión y aprobación de narrativas generadas por inteligencia artificial</p>
    </div>
    <button class="btn btn-ghost btn-sm" on:click={load} disabled={loading}>
      {#if loading}<span class="loading loading-spinner loading-xs"></span>{:else}Actualizar{/if}
    </button>
  </div>

  <!-- Tabs -->
  <div role="tablist" class="tabs tabs-boxed mb-6">
    <button role="tab" class="tab {tab === 'pending' ? 'tab-active' : ''}" on:click={() => (tab = 'pending')}>
      Pendientes
      {#if pendingCount > 0}<span class="badge badge-sm badge-warning ml-1">{pendingCount}</span>{/if}
    </button>
    <button role="tab" class="tab {tab === 'approved' ? 'tab-active' : ''}" on:click={() => (tab = 'approved')}>
      Aprobadas
      {#if approvedCount > 0}<span class="badge badge-sm badge-success ml-1">{approvedCount}</span>{/if}
    </button>
    <button role="tab" class="tab {tab === 'all' ? 'tab-active' : ''}" on:click={() => (tab = 'all')}>
      Todas ({total})
    </button>
  </div>

  {#if loading}
    <div class="space-y-3">
      {#each Array(4) as _}<div class="skeleton h-28 rounded-lg"></div>{/each}
    </div>
  {:else if filtered.length === 0}
    <div class="text-center py-16 text-base-content/40">
      <p class="text-lg font-semibold">
        {tab === 'pending' ? 'No hay narrativas pendientes de aprobación' : 'Sin narrativas en esta vista'}
      </p>
    </div>
  {:else}
    <div class="space-y-3">
      {#each filtered as n (n.id)}
        <div class="card bg-base-100 border {n.is_approved ? 'border-base-200' : 'border-warning/30'} shadow-sm">
          <div class="card-body p-4">
            <!-- Header row -->
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span class="text-xs text-base-content/50">Foto #{n.image_id}</span>
              <span class="badge badge-xs {CONFIDENCE_BADGE[n.confidence_level] ?? 'badge-ghost'}">
                {CONFIDENCE_LABEL[n.confidence_level] ?? n.confidence_level}
              </span>
              {#if n.trazabilidad}
                <span class="badge badge-xs {n.trazabilidad.primary_source_type === 'veraz' ? 'badge-info' : 'badge-ghost'}">
                  {n.trazabilidad.primary_source_type === 'veraz' ? 'VERAZ' : 'VEROSÍMIL'}
                </span>
                <span class="text-xs text-base-content/40">
                  {Math.round(n.trazabilidad.confidence_score * 100)}% confianza
                </span>
              {/if}
              {#if n.is_approved}
                <span class="badge badge-xs badge-success">aprobada</span>
              {:else}
                <span class="badge badge-xs badge-warning">pendiente</span>
              {/if}
              <span class="ml-auto text-xs text-base-content/40">{fmt(n.created_at)}</span>
            </div>

            <!-- Text -->
            <p class="text-sm leading-relaxed text-base-content/80">
              {expandedId === n.id ? n.text : excerpt(n.text)}
            </p>
            {#if n.text.length > 200}
              <button class="text-xs text-primary mt-1 text-left" on:click={() => (expandedId = expandedId === n.id ? null : n.id)}>
                {expandedId === n.id ? 'Ver menos' : 'Ver completo'}
              </button>
            {/if}

            <!-- Sources -->
            {#if n.trazabilidad?.sources?.length > 0}
              <div class="flex flex-wrap gap-1 mt-2">
                {#each n.trazabilidad.sources as src}
                  <span class="badge badge-xs badge-ghost" title={src.reference ?? ''}>
                    {src.source_type === 'veraz' ? '✓' : '~'} {src.text.slice(0, 40)}{src.text.length > 40 ? '…' : ''}
                  </span>
                {/each}
              </div>
            {/if}

            <!-- Actions -->
            <div class="flex gap-2 mt-3 flex-wrap">
              {#if !n.is_approved}
                <button class="btn btn-success btn-xs" on:click={() => approve(n)} disabled={submitting}>
                  Aprobar
                </button>
              {:else}
                <button class="btn btn-ghost btn-xs" on:click={() => unapprove(n)} disabled={submitting}>
                  Retirar aprobación
                </button>
              {/if}
              <a href="/colecciones?image={n.image_id}" target="_blank" class="btn btn-ghost btn-xs">
                Ver foto
              </a>
              <button class="btn btn-error btn-xs btn-outline ml-auto" on:click={() => (deletingId = n.id)} disabled={submitting}>
                Eliminar
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Delete confirm modal -->
{#if deletingId !== null}
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
  <div class="modal modal-open" on:click|self={() => (deletingId = null)}>
    <div class="modal-box">
      <button class="btn btn-sm btn-circle btn-ghost absolute right-3 top-3" on:click={() => (deletingId = null)}>✕</button>
      <h3 class="text-lg font-bold mb-2">Eliminar narrativa</h3>
      <p class="text-sm text-base-content/70">Esta acción es permanente y no se puede deshacer.</p>
      <div class="modal-action">
        <button class="btn btn-ghost btn-sm" on:click={() => (deletingId = null)}>Cancelar</button>
        <button class="btn btn-error btn-sm" on:click={confirmDelete} disabled={submitting}>
          {#if submitting}<span class="loading loading-spinner loading-xs"></span>{/if}
          Eliminar
        </button>
      </div>
    </div>
  </div>
{/if}
