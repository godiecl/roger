<script lang="ts">
  import MapView from '$lib/components/maps/MapView.svelte';
  import type { PhotoPin } from '$lib/types';

  // ---------------------------------------------------------------------------
  // Datos de ejemplo — cuando el backend agregue lat/lng a las fotografías,
  // reemplazar esta lista con una llamada a imageService.listImages()
  // y mapear Image[] → PhotoPin[] usando la tabla de coordenadas por ubicación.
  // ---------------------------------------------------------------------------
  const allPins: PhotoPin[] = [
    {
      id: 1,
      title: 'Puerto de Antofagasta',
      year: 1928,
      location: 'Antofagasta',
      region: 'Región de Antofagasta',
      lat: -23.6509,
      lng: -70.3975,
      tags: ['Puerto', 'Ciudad', 'Comercio']
    },
    {
      id: 2,
      title: 'Faena en Chuquicamata',
      year: 1930,
      location: 'Calama',
      region: 'Región de Antofagasta',
      lat: -22.4569,
      lng: -68.9296,
      tags: ['Minería', 'Industria', 'Trabajadores']
    },
    {
      id: 3,
      title: 'Paisaje del desierto de Atacama',
      year: 1926,
      location: 'Norte Grande',
      region: 'Región de Atacama',
      lat: -24.5,
      lng: -69.0,
      tags: ['Desierto', 'Paisaje', 'Naturaleza']
    },
    {
      id: 4,
      title: 'Vista panorámica de Arica',
      year: 1925,
      location: 'Arica',
      region: 'Región de Arica y Parinacota',
      lat: -18.4783,
      lng: -70.3126,
      tags: ['Ciudad', 'Puerto', 'Norte']
    },
    {
      id: 5,
      title: 'Playa Cavancha, Iquique',
      year: 1927,
      location: 'Iquique',
      region: 'Región de Tarapacá',
      lat: -20.2139,
      lng: -70.1522,
      tags: ['Playa', 'Ciudad', 'Recreación']
    },
    {
      id: 6,
      title: 'Minería del cobre, Copiapó',
      year: 1932,
      location: 'Copiapó',
      region: 'Región de Atacama',
      lat: -27.3668,
      lng: -70.3321,
      tags: ['Minería', 'Cobre', 'Industria']
    },
    {
      id: 7,
      title: 'Plaza de Armas de La Serena',
      year: 1934,
      location: 'La Serena',
      region: 'Región de Coquimbo',
      lat: -29.9027,
      lng: -71.2519,
      tags: ['Ciudad', 'Arquitectura', 'Plaza']
    },
    {
      id: 8,
      title: 'El puerto de Valparaíso',
      year: 1935,
      location: 'Valparaíso',
      region: 'Región de Valparaíso',
      lat: -33.0472,
      lng: -71.6127,
      tags: ['Puerto', 'Ciudad', 'Barcos']
    },
    {
      id: 9,
      title: 'Cerros y funiculares, Valparaíso',
      year: 1936,
      location: 'Valparaíso',
      region: 'Región de Valparaíso',
      lat: -33.0558,
      lng: -71.6197,
      tags: ['Arquitectura', 'Funicular', 'Cerros']
    },
    {
      id: 10,
      title: 'La Alameda, Santiago',
      year: 1938,
      location: 'Santiago',
      region: 'Región Metropolitana',
      lat: -33.4489,
      lng: -70.6693,
      tags: ['Ciudad', 'Alameda', 'Vida urbana']
    },
    {
      id: 11,
      title: 'Mercado Central, Santiago',
      year: 1940,
      location: 'Santiago',
      region: 'Región Metropolitana',
      lat: -33.4384,
      lng: -70.6511,
      tags: ['Mercado', 'Vida cotidiana', 'Ciudad']
    },
    {
      id: 12,
      title: 'Balneario de Viña del Mar',
      year: 1937,
      location: 'Viña del Mar',
      region: 'Región de Valparaíso',
      lat: -33.0245,
      lng: -71.5518,
      tags: ['Playa', 'Balneario', 'Veraneo']
    },
    {
      id: 13,
      title: 'El Teniente, mina de cobre',
      year: 1942,
      location: 'Rancagua',
      region: "Región de O'Higgins",
      lat: -34.1703,
      lng: -70.7444,
      tags: ['Minería', 'Cobre', 'Industria']
    },
    {
      id: 14,
      title: 'Vendimia en el Valle del Maule',
      year: 1944,
      location: 'Talca',
      region: 'Región del Maule',
      lat: -35.4264,
      lng: -71.6553,
      tags: ['Vendimia', 'Campo', 'Vino']
    },
    {
      id: 15,
      title: 'Puerto de Concepción',
      year: 1945,
      location: 'Concepción',
      region: 'Región del Biobío',
      lat: -36.8201,
      lng: -73.0444,
      tags: ['Industria', 'Ciudad', 'Puerto']
    },
    {
      id: 16,
      title: 'Feria de Temuco',
      year: 1946,
      location: 'Temuco',
      region: 'Región de La Araucanía',
      lat: -38.7359,
      lng: -72.5904,
      tags: ['Mercado', 'Vida cotidiana', 'Araucanía']
    },
    {
      id: 17,
      title: 'Astilleros del río Valdivia',
      year: 1948,
      location: 'Valdivia',
      region: 'Región de Los Ríos',
      lat: -39.8142,
      lng: -73.2459,
      tags: ['Río', 'Industria', 'Astilleros']
    },
    {
      id: 18,
      title: 'Lago Llanquihue, Puerto Montt',
      year: 1950,
      location: 'Puerto Montt',
      region: 'Región de Los Lagos',
      lat: -41.4693,
      lng: -72.9424,
      tags: ['Lago', 'Naturaleza', 'Paisaje']
    },
    {
      id: 19,
      title: 'Iglesias de madera de Chiloé',
      year: 1951,
      location: 'Castro',
      region: 'Región de Los Lagos',
      lat: -42.4868,
      lng: -73.7613,
      tags: ['Arquitectura', 'Iglesias', 'Patrimonio']
    },
    {
      id: 20,
      title: 'Estrecho de Magallanes',
      year: 1953,
      location: 'Punta Arenas',
      region: 'Región de Magallanes',
      lat: -53.1638,
      lng: -70.9171,
      tags: ['Patagonia', 'Paisaje', 'Extremo sur']
    }
  ];

  // Regiones únicas para el filtro
  const regions = ['Todas', ...new Set(allPins.map((p) => p.region))];

  // Tags únicos para el filtro rápido
  const allTags = [...new Set(allPins.flatMap((p) => p.tags))].sort();

  // ---------- Estado de filtros ----------
  let searchQuery = '';
  let yearFrom = 1920;
  let yearTo = 1960;
  let selectedRegion = 'Todas';
  let selectedTags: string[] = [];
  let selectedPinId: number | null = null;

  // Elemento del listado para hacer scroll automático
  let cardRefs: Record<number, HTMLElement> = {};

  // ---------- Filtrado reactivo ----------
  $: filteredPins = allPins.filter((pin) => {
    const matchSearch =
      !searchQuery ||
      pin.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pin.location.toLowerCase().includes(searchQuery.toLowerCase());

    const matchYear = pin.year >= yearFrom && pin.year <= yearTo;

    const matchRegion = selectedRegion === 'Todas' || pin.region === selectedRegion;

    const matchTags =
      selectedTags.length === 0 || selectedTags.some((t) => pin.tags.includes(t));

    return matchSearch && matchYear && matchRegion && matchTags;
  });

  function toggleTag(tag: string) {
    if (selectedTags.includes(tag)) {
      selectedTags = selectedTags.filter((t) => t !== tag);
    } else {
      selectedTags = [...selectedTags, tag];
    }
  }

  function selectPin(pin: PhotoPin) {
    selectedPinId = pin.id;
    // Scroll al card en el sidebar
    setTimeout(() => {
      cardRefs[pin.id]?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
  }

  function clearFilters() {
    searchQuery = '';
    yearFrom = 1920;
    yearTo = 1960;
    selectedRegion = 'Todas';
    selectedTags = [];
    selectedPinId = null;
  }

  $: hasActiveFilters =
    searchQuery ||
    yearFrom !== 1920 ||
    yearTo !== 1960 ||
    selectedRegion !== 'Todas' ||
    selectedTags.length > 0;
</script>

<svelte:head>
  <title>Mapa del Archivo — ROGER</title>
  <meta
    name="description"
    content="Explora geográficamente la colección fotográfica de Robert Gerstmann a lo largo de Chile"
  />
</svelte:head>

<div style="height: calc(100vh - 148px);" class="flex overflow-hidden">
  <!-- ===== SIDEBAR ===== -->
  <aside
    class="w-[420px] flex-shrink-0 bg-base-100 border-r border-base-content/10 flex flex-col overflow-hidden shadow-lg z-20"
  >
    <!-- Header del sidebar -->
    <div class="px-4 pt-4 pb-3 border-b border-base-content/10 bg-base-100">
      <h1 class="text-lg font-bold text-base-content leading-tight">Mapa del Archivo</h1>
      <p class="text-xs text-base-content/50 mt-0.5">
        Fotografías de Robert Gerstmann en Chile
      </p>
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
          <button
            class="btn btn-sm join-item btn-ghost"
            on:click={() => (searchQuery = '')}
            aria-label="Limpiar búsqueda"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-3.5 w-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2.5"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        {/if}
      </div>

      <!-- Año -->
      <div>
        <span class="text-xs font-semibold text-base-content/60 uppercase tracking-wide">Período</span>
        <div class="flex items-center gap-2 mt-1.5">
          <input
            id="year-from"
            type="number"
            class="input input-bordered input-xs w-20 text-center"
            bind:value={yearFrom}
            min="1880"
            max={yearTo}
            aria-label="Año desde"
          />
          <span class="text-base-content/40 text-sm">—</span>
          <input
            id="year-to"
            type="number"
            class="input input-bordered input-xs w-20 text-center"
            bind:value={yearTo}
            min={yearFrom}
            max="1970"
            aria-label="Año hasta"
          />
        </div>
      </div>

      <!-- Región -->
      <div>
        <label for="region-select" class="text-xs font-semibold text-base-content/60 uppercase tracking-wide">
          Región
        </label>
        <select id="region-select" class="select select-bordered select-sm w-full mt-1.5" bind:value={selectedRegion}>
          {#each regions as region}
            <option value={region}>{region}</option>
          {/each}
        </select>
      </div>

      <!-- Temas -->
      <div>
        <span class="text-xs font-semibold text-base-content/60 uppercase tracking-wide">Temas</span>
        <div class="flex flex-wrap gap-1.5 mt-1.5">
          {#each allTags.slice(0, 12) as tag}
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

      <!-- Limpiar filtros -->
      {#if hasActiveFilters}
        <button class="btn btn-ghost btn-xs w-full gap-1 text-error" on:click={clearFilters}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-3.5 w-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
          Limpiar filtros
        </button>
      {/if}
    </div>

    <!-- Contador de resultados -->
    <div class="px-4 py-2 bg-base-200/50 border-b border-base-content/10">
      <span class="text-xs text-base-content/60">
        <span class="font-bold text-primary">{filteredPins.length}</span>
        {filteredPins.length === 1 ? 'fotografía encontrada' : 'fotografías encontradas'}
      </span>
    </div>

    <!-- Lista de resultados -->
    <div class="flex-1 overflow-y-auto">
      {#if filteredPins.length === 0}
        <div class="flex flex-col items-center justify-center h-40 text-center px-6">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-10 w-10 text-base-content/20 mb-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
            />
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
              <!-- Indicador -->
              <div
                class="mt-1.5 w-2 h-2 rounded-full flex-shrink-0"
                class:bg-primary={selectedPinId !== pin.id}
                class:bg-white={selectedPinId === pin.id}
              ></div>

              <div class="flex-1 min-w-0">
                <p class="font-semibold text-sm leading-tight truncate">
                  {pin.title}
                </p>
                <p class="text-xs mt-0.5 {selectedPinId === pin.id ? 'text-primary-content/70' : 'text-base-content/50'}">
                  {pin.location} · {pin.year}
                </p>
                <div class="flex flex-wrap gap-1 mt-1.5">
                  {#each pin.tags.slice(0, 3) as tag}
                    <span class="text-[10px] px-1.5 py-0.5 rounded-full font-medium {selectedPinId === pin.id ? 'bg-white text-primary' : 'bg-base-200 text-base-content/70'}">
                      {tag}
                    </span>
                  {/each}
                </div>
              </div>

              <!-- Flecha -->
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 flex-shrink-0 mt-1 opacity-0 group-hover:opacity-100 transition-opacity {selectedPinId === pin.id ? 'text-primary-content' : 'text-primary'}"
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </button>
        {/each}
      {/if}
    </div>

    <!-- Footer del sidebar -->
    <div class="px-4 py-2.5 border-t border-base-content/10 bg-base-200/50">
      <p class="text-[10px] text-base-content/35 text-center">
        Datos de ejemplo — se conectará al archivo fotográfico real
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

    <!-- Badge flotante top-right -->
    <div
      class="absolute top-3 right-3 z-[500] bg-base-100/90 backdrop-blur-sm rounded-xl px-3 py-2 shadow-lg border border-base-content/10 text-xs"
    >
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full bg-primary"></div>
        <span class="font-medium text-base-content/70">Fotografías de Gerstmann</span>
      </div>
    </div>
  </div>
</div>
