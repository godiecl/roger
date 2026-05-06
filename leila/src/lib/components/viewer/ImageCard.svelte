<script lang="ts">
  import type { Image } from '$lib/types';

  export let image: Image;
  export let onClick: ((image: Image) => void) | undefined = undefined;

  function handleClick() {
    if (onClick) {
      onClick(image);
    }
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' || event.key === ' ') {
      handleClick();
    }
  }
</script>

<div
  class="card bg-base-100 shadow-xl hover:shadow-2xl transition-all duration-200 cursor-pointer group"
  on:click={handleClick}
  on:keypress={handleKeyPress}
  role="button"
  tabindex="0"
>
  <figure class="relative overflow-hidden aspect-[4/3]">
    <img
      src={image.file_path}
      alt={image.title}
      class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
      loading="lazy"
    />
    {#if !image.is_public}
      <div class="badge badge-warning absolute top-2 right-2">Privada</div>
    {/if}
  </figure>

  <div class="card-body p-4">
    <h3 class="card-title text-base line-clamp-2">
      {image.title}
    </h3>

    <div class="flex flex-wrap gap-2 text-sm text-base-content/70">
      {#if image.year}
        <span class="badge badge-outline badge-sm">{image.year}</span>
      {/if}
      {#if image.location}
        <span class="badge badge-outline badge-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {image.location}
        </span>
      {/if}
    </div>

    {#if image.description}
      <p class="text-sm line-clamp-2 text-base-content/70 mt-2">
        {image.description}
      </p>
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

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
