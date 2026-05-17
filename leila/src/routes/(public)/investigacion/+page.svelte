<svelte:head>
  <title>Investigación — ROGER</title>
  <meta name="description" content="Conoce cómo digitalizamos, catalogamos y preservamos el archivo fotográfico de Robert Gerstmann con inteligencia artificial." />
</svelte:head>

<div class="min-h-screen bg-base-100">

  <!-- Hero -->
  <section class="relative text-neutral-content py-20 overflow-hidden">
    <img
      src="/images/digitalizar_fotos.jpg"
      alt=""
      aria-hidden="true"
      class="absolute inset-0 w-full h-full object-cover"
      style="filter: blur(3px); transform: scale(1.05);"
    />
    <div class="absolute inset-0 bg-neutral/70"></div>
    <div class="relative container mx-auto px-4 max-w-4xl text-center">
    <br>
      <h1 class="text-4xl md:text-5xl font-bold mb-6 leading-tight">
        Digitalización e investigación<br class="hidden md:block" /> del archivo Gerstmann
      </h1>
      <p class="text-lg text-neutral-content/70 max-w-2xl mx-auto leading-relaxed">
        Un equipo multidisciplinario en la Universidad Católica del Norte trabaja para preservar, catalogar y poner al alcance de todos las miles de fotografías que Robert Gerstmann tomó recorriendo Chile durante el siglo XX.
      </p>
    </div>
  </section>

  <div class="container mx-auto px-4 max-w-5xl py-16 space-y-20">

    <!-- Qué estamos haciendo -->
    <section>
      <div class="grid md:grid-cols-2 gap-12 items-center">
        <div>
          <h2 class="text-3xl font-bold text-base-content mb-4">¿Qué estamos haciendo?</h2>
          <p class="text-base-content/70 leading-relaxed mb-4">
            Las fotografías de Robert Gerstmann —tomadas entre 1920 y 1960— están siendo digitalizadas por un equipo profesional en alta resolución, asegurando que cada imagen capture los detalles originales de las placas y negativos históricos.
          </p>
          <p class="text-base-content/70 leading-relaxed mb-4">
            Una vez digitalizadas, cada fotografía se procesa mediante algoritmos de <strong class="text-base-content">inteligencia artificial y machine learning</strong> que permiten:
          </p>
          <ul class="space-y-2">
            {#each [
              'Georreferenciación de las ubicaciones fotografiadas',
              'Identificación de personas, paisajes y actividades',
              'Agrupación temática y por períodos históricos',
            ] as item}
              <li class="flex items-start gap-2 text-sm text-base-content/70">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                </svg>
                {item}
              </li>
            {/each}
          </ul>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {#each [
            { label: 'Fotografías', value: '+47.000', sub: 'en proceso de digitalización' },
            { label: 'Años de historia', value: '100+', sub: 'cubiertos por el archivo' },
            { label: 'Territorios documentados', value: '+20', sub: 'en Chile y Latinoamérica' },
            { label: 'Años de proyecto', value: '2', sub: 'de investigación activa' },
          ] as stat}
            <div class="bg-base-200 rounded-2xl p-5 text-center">
              <div class="text-3xl font-bold text-primary mb-1">{stat.value}</div>
              <div class="text-sm font-semibold text-base-content">{stat.label}</div>
              <div class="text-xs text-base-content/50 mt-1">{stat.sub}</div>
            </div>
          {/each}
        </div>
      </div>
    </section>

    <!-- Caso de estudio -->
    <section>
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold text-base-content mb-4">Cómo funciona ROGER</h2>
        <p class="text-base-content/60 max-w-2xl mx-auto text-lg leading-relaxed">
          El archivo de Gerstmann funciona a través del reconocimiento de imágenes y el análisis de metadatos. Aunque algunas fotografías ya cuentan con información, muchas otras no tienen fecha, orden ni descripción, por lo que utilizamos inteligencia artificial para ayudar a reconstruir su contexto.
        </p>
      </div>

      <!-- Caso real -->
      <div class="bg-base-200 rounded-3xl p-8 md:p-10 mb-12">
        <div class="flex flex-col md:flex-row gap-8 items-start">
          <div class="flex-1">
            <div class="flex flex-wrap items-center gap-2 mb-4">
              <span class="badge badge-primary">Investigación publicada</span>
              <span class="text-xs text-base-content/40">Universidad Católica del Norte · Virginia Tech</span>
            </div>
            <h3 class="text-2xl font-bold text-base-content mb-3">
              La Expedición Sacambaya: 500 fotos, ningún orden, una historia reconstruida
            </h3>
            <!-- El desafío -->
            <div class="mb-5">
              <p class="text-xs font-bold uppercase tracking-widest text-base-content/30 mb-2">El desafío</p>
              <p class="text-base-content/70 leading-relaxed">
                En 1928, Robert Gerstmann documentó con su cámara la <strong>Expedición Sacambaya</strong>, una búsqueda de tesoros en Bolivia que terminó en fracaso. El archivo conserva 500 negativos de esa expedición —mezclados con el resto de la colección, sin fechas y sin ninguna referencia de a qué etapa del viaje pertenecen.
              </p>
            </div>

            <div class="border-t border-base-content/10 mb-5"></div>

            <!-- El resultado -->
            <div>
              <p class="text-xs font-bold uppercase tracking-widest text-primary/60 mb-2">El resultado</p>
              <p class="text-base-content/70 leading-relaxed">
                Usando inteligencia artificial, el sistema analiza el contenido visual de cada fotografía, identifica similitudes entre escenas y reconstruye la secuencia del viaje. Los historiadores que revisaron el resultado confirmaron que <strong class="text-base-content">el orden generado por la IA coincide con la cronología real de los hechos.</strong>
              </p>
            </div>
            <p class="text-xs text-base-content/40 mt-5">
              Fausto German · Brian Keith · Mauricio Matus · Diego Urrutia · Claudio Meneses
            </p>
          </div>
          <div class="flex-shrink-0 flex flex-col gap-3 md:w-44">
            <div class="bg-base-100 rounded-2xl p-4 text-center">
              <div class="text-3xl font-black text-primary">500</div>
              <div class="text-xs text-base-content/50 mt-1 leading-snug">fotografías desordenadas procesadas</div>
            </div>
            <div class="bg-base-100 rounded-2xl p-4 text-center">
              <div class="text-3xl font-black text-primary">1928</div>
              <div class="text-xs text-base-content/50 mt-1 leading-snug">expedición real documentada por Gerstmann</div>
            </div>
            <div class="bg-base-100 rounded-2xl p-4 text-center">
              <div class="text-3xl font-black text-primary">✓</div>
              <div class="text-xs text-base-content/50 mt-1 leading-snug">secuencia validada por expertos en historia</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Cómo funciona -->
      <div class="text-center mb-8">
        <h3 class="text-2xl font-bold text-base-content mb-2">Cómo trabaja ROGER</h3>
        <p class="text-base-content/50 max-w-xl mx-auto text-sm">El procesamiento de las fotografías paso a paso</p>
      </div>

      <div class="grid md:grid-cols-3 gap-6">

        <div class="bg-base-100 border border-base-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
          <h3 class="font-bold text-base-content mb-2">La IA lee cada fotografía</h3>
          <p class="text-sm text-base-content/60 leading-relaxed">
            Cada imagen es analizada por un sistema de visión que identifica qué hay en ella: personas, paisajes, objetos, tipo de escena. Así como tú reconocerías que dos fotos muestran el mismo puerto aunque nunca las hayas visto, la IA detecta esas similitudes a escala masiva.
          </p>
        </div>

        <div class="bg-base-100 border border-base-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
            </svg>
          </div>
          <h3 class="font-bold text-base-content mb-2">Los historiadores aportan las claves</h3>
          <p class="text-sm text-base-content/60 leading-relaxed">
            Un experto revisa solo una pequeña parte de la colección y anota brevemente qué muestra cada foto. Con esas pistas, el sistema aprende a clasificar el resto de manera autónoma, sin necesidad de revisar imagen por imagen.
          </p>
        </div>

        <div class="bg-base-100 border border-base-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="w-10 h-10 rounded-xl bg-secondary/10 flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
          </div>
          <h3 class="font-bold text-base-content mb-2">Se arma la historia más coherente</h3>
          <p class="text-sm text-base-content/60 leading-relaxed">
            El sistema ordena las fotografías buscando la secuencia que tenga más sentido de principio a fin —igual que armar un puzle buscando que cada pieza encaje con la siguiente. El resultado es un relato visual completo y coherente.
          </p>
        </div>

        <div class="bg-base-100 border border-base-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
          </div>
          <h3 class="font-bold text-base-content mb-2">Validado por quienes conocen la historia</h3>
          <p class="text-sm text-base-content/60 leading-relaxed">
            El orden generado por la IA se comparó con la cronología real de la Expedición Sacambaya, construida manualmente por historiadores. La coincidencia fue mucho mayor que cualquier ordenamiento al azar, confirmando que el sistema funciona.
          </p>
        </div>

        <div class="bg-base-100 border border-base-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h3 class="font-bold text-base-content mb-2">Búsqueda por ideas, no por palabras</h3>
          <p class="text-sm text-base-content/60 leading-relaxed">
            El mismo sistema que lee las imágenes permite buscar en el archivo con frases cotidianas: "niños jugando en la costa" o "trabajadores en la pampa salitrera". Aparecen fotos relevantes aunque ninguna tenga esas palabras como etiqueta.
          </p>
        </div>

        <div class="bg-base-100 border border-base-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="w-10 h-10 rounded-xl bg-secondary/10 flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h3 class="font-bold text-base-content mb-2">Conversa con el archivo</h3>
          <p class="text-sm text-base-content/60 leading-relaxed">
            La plataforma incluye un asistente con el que puedes hacer preguntas directamente sobre la colección: "¿Qué fotos hay de Antofagasta en los años 30?" o "¿Dónde viajó Gerstmann en 1928?". El sistema responde usando las propias fotografías como fuente.
          </p>
        </div>

      </div>
    </section>

    <!-- Líneas de investigación -->
    <section class="bg-base-200 rounded-3xl p-8 md:p-12">
      <h2 class="text-3xl font-bold text-base-content mb-2">Lo que hace posible la plataforma</h2>
      <p class="text-base-content/50 text-sm mb-8">Investigación aplicada UCN </p>
      <div class="grid md:grid-cols-2 gap-6">

        <div class="flex gap-4">
          <div class="text-4xl font-black text-primary/20 leading-none flex-shrink-0 w-10">01</div>
          <div>
            <h3 class="font-bold text-base-content mb-1">Historias recuperadas desde el desorden</h3>
            <p class="text-sm text-base-content/60 leading-relaxed">
              Miles de fotografías del archivo no tienen fecha ni descripción. La plataforma las organiza automáticamente en relatos visuales coherentes, recuperando el sentido narrativo de colecciones que parecían irrecuperables.
            </p>
          </div>
        </div>

        <div class="flex gap-4">
          <div class="text-4xl font-black text-primary/20 leading-none flex-shrink-0 w-10">02</div>
          <div>
            <h3 class="font-bold text-base-content mb-1">Un siglo de Chile visto por su lente</h3>
            <p class="text-sm text-base-content/60 leading-relaxed">
              Gerstmann no solo tomó fotos bonitas: dejó un registro visual de cómo era Chile en transformación. La plataforma permite explorar qué documentó, dónde estuvo y qué nos dicen esas imágenes sobre la vida, el trabajo y los paisajes de hace cien años.
            </p>
          </div>
        </div>

        <div class="flex gap-4">
          <div class="text-4xl font-black text-primary/20 leading-none flex-shrink-0 w-10">03</div>
          <div>
            <h3 class="font-bold text-base-content mb-1">Inteligencia artificial entrenada para el pasado</h3>
            <p class="text-sm text-base-content/60 leading-relaxed">
              Los sistemas de visión fueron adaptados para entender fotografías históricas en blanco y negro: reconoce vestimentas, oficios y paisajes del Chile del siglo XX con mucha mayor precisión que un sistema genérico.
            </p>
          </div>
        </div>

        <div class="flex gap-4">
          <div class="text-4xl font-black text-primary/20 leading-none flex-shrink-0 w-10">04</div>
          <div>
            <h3 class="font-bold text-base-content mb-1">El itinerario completo de Gerstmann</h3>
            <p class="text-sm text-base-content/60 leading-relaxed">
              Cada fotografía está ubicada en el mapa. El resultado es la reconstrucción de los recorridos que hizo Gerstmann por Chile y América Latina: qué lugares visitó, con qué frecuencia y qué eligió retratar en cada uno.
            </p>
          </div>
        </div>

      </div>
    </section>

    <!-- CTAs -->
    <section class="grid md:grid-cols-2 gap-8">

      <!-- CTA: Fuentes -->
      <div class="bg-primary text-primary-content rounded-3xl p-8 flex flex-col">
        <h3 class="text-2xl font-bold mb-3">¿Tienes fotografías o documentos históricos?</h3>
        <p class="text-primary-content/80 text-sm leading-relaxed mb-6 flex-1">
          Si posees fotografías de Robert Gerstmann, archivos personales, cartas o cualquier material relacionado con su obra, nos gustaría conocerlos. Cada nueva fuente enriquece el conocimiento histórico colectivo.
        </p>
        <a href="/contacto" class="btn gap-2 bg-white text-black border-white hover:bg-white/90 mt-auto">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          Ponerse en contacto
        </a>
      </div>

      <!-- CTA: Plataforma -->
      <div class="bg-base-200 rounded-3xl p-8 flex flex-col">
        <h3 class="text-2xl font-bold text-base-content mb-3">Prueba la plataforma de investigación</h3>
        <p class="text-base-content/60 text-sm leading-relaxed mb-6 flex-1">
          Crea una cuenta gratuita y accede a herramientas diseñadas para investigadores: conversa con el archivo mediante IA, construye líneas de tiempo visuales, agrupa fotografías por temáticas y crea proyectos colaborativos con otros equipos.
        </p>
        <a href="/login" class="btn btn-primary gap-2 mt-auto">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Crear cuenta gratuita
        </a>
      </div>

    </section>

  </div>
</div>
