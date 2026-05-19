<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated, authStore } from '$lib/stores/auth';
  import { moderationService } from '$lib/services/moderationService';
  import { narrativeService } from '$lib/services/narrativeService';

  const REVIEWER_ROLES = ['curador', 'administrador', 'mesa_evaluadora'];

  let pendingContributions = 0;
  let pendingTags = 0;
  let pendingNarratives = 0;
  let loading = true;

  onMount(async () => {
    if (!$isAuthenticated) { goto('/login'); return; }
    const role = $authStore.user?.role ?? '';
    if (!REVIEWER_ROLES.includes(role)) { goto('/'); return; }

    try {
      const [stats, tagsRes, narrativesRes] = await Promise.all([
        moderationService.getStats(),
        moderationService.getPendingTags({ limit: 1 }),
        narrativeService.listNarratives(0, 1, false),
      ]);
      pendingContributions = stats.pending;
      pendingTags = tagsRes.total;
      pendingNarratives = narrativesRes.narratives.filter((n) => !n.is_approved).length > 0
        ? narrativesRes.total
        : 0;
    } catch {
      // counts are best-effort
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head><title>Curación · ROGER</title></svelte:head>

<div class="container mx-auto px-4 py-8 max-w-4xl">
  <h1 class="text-2xl font-bold mb-1">Panel de curación</h1>
  <p class="text-base-content/60 text-sm mb-8">Gestión de contenido y calidad del archivo</p>

  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">

    <!-- Moderación -->
    <a href="/curador/moderacion" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-warning/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          {#if !loading && (pendingContributions + pendingTags) > 0}
            <span class="badge badge-warning badge-sm">{pendingContributions + pendingTags} pendientes</span>
          {/if}
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Moderación</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">Revisión de contribuciones de usuarios y etiquetas sugeridas por IA.</p>
        <div class="mt-4 text-xs text-base-content/40 flex gap-3">
          {#if loading}
            <span class="loading loading-dots loading-xs"></span>
          {:else}
            <span>{pendingContributions} contribuciones</span>
            <span>{pendingTags} tags IA</span>
          {/if}
        </div>
      </div>
    </a>

    <!-- Metadatos -->
    <a href="/curador/metadatos" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-info/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Auditoría de metadatos</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">Vista completa de atributos taxonómicos 01–04 por fotografía.</p>
        <div class="mt-4 text-xs text-base-content/40">
          Técnicos · Cronología · Geográfico · Ambiental
        </div>
      </div>
    </a>

    <!-- Narrativas -->
    <a href="/curador/narrativas" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-success/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Narrativas IA</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">Revisar, aprobar y gestionar narrativas generadas por inteligencia artificial.</p>
        <div class="mt-4 text-xs text-base-content/40">
          VERAZ · VEROSÍMIL · confianza
        </div>
      </div>
    </a>

    <!-- Métricas FONDEF -->
    <a href="/curador/evaluacion" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-primary/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Métricas FONDEF</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">
          Dashboard ICa1–ICa4 calculado desde anotaciones de expertos. Muestra cumplimiento de indicadores.
        </p>
        <div class="mt-4 text-xs text-base-content/40">
          ICa1 ≥80% · ICa2 ≥70% · ICa3 ≥70% · ICa4 100%
        </div>
      </div>
    </a>

    <!-- Anotación de detecciones -->
    <a href="/curador/anotacion-objetos" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-error/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Anotación de objetos</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">
          Valida las detecciones YOLO: correcto / incorrecto / incierto. Ground truth para ICa1/ICa2.
        </p>
        <div class="mt-4 text-xs text-base-content/40">
          FONDEF ICa1 · ICa2 · mesa evaluadora
        </div>
      </div>
    </a>

    <!-- Anotación de descripciones -->
    <a href="/curador/anotacion-descripciones" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-accent/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </div>
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Anotación de descripciones</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">
          Escribe la descripción ground truth por fotografía y califica la calidad de la IA. Para ICa3.
        </p>
        <div class="mt-4 text-xs text-base-content/40">
          FONDEF ICa3 · similitud semántica · investigador
        </div>
      </div>
    </a>

    <!-- Narrativa temporal de colección -->
    <a href="/curador/narrativa-coleccion" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-secondary/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Narrativa temporal</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">
          Genera una narrativa cohesiva del corpus completo ordenando los clusters por cronología.
        </p>
        <div class="mt-4 text-xs text-base-content/40">
          Clustering visual · ordenamiento temporal · LLM
        </div>
      </div>
    </a>

    <!-- Comparación multi-LLM -->
    <a href="/curador/comparacion-llm" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-neutral/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-neutral-content" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </div>
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Comparación LLM</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">
          Envía el mismo contexto fotográfico a múltiples modelos en paralelo y compara sus respuestas.
        </p>
        <div class="mt-4 text-xs text-base-content/40">
          Groq · OpenAI · Anthropic · side-by-side
        </div>
      </div>
    </a>

    <!-- Georeferencia -->
    <a href="/curador/georeferencia" class="card bg-base-100 border border-base-200 hover:border-primary/40 hover:shadow-md transition-all group">
      <div class="card-body p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="p-2 bg-primary/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
        </div>
        <h2 class="font-semibold mb-1 group-hover:text-primary transition-colors">Georeferencia</h2>
        <p class="text-xs text-base-content/60 leading-relaxed">Validar, inferir y gestionar coordenadas geográficas de las fotografías.</p>
        <div class="mt-4 text-xs text-base-content/40">
          IA inferida · validación curador · mapa
        </div>
      </div>
    </a>

  </div>
</div>
