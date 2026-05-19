<script lang="ts">
  import { onMount } from 'svelte';
  import MapView from '$lib/components/maps/MapView.svelte';
  import { georeferenceService } from '$lib/services/georeferenceService';
  import type { PhotoPin } from '$lib/types';

  let allPins: PhotoPin[] = [];
  let loading = true;

  // ---------- State ----------
  let searchQuery = '';
  let yearFrom = 1900;
  let yearTo = 1970;
  let selectedTags: string[] = [];
  let selectedSource: 'all' | 'ai' | 'curator' | 'metadata' = 'all';
  let selectedPinId: number | null = null;
  let cardRefs: Record<number, HTMLElement> = {};

  onMount(async () => {
    try {
      const res = await georeferenceService.listPins();
      allPins = res.pins.map((p) => ({
        id: p.photograph_id,
        attribute_id: p.attribute_id,
        title: p.title,
        year: p.year,
        location: p.location,
        lat: p.lat,
        lng: p.lng,
        tags: [],
        source: p.source,
        validated: p.validated,
        confidence: p.confidence,
      }));
    } catch {
      // keep allPins empty
    } finally {
      loading = false;
    }
  });

  $: allTags = [...new Set(allPins.flatMap((p) => p.tags))].sort();

  $: filteredPins = allPins.filter((pin) => {
    const matchSearch =
      !searchQuery ||
      pin.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pin.location.toLowerCase().includes(searchQuery.toLowerCase());

    const matchYear =
      (pin.year === null) ||
      (pin.year >= yearFrom && pin.year <= yearTo);

    const matchTags =
      selectedTags.length === 0 || selectedTags.some((t) => pin.tags.includes(t));

    const matchSource = selectedSource === 'all' || pin.source === selectedSource;

    return matchSearch && matchYear && matchTags && matchSource;
  });

  function toggleTag(tag: string) {
    selectedTags = selectedTags.includes(tag)
      ? selectedTags.filter((t) => t !== tag)
      : [...selectedTags, tag];
  }

  function selectPin(pin: PhotoPin) {
    selectedPinId = pin.id;
    setTimeout(() => {
      cardRefs[pin.id]?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
  }

  function clearFilters() {
    searchQuery = '';
    yearFrom = 1900;
    yearTo = 1970;
    selectedTags = [];
    selectedSource = 'all';
    selectedPinId = null;
  }

  $: hasActiveFilters =
    searchQuery ||
    yearFrom !== 1900 ||
    yearTo !== 1970 ||
    selectedTags.length > 0 ||
    selectedSource !== 'all';

  function sourceLabel(source?: string) {
    if (source === 'curator') return 'Validado';
    if (source === 'ai') return 'Inferido IA';
    if (source === 'metadata') return 'Metadato';
    return '';
  }

  function sourceBadgeClass(source?: string, validated?: boolean) {
    if (validated || source === 'curator') return 'badge-success';
    if (source === 'ai') return 'badge-warning';
    return 'badge-ghost';
  }
</script>

<svelte:head>
  <title>Mapa del Archivo — ROGER</title>
  <meta name="description" content="Explora geográficamente la colección fotográfica histórica del archivo ROGER" />
</svelte:head>

<div style="height: calc(100svh - 148px);" class="flex flex-col md:flex-row overflow-hidden">
  <!-- ===== SIDEBAR ===== -->
  <aside
    class="w-full md:w-[420px] md:flex-shrink-0 max-h-48 md:max-h-none bg-base-100 border-b md:border-b-0 md:border-r border-base-content/10 flex flex-col overflow-y-auto md:overflow-hidden shadow-lg z-20"
  >
    <!-- Header -->
    <div class="px-4 pt-4 pb-3 border-b border-base-content/10 bg-base-100">
      <h1 class="text-lg font-bold leading-tight">Mapa del Archivo</h1>
      <p class="text-xs text-base-content/50 mt-0.5">Fotografías georreferenciadas del archivo</p>
    </div>

    <!-- Filtros -->
    <div class="px-4 py-3 border-b border-base-content/10 space-y-3 bg-base-100/80">
      <!-- Búsqueda -->
      <div class="join w-full">
        <input
          type="text"
          placeholder="Buscar lugar o fotografía..."
          class="input input-bordered input-sm join-item flex-1 focus:outline-primary"
          bind:value={searchQuery}
        />
        {#if searchQuery}
          <button class="btn btn-sm join-item btn-ghost" on:click={() => (searchQuery = '')} aria-label="Limpiar búsqueda">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        {/if}
      </div>

      <!-- Año -->
      <div>
        <span class="text-xs font-semibold text-base-content/60 uppercase tracking-wide">Período</span>
        <div class="flex items-center gap-2 mt-1.5">
          <input
            type="number"
            class="input input-bordered input-xs w-20 text-center"
            bind:value={yearFrom}
            min="1880"
            max={yearTo}
            aria-label="Año desde"
          />
          <span class="text-base-content/40 text-sm">—</span>
          <input
            type="number"
            class="input input-bordered input-xs w-20 text-center"
            bind:value={yearTo}
            min={yearFrom}
            max="1990"
            aria-label="Año hasta"
          />
        </div>
      </div>

      <!-- Fuente de datos -->
      <div>
        <span class="text-xs font-semibold text-base-content/60 uppercase tracking-wide">Fuente</span>
        <div class="flex flex-wrap gap-1.5 mt-1.5">
          {#each [['all', 'Todas'], ['ai', 'Inferido IA'], ['curator', 'Validado'], ['metadata', 'Metadato']] as [val, label]}
            <button
              class="badge badge-sm cursor-pointer transition-all"
              class:badge-primary={selectedSource === val}
              class:badge-outline={selectedSource !== val}
              on:click={() => (selectedSource = val as typeof selectedSource)}
            >
              {label}
            </button>
          {/each}
        </div>
      </div>

      <!-- Temas (si los hay) -->
      {#if allTags.length > 0}
        <div>
          <span class="text-xs font-semibold text-base-content/60 uppercase tracking-wide">Temas</span>
          <div class="flex flex-wrap gap-1.5 mt-1.5">
            {#each allTags.slice(0, 10) as tag}
              <button
                class="badge badge-sm cursor-pointer transition-all"
                class:badge-primary={selectedTags.includes(tag)}
                class:badge-outline={!selectedTags.includes(tag)}
                on:click={() => toggleTag(tag)}
              >
                {tag}
              </button>
            {/each}
          </div>
        </div>
      {/if}

      {#if hasActiveFilters}
        <button class="btn btn-ghost btn-xs w-full gap-1 text-error" on:click={clearFilters}>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          Limpiar filtros
        </button>
      {/if}
    </div>

    <!-- Contador -->
    <div class="px-4 py-2 bg-base-200/50 border-b border-base-content/10">
      {#if loading}
        <span class="text-xs text-base-content/60"><span class="loading loading-spinner loading-xs mr-1"></span>Cargando…</span>
      {:else}
        <span class="text-xs text-base-content/60">
          <span class="font-bold text-primary">{filteredPins.length}</span>
          {filteredPins.length === 1 ? 'fotografía encontrada' : 'fotografías encontradas'}
        </span>
      {/if}
    </div>

    <!-- Lista -->
    <div class="flex-1 overflow-y-auto">
      {#if loading}
        <div class="space-y-2 p-3">
          {#each Array(5) as _}<div class="skeleton h-16 rounded-lg"></div>{/each}
        </div>
      {:else if filteredPins.length === 0}
        <div class="flex flex-col items-center justify-center h-40 text-center px-6">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-base-content/20 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          <p class="text-sm font-semibold text-base-content/40">Sin resultados</p>
          <p class="text-xs text-base-content/30 mt-1">Prueba con otros filtros</p>
        </div>
      {:else}
        {#each filteredPins as pin (pin.id)}
          <button
            bind:this={cardRefs[pin.id]}
            class="w-full text-left px-4 py-3 border-b border-base-content/5 transition-all duration-150 hover:bg-base-200/60 group"
            class:bg-primary={selectedPinId === pin.id}
            class:text-primary-content={selectedPinId === pin.id}
            on:click={() => selectPin(pin)}
          >
            <div class="flex items-start gap-2.5">
              <div
                class="mt-1.5 w-2 h-2 rounded-full flex-shrink-0"
                class:bg-primary={selectedPinId !== pin.id}
                class:bg-white={selectedPinId === pin.id}
              ></div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-sm leading-tight truncate">{pin.title}</p>
                <p class="text-xs mt-0.5 {selectedPinId === pin.id ? 'text-primary-content/70' : 'text-base-content/50'}">
                  {pin.location}{pin.year ? ` · ${pin.year}` : ''}
                </p>
                <div class="flex flex-wrap gap-1 mt-1">
                  {#if pin.source}
                    <span class="badge badge-xs {sourceBadgeClass(pin.source, pin.validated)} {selectedPinId === pin.id ? 'opacity-80' : ''}">
                      {sourceLabel(pin.source)}
                    </span>
                  {/if}
                  {#each pin.tags.slice(0, 2) as tag}
                    <span class="text-[10px] px-1.5 py-0.5 rounded-full font-medium {selectedPinId === pin.id ? 'bg-white text-primary' : 'bg-base-200 text-base-content/70'}">
                      {tag}
                    </span>
                  {/each}
                </div>
              </div>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0 mt-1 opacity-0 group-hover:opacity-100 transition-opacity {selectedPinId === pin.id ? 'text-primary-content' : 'text-primary'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </button>
        {/each}
      {/if}
    </div>

    <!-- Footer -->
    <div class="px-4 py-2.5 border-t border-base-content/10 bg-base-200/50">
      <p class="text-[10px] text-base-content/35 text-center">
        {allPins.length > 0
          ? `${allPins.length} pin${allPins.length === 1 ? '' : 's'} en el archivo`
          : 'Conectando al archivo…'}
      </p>
    </div>
  </aside>

  <!-- ===== MAPA ===== -->
  <div class="flex-1 relative overflow-hidden">
    <MapView
      pins={filteredPins}
      selectedId={selectedPinId}
      on:select={(e) => selectPin(e.detail)}
    />

    <!-- Leyenda flotante -->
    <div class="absolute top-3 right-3 z-[500] bg-base-100/90 backdrop-blur-sm rounded-xl px-3 py-2 shadow-lg border border-base-content/10 text-xs space-y-1">
      <div class="flex items-center gap-2">
        <span class="badge badge-xs badge-success">Validado</span>
        <span class="text-base-content/60">curador confirmó</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="badge badge-xs badge-warning">Inferido IA</span>
        <span class="text-base-content/60">pendiente validación</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="badge badge-xs badge-ghost">Metadato</span>
        <span class="text-base-content/60">del archivo original</span>
      </div>
    </div>
  </div>
</div>
