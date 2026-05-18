<script lang="ts">
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/services/apiClient';
  import { notificationsStore } from '$lib/stores/notifications';

  export let contentType: 'context' | 'narrative';
  export let contentId: number;
  export let likeCount: number = 0;

  let liked = false;
  let reported = false;
  let ready = false;           // false during 3s anti-spam window
  let count = likeCount;
  let likeLoading = false;
  let reportLoading = false;
  let showConfirm = false;

  const likeKey   = () => `roger_like_${contentType}_${contentId}`;
  const reportKey = () => `roger_report_${contentType}_${contentId}`;
  const endpoint  = () => contentType === 'context' ? `/context/${contentId}` : `/narratives/${contentId}`;

  onMount(() => {
    liked    = localStorage.getItem(likeKey())   === 'true';
    reported = localStorage.getItem(reportKey()) === 'true';

    const timer = setTimeout(() => { ready = true; }, 3000);
    return () => clearTimeout(timer);
  });

  async function toggleLike() {
    if (!ready || likeLoading) return;

    const wasLiked = liked;
    const prevCount = count;

    // Optimistic update
    liked = !wasLiked;
    count = wasLiked ? Math.max(0, count - 1) : count + 1;
    likeLoading = true;

    try {
      const res = await apiClient.post<{ liked: boolean; like_count: number }>(
        `${endpoint()}/like`
      );
      liked = res.liked;
      count = res.like_count;
      localStorage.setItem(likeKey(), String(liked));
    } catch {
      // Revert
      liked = wasLiked;
      count = prevCount;
      notificationsStore.error('No se pudo registrar el like');
    } finally {
      likeLoading = false;
    }
  }

  async function submitReport() {
    showConfirm = false;
    if (reportLoading) return;
    reportLoading = true;

    try {
      await apiClient.post(`${endpoint()}/report`, {});
      reported = true;
      localStorage.setItem(reportKey(), 'true');
    } catch (e: any) {
      if (e.status === 409) {
        reported = true;
        localStorage.setItem(reportKey(), 'true');
      } else {
        notificationsStore.error('No se pudo enviar el reporte');
      }
    } finally {
      reportLoading = false;
    }
  }
</script>

<div class="flex items-center gap-3" role="group" aria-label="Acciones de contenido">
  <!-- Like button -->
  <button
    class="flex items-center gap-1.5 text-sm transition-colors
      {liked
        ? 'text-rose-500 hover:text-rose-400'
        : 'text-base-content/40 hover:text-rose-400'}
      disabled:opacity-40 disabled:cursor-not-allowed"
    on:click={toggleLike}
    disabled={!ready || likeLoading}
    aria-label={liked ? 'Quitar like' : 'Dar like'}
    aria-pressed={liked}
  >
    {#if likeLoading}
      <span class="loading loading-spinner loading-xs"></span>
    {:else if liked}
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
        <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
      </svg>
    {:else}
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
    {/if}
    <span>{count}</span>
  </button>

  <!-- Report button -->
  {#if reported}
    <span class="flex items-center gap-1 text-xs text-base-content/35" aria-label="Contenido reportado">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
      </svg>
      Reportado
    </span>
  {:else}
    <button
      class="flex items-center gap-1 text-xs text-base-content/35 hover:text-warning transition-colors
        disabled:opacity-40 disabled:cursor-not-allowed"
      on:click={() => { if (ready && !reportLoading) showConfirm = true; }}
      disabled={!ready || reportLoading}
      aria-label="Reportar contenido"
    >
      {#if reportLoading}
        <span class="loading loading-spinner loading-xs"></span>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
        </svg>
      {/if}
      Reportar
    </button>
  {/if}
</div>

<!-- Confirm report modal -->
{#if showConfirm}
  <div
    class="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4"
    on:click|self={() => { showConfirm = false; }}
    role="presentation"
  >
    <div
      class="bg-base-100 rounded-xl p-6 max-w-sm w-full shadow-2xl"
      role="dialog"
      aria-modal="true"
      aria-labelledby="report-title"
    >
      <h3 id="report-title" class="font-semibold text-base mb-2">¿Reportar este contenido?</h3>
      <p class="text-sm text-base-content/60 mb-5 leading-relaxed">
        Indica que el contenido tiene errores o información incorrecta. Un curador lo revisará.
      </p>
      <div class="flex gap-2 justify-end">
        <button
          class="btn btn-ghost btn-sm"
          on:click={() => { showConfirm = false; }}
        >
          Cancelar
        </button>
        <button
          class="btn btn-warning btn-sm"
          on:click={submitReport}
        >
          Reportar
        </button>
      </div>
    </div>
  </div>
{/if}
