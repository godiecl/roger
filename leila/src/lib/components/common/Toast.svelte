<script lang="ts">
  import { fly } from 'svelte/transition';
  import { notificationsStore } from '$lib/stores/notifications';
  import type { Notification } from '$lib/stores/notifications';

  $: notifications = $notificationsStore.notifications;

  const palette: Record<string, { stripe: string; icon: string; ring: string }> = {
    success: { stripe: 'bg-success',  icon: 'text-success bg-success/10',  ring: 'border-success/20'  },
    error:   { stripe: 'bg-error',    icon: 'text-error bg-error/10',      ring: 'border-error/20'    },
    warning: { stripe: 'bg-warning',  icon: 'text-warning bg-warning/10',  ring: 'border-warning/20'  },
    info:    { stripe: 'bg-info',     icon: 'text-info bg-info/10',        ring: 'border-info/20'     },
  };

  const iconPaths: Record<string, string> = {
    success: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    error:   'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
    warning: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
    info:    'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  };

  function c(type: string) {
    return palette[type] ?? palette.info;
  }

  function dismiss(n: Notification) {
    notificationsStore.dismiss(n.id);
  }
</script>

<div class="fixed top-4 right-4 z-[999] flex flex-col gap-2.5 w-80 pointer-events-none">
  {#each notifications as n (n.id)}
    <div
      class="pointer-events-auto"
      in:fly={{ x: 48, duration: 220, opacity: 0 }}
      out:fly={{ x: 380, duration: 300, opacity: 0 }}
    >
      <div class="relative overflow-hidden rounded-2xl bg-base-100 border {c(n.type).ring} shadow-2xl shadow-base-content/10">

        <!-- Colored left stripe -->
        <div class="absolute inset-y-0 left-0 w-1 {c(n.type).stripe}"></div>

        <div class="flex items-start gap-3 px-4 py-3.5 pl-5">

          <!-- Icon -->
          <div class="flex-shrink-0 w-8 h-8 rounded-full {c(n.type).icon} flex items-center justify-center mt-0.5">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d={iconPaths[n.type] ?? iconPaths.info} />
            </svg>
          </div>

          <!-- Text -->
          <div class="flex-1 min-w-0 pr-5">
            {#if n.title}
              <p class="text-sm font-bold text-base-content leading-tight">{n.title}</p>
              <p class="text-xs text-base-content/60 mt-0.5 leading-snug">{n.message}</p>
            {:else}
              <p class="text-sm font-medium text-base-content leading-snug">{n.message}</p>
            {/if}
          </div>

        </div>

        <!-- Dismiss button -->
        {#if n.dismissible}
          <button
            class="absolute top-2.5 right-2.5 w-6 h-6 flex items-center justify-center rounded-full text-base-content/25 hover:text-base-content/60 hover:bg-base-200 transition-colors"
            on:click={() => dismiss(n)}
            aria-label="Cerrar"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        {/if}

        <!-- Progress bar -->
        {#if n.duration && n.duration > 0}
          <div class="h-0.5 bg-base-200">
            <div
              class="{c(n.type).stripe} h-full opacity-50"
              style="animation: toast-shrink {n.duration}ms linear forwards"
            ></div>
          </div>
        {/if}

      </div>
    </div>
  {/each}
</div>

<style>
  @keyframes toast-shrink {
    from { width: 100%; }
    to   { width: 0%; }
  }
</style>
