<script lang="ts">
  import { fly } from 'svelte/transition';
  import { selection, selectedCount, canCluster, MIN_FOR_CLUSTERING } from '$lib/stores/selection';

  export let onCluster: () => void = () => {};
  export let onTimeline: () => void = () => {};
  export let onAddToProject: () => void = () => {};
  export let busy: boolean = false;

  $: needed = Math.max(0, MIN_FOR_CLUSTERING - $selectedCount);
</script>

{#if $selectedCount > 0}
  <div
    class="fixed bottom-4 left-1/2 -translate-x-1/2 z-40 max-w-3xl w-[min(95vw,720px)]"
    transition:fly={{ y: 100, duration: 220 }}
  >
    <div class="bg-base-100 shadow-2xl border border-base-300 rounded-2xl px-4 py-3 flex flex-wrap items-center gap-3">
      <div class="flex items-center gap-2 flex-1 min-w-0">
        <span class="badge badge-primary badge-lg">{$selectedCount}</span>
        <span class="font-medium truncate">
          {$selectedCount === 1 ? 'foto seleccionada' : 'fotos seleccionadas'}
        </span>
      </div>

      <div class="flex flex-wrap gap-2 items-center">
        <button class="btn btn-ghost btn-sm" on:click={() => selection.clear()} disabled={busy}>
          Limpiar
        </button>

        <div class="tooltip tooltip-top" data-tip={$canCluster ? 'Agrupar por similitud semántica' : `Selecciona ${needed} foto${needed !== 1 ? 's' : ''} más`}>
          <button
            class="btn btn-sm btn-secondary"
            on:click={onCluster}
            disabled={!$canCluster || busy}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 110-6 3 3 0 010 6z" />
            </svg>
            Agrupar
          </button>
        </div>

        <div class="tooltip tooltip-top" data-tip="Línea de tiempo">
          <button class="btn btn-sm btn-accent" on:click={onTimeline} disabled={$selectedCount < 2 || busy}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Tiempo
          </button>
        </div>

        <button class="btn btn-sm btn-primary" on:click={onAddToProject} disabled={busy}>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Añadir a proyecto
        </button>
      </div>
    </div>
  </div>
{/if}
