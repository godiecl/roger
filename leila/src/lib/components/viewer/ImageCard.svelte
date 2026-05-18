<script lang="ts">
  import type { Image, Photograph } from '$lib/types';
  import { selection, isSelected } from '$lib/stores/selection';

  export let image: Image;
  export let onClick: ((image: Image) => void) | undefined = undefined;

  /** Habilita el modo selección: el card actúa como toggle (role=switch) */
  export let selectable: boolean = false;
  /** Objeto Photograph asociado, requerido cuando selectable=true */
  export let photograph: Photograph | undefined = undefined;

  $: selected = selectable && photograph ? $isSelected(photograph.id) : false;

  function handleClick() {
    if (selectable && photograph) {
      selection.toggle(photograph);
    } else if (onClick) {
      onClick(image);
    }
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleClick();
    }
  }
</script>

{#if selectable && photograph}
  <button
    type="button"
    class="card bg-base-100 shadow-xl hover:shadow-2xl transition-all duration-200 cursor-pointer group relative text-left p-0 w-full
           focus-visible:ring-4 focus-visible:ring-primary focus-visible:outline-none"
    class:ring-4={selected}
    class:ring-primary={selected}
    role="switch"
    aria-checked={selected}
    aria-label="{selected ? 'Quitar' : 'Añadir'} fotografía «{image.title}» {selected ? 'de' : 'a'} la selección"
    on:click={handleClick}
  >
    <span
      aria-hidden="true"
      class="absolute top-2 left-2 z-10 w-8 h-8 min-w-[44px] min-h-[44px] sm:min-w-0 sm:min-h-0 rounded-md border-2 flex items-center justify-center transition-all
             {selected
               ? 'bg-primary border-primary text-primary-content opacity-100'
               : 'bg-base-100/80 border-base-content/30 opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100'}"
    >
      {#if selected}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      {/if}
    </span>

    <figure class="relative overflow-hidden aspect-[4/3] rounded-t-2xl">
      {#if image.file_path}
        <img
          src={image.file_path}
          alt=""
          class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          loading="lazy"
        />
      {:else}
        <div class="w-full h-full flex items-center justify-center bg-base-300 text-base-content/40" aria-hidden="true">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      {/if}
      {#if !image.is_public}
        <span class="badge badge-warning absolute top-2 right-2" aria-label="Fotografía privada">Privada</span>
      {/if}
    </figure>

    <div class="card-body p-4">
      <h3 class="card-title text-base line-clamp-2">{image.title}</h3>

      <div class="flex flex-wrap gap-2 text-sm text-base-content/70">
        {#if image.year}
          <span class="badge badge-outline badge-sm">{image.year}</span>
        {/if}
        {#if image.location}
          <span class="badge badge-outline badge-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {image.location}
          </span>
        {/if}
      </div>

      {#if image.description}
        <p class="text-sm line-clamp-2 text-base-content/70 mt-2">{image.description}</p>
      {/if}

      {#if image.tags && image.tags.length > 0}
        <div class="flex flex-wrap gap-1 mt-2">
          {#each image.tags.slice(0, 3) as tag}
            <span class="badge badge-sm badge-ghost">{tag}</span>
          {/each}
          {#if image.tags.length > 3}
            <span class="badge badge-sm badge-ghost">+{image.tags.length - 3}</span>
          {/if}
        </div>
      {/if}
    </div>
  </button>
{:else}
  <div
    class="card bg-base-100 shadow-xl hover:shadow-2xl transition-all duration-200 cursor-pointer group
           focus-visible:ring-4 focus-visible:ring-primary focus-visible:outline-none"
    on:click={handleClick}
    on:keydown={handleKeyDown}
    role="button"
    tabindex="0"
  >
    <figure class="relative overflow-hidden aspect-[4/3] rounded-t-2xl">
      {#if image.file_path}
        <img
          src={image.file_path}
          alt={image.title}
          class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          loading="lazy"
        />
      {:else}
        <div class="w-full h-full flex items-center justify-center bg-base-300 text-base-content/40" aria-hidden="true">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      {/if}
      {#if !image.is_public}
        <span class="badge badge-warning absolute top-2 right-2" aria-label="Fotografía privada">Privada</span>
      {/if}
    </figure>

    <div class="card-body p-4">
      <h3 class="card-title text-base line-clamp-2">{image.title}</h3>

      <div class="flex flex-wrap gap-2 text-sm text-base-content/70">
        {#if image.year}
          <span class="badge badge-outline badge-sm">{image.year}</span>
        {/if}
        {#if image.location}
          <span class="badge badge-outline badge-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {image.location}
          </span>
        {/if}
      </div>

      {#if image.description}
        <p class="text-sm line-clamp-2 text-base-content/70 mt-2">{image.description}</p>
      {/if}

      {#if image.tags && image.tags.length > 0}
        <div class="flex flex-wrap gap-1 mt-2">
          {#each image.tags.slice(0, 3) as tag}
            <span class="badge badge-sm badge-ghost">{tag}</span>
          {/each}
          {#if image.tags.length > 3}
            <span class="badge badge-sm badge-ghost">+{image.tags.length - 3}</span>
          {/if}
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-clamp: 2;
    overflow: hidden;
  }
</style>
