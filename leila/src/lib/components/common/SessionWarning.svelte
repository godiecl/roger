<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { authStore } from '$lib/stores/auth';
  import { getTimeUntilExpiration } from '$lib/utils/token.utils';
  import { activityTracker } from '$lib/services/activityTracker';
  import { tokenRefreshService } from '$lib/services/tokenRefreshService';

  let showWarning = false;
  let minutesRemaining = 0;
  let inactivityMinutes = 0;
  let intervalId: number | null = null;

  function checkTokenExpiration() {
    const tokens = $authStore.tokens;
    if (!tokens?.access_token) {
      showWarning = false;
      return;
    }

    const timeRemaining = getTimeUntilExpiration(tokens.access_token);
    minutesRemaining = Math.floor(timeRemaining / 60000); // Convert to minutes

    // Check inactivity
    const timeSinceActivity = activityTracker.getTimeSinceLastActivity();
    inactivityMinutes = Math.floor(timeSinceActivity / 60000);

    // Show warning if:
    // 1. Less than 10 minutes until token expires, OR
    // 2. Inactive for more than 25 minutes (5 min warning before 30 min timeout)
    const tokenExpiringSoon = minutesRemaining <= 10 && minutesRemaining > 0;
    const inactivityWarning = inactivityMinutes >= 25 && inactivityMinutes < 30;

    showWarning = tokenExpiringSoon || inactivityWarning;

    // If inactive for 30+ minutes, logout
    if (inactivityMinutes >= 30 && $authStore.user) {
      authStore.logout();
    }
  }

  async function extendSession() {
    // Refresh activity
    activityTracker.updateActivity();

    // Trigger token refresh if needed
    const tokens = $authStore.tokens;
    if (tokens?.refresh_token) {
      await tokenRefreshService.refreshToken(tokens.refresh_token);
    }

    showWarning = false;
  }

  onMount(() => {
    // Start tracking user activity
    activityTracker.startTracking();

    // Start automatic token refresh
    tokenRefreshService.start();

    // Check every 30 seconds
    intervalId = setInterval(checkTokenExpiration, 30000) as unknown as number;
    checkTokenExpiration();
  });

  onDestroy(() => {
    if (intervalId) {
      clearInterval(intervalId);
    }
    activityTracker.stopTracking();
    tokenRefreshService.stop();
  });
</script>

{#if showWarning}
  <div class="toast toast-top toast-center z-50">
    <div class="alert alert-warning shadow-lg max-w-md">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="stroke-current flex-shrink-0 h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
      <div>
        <h3 class="font-bold">Tu sesión expirará pronto</h3>
        <div class="text-sm">
          {minutesRemaining} minuto{minutesRemaining !== 1 ? 's' : ''} restante{minutesRemaining !== 1 ? 's' : ''}
        </div>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-sm btn-ghost" on:click={() => showWarning = false}>
          Ignorar
        </button>
        <button class="btn btn-sm btn-primary" on:click={extendSession}>
          Continuar sesión
        </button>
      </div>
    </div>
  </div>
{/if}
