<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import ImageGrid from '$lib/components/viewer/ImageGrid.svelte';
  import ImageViewer from '$lib/components/viewer/ImageViewer.svelte';
  import { imageService } from '$lib/services/imageService';
  import { archiveService } from '$lib/services/archiveService';
  import { narrativeService } from '$lib/services/narrativeService';
  import { notificationsStore } from '$lib/stores/notifications';
  import type { Image, Collection } from '$lib/types';

  const ITEMS_PER_PAGE = 24;

  let collectionId: number;
  let collection: Collection | null = null;
  let images: Image[] = [];
  let total = 0;
  let currentPage = 0;
  let loadingCollection = true;
  let loadingImages = true;
  let error: string | null = null;

  let showViewer = false;
  let currentImage: Image | null = null;
  let narratives: any[] = [];

  $: totalPages = Math.ceil(total / ITEMS_PER_PAGE);
  $: dateRange = collection
    ? [collection.date_range_from, collection.date_range_to].filter(Boolean).join(' – ')
    : '';

  onMount(async () => {
    collectionId = parseInt($page.params.id ?? '');
    if (!collectionId || isNaN(collectionId)) { goto('/colecciones'); return; }

    const imageId = $page.url.searchParams.get('image');

    await Promise.all([loadCollection(), loadImages()]);

    if (imageId) {
      try {
        const img = await imageService.getImage(parseInt(imageId));
        openViewer(img);
      } catch {
        // ignore — image may not belong to collection
      }
    }
  });

  async function loadCollection() {
    loadingCollection = true;
    try {
      collection = await archiveService.getCollection(collectionId);
    } catch (e: any) {
      error = e?.detail ?? 'Colección no encontrada.';
      notificationsStore.error(error!);
    } finally {
      loadingCollection = false;
    }
  }

  async function loadImages() {
    loadingImages = true;
    try {
      const res = await imageService.listImages({
        collection_id: collectionId,
        skip: currentPage * ITEMS_PER_PAGE,
        limit: ITEMS_PER_PAGE,
      });
      images = res.images;
      total = res.total;
    } catch (e: any) {
      notificationsStore.error('Error al cargar imágenes.');
    } finally {
      loadingImages = false;
    }
  }

  function openViewer(image: Image) {
    currentImage = image;
    showViewer = true;
    goto(`/colecciones/${collectionId}?image=${image.id}`, { replaceState: true });
    loadNarratives(image.id);
  }

  function closeViewer() {
    showViewer = false;
    currentImage = null;
    narratives = [];
    goto(`/colecciones/${collectionId}`, { replaceState: true });
  }

  async function loadNarratives(imageId: number) {
    try {
      const res = await narrativeService.getNarrativesForImage(imageId, true);
      narratives = res.narratives;
    } catch {
      narratives = [];
    }
  }

  async function changePage(delta: number) {
    currentPage += delta;
    await loadImages();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
</script>

<svelte:head>
  <title>{collection?.name ?? 'Colección'} · ROGER</title>
  {#if collection?.description}
    <meta name="description" content={collection.description} />
  {/if}
</svelte:head>

<div class="container mx-auto px-4 sm:px-6 py-8 space-y-6 max-w-6xl">

  <!-- Back link -->
  <a href="/colecciones" class="inline-flex items-center gap-1.5 text-sm text-base-content/60 hover:text-base-content transition-colors">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
    </svg>
    Todas las colecciones
  </a>

  <!-- Collection header -->
  {#if loadingCollection}
    <div class="space-y-3">
      <div class="skeleton h-10 w-2/3 rounded-lg"></div>
      <div class="skeleton h-5 w-1/3 rounded"></div>
      <div class="skeleton h-16 w-full rounded-lg"></div>
    </div>
  {:else if collection}
    <div class="space-y-2">
      <h1 class="text-3xl sm:text-4xl font-bold">{collection.name}</h1>

      <!-- Meta chips -->
      <div class="flex flex-wrap gap-2 text-sm">
        {#if collection.photographer_name}
          <span class="badge badge-ghost gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {collection.photographer_name}
          </span>
        {/if}
        {#if dateRange}
          <span class="badge badge-ghost">{dateRange}</span>
        {/if}
        {#if collection.origin_country}
          <span class="badge badge-ghost">{collection.origin_country}</span>
        {/if}
        <span class="badge badge-ghost">{total} fotografías</span>
      </div>

      {#if collection.description}
        <p class="text-base-content/70 text-sm leading-relaxed max-w-3xl">{collection.description}</p>
      {/if}

      {#if collection.license}
        <p class="text-xs text-base-content/40">{collection.license}</p>
      {/if}
    </div>

    <div class="divider my-2"></div>
  {:else if error}
    <div class="alert alert-error">
      <span>{error}</span>
      <a href="/colecciones" class="btn btn-sm btn-ghost">Volver</a>
    </div>
  {/if}

  <!-- Image grid -->
  <ImageGrid
    {images}
    loading={loadingImages}
    error={null}
    onImageClick={openViewer}
    onRetry={loadImages}
  />

  <!-- Pagination -->
  {#if !loadingImages && total > ITEMS_PER_PAGE}
    <div class="flex items-center justify-center gap-3">
      <button
        class="btn btn-sm"
        on:click={() => changePage(-1)}
        disabled={currentPage === 0}
      >
        Anterior
      </button>
      <span class="text-sm text-base-content/60">
        Página {currentPage + 1} de {totalPages}
      </span>
      <button
        class="btn btn-sm"
        on:click={() => changePage(1)}
        disabled={currentPage >= totalPages - 1}
      >
        Siguiente
      </button>
    </div>
  {/if}

</div>

{#if showViewer && currentImage}
  <ImageViewer
    image={currentImage}
    {narratives}
    on:close={closeViewer}
  />
{/if}
