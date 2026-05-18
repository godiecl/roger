<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import ImageGrid from '$lib/components/viewer/ImageGrid.svelte';
  import ImageViewer from '$lib/components/viewer/ImageViewer.svelte';
  import { imagesStore } from '$lib/stores/images';
  import { searchStore, hasActiveFilters } from '$lib/stores/search';
  import { searchService, imageService, narrativeService } from '$lib/services';
  import { notificationsStore } from '$lib/stores/notifications';
  import type { Image } from '$lib/types';

  let loading = true;
  let error: string | null = null;
  let showViewer = false;
  let currentImage: Image | null = null;
  let narratives: any[] = [];

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
    // Check if image ID in URL
    const imageId = $page.url.searchParams.get('image');
    if (imageId) {
      await loadAndShowImage(parseInt(imageId));
    }

    await loadImages();
  });

  async function loadImages() {
    try {
      loading = true;
      error = null;

      if ($hasActiveFilters) {
        // Use search API
        const response = await searchService.searchImages(
          $searchStore.filters,
          currentPage * itemsPerPage,
          itemsPerPage
        );
        imagesStore.setImages(response.images, response.total_count);
      } else {
        // Use regular list API
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
    } catch (e: any) {
      notificationsStore.error('Error al cargar imagen');
    }
  }

  function handleImageClick(image: Image) {
    currentImage = image;
    showViewer = true;
    loadNarratives(image.id);

    // Update URL
    goto(`/colecciones?image=${image.id}`, { replaceState: true });
  }

  function handleCloseViewer() {
    showViewer = false;
    currentImage = null;
    narratives = [];

    // Remove image from URL
    goto('/colecciones', { replaceState: true });
  }

  async function loadNarratives(imageId: number) {
    try {
      const response = await narrativeService.getNarrativesForImage(imageId, true);
      narratives = response.narratives;
    } catch (e: any) {
      console.error('Error loading narratives:', e);
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
</script>

<svelte:head>
  <title>Colecciones - ROGER</title>
  <meta name="description" content="Explora la colección completa de fotografías históricas" />
</svelte:head>

<div class="container mx-auto px-4 sm:px-6 py-8 space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <h1 class="text-4xl font-bold">Colecciones</h1>
    <div class="text-sm text-base-content/70">
      {$imagesStore.total} imágenes
    </div>
  </div>

  <!-- Search and Filters -->
  <div class="card bg-base-100 shadow-xl">
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
        <div class="form-control">
          <label class="label cursor-pointer">
            <div class="flex items-center gap-1.5">
              <span class="label-text">Búsqueda semántica (IA)</span>
              <div class="tooltip tooltip-right"
                data-tip="Modo normal: busca palabras exactas en títulos y etiquetas. Modo IA: entiende el significado de tu consulta y encuentra fotografías conceptualmente similares, aunque no compartan las mismas palabras. Ej: «personas trabajando bajo el sol» puede devolver fotos de faenas mineras.">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-base-content/40 cursor-help" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <input
              type="checkbox"
              class="toggle toggle-primary"
              bind:checked={semanticSearch}
            />
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
          <button class="btn btn-ghost" on:click={handleClearFilters}>
            Limpiar filtros
          </button>
        {/if}
        <button class="btn btn-primary" on:click={handleSearch}>
          Buscar
        </button>
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
      <button
        class="btn btn-sm"
        on:click={previousPage}
        disabled={currentPage === 0}
      >
        Anterior
      </button>

      <span class="text-sm">
        Página {currentPage + 1} de {totalPages}
      </span>

      <button
        class="btn btn-sm"
        on:click={nextPage}
        disabled={currentPage >= totalPages - 1}
      >
        Siguiente
      </button>
    </div>
  {/if}
</div>

<!-- Image Viewer Modal -->
{#if showViewer && currentImage}
  <ImageViewer
    image={currentImage}
    {narratives}
    on:close={handleCloseViewer}
  />
{/if}
