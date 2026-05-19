<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import ImageGrid from '$lib/components/viewer/ImageGrid.svelte';
  import ImageViewer from '$lib/components/viewer/ImageViewer.svelte';
  import { imagesStore } from '$lib/stores/images';
  import { searchStore, hasActiveFilters } from '$lib/stores/search';
  import { searchService, imageService, narrativeService } from '$lib/services';
  import { archiveService } from '$lib/services/archiveService';
  import { notificationsStore } from '$lib/stores/notifications';
  import type { Image, Collection } from '$lib/types';

  let loading = true;
  let error: string | null = null;
  let showViewer = false;
  let currentImage: Image | null = null;
  let narratives: any[] = [];

  let collections: Collection[] = [];
  let loadingCollections = true;

  // Search/filter state
  let searchQuery = '';
  let yearFrom: number | undefined;
  let yearTo: number | undefined;
  let selectedLocations: string[] = [];
  let selectedTags: string[] = [];
  let semanticSearch = false;

  // Pagination
  let currentPage = 0;
  let itemsPerPage = 20;

  $: images = $imagesStore.images;
  $: totalPages = Math.ceil($imagesStore.total / itemsPerPage);

  onMount(async () => {
    const imageId = $page.url.searchParams.get('image');
    if (imageId) await loadAndShowImage(parseInt(imageId));

    await Promise.all([loadCollections(), loadImages()]);
  });

  async function loadCollections() {
    loadingCollections = true;
    try {
      const res = await archiveService.listCollections({ limit: 50 });
      collections = res.collections;
    } catch {
      // non-critical — gallery still works
    } finally {
      loadingCollections = false;
    }
  }

  async function loadImages() {
    try {
      loading = true;
      error = null;

      if ($hasActiveFilters) {
        const response = await searchService.searchImages(
          $searchStore.filters,
          currentPage * itemsPerPage,
          itemsPerPage
        );
        imagesStore.setImages(response.images, response.total_count);
      } else {
        const response = await imageService.listImages({
          skip: currentPage * itemsPerPage,
          limit: itemsPerPage
        });
        imagesStore.setImages(response.images, response.total);
      }
    } catch (e: any) {
      error = e.detail || 'Error al cargar imágenes';
      notificationsStore.error('Error al cargar imágenes');
    } finally {
      loading = false;
    }
  }

  async function loadAndShowImage(imageId: number) {
    try {
      const image = await imageService.getImage(imageId);
      handleImageClick(image);
    } catch {
      notificationsStore.error('Error al cargar imagen');
    }
  }

  function handleImageClick(image: Image) {
    currentImage = image;
    showViewer = true;
    loadNarratives(image.id);
    goto(`/colecciones?image=${image.id}`, { replaceState: true });
  }

  function handleCloseViewer() {
    showViewer = false;
    currentImage = null;
    narratives = [];
    goto('/colecciones', { replaceState: true });
  }

  async function loadNarratives(imageId: number) {
    try {
      const response = await narrativeService.getNarrativesForImage(imageId, true);
      narratives = response.narratives;
    } catch {
      narratives = [];
    }
  }

  async function handleSearch() {
    searchStore.setFilters({
      query: searchQuery || undefined,
      year_from: yearFrom,
      year_to: yearTo,
      locations: selectedLocations.length > 0 ? selectedLocations : undefined,
      tags: selectedTags.length > 0 ? selectedTags : undefined,
      semantic: semanticSearch
    });
    currentPage = 0;
    await loadImages();
  }

  function handleClearFilters() {
    searchQuery = '';
    yearFrom = undefined;
    yearTo = undefined;
    selectedLocations = [];
    selectedTags = [];
    semanticSearch = false;
    searchStore.clearFilters();
    loadImages();
  }

  function nextPage() {
    if (currentPage < totalPages - 1) {
      currentPage++;
      loadImages();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  function previousPage() {
    if (currentPage > 0) {
      currentPage--;
      loadImages();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  function dateRange(c: Collection) {
    const parts = [c.date_range_from, c.date_range_to].filter(Boolean);
    return parts.length ? parts.join(' – ') : null;
  }
</script>

<svelte:head>
  <title>Colecciones · ROGER</title>
  <meta name="description" content="Explora las colecciones fotográficas históricas del archivo ROGER" />
</svelte:head>

<div class="container mx-auto px-4 sm:px-6 py-8 space-y-8">

  <!-- Header -->
  <div class="flex items-center justify-between">
    <h1 class="text-4xl font-bold">Colecciones</h1>
    <div class="text-sm text-base-content/50">{$imagesStore.total} fotografías</div>
  </div>

  <!-- Collection cards -->
  {#if loadingCollections}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each Array(3) as _}
        <div class="skeleton h-36 rounded-xl"></div>
      {/each}
    </div>
  {:else if collections.length > 0}
    <div>
      <h2 class="text-sm font-semibold text-base-content/50 uppercase tracking-wider mb-3">Fondos disponibles</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each collections as col (col.id)}
          <a
            href="/colecciones/{col.id}"
            class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group"
          >
            {#if col.cover_image_path}
              <figure class="h-32 overflow-hidden rounded-t-xl">
                <img
                  src={col.cover_image_path}
                  alt={col.name}
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </figure>
            {/if}
            <div class="card-body p-4 {col.cover_image_path ? '' : 'pt-5'}">
              <h3 class="font-semibold text-sm leading-tight group-hover:text-primary transition-colors">
                {col.name}
              </h3>
              <div class="flex flex-wrap gap-1 mt-1">
                {#if col.photographer_name}
                  <span class="badge badge-ghost badge-xs">{col.photographer_name}</span>
                {/if}
                {#if dateRange(col)}
                  <span class="badge badge-ghost badge-xs">{dateRange(col)}</span>
                {/if}
                {#if col.origin_country}
                  <span class="badge badge-ghost badge-xs">{col.origin_country}</span>
                {/if}
              </div>
              {#if col.description}
                <p class="text-xs text-base-content/55 mt-1 leading-relaxed line-clamp-2">{col.description}</p>
              {/if}
            </div>
          </a>
        {/each}
      </div>
    </div>
    <div class="divider text-xs text-base-content/40">Explorar todas las fotografías</div>
  {/if}

  <!-- Search and Filters -->
  <div class="card bg-base-100 shadow-sm border border-base-200">
    <div class="card-body">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Search -->
        <div class="form-control lg:col-span-2">
          <label class="label" for="search">
            <span class="label-text">Buscar</span>
          </label>
          <input
            id="search"
            type="text"
            placeholder="Título, descripción, ubicación..."
            class="input input-bordered"
            bind:value={searchQuery}
            on:keypress={(e) => e.key === 'Enter' && handleSearch()}
          />
        </div>

        <!-- Year From -->
        <div class="form-control">
          <label class="label" for="year-from">
            <span class="label-text">Desde año</span>
          </label>
          <input
            id="year-from"
            type="number"
            placeholder="1920"
            class="input input-bordered"
            bind:value={yearFrom}
            min="1800"
            max="2100"
          />
        </div>

        <!-- Year To -->
        <div class="form-control">
          <label class="label" for="year-to">
            <span class="label-text">Hasta año</span>
          </label>
          <input
            id="year-to"
            type="number"
            placeholder="1950"
            class="input input-bordered"
            bind:value={yearTo}
            min="1800"
            max="2100"
          />
        </div>

        <!-- Semantic Search Toggle -->
        <div class="form-control lg:col-span-2">
          <label class="label cursor-pointer">
            <div class="flex items-center gap-1.5">
              <span class="label-text">Búsqueda semántica (IA)</span>
              <div class="tooltip tooltip-right"
                data-tip="Modo normal: busca palabras exactas en títulos y etiquetas. Modo IA: entiende el significado de tu consulta y encuentra fotografías conceptualmente similares, aunque no compartan las mismas palabras.">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-base-content/40 cursor-help" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <input type="checkbox" class="toggle toggle-primary" bind:checked={semanticSearch} />
          </label>
          {#if semanticSearch}
            <p class="text-xs text-primary/70 mt-1 leading-relaxed">
              Describe lo que buscas con tus propias palabras. La IA encontrará fotografías conceptualmente similares.
            </p>
          {/if}
        </div>
      </div>

      <div class="card-actions justify-end mt-4">
        {#if $hasActiveFilters}
          <button class="btn btn-ghost" on:click={handleClearFilters}>Limpiar filtros</button>
        {/if}
        <button class="btn btn-primary" on:click={handleSearch}>Buscar</button>
      </div>
    </div>
  </div>

  <!-- Images Grid -->
  <ImageGrid
    {images}
    {loading}
    {error}
    onImageClick={handleImageClick}
    onRetry={loadImages}
  />

  <!-- Pagination -->
  {#if !loading && images.length > 0}
    <div class="flex items-center justify-center gap-2">
      <button class="btn btn-sm" on:click={previousPage} disabled={currentPage === 0}>Anterior</button>
      <span class="text-sm">Página {currentPage + 1} de {totalPages}</span>
      <button class="btn btn-sm" on:click={nextPage} disabled={currentPage >= totalPages - 1}>Siguiente</button>
    </div>
  {/if}

</div>

{#if showViewer && currentImage}
  <ImageViewer image={currentImage} {narratives} on:close={handleCloseViewer} />
{/if}
