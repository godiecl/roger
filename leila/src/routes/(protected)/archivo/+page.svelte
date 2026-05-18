<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { archiveService } from '$lib/services/archiveService';
  import CajonCard from '$lib/components/archive/CajonCard.svelte';
  import type { Collection, Box } from '$lib/types';

  interface BoxWithCollection extends Box {
    collection_name?: string;
  }

  let collections: Collection[] = [];
  let boxes: BoxWithCollection[] = [];
  let loading = true;
  let error: string | null = null;
  let selectedCollectionId: number | 'all' = 'all';
  let search = '';

  onMount(async () => {
    try {
      const collectionsRes = await archiveService.listCollections({ limit: 100 });
      collections = collectionsRes.collections;

      const allBoxes: BoxWithCollection[] = [];
      for (const col of collections) {
        const boxRes = await archiveService.listBoxes(col.id, { limit: 200 });
        for (const b of boxRes.boxes) {
          allBoxes.push({ ...b, collection_name: col.name });
        }
      }
      boxes = allBoxes;
    } catch (e: any) {
      error = e?.detail || e?.message || 'No se pudo cargar el archivo';
    } finally {
      loading = false;
    }
  });

  $: filteredBoxes = boxes
    .filter((b) => selectedCollectionId === 'all' || b.collection_id === selectedCollectionId)
    .filter((b) => {
      if (!search.trim()) return true;
      const q = search.toLowerCase();
      return (
        (b.name?.toLowerCase().includes(q) ?? false) ||
        b.box_number.toString().includes(q) ||
        (b.collection_name?.toLowerCase().includes(q) ?? false)
      );
    });

  function openBox(box: Box) {
    goto(`/archivo/${box.id}`);
  }
</script>

<svelte:head>
  <title>Archivo · ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-7xl">
  <header class="mb-8">
    <h1 class="text-3xl font-bold">Archivo</h1>
    <p class="text-base-content/70 mt-1">
      Navega los cajones del archivo, selecciona fotografías y agrúpalas para análisis colaborativo.
    </p>
  </header>

  <div class="flex flex-col md:flex-row gap-3 mb-6">
    <div class="form-control flex-1">
      <input
        type="text"
        placeholder="Buscar cajón por número, nombre o colección…"
        class="input input-bordered w-full"
        bind:value={search}
      />
    </div>
    {#if collections.length > 1}
      <select class="select select-bordered" bind:value={selectedCollectionId}>
        <option value="all">Todas las colecciones</option>
        {#each collections as col}
          <option value={col.id}>{col.name}</option>
        {/each}
      </select>
    {/if}
  </div>

  {#if loading}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {#each Array(8) as _}
        <div class="card bg-base-100 shadow-md">
          <div class="card-body p-5 animate-pulse">
            <div class="w-12 h-12 rounded-lg bg-base-300"></div>
            <div class="h-5 bg-base-300 rounded mt-3 w-3/4"></div>
            <div class="h-4 bg-base-300 rounded mt-2 w-1/2"></div>
          </div>
        </div>
      {/each}
    </div>
  {:else if error}
    <div class="alert alert-error">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{error}</span>
    </div>
  {:else if filteredBoxes.length === 0}
    <div class="text-center py-16 text-base-content/60">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
      </svg>
      <p>{search ? 'No se encontraron cajones que coincidan con tu búsqueda.' : 'No hay cajones disponibles.'}</p>
    </div>
  {:else}
    <p class="text-sm text-base-content/60 mb-3">
      {filteredBoxes.length} {filteredBoxes.length === 1 ? 'cajón' : 'cajones'}
    </p>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {#each filteredBoxes as box (box.id)}
        <CajonCard
          {box}
          collectionName={collections.length > 1 ? box.collection_name : undefined}
          onClick={openBox}
        />
      {/each}
    </div>
  {/if}
</div>
