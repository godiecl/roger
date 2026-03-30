<script lang="ts">
  import { authService } from '$lib/services';

  let email = '';
  let loading = false;
  let sent = false;
  let error = '';

  async function handleSubmit() {
    if (!email) return;
    error = '';
    loading = true;
    try {
      await authService.forgotPassword(email.trim());
      sent = true;
    } catch {
      // Siempre mostramos éxito por seguridad (no revelar si el email existe)
      sent = true;
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Recuperar contraseña — ROGER</title>
</svelte:head>

<div class="min-h-[80vh] flex items-center justify-center px-4">
  <div class="w-full max-w-md">

    <!-- Logo / volver -->
    <div class="text-center mb-8">
      <a href="/login" class="inline-flex items-center gap-2 text-sm text-base-content/50 hover:text-primary transition-colors mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Volver al inicio de sesión
      </a>
      <h1 class="text-3xl font-bold text-base-content">Recuperar contraseña</h1>
      <p class="text-base-content/50 mt-2 text-sm">
        Ingresa tu correo y te enviaremos un enlace para restablecer tu contraseña.
      </p>
    </div>

    <div class="card bg-base-100 shadow-xl border border-base-200">
      <div class="card-body">

        {#if sent}
          <!-- Estado de éxito -->
          <div class="text-center py-4 space-y-4">
            <div class="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h3 class="font-bold text-base-content text-lg">Revisa tu correo</h3>
              <p class="text-sm text-base-content/60 mt-1 max-w-xs mx-auto">
                Si el correo <strong>{email}</strong> está registrado, recibirás un enlace para restablecer tu contraseña en los próximos minutos.
              </p>
            </div>
            <p class="text-xs text-base-content/40">
              ¿No lo ves? Revisa la carpeta de spam.
            </p>
            <div class="pt-2">
              <button class="btn btn-ghost btn-sm" on:click={() => { sent = false; email = ''; }}>
                Intentar con otro correo
              </button>
            </div>
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
              <label class="label pb-1" for="email">
                <span class="label-text font-medium">Correo electrónico</span>
              </label>
              <input
                id="email"
                type="email"
                placeholder="tu@email.com"
                class="input input-bordered w-full focus:outline-primary"
                bind:value={email}
                required
                autocomplete="email"
              />
            </div>

            <button type="submit" class="btn btn-primary w-full" disabled={loading}>
              {#if loading}
                <span class="loading loading-spinner loading-sm"></span>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              {/if}
              Enviar enlace de recuperación
            </button>
          </form>
        {/if}

      </div>
    </div>

  </div>
</div>
