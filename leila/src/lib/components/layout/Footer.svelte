<script lang="ts">
  const currentYear = new Date().getFullYear();
</script>

<footer class="bg-slate-800 text-slate-200">
  <div class="container mx-auto px-4 py-16">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-12">
      <!-- Descripción -->
      <div class="md:col-span-2">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div>
            <div class="font-bold text-xl text-white">ROGER</div>
            <div class="text-xs text-slate-400">Archivo Gerstmann</div>
          </div>
        </div>
        <p class="text-sm text-slate-300 mb-6 max-w-md leading-relaxed">
          Plataforma digital para la visibilización, preservación y enriquecimiento
          del archivo fotográfico de Roberto Gerstmann mediante inteligencia artificial.
        </p>
        <div class="flex gap-4 mb-6">
          <div class="w-20 h-20 bg-slate-700 rounded-lg flex items-center justify-center hover:bg-slate-600 transition-colors">
            <span class="text-xs text-slate-300 font-semibold">UCN</span>
          </div>
          <div class="w-20 h-20 bg-slate-700 rounded-lg flex items-center justify-center hover:bg-slate-600 transition-colors">
            <span class="text-xs text-slate-300 font-semibold">FONDEF</span>
          </div>
        </div>
      </div>

      <!-- Navegación -->
      <div>
        <h3 class="font-bold text-white mb-4 text-lg">Navegación</h3>
        <ul class="space-y-3 text-sm">
          <li><a href="/" class="hover:text-white transition-colors hover:underline">Inicio</a></li>
          <li><a href="/gallery" class="hover:text-white transition-colors hover:underline">Colecciones</a></li>
          <li><a href="/map" class="hover:text-white transition-colors hover:underline">Mapa</a></li>
          <li><a href="/research" class="hover:text-white transition-colors hover:underline">Investigación</a></li>
          <li><a href="/about" class="hover:text-white transition-colors hover:underline">Acerca del Proyecto</a></li>
        </ul>
      </div>

      <!-- Legal y Contacto -->
      <div>
        <h3 class="font-bold text-white mb-4 text-lg">Legal y Contacto</h3>
        <ul class="space-y-3 text-sm">
          <li><a href="/contact" class="hover:text-white transition-colors hover:underline">Contacto</a></li>
          <li><a href="/help" class="hover:text-white transition-colors hover:underline">Ayuda</a></li>
          <li><a href="/privacy" class="hover:text-white transition-colors hover:underline">Política de Privacidad</a></li>
          <li><a href="/terms" class="hover:text-white transition-colors hover:underline">Términos de Uso</a></li>
          <li><a href="/accessibility" class="hover:text-white transition-colors hover:underline">Accesibilidad</a></li>
        </ul>
      </div>
    </div>

    <!-- Copyright y Social -->
    <div class="border-t border-slate-700 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-slate-400">
      <p>© {currentYear} Universidad Católica del Norte. Todos los derechos reservados.</p>
      <div class="flex gap-6 mt-4 md:mt-0">
        <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" class="hover:text-white transition-colors" aria-label="Twitter">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" class="fill-current">
            <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
          </svg>
        </a>
        <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" class="hover:text-white transition-colors" aria-label="Facebook">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" class="fill-current">
            <path d="M9 8h-3v4h3v12h5v-12h3.642l.358-4h-4v-1.667c0-.955.192-1.333 1.115-1.333h2.885v-5h-3.808c-3.596 0-5.192 1.583-5.192 4.615v3.385z"></path>
          </svg>
        </a>
        <a href="https://youtube.com" target="_blank" rel="noopener noreferrer" class="hover:text-white transition-colors" aria-label="YouTube">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" class="fill-current">
            <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"></path>
          </svg>
        </a>
      </div>
    </div>
  </div>
</footer>
