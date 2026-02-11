<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import ImageGrid from '$lib/components/viewer/ImageGrid.svelte';
  import { imagesStore } from '$lib/stores/images';
  import { imageService } from '$lib/services';
  import { notificationsStore } from '$lib/stores/notifications';
  import type { Image } from '$lib/types';

  let loading = true;
  let error: string | null = null;
  let featuredImages: Image[] = [];

  onMount(async () => {
    await loadFeaturedImages();
  });

  async function loadFeaturedImages() {
    try {
      loading = true;
      error = null;
      const response = await imageService.listImages({ limit: 8 });
      featuredImages = response.images;
    } catch (e: any) {
      error = e.detail || 'Error al cargar imágenes destacadas';
      notificationsStore.error('Error al cargar imágenes destacadas');
    } finally {
      loading = false;
    }
  }

  function handleImageClick(image: Image) {
    imagesStore.setCurrentImage(image);
    goto(`/gallery?image=${image.id}`);
  }
</script>

<svelte:head>
  <title>ROGER - Archivo Robert Gerstmann</title>
  <meta name="description" content="Explora la colección fotográfica histórica de Robert Gerstmann" />
</svelte:head>

<!-- Hero Section -->
<section class="relative bg-gradient-to-br from-slate-800 via-slate-900 to-slate-950 text-white overflow-hidden -mx-4 -mt-8">
  <div class="absolute inset-0 opacity-10 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRoMnYyaC0yeiIvPjwvZz48L2c+PC9zdmc+')]"></div>

  <div class="container mx-auto px-4 py-24 md:py-32 relative">
    <div class="max-w-4xl mx-auto text-center">
      <div class="badge badge-accent badge-lg mb-6 shadow-lg">Patrimonio Digital</div>

      <h1 class="text-4xl md:text-6xl font-bold mb-6 leading-tight">
        Explora el Legado Visual de Roberto Gerstmann
      </h1>

      <p class="text-lg md:text-xl text-slate-200 mb-8 max-w-3xl mx-auto">
        Más de 47.000 fotografías históricas que documentan la vida, cultura, paisajes y
        transformaciones de Chile y América Latina durante el siglo XX
      </p>

      <div class="flex gap-4 justify-center flex-wrap">
        <a href="/gallery" class="btn btn-accent btn-lg shadow-lg hover:shadow-xl transition-shadow">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          Explorar Colecciones
        </a>
        <a href="/about" class="btn btn-outline btn-lg border-white text-white hover:bg-white hover:text-slate-900 hover:border-white">
          Conocer el Proyecto
        </a>
      </div>
    </div>
  </div>
</section>

<!-- Features Section -->
<section class="py-16 bg-base-100">
  <div class="container mx-auto px-4">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Feature 1 -->
      <div class="card bg-base-100 border-2 border-primary/20 hover:border-primary/50 shadow-lg hover:shadow-xl transition-all duration-300">
        <div class="card-body items-center text-center">
          <div class="bg-gradient-to-br from-primary to-primary/60 p-4 rounded-full mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h2 class="card-title text-xl font-bold mb-3">Archivo Histórico Único</h2>
          <p class="text-sm text-base-content/70">
            Acceso digital a una de las colecciones fotográficas más importantes de América Latina,
            preservando la memoria visual del siglo XX
          </p>
        </div>
      </div>

      <!-- Feature 2 -->
      <div class="card bg-base-100 border-2 border-accent/20 hover:border-accent/50 shadow-lg hover:shadow-xl transition-all duration-300">
        <div class="card-body items-center text-center">
          <div class="bg-gradient-to-br from-accent to-accent/60 p-4 rounded-full mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h2 class="card-title text-xl font-bold mb-3">Metodología ROGER</h2>
          <ul class="text-sm text-left space-y-2">
            <li class="flex items-start gap-2">
              <span class="text-accent mt-0.5">✓</span>
              <span>Detección de objetos y personas con IA</span>
            </li>
            <li class="flex items-start gap-2">
              <span class="text-accent mt-0.5">✓</span>
              <span>Narrativas históricas contextualizadas</span>
            </li>
            <li class="flex items-start gap-2">
              <span class="text-accent mt-0.5">✓</span>
              <span>Clusterización semántica avanzada</span>
            </li>
            <li class="flex items-start gap-2">
              <span class="text-accent mt-0.5">✓</span>
              <span>Búsqueda híbrida inteligente</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Feature 3 -->
      <div class="card bg-base-100 border-2 border-secondary/20 hover:border-secondary/50 shadow-lg hover:shadow-xl transition-all duration-300">
        <div class="card-body items-center text-center">
          <div class="bg-gradient-to-br from-secondary to-secondary/60 p-4 rounded-full mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h2 class="card-title text-xl font-bold mb-3">Investigación FONDEF</h2>
          <p class="text-sm text-base-content/70">
            Proyecto de investigación aplicada que combina inteligencia artificial,
            patrimonio cultural y tecnologías de vanguardia
          </p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Featured Collections -->
<section class="py-16 bg-base-200">
  <div class="container mx-auto px-4">
    <h2 class="text-3xl md:text-4xl font-bold mb-12 text-center">Colecciones Destacadas</h2>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Collection 1 -->
      <div class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
        <div class="card-body">
          <div class="badge badge-primary mb-3">545 fotografías</div>
          <h3 class="card-title text-2xl mb-2">Norte de Chile</h3>
          <p class="text-sm text-base-content/70 mb-3">Antofagasta y alrededores • 1925-1935</p>
          <div class="flex gap-2 flex-wrap mb-4">
            <span class="badge badge-outline badge-sm">Desierto</span>
            <span class="badge badge-outline badge-sm">Minería</span>
            <span class="badge badge-outline badge-sm">Salitre</span>
          </div>
          <a href="/gallery?collection=norte" class="btn btn-primary btn-sm mt-auto">
            Explorar Colección
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </a>
        </div>
      </div>

      <!-- Collection 2 -->
      <div class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
        <div class="card-body">
          <div class="badge badge-accent mb-3">3.200 fotografías</div>
          <h3 class="card-title text-2xl mb-2">Valparaíso y Puerto</h3>
          <p class="text-sm text-base-content/70 mb-3">Región de Valparaíso • 1930-1945</p>
          <div class="flex gap-2 flex-wrap mb-4">
            <span class="badge badge-outline badge-sm">Puerto</span>
            <span class="badge badge-outline badge-sm">Ciudad</span>
            <span class="badge badge-outline badge-sm">Arquitectura</span>
          </div>
          <a href="/gallery?collection=valparaiso" class="btn btn-accent btn-sm mt-auto">
            Explorar Colección
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </a>
        </div>
      </div>

      <!-- Collection 3 -->
      <div class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
        <div class="card-body">
          <div class="badge badge-secondary mb-3">892 fotografías</div>
          <h3 class="card-title text-2xl mb-2">Zona Central</h3>
          <p class="text-sm text-base-content/70 mb-3">Santiago y alrededores • 1935-1955</p>
          <div class="flex gap-2 flex-wrap mb-4">
            <span class="badge badge-outline badge-sm">Urbano</span>
            <span class="badge badge-outline badge-sm">Vida cotidiana</span>
            <span class="badge badge-outline badge-sm">Modernización</span>
          </div>
          <a href="/gallery?collection=central" class="btn btn-secondary btn-sm mt-auto">
            Explorar Colección
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Featured Images -->
{#if featuredImages.length > 0}
<section class="py-16 bg-base-100">
  <div class="container mx-auto px-4">
    <div class="flex items-center justify-between mb-8">
      <h2 class="text-3xl md:text-4xl font-bold">Imágenes Destacadas</h2>
      <a href="/gallery" class="btn btn-ghost btn-sm gap-2">
        Ver todas
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </a>
    </div>

    <ImageGrid
      images={featuredImages}
      {loading}
      {error}
      onImageClick={handleImageClick}
      onRetry={loadFeaturedImages}
    />
  </div>
</section>
{/if}

<!-- CTA Section -->
<section class="py-20 bg-gradient-to-br from-primary to-accent text-white">
  <div class="container mx-auto px-4">
    <div class="max-w-4xl mx-auto text-center">
      <h2 class="text-3xl md:text-5xl font-bold mb-6">¿Interesado en colaborar?</h2>
      <p class="text-lg md:text-xl mb-8 text-white/90">
        Si tienes información adicional sobre estas fotografías, quieres contribuir
        a la documentación histórica o deseas usar el archivo para tu investigación, contáctanos
      </p>
      <div class="flex gap-4 flex-wrap justify-center">
        <a href="/contact" class="btn btn-neutral btn-lg shadow-lg">
          Contactar
        </a>
        <a href="/research" class="btn btn-outline btn-lg border-white text-white hover:bg-white hover:text-primary hover:border-white">
          Ver Investigaciones
        </a>
      </div>
    </div>
  </div>
</section>
