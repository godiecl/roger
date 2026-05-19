<script lang="ts">
  import { onMount } from 'svelte';
  import { imageService } from '$lib/services/imageService';
  import { timelineService, type TimelineEvent } from '$lib/services/timelineService';
  import type { Image } from '$lib/types';

  interface YearBlock {
    year: number;
    photos: Image[];
    events: TimelineEvent[];
    eventsState: 'idle' | 'loading' | 'done' | 'empty';
  }

  let blocks: YearBlock[] = [];
  let loading = true;
  let error: string | null = null;

  onMount(async () => {
    try {
      const response = await imageService.listImages({ skip: 0, limit: 1000 });
      const withYear = response.images.filter((img) => img.year != null);

      const byYear = new Map<number, Image[]>();
      for (const img of withYear) {
        const y = img.year!;
        if (!byYear.has(y)) byYear.set(y, []);
        byYear.get(y)!.push(img);
      }

      blocks = [...byYear.entries()]
        .sort(([a], [b]) => a - b)
        .map(([year, photos]) => ({ year, photos, events: [], eventsState: 'idle' }));
    } catch (e: any) {
      error = e?.detail || 'Error al cargar las fotografías';
    } finally {
      loading = false;
    }
  });

  function lazyWikipedia(node: Element, index: number) {
    const observer = new IntersectionObserver(
      async (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          observer.disconnect();

          const block = blocks[index];
          if (block.eventsState !== 'idle') return;

          blocks[index] = { ...block, eventsState: 'loading' };
          blocks = blocks;

          try {
            const events = await timelineService.getWikipediaEvents(block.year);
            blocks[index] = {
              ...blocks[index],
              events,
              eventsState: events.length > 0 ? 'done' : 'empty',
            };
          } catch {
            blocks[index] = { ...blocks[index], eventsState: 'empty' };
          }
          blocks = blocks;
        }
      },
      { rootMargin: '300px' },
    );
    observer.observe(node);
    return { destroy: () => observer.disconnect() };
  }
</script>

<svelte:head>
  <title>Línea de tiempo · ROGER</title>
  <meta
    name="description"
    content="Recorre cronológicamente la colección fotográfica de Robert Gerstmann y el contexto histórico de cada época."
  />
</svelte:head>

<div class="container mx-auto px-4 sm:px-6 py-10 max-w-4xl">
  <header class="mb-10">
    <h1 class="text-4xl font-bold mb-2">Línea de tiempo</h1>
    <p class="text-base-content/60 text-lg">
      La colección ordenada cronológicamente con el contexto histórico de cada año.
    </p>
  </header>

  {#if loading}
    <div class="space-y-8">
      {#each Array(5) as _}
        <div class="flex gap-6">
          <div class="skeleton w-16 h-8 rounded shrink-0"></div>
          <div class="flex-1 space-y-3">
            <div class="skeleton h-4 w-full rounded"></div>
            <div class="skeleton h-4 w-3/4 rounded"></div>
            <div class="flex gap-2 mt-3">
              {#each Array(3) as _}
                <div class="skeleton w-20 h-20 rounded"></div>
              {/each}
            </div>
          </div>
        </div>
      {/each}
    </div>

  {:else if error}
    <div class="alert alert-error">
      <span>{error}</span>
    </div>

  {:else if blocks.length === 0}
    <div class="alert alert-info">
      <span>No hay fotografías con fecha registrada en la colección.</span>
    </div>

  {:else}
    <ol class="relative border-l border-base-300 space-y-0 ml-4">
      {#each blocks as block, i (block.year)}
        <li class="mb-12 ml-8" use:lazyWikipedia={i}>
          <!-- Year marker -->
          <span
            class="absolute -left-4 flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-content text-xs font-bold shadow"
            aria-hidden="true"
          ></span>
          <h2 class="text-2xl font-bold text-primary mb-4">{block.year}</h2>

          <!-- Photos row -->
          <div class="flex flex-wrap gap-2 mb-5">
            {#each block.photos.slice(0, 6) as photo (photo.id)}
              <a
                href="/colecciones?image={photo.id}"
                class="block w-20 h-20 rounded overflow-hidden bg-base-200 hover:opacity-80 transition-opacity focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                aria-label={photo.title}
              >
                {#if photo.file_path}
                  <img
                    src={photo.file_path}
                    alt={photo.title}
                    class="w-full h-full object-cover"
                    loading="lazy"
                  />
                {:else}
                  <div class="w-full h-full flex items-center justify-center text-base-content/30">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                {/if}
              </a>
            {/each}
            {#if block.photos.length > 6}
              <a
                href="/colecciones?year={block.year}"
                class="w-20 h-20 rounded bg-base-200 flex items-center justify-center text-xs text-base-content/60 hover:bg-base-300 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              >
                +{block.photos.length - 6} más
              </a>
            {/if}
          </div>

          <!-- Wikipedia events -->
          {#if block.eventsState === 'loading'}
            <div class="space-y-2" aria-live="polite" aria-label="Cargando contexto histórico">
              {#each Array(3) as _}
                <div class="skeleton h-4 w-full rounded"></div>
              {/each}
            </div>

          {:else if block.eventsState === 'done'}
            <section aria-label="Contexto histórico {block.year}">
              <p class="text-xs font-semibold text-base-content/40 uppercase tracking-wider mb-2">
                Contexto histórico
              </p>
              <ul class="space-y-3">
                {#each block.events as event (event.title)}
                  <li class="border-l-2 border-info pl-3">
                    <p class="text-sm font-medium leading-snug">{event.title}</p>
                    {#if event.description !== event.title}
                      <p class="text-xs text-base-content/60 mt-0.5 leading-relaxed">
                        {event.description}
                      </p>
                    {/if}
                  </li>
                {/each}
              </ul>
            </section>
          {/if}
        </li>
      {/each}
    </ol>
  {/if}
</div>
