<script lang="ts">
  import type { Image } from '$lib/types';
  import { createEventDispatcher } from 'svelte';

  export let image: Image;
  export let narratives: any[] = [];
  export let loading: boolean = false;

  const dispatch = createEventDispatcher();

  function handleClose() {
    dispatch('close');
  }

  function handleGenerateNarrative() {
    dispatch('generateNarrative', { imageId: image.id });
  }
</script>

<div class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
  <div class="bg-base-100 rounded-lg max-w-7xl w-full max-h-[90vh] overflow-hidden flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-base-300">
      <h2 class="text-2xl font-bold">{image.title}</h2>
      <button
        class="btn btn-ghost btn-circle"
        on:click={handleClose}
        aria-label="Cerrar"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
        <!-- Image -->
        <div class="flex items-center justify-center bg-base-200 rounded-lg overflow-hidden">
          <img
            src={image.file_path}
            alt={image.title}
            class="max-w-full max-h-[60vh] object-contain"
          />
        </div>

        <!-- Details -->
        <div class="space-y-6">
          <!-- Metadata -->
          <div class="card bg-base-200">
            <div class="card-body">
              <h3 class="card-title text-lg">Información</h3>

              <div class="space-y-2 text-sm">
                {#if image.year}
                  <div class="flex items-center gap-2">
                    <span class="font-semibold">Año:</span>
                    <span>{image.year}</span>
                  </div>
                {/if}

                {#if image.location}
                  <div class="flex items-center gap-2">
                    <span class="font-semibold">Ubicación:</span>
                    <span>{image.location}</span>
                  </div>
                {/if}

                {#if image.author}
                  <div class="flex items-center gap-2">
                    <span class="font-semibold">Autor:</span>
                    <span>{image.author}</span>
                  </div>
                {/if}

                {#if image.description}
                  <div class="mt-4">
                    <p class="font-semibold mb-2">Descripción:</p>
                    <p class="text-base-content/80">{image.description}</p>
                  </div>
                {/if}

                {#if image.tags && image.tags.length > 0}
                  <div class="mt-4">
                    <p class="font-semibold mb-2">Etiquetas:</p>
                    <div class="flex flex-wrap gap-2">
                      {#each image.tags as tag}
                        <span class="badge badge-primary badge-outline">{tag}</span>
                      {/each}
                    </div>
                  </div>
                {/if}
              </div>
            </div>
          </div>

          <!-- Narratives -->
          <div class="card bg-base-200">
            <div class="card-body">
              <div class="flex items-center justify-between">
                <h3 class="card-title text-lg">Narrativas</h3>
                <button
                  class="btn btn-primary btn-sm"
                  on:click={handleGenerateNarrative}
                  disabled={loading}
                >
                  {#if loading}
                    <span class="loading loading-spinner loading-sm"></span>
                  {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                  {/if}
                  Generar Narrativa
                </button>
              </div>

              {#if narratives.length === 0}
                <p class="text-sm text-base-content/70 mt-4">
                  No hay narrativas generadas para esta imagen. Genera una usando IA.
                </p>
              {:else}
                <div class="space-y-4 mt-4">
                  {#each narratives as narrative}
                    <div class="p-4 bg-base-100 rounded-lg border border-base-300">
                      <div class="flex items-center gap-2 mb-2">
                        <span class="badge badge-sm {narrative.is_verified ? 'badge-success' : 'badge-warning'}">
                          {narrative.is_verified ? 'Verificado' : 'Verosímil'}
                        </span>
                        <span class="badge badge-sm badge-outline">
                          Confianza: {Math.round(narrative.trazabilidad.confidence_score * 100)}%
                        </span>
                      </div>
                      <p class="text-sm text-base-content/90">{narrative.text}</p>
                      <p class="text-xs text-base-content/50 mt-2">
                        Generado: {new Date(narrative.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<svelte:window
  on:keydown={(e) => {
    if (e.key === 'Escape') {
      handleClose();
    }
  }}
/>
