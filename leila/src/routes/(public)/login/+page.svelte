<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { authStore } from '$lib/stores/auth';
  import { authService } from '$lib/services';
  import { notificationsStore } from '$lib/stores/notifications';
  import { sanitizeEmail, sanitizeUsername, sanitizeText } from '$lib/utils/sanitize';
  import { loginRateLimiter } from '$lib/utils/rateLimiter';

  let email = '';
  let password = '';
  let loading = false;
  let showRegister = false;
  let loginError = '';

  $: redirectUrl = $page.url.searchParams.get('redirect') || '/';

  // Registration — step 1: form data
  let registerEmail = '';
  let registerUsername = '';
  let registerPassword = '';
  let registerConfirmPassword = '';
  let registerFullName = '';

  // Registration — step 2: math captcha
  let captchaA = 0;
  let captchaB = 0;
  let captchaAnswer = '';
  let captchaPassed = false;

  // Registration — step 3: email verification
  let verificationToken = '';
  let verificationCode = '';
  let codeSent = false;
  let codeLoading = false;

  // Which step: 'form' | 'captcha' | 'code'
  let regStep: 'form' | 'captcha' | 'code' = 'form';

  function generateCaptcha() {
    captchaA = Math.floor(Math.random() * 10) + 1;
    captchaB = Math.floor(Math.random() * 10) + 1;
    captchaAnswer = '';
    captchaPassed = false;
  }

  function validateFormStep() {
    if (!registerEmail || !registerUsername || !registerPassword) {
      notificationsStore.warning('Por favor completa todos los campos obligatorios');
      return false;
    }
    const sanitizedEmail = sanitizeEmail(registerEmail.trim());
    const sanitizedUsername = sanitizeUsername(registerUsername.trim());
    if (!sanitizedEmail || !sanitizedUsername) {
      notificationsStore.warning('Por favor ingresa datos válidos');
      return false;
    }
    if (registerPassword !== registerConfirmPassword) {
      notificationsStore.warning('Las contraseñas no coinciden');
      return false;
    }
    if (registerPassword.length < 6) {
      notificationsStore.warning('La contraseña debe tener al menos 6 caracteres');
      return false;
    }
    return true;
  }

  function goToCaptcha() {
    if (!validateFormStep()) return;
    generateCaptcha();
    regStep = 'captcha';
  }

  async function solveCaptchaAndSendCode() {
    const expected = captchaA + captchaB;
    if (parseInt(captchaAnswer) !== expected) {
      notificationsStore.warning('Respuesta incorrecta, intenta de nuevo');
      generateCaptcha();
      return;
    }
    captchaPassed = true;

    // Send verification code
    try {
      codeLoading = true;
      const sanitizedEmail = sanitizeEmail(registerEmail.trim());
      const res = await authService.sendVerificationCode(sanitizedEmail);
      verificationToken = res.token;
      codeSent = true;
      regStep = 'code';
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al enviar el código. Intenta de nuevo.');
      regStep = 'form';
    } finally {
      codeLoading = false;
    }
  }

  async function handleRegister() {
    if (!verificationCode || verificationCode.length !== 6) {
      notificationsStore.warning('Ingresa el código de 6 dígitos');
      return;
    }

    try {
      loading = true;
      const sanitizedEmail = sanitizeEmail(registerEmail.trim());
      const sanitizedUsername = sanitizeUsername(registerUsername.trim());
      const sanitizedFullName = registerFullName ? sanitizeText(registerFullName, 100) : undefined;

      await authService.register({
        email: sanitizedEmail,
        username: sanitizedUsername,
        password: registerPassword,
        full_name: sanitizedFullName,
        verification_token: verificationToken,
        verification_code: verificationCode
      });

      notificationsStore.success('Cuenta creada exitosamente', 'Ahora puedes iniciar sesión');

      // Reset and go to login
      showRegister = false;
      regStep = 'form';
      verificationCode = '';
      verificationToken = '';
      codeSent = false;
      email = registerEmail;
    } catch (e: any) {
      const msg = e.detail || 'Error al crear cuenta';
      notificationsStore.error(msg);
      if (msg.includes('código') || msg.includes('token')) {
        regStep = 'code';
      }
    } finally {
      loading = false;
    }
  }

  async function resendCode() {
    try {
      codeLoading = true;
      const sanitizedEmail = sanitizeEmail(registerEmail.trim());
      const res = await authService.sendVerificationCode(sanitizedEmail);
      verificationToken = res.token;
      verificationCode = '';
      notificationsStore.success('Nuevo código enviado a tu correo');
    } catch (e: any) {
      notificationsStore.error('Error al reenviar el código');
    } finally {
      codeLoading = false;
    }
  }

  async function handleLogin() {
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

    const sanitizedEmail = sanitizeEmail(email.trim());
    const sanitizedPassword = password.trim();

    if (!sanitizedEmail || !sanitizedPassword) {
      notificationsStore.warning('Por favor ingresa credenciales válidas');
      return;
    }

    loginError = '';
    try {
      loading = true;
      const response = await authService.login(sanitizedEmail, sanitizedPassword);

      loginRateLimiter.reset();

      authStore.login(response.user, {
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        token_type: response.token_type
      });

      notificationsStore.success(`Bienvenido, ${response.user.full_name || response.user.email}!`);
      goto(redirectUrl);
    } catch (e: any) {
      loginRateLimiter.record();
      const attempts = loginRateLimiter.getAttempts();
      loginError = attempts >= 3
        ? `Credenciales incorrectas. ${5 - attempts} intentos restantes antes del bloqueo.`
        : 'Credenciales incorrectas. Verifica tu email y contraseña.';
      notificationsStore.error(loginError, 'Verifica tus credenciales');
    } finally {
      loading = false;
    }
  }

  function toggleRegister() {
    showRegister = !showRegister;
    loginError = '';
    regStep = 'form';
    verificationCode = '';
    verificationToken = '';
    codeSent = false;
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
      {#if !showRegister}
        <!-- ─── LOGIN ─── -->
        <form class="card-body" on:submit|preventDefault={handleLogin}>
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

          {#if loginError}
            <div class="alert alert-error py-2 px-3 text-sm">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
              </svg>
              <span>{loginError}</span>
            </div>
          {/if}

          <div class="form-control mt-2">
            <button type="submit" class="btn btn-primary" disabled={loading}>
              {#if loading}<span class="loading loading-spinner loading-sm"></span>{/if}
              Iniciar sesión
            </button>
          </div>

          <div class="divider">O</div>

          <button type="button" class="btn btn-ghost btn-sm" on:click={toggleRegister}>
            ¿No tienes cuenta? Regístrate
          </button>
        </form>

      {:else if regStep === 'form'}
        <!-- ─── REGISTER STEP 1: FORM ─── -->
        <form class="card-body" on:submit|preventDefault={goToCaptcha}>
          <div class="text-xs text-base-content/50 text-center mb-2">Paso 1 de 3 — Tus datos</div>

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
            {#if registerConfirmPassword && registerPassword !== registerConfirmPassword}
              <p class="text-error text-xs mt-1 ml-1">Las contraseñas no coinciden</p>
            {/if}
          </div>

          <div class="form-control mt-2">
            <button type="submit" class="btn btn-primary">
              Continuar
            </button>
          </div>

          <div class="divider">O</div>

          <button type="button" class="btn btn-ghost btn-sm" on:click={toggleRegister}>
            ¿Ya tienes cuenta? Inicia sesión
          </button>
        </form>

      {:else if regStep === 'captcha'}
        <!-- ─── REGISTER STEP 2: CAPTCHA ─── -->
        <form class="card-body" on:submit|preventDefault={solveCaptchaAndSendCode}>
          <div class="text-xs text-base-content/50 text-center mb-2">Paso 2 de 3 — Verificación humana</div>

          <div class="text-center my-4">
            <p class="text-sm text-base-content/70 mb-4">
              Resuelve esta operación para confirmar que no eres un robot:
            </p>
            <div class="bg-base-200 rounded-xl py-6 px-8 inline-block">
              <p class="text-3xl font-black tracking-widest">
                {captchaA} + {captchaB} = ?
              </p>
            </div>
          </div>

          <div class="form-control">
            <input
              type="number"
              placeholder="Tu respuesta"
              class="input input-bordered text-center text-xl font-bold"
              bind:value={captchaAnswer}
              min="0"
              max="99"
              required
            />
          </div>

          <div class="form-control mt-2">
            <button type="submit" class="btn btn-primary" disabled={codeLoading}>
              {#if codeLoading}
                <span class="loading loading-spinner loading-sm"></span>
                Enviando código...
              {:else}
                Verificar y enviar código
              {/if}
            </button>
          </div>

          <button type="button" class="btn btn-ghost btn-sm mt-1" on:click={() => { regStep = 'form'; }}>
            ← Volver
          </button>
        </form>

      {:else if regStep === 'code'}
        <!-- ─── REGISTER STEP 3: CODE VERIFICATION ─── -->
        <form class="card-body" on:submit|preventDefault={handleRegister}>
          <div class="text-xs text-base-content/50 text-center mb-2">Paso 3 de 3 — Código de verificación</div>

          <div class="text-center my-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-primary mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <p class="text-sm text-base-content/70">
              Enviamos un código de 6 dígitos a
            </p>
            <p class="font-semibold text-sm mt-0.5">{registerEmail}</p>
            <p class="text-xs text-base-content/50 mt-1">Válido por 10 minutos</p>
          </div>

          <div class="form-control">
            <label class="label" for="verification-code">
              <span class="label-text">Código de verificación</span>
            </label>
            <input
              id="verification-code"
              type="text"
              inputmode="numeric"
              maxlength="6"
              placeholder="000000"
              class="input input-bordered text-center text-2xl font-black tracking-[0.5em]"
              bind:value={verificationCode}
              required
            />
          </div>

          <div class="form-control mt-2">
            <button type="submit" class="btn btn-primary" disabled={loading}>
              {#if loading}
                <span class="loading loading-spinner loading-sm"></span>
                Creando cuenta...
              {:else}
                Confirmar y crear cuenta
              {/if}
            </button>
          </div>

          <div class="text-center mt-3">
            <button
              type="button"
              class="btn btn-ghost btn-xs"
              on:click={resendCode}
              disabled={codeLoading}
            >
              {codeLoading ? 'Enviando...' : '¿No recibiste el código? Reenviar'}
            </button>
          </div>

          <button type="button" class="btn btn-ghost btn-sm mt-1" on:click={() => { regStep = 'captcha'; generateCaptcha(); }}>
            ← Volver
          </button>
        </form>
      {/if}
    </div>
  </div>
</div>
