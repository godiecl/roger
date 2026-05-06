<svelte:head>
  <title>Accesibilidad — ROGER</title>
  <meta name="description" content="Compromiso de la plataforma ROGER con la accesibilidad y el acceso universal al patrimonio fotográfico de Robert Gerstmann." />
</svelte:head>

<div class="min-h-screen bg-base-100">

  <!-- Header -->
  <section class="bg-neutral text-neutral-content py-16">
    <div class="container mx-auto px-4 max-w-3xl text-center">
      <h1 class="text-4xl font-bold mb-4">Accesibilidad</h1>
      <p class="text-neutral-content/70 text-lg max-w-xl mx-auto">
        Nuestro compromiso es que cualquier persona, independientemente de sus capacidades, pueda acceder al patrimonio fotográfico de Chile.
      </p>
    </div>
  </section>

  <div class="container mx-auto px-4 max-w-3xl py-16 space-y-12">

    <!-- Compromiso -->
    <section>
      <h2 class="text-2xl font-bold text-base-content mb-4">Nuestro compromiso</h2>
      <p class="text-base-content/70 leading-relaxed mb-4">
        El proyecto ROGER se desarrolla con el principio de que el patrimonio cultural es de todos. Trabajamos para que la plataforma cumpla con las pautas de accesibilidad <strong class="text-base-content">WCAG 2.1 nivel AA</strong>, el estándar internacional que garantiza la usabilidad para personas con diversidad funcional visual, auditiva, motora y cognitiva.
      </p>
      <p class="text-base-content/70 leading-relaxed">
        Esto cobra especial relevancia en un archivo de fotografías históricas: las imágenes no solo deben verse, sino también poder ser <em>comprendidas</em> por cualquier persona.
      </p>
    </section>

    <!-- Funciones de accesibilidad -->
    <section>
      <h2 class="text-2xl font-bold text-base-content mb-6">Funciones de accesibilidad implementadas</h2>
      <div class="grid md:grid-cols-2 gap-5">
        {#each [
          {
            icon: '🔤',
            title: 'Texto alternativo en imágenes',
            desc: 'Cada fotografía cuenta con una descripción textual generada y revisada por el equipo, accesible para lectores de pantalla.',
          },
          {
            icon: '⌨️',
            title: 'Navegación por teclado',
            desc: 'Toda la interfaz es navegable usando únicamente el teclado, con indicadores de foco claramente visibles.',
          },
          {
            icon: '🌗',
            title: 'Modo oscuro y claro',
            desc: 'La plataforma adapta su apariencia al modo del sistema operativo del usuario, reduciendo la fatiga visual.',
          },
          {
            icon: '📐',
            title: 'Texto escalable',
            desc: 'El texto de la plataforma puede aumentarse hasta un 200% sin pérdida de funcionalidad ni superposición de contenidos.',
          },
          {
            icon: '🎨',
            title: 'Contraste suficiente',
            desc: 'Los colores cumplen la relación de contraste mínima de 4.5:1 para texto y 3:1 para elementos de interfaz.',
          },
          {
            icon: '💬',
            title: 'Descripciones contextuales',
            desc: 'El asistente de IA puede describir fotografías en lenguaje natural, facilitando el acceso a personas con discapacidad visual.',
          },
        ] as feat}
          <div class="flex gap-4 p-5 bg-base-200 rounded-2xl">
            <div class="text-2xl flex-shrink-0">{feat.icon}</div>
            <div>
              <h3 class="font-semibold text-base-content mb-1">{feat.title}</h3>
              <p class="text-sm text-base-content/60 leading-relaxed">{feat.desc}</p>
            </div>
          </div>
        {/each}
      </div>
    </section>

    <!-- Limitaciones conocidas -->
    <section>
      <h2 class="text-2xl font-bold text-base-content mb-4">Limitaciones conocidas</h2>
      <div class="bg-warning/10 border border-warning/30 rounded-2xl p-6">
        <p class="text-sm text-base-content/70 leading-relaxed mb-3">
          Somos conscientes de que la plataforma está en desarrollo activo y algunas áreas aún no cumplen plenamente los estándares de accesibilidad:
        </p>
        <ul class="space-y-2 text-sm text-base-content/70">
          {#each [
            'El visor de mapa interactivo tiene limitaciones de accesibilidad inherentes a la tecnología Leaflet.',
            'Algunas fotografías antiguas de baja resolución pueden no contar aún con descripción alternativa completa.',
            'La funcionalidad de arrastrar y soltar en colecciones no tiene alternativa de teclado en esta versión.',
          ] as item}
            <li class="flex gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-warning mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              {item}
            </li>
          {/each}
        </ul>
      </div>
    </section>

    <!-- Reportar -->
    <section class="bg-primary/5 border border-primary/20 rounded-3xl p-8">
      <h3 class="text-xl font-bold text-base-content mb-3">¿Encontraste una barrera de accesibilidad?</h3>
      <p class="text-base-content/60 text-sm leading-relaxed mb-5">
        Tu retroalimentación es fundamental para mejorar. Si encontraste algún elemento de la plataforma que te impidió o dificultó el acceso a contenido, escríbenos indicando qué intentabas hacer y cuál fue el obstáculo.
      </p>
      <a href="/contacto" class="btn btn-primary gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        Reportar un problema de accesibilidad
      </a>
    </section>

  </div>
</div>
