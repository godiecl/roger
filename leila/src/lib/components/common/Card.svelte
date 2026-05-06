<script lang="ts">
  export let title: string | undefined = undefined;
  export let compact: boolean = false;
</script>

<div class="card bg-base-100 shadow-xl {compact ? 'card-compact' : ''}">
  {#if title || $$slots.title}
    <div class="card-body">
      {#if title}
        <h2 class="card-title">{title}</h2>
      {:else if $$slots.title}
        <div class="card-title">
          <slot name="title" />
        </div>
      {/if}

      <slot />

      {#if $$slots.actions}
        <div class="card-actions justify-end">
          <slot name="actions" />
        </div>
      {/if}
    </div>
  {:else}
    <div class="card-body">
      <slot />

      {#if $$slots.actions}
        <div class="card-actions justify-end">
          <slot name="actions" />
        </div>
      {/if}
    </div>
  {/if}
</div>
