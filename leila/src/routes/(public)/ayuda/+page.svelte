<script lang="ts">
  let openFaq: number | null = null;

  const faqs = [
    {
      q: '¿Necesito una cuenta para ver las fotografías?',
      a: 'No. La colección fotográfica y el mapa interactivo son de acceso público y gratuito. Crear una cuenta te da acceso a herramientas adicionales de investigación como el chat con el archivo, las líneas de tiempo y los proyectos colaborativos.',
    },
    {
      q: '¿Cómo puedo buscar fotografías de un lugar específico?',
      a: 'Puedes usar el buscador en la galería de colecciones, explorar el mapa interactivo filtrando por región, período y temática, o —si tienes cuenta— usar la búsqueda semántica que permite describir lo que buscas en lenguaje natural.',
    },
    {
      q: '¿Qué es el "chat con el archivo"?',
      a: 'Es un asistente de inteligencia artificial entrenado con la información del archivo Gerstmann. Puedes hacerle preguntas en lenguaje natural, como "¿Qué fotografías hay de pescadores en el norte de Chile en los años 30?" y obtendrás respuestas contextualizadas con referencias a imágenes reales del archivo.',
    },
    {
      q: '¿Puedo usar las fotografías en mi investigación o publicación?',
      a: 'Sí, con condiciones. Las fotografías de Robert Gerstmann datan de hace más de 80 años y muchas están en dominio público. Sin embargo, los derechos sobre las digitalizaciones pueden variar. Te recomendamos revisar la política de uso o contactarnos para consultas específicas.',
    },
    {
      q: '¿Cómo funciona la georreferenciación del mapa?',
      a: 'Cada fotografía ha sido asociada a coordenadas geográficas mediante un proceso combinado de análisis de metadatos originales, reconocimiento de paisajes por IA y revisión humana por parte del equipo de investigación. El mapa permite filtrar por región, año y temática.',
    },
    {
      q: '¿Qué son los proyectos colaborativos?',
      a: 'Son espacios de trabajo compartido donde múltiples investigadores o usuarios pueden reunir fotografías, añadir notas, construir narrativas históricas y trabajar en conjunto sobre un tema específico del archivo.',
    },
    {
      q: '¿Cómo puedo aportar fotografías o documentos al archivo?',
      a: 'Puedes escribirnos desde la página de contacto. El equipo evaluará el material y te indicará el proceso de donación o préstamo para digitalización.',
    },
    {
      q: 'Encontré un error en la descripción de una fotografía, ¿qué hago?',
      a: 'Los errores en la catalogación pueden reportarse directamente desde la vista de cada fotografía (botón "Reportar") o escribiéndonos a través del formulario de contacto. Agradecemos mucho la colaboración de la comunidad para mejorar el archivo.',
    },
  ];
</script>

<svelte:head>
  <title>Ayuda — ROGER</title>
  <meta name="description" content="Preguntas frecuentes y guía de uso de la plataforma ROGER — Archivo fotográfico de Robert Gerstmann." />
</svelte:head>

<div class="min-h-screen bg-base-100">

  <!-- Header -->
  <section class="bg-neutral text-neutral-content py-16">
    <div class="container mx-auto px-4 max-w-3xl text-center">
      <h1 class="text-4xl font-bold mb-4">Centro de ayuda</h1>
      <p class="text-neutral-content/70 text-lg">Respuestas a las preguntas más frecuentes sobre la plataforma y el archivo.</p>
    </div>
  </section>

  <div class="container mx-auto px-4 max-w-4xl py-16 space-y-16">

    <!-- Guía rápida -->
    <section>
      <h2 class="text-2xl font-bold text-base-content mb-8">Guía rápida</h2>
      <div class="grid md:grid-cols-3 gap-6">
        {#each [
          { icon: '🗺️', title: 'Explorar el mapa', desc: 'Visita la sección Mapa para ver las fotografías geolocalizadas en Chile. Usa los filtros de región, año y temática para afinar tu búsqueda.' },
          { icon: '🖼️', title: 'Navegar colecciones', desc: 'En la galería encontrarás las fotografías organizadas por colección, período y región. Haz clic en cualquier imagen para ver su ficha completa.' },
          { icon: '💬', title: 'Usar el chat con IA', desc: 'Crea una cuenta gratuita y accede al asistente de inteligencia artificial. Puedes hacerle preguntas sobre el archivo en lenguaje natural.' },
        ] as step}
          <div class="bg-base-200 rounded-2xl p-6">
            <div class="text-3xl mb-3">{step.icon}</div>
            <h3 class="font-bold text-base-content mb-2">{step.title}</h3>
            <p class="text-sm text-base-content/60 leading-relaxed">{step.desc}</p>
          </div>
        {/each}
      </div>
    </section>

    <!-- FAQ -->
    <section>
      <h2 class="text-2xl font-bold text-base-content mb-6">Preguntas frecuentes</h2>
      <div class="space-y-2">
        {#each faqs as faq, i}
          <div class="border border-base-200 rounded-xl overflow-hidden">
            <button
              class="w-full flex items-center justify-between px-6 py-4 text-left font-semibold text-base-content hover:bg-base-200/50 transition-colors"
              on:click={() => openFaq = openFaq === i ? null : i}
              aria-expanded={openFaq === i}
            >
              <span>{faq.q}</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 text-base-content/40 flex-shrink-0 ml-4 transition-transform {openFaq === i ? 'rotate-180' : ''}"
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {#if openFaq === i}
              <div class="px-6 pb-4 text-sm text-base-content/70 leading-relaxed border-t border-base-200 pt-4">
                {faq.a}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </section>

    <!-- Contacto -->
    <section class="bg-primary/5 border border-primary/20 rounded-3xl p-8 text-center">
      <h3 class="text-xl font-bold text-base-content mb-3">¿No encontraste lo que buscabas?</h3>
      <p class="text-base-content/60 text-sm mb-5">Escríbenos directamente y te ayudaremos a resolver tu consulta.</p>
      <a href="/contacto" class="btn btn-primary gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        Ir al formulario de contacto
      </a>
    </section>

  </div>
</div>
