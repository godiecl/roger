<script lang="ts">
  import type { Box } from '$lib/types';

  export let box: Box;
  export let collectionName: string | undefined = undefined;
  export let onClick: ((box: Box) => void) | undefined = undefined;

  function handleClick() {
    if (onClick) onClick(box);
  }
</script>

<button
  type="button"
  class="card bg-base-100 shadow-md hover:shadow-xl hover:-translate-y-0.5 transition-all duration-200 cursor-pointer group text-left p-0 w-full focus-visible:ring-4 focus-visible:ring-primary focus-visible:outline-none"
  on:click={handleClick}
  aria-label="Abrir cajón {box.box_number}{box.name ? `: ${box.name}` : ''}"
>
  <div class="card-body p-5">
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10 text-primary group-hover:bg-primary/20 transition-colors" aria-hidden="true">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
      </div>
      <span class="badge badge-ghost text-xs">Cajón #{box.box_number}</span>
    </div>

    <h3 class="card-title text-lg mt-2 line-clamp-2">
      {box.name || `Cajón ${box.box_number}`}
    </h3>

    {#if collectionName}
      <p class="text-sm text-base-content/60">{collectionName}</p>
    {/if}

    {#if box.location_in_archive}
      <p class="text-xs text-base-content/50 mt-1 flex items-center gap-1">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        {box.location_in_archive}
      </p>
    {/if}
  </div>
</button>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-clamp: 2;
    overflow: hidden;
  }
</style>
