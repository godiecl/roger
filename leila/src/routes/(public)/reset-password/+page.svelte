<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { authService } from '$lib/services';

  $: token = $page.url.searchParams.get('token') ?? '';

  let password = '';
  let confirmPassword = '';
  let loading = false;
  let error = '';
  let success = false;

  async function handleSubmit() {
    error = '';

    if (!token) {
      error = 'Enlace inválido o expirado. Solicita uno nuevo.';
      return;
    }
    if (password.length < 8) {
      error = 'La contraseña debe tener al menos 8 caracteres.';
      return;
    }
    if (password !== confirmPassword) {
      error = 'Las contraseñas no coinciden.';
      return;
    }

    loading = true;
    try {
      await authService.resetPassword(token, password);
      success = true;
      setTimeout(() => goto('/login'), 3000);
    } catch (e: any) {
      error = e.detail || 'El enlace es inválido o ha expirado. Solicita uno nuevo.';
    } finally {
      loading = false;
    }
  }

  $: strength = password.length === 0 ? 0
    : password.length < 6 ? 1
    : password.length < 8 ? 2
    : /[A-Z]/.test(password) && /[0-9]/.test(password) ? 4
    : 3;

  const strengthLabel = ['', 'Muy débil', 'Débil', 'Aceptable', 'Segura'];
  const strengthColor = ['', 'bg-error', 'bg-warning', 'bg-info', 'bg-success'];
</script>

<svelte:head>
  <title>Nueva contraseña — ROGER</title>
</svelte:head>

<div class="min-h-[80vh] flex items-center justify-center px-4">
  <div class="w-full max-w-md">

    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold text-base-content">Nueva contraseña</h1>
      <p class="text-base-content/50 mt-2 text-sm">Elige una contraseña segura para tu cuenta.</p>
    </div>

    <div class="card bg-base-100 shadow-xl border border-base-200">
      <div class="card-body">

        {#if !token}
          <!-- Token ausente -->
          <div class="text-center py-4 space-y-4">
            <div class="w-16 h-16 bg-error/10 rounded-full flex items-center justify-center mx-auto">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
              </svg>
            </div>
            <p class="text-sm text-base-content/60">Enlace inválido o expirado.</p>
            <a href="/forgot-password" class="btn btn-primary btn-sm">Solicitar nuevo enlace</a>
          </div>

        {:else if success}
          <!-- Éxito -->
          <div class="text-center py-4 space-y-4">
            <div class="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <h3 class="font-bold text-base-content text-lg">Contraseña actualizada</h3>
              <p class="text-sm text-base-content/60 mt-1">Serás redirigido al inicio de sesión en unos segundos.</p>
            </div>
            <a href="/login" class="btn btn-primary btn-sm">Ir al inicio de sesión</a>
          </div>

        {:else}
          <!-- Formulario -->
          {#if error}
            <div class="alert alert-error py-2 px-3 text-sm mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
              </svg>
              <span>{error}</span>
            </div>
          {/if}

          <form on:submit|preventDefault={handleSubmit} class="space-y-4">
            <div class="form-control">
              <label class="label pb-1" for="password">
                <span class="label-text font-medium">Nueva contraseña</span>
              </label>
              <input
                id="password"
                type="password"
                placeholder="Mínimo 8 caracteres"
                class="input input-bordered w-full focus:outline-primary"
                bind:value={password}
                required
                autocomplete="new-password"
              />
              {#if password.length > 0}
                <div class="mt-2 space-y-1">
                  <div class="flex gap-1">
                    {#each [1,2,3,4] as i}
                      <div class="h-1 flex-1 rounded-full {i <= strength ? strengthColor[strength] : 'bg-base-300'} transition-all"></div>
                    {/each}
                  </div>
                  <p class="text-xs text-base-content/50">{strengthLabel[strength]}</p>
                </div>
              {/if}
            </div>

            <div class="form-control">
              <label class="label pb-1" for="confirm">
                <span class="label-text font-medium">Confirmar contraseña</span>
              </label>
              <input
                id="confirm"
                type="password"
                placeholder="Repite la contraseña"
                class="input input-bordered w-full focus:outline-primary {confirmPassword && confirmPassword !== password ? 'input-error' : ''}"
                bind:value={confirmPassword}
                required
                autocomplete="new-password"
              />
              {#if confirmPassword && confirmPassword !== password}
                <p class="text-xs text-error mt-1">Las contraseñas no coinciden</p>
              {/if}
            </div>

            <button type="submit" class="btn btn-primary w-full" disabled={loading || (!!confirmPassword && confirmPassword !== password)}>
              {#if loading}
                <span class="loading loading-spinner loading-sm"></span>
              {/if}
              Guardar nueva contraseña
            </button>
          </form>
        {/if}

      </div>
    </div>

    <p class="text-center text-xs text-base-content/40 mt-4">
      ¿Recordaste tu contraseña?
      <a href="/login" class="text-primary hover:underline">Iniciar sesión</a>
    </p>

  </div>
</div>
