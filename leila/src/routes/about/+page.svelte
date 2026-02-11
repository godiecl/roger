<svelte:head>
  <title>Acerca de - ROGER</title>
  <meta name="description" content="Conoce más sobre el proyecto ROGER y Robert Gerstmann" />
</svelte:head>

<div class="space-y-12">
  <!-- Header -->
  <div class="hero bg-base-200 rounded-lg">
    <div class="hero-content text-center py-12">
      <div class="max-w-3xl">
        <h1 class="text-5xl font-bold mb-4">Acerca del Proyecto</h1>
        <p class="text-xl">
          ROGER es una plataforma tecnológica para la visibilización de colecciones
          patrimoniales fotográficas
        </p>
      </div>
    </div>
  </div>

  <!-- Robert Gerstmann -->
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-3xl mb-4">Robert Gerstmann</h2>
      <div class="prose max-w-none">
        <p class="text-lg">
          Robert Gerstmann (1896-1964) fue un fotógrafo alemán que desarrolló una
          destacada carrera en Chile durante el siglo XX. Su trabajo documenta de
          manera excepcional la vida social, cultural y geográfica del país entre
          las décadas de 1920 y 1950.
        </p>
        <p>
          La colección Gerstmann comprende miles de fotografías que registran paisajes,
          retratos, escenas urbanas y rurales, actividades económicas, y eventos
          culturales de Chile. Estas imágenes constituyen un valioso testimonio
          histórico y patrimonial.
        </p>
      </div>
    </div>
  </div>

  <!-- Project Features -->
  <div>
    <h2 class="text-3xl font-bold mb-6 text-center">Características del Proyecto</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Colección Digitalizada
          </h3>
          <p>
            Acceso digital a miles de fotografías históricas de alta calidad,
            preservadas y catalogadas cuidadosamente.
          </p>
        </div>
      </div>

      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Narrativas con IA
          </h3>
          <p>
            Generación de contexto histórico enriquecido mediante inteligencia
            artificial y recuperación aumentada por generación (RAG).
          </p>
        </div>
      </div>

      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Trazabilidad de Fuentes
          </h3>
          <p>
            Sistema de trazabilidad que distingue entre fuentes verificadas (VERAZ)
            y fuentes verosímiles (VEROSÍMIL) para transparencia informativa.
          </p>
        </div>
      </div>

      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Búsqueda Avanzada
          </h3>
          <p>
            Búsqueda por metadatos (año, ubicación, tags) y búsqueda semántica
            mediante embeddings de IA.
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- Technology -->
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-3xl mb-4">Tecnología</h2>
      <div class="prose max-w-none">
        <p>
          ROGER está construido con tecnologías modernas que permiten una experiencia
          de usuario fluida y escalable:
        </p>
        <ul>
          <li><strong>Frontend (Leila):</strong> SvelteKit + TypeScript + DaisyUI</li>
          <li><strong>Backend (Valeria):</strong> FastAPI + Python + PostgreSQL</li>
          <li><strong>IA:</strong> OpenAI GPT-4, ChromaDB para vectores, LangChain</li>
          <li><strong>Arquitectura:</strong> Hexagonal con vertical slices</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Team -->
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-3xl mb-4">Equipo</h2>
      <p class="text-lg">
        Este proyecto es desarrollado en colaboración con la Universidad Católica
        del Norte (UCN) como parte de los esfuerzos de preservación y difusión
        del patrimonio cultural chileno.
      </p>
    </div>
  </div>

  <!-- Contact CTA -->
  <div class="card bg-primary text-primary-content shadow-xl">
    <div class="card-body items-center text-center">
      <h2 class="card-title text-2xl mb-2">¿Tienes preguntas o comentarios?</h2>
      <p class="mb-4">Nos encantaría escucharte</p>
      <a href="/contact" class="btn btn-secondary">Contáctanos</a>
    </div>
  </div>
</div>
