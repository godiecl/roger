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
    goto(`/colecciones?image=${image.id}`);
  }
</script>

<svelte:head>
  <title>ROGER – Archivo Fotográfico Robert Gerstmann</title>
  <meta name="description" content="Más de 47.000 fotografías históricas de Chile y América Latina del siglo XX, digitalizadas y enriquecidas con inteligencia artificial por la Universidad Católica del Norte." />

  <!-- Open Graph -->
  <meta property="og:type"        content="website" />
  <meta property="og:title"       content="ROGER – Archivo Fotográfico Robert Gerstmann" />
  <meta property="og:description" content="Explora, busca y descubre más de 47.000 fotografías históricas de Chile y América Latina. Patrimonio digital preservado con IA por la Universidad Católica del Norte." />
  <meta property="og:image"       content="/images/panorama-1.jpg" />
  <meta property="og:url"         content="https://roger.ucn.cl" />
  <meta property="og:locale"      content="es_CL" />
  <meta property="og:site_name"   content="ROGER – Fondo Robert Gerstmann" />

  <!-- Twitter Card -->
  <meta name="twitter:card"        content="summary_large_image" />
  <meta name="twitter:title"       content="ROGER – Archivo Fotográfico Robert Gerstmann" />
  <meta name="twitter:description" content="Más de 47.000 fotografías históricas digitalizadas con IA. Patrimonio visual de Chile y América Latina del siglo XX." />
  <meta name="twitter:image"       content="/images/panorama-1.jpg" />

  <!-- Additional SEO -->
  <meta name="keywords" content="Robert Gerstmann, fotografía histórica, Chile, archivo fotográfico, patrimonio digital, inteligencia artificial, Universidad Católica del Norte, América Latina, siglo XX" />
  <link rel="canonical" href="https://roger.ucn.cl" />
</svelte:head>

<!-- Hero Section -->
<section class="relative text-white overflow-hidden w-full">
  <!-- Imagen de fondo con blur -->
  <img
    src="/images/panorama-1.jpg"
    alt=""
    aria-hidden="true"
    class="absolute inset-0 w-full h-full object-cover"
    style="filter: blur(3px); transform: scale(1.05);"
  />
  <!-- Overlay oscuro -->
  <div class="absolute inset-0 bg-slate-950/65"></div>

  <div class="container mx-auto px-4 py-24 md:py-32 relative">
    <div class="max-w-4xl mx-auto text-center">
      <div class="badge badge-accent badge-lg mb-6 shadow-lg">Patrimonio Digital</div>

      <h1 class="text-4xl md:text-6xl font-bold mb-6 leading-tight">
        Explora el Legado Visual de Robert Gerstmann
      </h1>

      <p class="text-lg md:text-xl text-slate-200 mb-8 max-w-3xl mx-auto">
        Más de 47.000 fotografías históricas que documentan la vida, cultura, paisajes y
        transformaciones de Chile y América Latina durante el siglo XX
      </p>

      <div class="flex gap-4 justify-center flex-wrap">
        <a href="/colecciones" class="btn btn-accent btn-lg shadow-lg hover:shadow-xl transition-shadow">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          Explorar Colecciones
        </a>
        <a href="/sobre-roger" class="btn btn-outline btn-lg border-white text-white hover:bg-white hover:text-slate-900 hover:border-white">
          Conocer el Proyecto
        </a>
      </div>
    </div>
  </div>
</section>

<!-- How it Works Section -->
<section class="py-20 bg-base-100">
  <div class="container mx-auto px-4 sm:px-6">

    <div class="text-center mb-16">
      <div class="badge badge-primary badge-lg mb-4">Proceso</div>
      <h2 class="text-3xl md:text-4xl font-bold mb-4">¿Cómo preservamos el legado?</h2>
      <p class="text-base-content/60 max-w-2xl mx-auto text-lg">
        Desde el negativo original hasta la exploración inteligente — cada fotografía sigue
        un proceso riguroso de digitalización, análisis y enriquecimiento.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">

      <!-- Step 1 -->
      <div class="flex flex-col items-center text-center group">
        <div class="relative mb-5">
          <div class="w-16 h-16 rounded-2xl bg-primary/10 group-hover:bg-primary/20 transition-colors flex items-center justify-center border-2 border-primary/20 group-hover:border-primary/50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <span class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-primary text-primary-content text-xs font-black flex items-center justify-center">1</span>
        </div>
        <h3 class="font-bold text-base mb-2">Digitalización</h3>
        <p class="text-sm text-base-content/60 leading-relaxed">
          Las fotografías originales son escaneadas a alta resolución por un equipo profesional de conservación.
        </p>
      </div>

      <!-- Connector -->
      <div class="hidden lg:flex items-center justify-center pt-4">
        <div class="w-full h-0.5 bg-gradient-to-r from-primary/30 to-accent/30 mt-[-2.5rem]"></div>
      </div>

      <!-- Step 2 -->
      <div class="flex flex-col items-center text-center group">
        <div class="relative mb-5">
          <div class="w-16 h-16 rounded-2xl bg-accent/10 group-hover:bg-accent/20 transition-colors flex items-center justify-center border-2 border-accent/20 group-hover:border-accent/50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <span class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-accent text-accent-content text-xs font-black flex items-center justify-center">2</span>
        </div>
        <h3 class="font-bold text-base mb-2">Análisis con IA</h3>
        <p class="text-sm text-base-content/60 leading-relaxed">
          Algoritmos detectan objetos, lugares y personas, generando metadatos semánticos automáticamente.
        </p>
      </div>

      <!-- Connector -->
      <div class="hidden lg:flex items-center justify-center pt-4">
        <div class="w-full h-0.5 bg-gradient-to-r from-accent/30 to-secondary/30 mt-[-2.5rem]"></div>
      </div>

      <!-- Step 3 -->
      <div class="flex flex-col items-center text-center group">
        <div class="relative mb-5">
          <div class="w-16 h-16 rounded-2xl bg-secondary/10 group-hover:bg-secondary/20 transition-colors flex items-center justify-center border-2 border-secondary/20 group-hover:border-secondary/50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <span class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-secondary text-secondary-content text-xs font-black flex items-center justify-center">3</span>
        </div>
        <h3 class="font-bold text-base mb-2">Búsqueda Inteligente</h3>
        <p class="text-sm text-base-content/60 leading-relaxed">
          Describe con palabras lo que buscas y la IA encuentra fotografías conceptualmente similares.
        </p>
      </div>

    </div>

    <!-- Second row of steps -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6 max-w-2xl mx-auto">

      <!-- Step 4 -->
      <div class="flex flex-col items-center text-center group">
        <div class="relative mb-5">
          <div class="w-16 h-16 rounded-2xl bg-primary/10 group-hover:bg-primary/20 transition-colors flex items-center justify-center border-2 border-primary/20 group-hover:border-primary/50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-primary text-primary-content text-xs font-black flex items-center justify-center">4</span>
        </div>
        <h3 class="font-bold text-base mb-2">Narrativas Históricas</h3>
        <p class="text-sm text-base-content/60 leading-relaxed">
          Genera relatos contextualizados sobre cada fotografía combinando IA con fuentes históricas.
        </p>
      </div>

      <!-- Step 5 -->
      <div class="flex flex-col items-center text-center group">
        <div class="relative mb-5">
          <div class="w-16 h-16 rounded-2xl bg-accent/10 group-hover:bg-accent/20 transition-colors flex items-center justify-center border-2 border-accent/20 group-hover:border-accent/50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <span class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-accent text-accent-content text-xs font-black flex items-center justify-center">5</span>
        </div>
        <h3 class="font-bold text-base mb-2">Colaboración Abierta</h3>
        <p class="text-sm text-base-content/60 leading-relaxed">
          Investigadores e historiadores pueden contribuir con fuentes, anotaciones y nueva información.
        </p>
      </div>

    </div>

    <div class="text-center mt-12">
      <a href="/investigacion" class="btn btn-primary btn-lg gap-2">
        Conocer la metodología
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </a>
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
          <a href="/colecciones?collection=norte" class="btn btn-primary btn-sm mt-auto">
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
          <a href="/colecciones?collection=valparaiso" class="btn btn-accent btn-sm mt-auto">
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
          <a href="/colecciones?collection=central" class="btn btn-secondary btn-sm mt-auto">
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
      <a href="/colecciones" class="btn btn-ghost btn-sm gap-2">
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
        <a href="/contacto" class="btn btn-neutral btn-lg shadow-lg">
          Contactar
        </a>
        <a href="/sobre-roger" class="btn btn-outline btn-lg border-white text-white hover:bg-white hover:text-primary hover:border-white">
          Acerca del Proyecto
        </a>
      </div>
    </div>
  </div>
</section>
