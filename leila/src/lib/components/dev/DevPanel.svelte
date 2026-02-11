<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { dev } from '$app/environment';
  import { authStore } from '$lib/stores/auth';
  import { activityTracker } from '$lib/services/activityTracker';
  import { getTimeUntilExpiration, getTokenExpiration, parseJWT } from '$lib/utils/token.utils';

  // Only show in development
  if (!dev) {
    // Component should not render in production
  }

  let isOpen = true;
  let isMinimized = false;
  let tokenInfo: any = null;
  let activityInfo = {
    lastActivity: 0,
    isActive: false,
    timeSinceActivity: 0
  };
  let updateInterval: number | null = null;

  function updateInfo() {
    if ($authStore.tokens?.access_token) {
      tokenInfo = parseJWT($authStore.tokens.access_token);
    }

    // Update activity info
    activityTracker.subscribe(state => {
      activityInfo = {
        ...state,
        timeSinceActivity: Date.now() - state.lastActivity
      };
    })();
  }

  function togglePanel() {
    isOpen = !isOpen;
  }

  function toggleMinimize() {
    isMinimized = !isMinimized;
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
  }

  function formatTime(ms: number): string {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  }

  function formatDate(timestamp: number): string {
    return new Date(timestamp * 1000).toLocaleString('es-CL');
  }

  onMount(() => {
    updateInfo();
    updateInterval = setInterval(updateInfo, 1000) as unknown as number;
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
  });

  $: timeUntilExpiration = $authStore.tokens?.access_token
    ? getTimeUntilExpiration($authStore.tokens.access_token)
    : 0;
</script>

{#if dev && isOpen}
  <div class="fixed bottom-4 right-4 z-[9999] font-mono">
    <div class="card bg-base-100 shadow-2xl border-2 border-primary w-96">
      <!-- Header -->
      <div class="card-body p-3">
        <div class="flex items-center justify-between mb-2">
          <h3 class="card-title text-sm flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            Dev Panel
            <span class="badge badge-xs badge-success">DEV</span>
          </h3>
          <div class="flex gap-1">
            <button
              class="btn btn-ghost btn-xs"
              on:click={toggleMinimize}
              title={isMinimized ? 'Expandir' : 'Minimizar'}
            >
              {isMinimized ? '▲' : '▼'}
            </button>
            <button
              class="btn btn-ghost btn-xs"
              on:click={togglePanel}
              title="Cerrar"
            >
              ✕
            </button>
          </div>
        </div>

        {#if !isMinimized}
          <div class="divider my-0"></div>

          <!-- Authentication Status -->
          <div class="space-y-2 text-xs">
            <div class="flex items-center gap-2">
              <span class="font-semibold">Estado:</span>
              {#if $authStore.user}
                <span class="badge badge-success badge-sm">Autenticado</span>
              {:else}
                <span class="badge badge-error badge-sm">No autenticado</span>
              {/if}
            </div>

            {#if $authStore.user}
              <!-- User Info -->
              <div class="bg-base-200 p-2 rounded space-y-1">
                <div class="font-semibold text-primary">👤 Usuario</div>
                <div><span class="text-slate-500">ID:</span> {$authStore.user.id}</div>
                <div><span class="text-slate-500">Email:</span> {$authStore.user.email}</div>
                <div><span class="text-slate-500">Nombre:</span> {$authStore.user.full_name || 'N/A'}</div>
                <div>
                  <span class="text-slate-500">Rol:</span>
                  <span class="badge badge-primary badge-xs capitalize">
                    {$authStore.user.role?.replace('_', ' ')}
                  </span>
                </div>
                <div>
                  <span class="text-slate-500">Activo:</span>
                  {$authStore.user.is_active ? '✅' : '❌'}
                </div>
                <div>
                  <span class="text-slate-500">Verificado:</span>
                  {$authStore.user.is_verified ? '✅' : '❌'}
                </div>
              </div>

              <!-- Token Info -->
              <div class="bg-base-200 p-2 rounded space-y-1">
                <div class="font-semibold text-secondary">🔑 Token</div>
                {#if tokenInfo}
                  <div>
                    <span class="text-slate-500">Expira en:</span>
                    <span class="badge badge-sm" class:badge-error={timeUntilExpiration < 5 * 60 * 1000}>
                      {formatTime(timeUntilExpiration)}
                    </span>
                  </div>
                  <div><span class="text-slate-500">Exp:</span> {formatDate(tokenInfo.exp)}</div>
                  <div><span class="text-slate-500">Type:</span> {tokenInfo.type || 'access'}</div>
                {:else}
                  <div class="text-slate-500">No token info</div>
                {/if}

                <button
                  class="btn btn-xs btn-outline w-full mt-1"
                  on:click={() => copyToClipboard($authStore.tokens?.access_token || '')}
                >
                  📋 Copiar Access Token
                </button>
              </div>

              <!-- Activity Info -->
              <div class="bg-base-200 p-2 rounded space-y-1">
                <div class="font-semibold text-accent">⚡ Actividad</div>
                <div>
                  <span class="text-slate-500">Estado:</span>
                  {#if activityInfo.isActive}
                    <span class="badge badge-success badge-xs">Activo</span>
                  {:else}
                    <span class="badge badge-warning badge-xs">Inactivo</span>
                  {/if}
                </div>
                <div>
                  <span class="text-slate-500">Última actividad:</span>
                  {formatTime(activityInfo.timeSinceActivity)} atrás
                </div>
                <div>
                  <span class="text-slate-500">Timeout en:</span>
                  {formatTime(Math.max(0, (30 * 60 * 1000) - activityInfo.timeSinceActivity))}
                </div>
              </div>

              <!-- Local Storage Info -->
              <div class="bg-base-200 p-2 rounded space-y-1">
                <div class="font-semibold text-info">💾 Storage</div>
                <div class="text-[10px] break-all">
                  <span class="text-slate-500">Tokens:</span>
                  {localStorage.getItem('auth_tokens') ? '✅ Guardado' : '❌ No guardado'}
                </div>
                <div class="text-[10px] break-all">
                  <span class="text-slate-500">User:</span>
                  {localStorage.getItem('auth_user') ? '✅ Guardado' : '❌ No guardado'}
                </div>
              </div>

              <!-- Actions -->
              <div class="flex gap-2 mt-2">
                <button
                  class="btn btn-error btn-xs flex-1"
                  on:click={() => authStore.logout()}
                >
                  🚪 Logout
                </button>
                <button
                  class="btn btn-outline btn-xs flex-1"
                  on:click={updateInfo}
                >
                  🔄 Refresh
                </button>
              </div>
            {:else}
              <div class="text-center text-slate-500 py-4">
                No hay usuario autenticado
              </div>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
{:else if dev && !isOpen}
  <!-- Floating button to reopen -->
  <button
    class="fixed bottom-4 right-4 z-[9999] btn btn-circle btn-primary shadow-lg"
    on:click={togglePanel}
    title="Abrir Dev Panel"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    </svg>
  </button>
{/if}

<style>
  /* Make sure it's always on top */
  :global(.fixed.z-\[9999\]) {
    z-index: 9999 !important;
  }
</style>
