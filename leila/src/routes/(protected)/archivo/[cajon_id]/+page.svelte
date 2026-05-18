<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { archiveService } from '$lib/services/archiveService';
  import { clusterService } from '$lib/services/clusterService';
  import { selection, selectedIds } from '$lib/stores/selection';
  import { notificationsStore } from '$lib/stores/notifications';
  import ImageCard from '$lib/components/viewer/ImageCard.svelte';
  import SelectionBar from '$lib/components/archive/SelectionBar.svelte';
  import ProjectPickerModal from '$lib/components/archive/ProjectPickerModal.svelte';
  import type { Box, Roll, Photograph, Image, Project } from '$lib/types';

  $: cajonId = Number($page.params.cajon_id);

  let box: Box | null = null;
  let rolls: Roll[] = [];
  let photos: Photograph[] = [];
  let loading = true;
  let error: string | null = null;
  let pickerOpen = false;
  let busy = false;

  onMount(async () => {
    try {
      const [boxRes, rollsRes] = await Promise.all([
        archiveService.getBox(cajonId),
        archiveService.listRolls(cajonId, { limit: 200 }),
      ]);
      box = boxRes;
      rolls = rollsRes.rolls;

      const allPhotos: Photograph[] = [];
      for (const roll of rolls) {
        const photoRes = await archiveService.listPhotographs(roll.id, { limit: 500 });
        allPhotos.push(...photoRes.photographs);
      }
      photos = allPhotos;
    } catch (e: any) {
      error = e?.detail || e?.message || 'No se pudo cargar el cajón';
    } finally {
      loading = false;
    }
  });

  function photographToImage(p: Photograph): Image {
    return {
      id: p.id,
      title: p.identifier || `Foto #${p.frame_number ?? p.id}`,
      file_path: '',
      author: 'Robert Gerstmann',
      tags: [],
      is_public: p.is_public,
      created_at: p.created_at,
      updated_at: p.created_at,
      metadata: {},
      year: p.internal_cronology ? parseInt(p.internal_cronology, 10) || undefined : undefined,
    };
  }

  function selectAllInBox() {
    selection.addMany(photos);
  }

  async function handleCluster() {
    busy = true;
    try {
      const ids = $selectedIds;
      const job = await clusterService.create({ photograph_ids: ids, algorithm: 'dbscan' });
      notificationsStore.success(`Agrupación generada (job #${job.id})`);
      if (job.id) goto(`/archivo/clusters/${job.id}`);
    } catch (e: any) {
      notificationsStore.error(e?.detail || e?.message || 'No se pudo agrupar');
    } finally {
      busy = false;
    }
  }

  async function handleTimeline() {
    const ids = $selectedIds;
    const params = new URLSearchParams();
    ids.forEach((id) => params.append('id', id.toString()));
    goto(`/archivo/timelines?${params.toString()}`);
  }

  function handleAttached(project: Project, added: number, skipped: number) {
    const msg =
      skipped > 0
        ? `${added} foto${added !== 1 ? 's' : ''} añadidas a "${project.name}" (${skipped} ya estaban)`
        : `${added} foto${added !== 1 ? 's' : ''} añadidas a "${project.name}"`;
    notificationsStore.success(msg);
    selection.clear();
  }
</script>

<svelte:head>
  <title>{box ? `Cajón ${box.box_number}` : 'Cajón'} · ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-7xl pb-32">
  <header class="mb-6">
    <a href="/archivo" class="text-sm text-base-content/60 hover:text-base-content inline-flex items-center gap-1 mb-3">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Volver al archivo
    </a>

    {#if box}
      <h1 class="text-3xl font-bold">{box.name || `Cajón ${box.box_number}`}</h1>
      <div class="flex flex-wrap items-center gap-3 text-sm text-base-content/60 mt-1">
        <span>Cajón #{box.box_number}</span>
        {#if box.location_in_archive}<span>·</span><span>{box.location_in_archive}</span>{/if}
        <span>·</span>
        <span>{rolls.length} rollo{rolls.length !== 1 ? 's' : ''}</span>
        <span>·</span>
        <span>{photos.length} fotografía{photos.length !== 1 ? 's' : ''}</span>
      </div>
    {/if}
  </header>

  {#if !loading && !error && photos.length > 0}
    <div class="flex justify-end mb-4">
      <button class="btn btn-sm btn-outline" on:click={selectAllInBox}>
        Seleccionar todas las del cajón
      </button>
    </div>
  {/if}

  {#if loading}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {#each Array(8) as _}
        <div class="card bg-base-100 shadow-md animate-pulse">
          <div class="aspect-[4/3] bg-base-300 rounded-t-2xl"></div>
          <div class="card-body p-4">
            <div class="h-5 bg-base-300 rounded w-3/4"></div>
            <div class="h-4 bg-base-300 rounded w-1/2 mt-2"></div>
          </div>
        </div>
      {/each}
    </div>
  {:else if error}
    <div class="alert alert-error">
      <span>{error}</span>
    </div>
  {:else if photos.length === 0}
    <div class="text-center py-16 text-base-content/60">
      <p>Este cajón aún no tiene fotografías digitalizadas.</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {#each photos as photograph (photograph.id)}
        <ImageCard
          image={photographToImage(photograph)}
          {photograph}
          selectable={true}
          onClick={() => selection.toggle(photograph)}
        />
      {/each}
    </div>
  {/if}
</div>

<SelectionBar
  onCluster={handleCluster}
  onTimeline={handleTimeline}
  onAddToProject={() => (pickerOpen = true)}
  {busy}
/>

<ProjectPickerModal
  open={pickerOpen}
  photographIds={$selectedIds}
  onClose={() => (pickerOpen = false)}
  onAttached={handleAttached}
/>
