<script lang="ts">
  export let title: string = 'Error';
  export let message: string;
  export let onRetry: (() => void) | null = null;
</script>

<div class="alert alert-error shadow-lg">
  <div>
    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <div>
      <h3 class="font-bold">{title}</h3>
      <div class="text-sm">{message}</div>
    </div>
  </div>
  {#if onRetry}
    <div class="flex-none">
      <button class="btn btn-sm btn-ghost" on:click={onRetry}>Reintentar</button>
    </div>
  {/if}
</div>
