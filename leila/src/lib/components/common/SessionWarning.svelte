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
  // Período de gracia: no volver a mostrar la advertencia durante 5 min tras extender
  let gracePeriodUntil = 0;

  function checkTokenExpiration() {
    if (!$authStore.user) { showWarning = false; return; }

    const tokens = $authStore.tokens;
    if (!tokens?.access_token) {
      showWarning = false;
      return;
    }

    // Dentro del período de gracia → no molestar
    if (Date.now() < gracePeriodUntil) {
      showWarning = false;
      return;
    }

    const timeRemaining = getTimeUntilExpiration(tokens.access_token);
    minutesRemaining = Math.max(0, Math.floor(timeRemaining / 60000));

    const timeSinceActivity = activityTracker.getTimeSinceLastActivity();
    inactivityMinutes = Math.floor(timeSinceActivity / 60000);

    // Logout por inactividad (tiene prioridad)
    if (inactivityMinutes >= 30) {
      authStore.logout();
      return;
    }

    // Logout si el token ya expiró y el refresh no funcionó
    if (timeRemaining <= 0) {
      authStore.logout();
      return;
    }

    const tokenExpiringSoon = minutesRemaining <= 10;
    const inactivityWarning = inactivityMinutes >= 25;

    showWarning = tokenExpiringSoon || inactivityWarning;
  }

  async function extendSession() {
    showWarning = false;
    // Resetear actividad → reinicia el contador de 30 minutos
    activityTracker.updateActivity();
    // Período de gracia: evita que el aviso reaparezca mientras se refresca el token
    gracePeriodUntil = Date.now() + 5 * 60 * 1000;

    const tokens = $authStore.tokens;
    if (tokens?.refresh_token) {
      await tokenRefreshService.refreshToken(tokens.refresh_token, false);
    }
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
          {#if inactivityMinutes >= 25}
            Sin actividad por {inactivityMinutes} min. Se cerrará en {30 - inactivityMinutes} min.
          {:else}
            {minutesRemaining} minuto{minutesRemaining !== 1 ? 's' : ''} restante{minutesRemaining !== 1 ? 's' : ''}
          {/if}
        </div>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-sm btn-primary" on:click={extendSession}>
          Continuar sesión
        </button>
      </div>
    </div>
  </div>
{/if}
