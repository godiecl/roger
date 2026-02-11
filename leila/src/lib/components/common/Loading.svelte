<script lang="ts">
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let text: string = 'Cargando...';

  const sizeClasses = {
    sm: 'loading-sm',
    md: 'loading-md',
    lg: 'loading-lg'
  };
</script>

<div class="flex flex-col items-center justify-center gap-4 p-8">
  <span class="loading loading-spinner {sizeClasses[size]} text-primary"></span>
  {#if text}
    <p class="text-sm text-base-content/70">{text}</p>
  {/if}
</div>
