<svelte:head>
  <title>Política de Privacidad y Uso — ROGER</title>
  <meta name="description" content="Política de privacidad, uso de imágenes históricas y condiciones de la plataforma ROGER." />
</svelte:head>

<div class="min-h-screen bg-base-100">

  <!-- Header -->
  <section class="bg-neutral text-neutral-content py-16">
    <div class="container mx-auto px-4 max-w-3xl text-center">
      <h1 class="text-4xl font-bold mb-4">Política de Privacidad y Uso</h1>
      <p class="text-neutral-content/70">Última actualización: marzo de 2025</p>
    </div>
  </section>

  <div class="container mx-auto px-4 max-w-3xl py-16 space-y-12">

    <!-- Introducción -->
    <section>
      <p class="text-base-content/70 leading-relaxed">
        La plataforma ROGER es desarrollada por la Universidad Católica del Norte (UCN) en el marco de un proyecto FONDEF–ANID. A continuación se detallan las condiciones de uso, la política de tratamiento de datos personales y el régimen aplicable a las fotografías del archivo de Robert Gerstmann.
      </p>
    </section>

    <!-- Fotografías históricas -->
    <section>
      <h2 class="text-2xl font-bold text-base-content mb-4 flex items-center gap-3">
        <span class="w-8 h-8 rounded-full bg-primary text-primary-content text-sm font-black flex items-center justify-center flex-shrink-0">1</span>
        Fotografías históricas y dominio público
      </h2>
      <div class="pl-11 space-y-4 text-base-content/70 text-sm leading-relaxed">
        <p>
          Las fotografías del archivo de Robert Gerstmann fueron tomadas entre los años <strong class="text-base-content">1920 y 1960</strong>, hace más de 80 años. De acuerdo con la legislación chilena sobre propiedad intelectual (Ley N.° 17.336) y los convenios internacionales de derecho de autor, las obras cuyo autor ha fallecido hace más de 70 años pasan al dominio público.
        </p>
        <p>
          Robert Gerstmann falleció en 1966. Sus fotografías, por tanto, se encuentran en <strong class="text-base-content">dominio público</strong> y pueden ser reproducidas, compartidas y utilizadas libremente, siempre que se cite adecuadamente la fuente.
        </p>
        <div class="bg-base-200 rounded-xl p-5">
          <p class="font-semibold text-base-content mb-2">Forma correcta de citar:</p>
          <p class="font-mono text-xs bg-base-100 rounded-lg p-3 border border-base-300">
            Robert Gerstmann / Archivo ROGER — Universidad Católica del Norte. [Año de la fotografía]. [Título o descripción]. Recuperado de roger.ucn.cl
          </p>
        </div>
        <p>
          Los <strong class="text-base-content">metadatos, descripciones, catalogaciones y digitalizaciones</strong> producidos por el proyecto ROGER son propiedad de la UCN y se distribuyen bajo licencia <strong class="text-base-content">Creative Commons CC BY 4.0</strong>, que permite su uso libre con atribución.
        </p>
      </div>
    </section>

    <!-- Datos personales -->
    <section>
      <h2 class="text-2xl font-bold text-base-content mb-4 flex items-center gap-3">
        <span class="w-8 h-8 rounded-full bg-primary text-primary-content text-sm font-black flex items-center justify-center flex-shrink-0">2</span>
        Tratamiento de datos personales
      </h2>
      <div class="pl-11 space-y-4 text-base-content/70 text-sm leading-relaxed">
        <p>Al crear una cuenta o contactarnos, recopilamos los siguientes datos:</p>
        <ul class="space-y-2">
          {#each [
            { dato: 'Nombre y correo electrónico', uso: 'Identificación de la cuenta y comunicaciones del proyecto' },
            { dato: 'Historial de búsquedas y uso', uso: 'Mejora de los algoritmos de catalogación y experiencia de usuario' },
            { dato: 'Proyectos y colecciones creados', uso: 'Prestación del servicio colaborativo de investigación' },
          ] as row}
            <li class="flex gap-3">
              <div class="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></div>
              <div>
                <span class="font-semibold text-base-content">{row.dato}:</span>
                {row.uso}
              </div>
            </li>
          {/each}
        </ul>
        <p>
          No vendemos ni compartimos datos personales con terceros. Los datos son tratados conforme a la <strong class="text-base-content">Ley N.° 19.628</strong> sobre protección de la vida privada (Chile). Puedes solicitar la eliminación de tu cuenta y datos en cualquier momento escribiéndonos a <a href="/contacto" class="text-primary underline">contacto</a>.
        </p>
      </div>
    </section>

    <!-- Cookies -->
    <section>
      <h2 class="text-2xl font-bold text-base-content mb-4 flex items-center gap-3">
        <span class="w-8 h-8 rounded-full bg-primary text-primary-content text-sm font-black flex items-center justify-center flex-shrink-0">3</span>
        Cookies y tecnologías de rastreo
      </h2>
      <div class="pl-11 space-y-3 text-base-content/70 text-sm leading-relaxed">
        <p>Utilizamos únicamente cookies técnicas necesarias para el funcionamiento de la plataforma (sesión de usuario, preferencias de idioma y tema). No usamos cookies de publicidad ni de seguimiento de terceros.</p>
      </div>
    </section>

    <!-- Uso aceptable -->
    <section>
      <h2 class="text-2xl font-bold text-base-content mb-4 flex items-center gap-3">
        <span class="w-8 h-8 rounded-full bg-primary text-primary-content text-sm font-black flex items-center justify-center flex-shrink-0">4</span>
        Condiciones de uso de la plataforma
      </h2>
      <div class="pl-11 space-y-3 text-base-content/70 text-sm leading-relaxed">
        <p>El acceso y uso de ROGER está permitido para fines educativos, de investigación, periodísticos o personales. Queda prohibido:</p>
        <ul class="space-y-2">
          {#each [
            'Reproducir las fotografías con fines comerciales sin autorización expresa',
            'Usar la plataforma para distribuir contenido falso o desinformación sobre el archivo',
            'Intentar acceder de forma no autorizada a colecciones privadas o datos de otros usuarios',
            'Realizar scraping masivo sin acuerdo previo con el equipo ROGER',
          ] as item}
            <li class="flex gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-error mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              {item}
            </li>
          {/each}
        </ul>
      </div>
    </section>

    <!-- Contacto -->
    <section class="border-t border-base-200 pt-8">
      <p class="text-sm text-base-content/50 text-center">
        ¿Tienes preguntas sobre esta política?
        <a href="/contacto" class="text-primary hover:underline">Escríbenos</a>
      </p>
    </section>

  </div>
</div>
