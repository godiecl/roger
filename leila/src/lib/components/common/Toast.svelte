<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import { notificationsStore } from '$lib/stores/notifications';
  import type { Notification } from '$lib/stores/notifications';

  $: notifications = $notificationsStore.notifications;

  function getAlertClass(type: string): string {
    switch (type) {
      case 'success':
        return 'alert-success';
      case 'error':
        return 'alert-error';
      case 'warning':
        return 'alert-warning';
      case 'info':
        return 'alert-info';
      default:
        return '';
    }
  }

  function getIcon(type: string) {
    switch (type) {
      case 'success':
        return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />`;
      case 'error':
        return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />`;
      case 'warning':
        return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />`;
      case 'info':
        return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />`;
      default:
        return '';
    }
  }

  function dismiss(notification: Notification) {
    notificationsStore.dismiss(notification.id);
  }
</script>

<div class="toast toast-top toast-end z-50">
  {#each notifications as notification (notification.id)}
    <div
      class="alert {getAlertClass(notification.type)} shadow-lg"
      in:fly={{ x: 300, duration: 300 }}
      out:fly={{ x: 300, duration: 300, opacity: 0 }}
    >
      <div>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="stroke-current flex-shrink-0 h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
        >
          {@html getIcon(notification.type)}
        </svg>
        <div>
          {#if notification.title}
            <h3 class="font-bold">{notification.title}</h3>
          {/if}
          <div class="text-sm">{notification.message}</div>
        </div>
      </div>
      {#if notification.dismissible}
        <button
          class="btn btn-sm btn-ghost btn-circle"
          on:click={() => dismiss(notification)}
          aria-label="Cerrar notificación"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      {/if}
    </div>
  {/each}
</div>
