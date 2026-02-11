<script lang="ts">
  import type { Image } from '$lib/types';
  import ImageCard from './ImageCard.svelte';
  import Loading from '../common/Loading.svelte';
  import ErrorMessage from '../common/ErrorMessage.svelte';

  export let images: Image[] = [];
  export let loading: boolean = false;
  export let error: string | null = null;
  export let onImageClick: ((image: Image) => void) | undefined = undefined;
  export let onRetry: (() => void) | null = null;
</script>

{#if loading}
  <Loading text="Cargando imágenes..." />
{:else if error}
  <ErrorMessage
    title="Error al cargar imágenes"
    message={error}
    {onRetry}
  />
{:else if images.length === 0}
  <div class="text-center py-12">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-base-content/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
    <p class="text-lg text-base-content/70 mt-4">No se encontraron imágenes</p>
    <p class="text-sm text-base-content/50 mt-2">Intenta ajustar los filtros de búsqueda</p>
  </div>
{:else}
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    {#each images as image (image.id)}
      <ImageCard {image} onClick={onImageClick} />
    {/each}
  </div>
{/if}
