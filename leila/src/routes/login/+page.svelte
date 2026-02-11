<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { authStore } from '$lib/stores/auth';
  import { authService } from '$lib/services';
  import { notificationsStore } from '$lib/stores/notifications';
  import { sanitizeEmail, sanitizeUsername, sanitizeText } from '$lib/utils/sanitize';
  import { loginRateLimiter, registerRateLimiter } from '$lib/utils/rateLimiter';

  let email = '';
  let password = '';
  let loading = false;
  let showRegister = false;

  // Get redirect URL from query params
  $: redirectUrl = $page.url.searchParams.get('redirect') || '/';

  // Registration fields
  let registerEmail = '';
  let registerUsername = '';
  let registerPassword = '';
  let registerConfirmPassword = '';
  let registerFullName = '';

  async function handleLogin() {
    // Check rate limit
    if (!loginRateLimiter.check()) {
      const blockTime = Math.ceil(loginRateLimiter.getBlockTime() / 60000);
      notificationsStore.error(
        'Demasiados intentos de inicio de sesión',
        `Por favor espera ${blockTime} minutos antes de intentar nuevamente`
      );
      return;
    }

    if (!email || !password) {
      notificationsStore.warning('Por favor completa todos los campos');
      return;
    }

    // Sanitize inputs
    const sanitizedEmail = sanitizeEmail(email.trim());
    const sanitizedPassword = password.trim();

    if (!sanitizedEmail || !sanitizedPassword) {
      notificationsStore.warning('Por favor ingresa credenciales válidas');
      return;
    }

    try {
      loading = true;
      const response = await authService.login(sanitizedEmail, sanitizedPassword);

      // Success - reset rate limiter
      loginRateLimiter.reset();

      authStore.login(response.user, {
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        token_type: response.token_type
      });

      notificationsStore.success(`Bienvenido, ${response.user.full_name || response.user.email}!`);

      // Redirect to the page they were trying to access, or home
      goto(redirectUrl);
    } catch (e: any) {
      // Record failed attempt
      loginRateLimiter.record();

      const attempts = loginRateLimiter.getAttempts();
      let errorMessage = e.detail || 'Error al iniciar sesión';

      if (attempts >= 3) {
        errorMessage += `. ${5 - attempts} intentos restantes`;
      }

      notificationsStore.error(errorMessage, 'Verifica tus credenciales');
    } finally {
      loading = false;
    }
  }

  async function handleRegister() {
    if (!registerEmail || !registerUsername || !registerPassword) {
      notificationsStore.warning('Por favor completa todos los campos obligatorios');
      return;
    }

    // Sanitize inputs
    const sanitizedEmail = sanitizeEmail(registerEmail.trim());
    const sanitizedUsername = sanitizeUsername(registerUsername.trim());
    const sanitizedFullName = registerFullName ? sanitizeText(registerFullName, 100) : undefined;

    if (!sanitizedEmail || !sanitizedUsername) {
      notificationsStore.warning('Por favor ingresa datos válidos');
      return;
    }

    if (registerPassword !== registerConfirmPassword) {
      notificationsStore.warning('Las contraseñas no coinciden');
      return;
    }

    if (registerPassword.length < 6) {
      notificationsStore.warning('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    // Password strength check
    if (registerPassword.length < 8) {
      notificationsStore.warning('Se recomienda una contraseña de al menos 8 caracteres');
    }

    try {
      loading = true;
      await authService.register({
        email: sanitizedEmail,
        username: sanitizedUsername,
        password: registerPassword,
        full_name: sanitizedFullName
      });

      notificationsStore.success(
        'Cuenta creada exitosamente',
        'Ahora puedes iniciar sesión'
      );

      // Switch to login view
      showRegister = false;
      email = registerEmail;
    } catch (e: any) {
      notificationsStore.error(
        e.detail || 'Error al crear cuenta'
      );
    } finally {
      loading = false;
    }
  }

  function toggleRegister() {
    showRegister = !showRegister;
  }
</script>

<svelte:head>
  <title>Iniciar sesión - ROGER</title>
</svelte:head>

<div class="hero min-h-[80vh]">
  <div class="hero-content flex-col lg:flex-row-reverse">
    <div class="text-center lg:text-left lg:ml-12">
      <h1 class="text-5xl font-bold">
        {showRegister ? 'Crear cuenta' : 'Iniciar sesión'}
      </h1>
      <p class="py-6 max-w-md">
        {#if showRegister}
          Crea una cuenta para acceder a funciones adicionales como generar narrativas
          y gestionar tu perfil.
        {:else}
          Accede a tu cuenta para aprovechar todas las funcionalidades de ROGER.
        {/if}
      </p>
    </div>

    <div class="card flex-shrink-0 w-full max-w-sm shadow-2xl bg-base-100">
      <form class="card-body" on:submit|preventDefault={showRegister ? handleRegister : handleLogin}>
        {#if !showRegister}
          <!-- Login Form -->
          <div class="form-control">
            <label class="label" for="email">
              <span class="label-text">Email</span>
            </label>
            <input
              id="email"
              type="email"
              placeholder="email@ejemplo.com"
              class="input input-bordered"
              bind:value={email}
              required
            />
          </div>

          <div class="form-control">
            <label class="label" for="password">
              <span class="label-text">Contraseña</span>
            </label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              class="input input-bordered"
              bind:value={password}
              required
            />
            <label class="label">
              <a href="/forgot-password" class="label-text-alt link link-hover">
                ¿Olvidaste tu contraseña?
              </a>
            </label>
          </div>
        {:else}
          <!-- Register Form -->
          <div class="form-control">
            <label class="label" for="register-email">
              <span class="label-text">Email *</span>
            </label>
            <input
              id="register-email"
              type="email"
              placeholder="email@ejemplo.com"
              class="input input-bordered"
              bind:value={registerEmail}
              required
            />
          </div>

          <div class="form-control">
            <label class="label" for="register-username">
              <span class="label-text">Nombre de usuario *</span>
            </label>
            <input
              id="register-username"
              type="text"
              placeholder="usuario123"
              class="input input-bordered"
              bind:value={registerUsername}
              required
            />
          </div>

          <div class="form-control">
            <label class="label" for="register-fullname">
              <span class="label-text">Nombre completo</span>
            </label>
            <input
              id="register-fullname"
              type="text"
              placeholder="Juan Pérez"
              class="input input-bordered"
              bind:value={registerFullName}
            />
          </div>

          <div class="form-control">
            <label class="label" for="register-password">
              <span class="label-text">Contraseña *</span>
            </label>
            <input
              id="register-password"
              type="password"
              placeholder="••••••••"
              class="input input-bordered"
              bind:value={registerPassword}
              required
            />
          </div>

          <div class="form-control">
            <label class="label" for="register-confirm-password">
              <span class="label-text">Confirmar contraseña *</span>
            </label>
            <input
              id="register-confirm-password"
              type="password"
              placeholder="••••••••"
              class="input input-bordered"
              bind:value={registerConfirmPassword}
              required
            />
          </div>
        {/if}

        <div class="form-control mt-6">
          <button type="submit" class="btn btn-primary" disabled={loading}>
            {#if loading}
              <span class="loading loading-spinner loading-sm"></span>
            {/if}
            {showRegister ? 'Crear cuenta' : 'Iniciar sesión'}
          </button>
        </div>

        <div class="divider">O</div>

        <button
          type="button"
          class="btn btn-ghost btn-sm"
          on:click={toggleRegister}
        >
          {showRegister ? '¿Ya tienes cuenta? Inicia sesión' : '¿No tienes cuenta? Regístrate'}
        </button>
      </form>
    </div>
  </div>
</div>
