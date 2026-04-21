<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import { apiClient } from '$lib/services/apiClient';
  import { notificationsStore } from '$lib/stores/notifications';

  // ── Edit profile ────────────────────────────────────────────────────────
  let editingProfile = false;
  let editFullName = '';
  let editEmail = '';
  let savingProfile = false;

  function startEditProfile() {
    editFullName = $authStore.user?.full_name || '';
    editEmail = $authStore.user?.email || '';
    editingProfile = true;
  }

  function cancelEditProfile() {
    editingProfile = false;
    editFullName = '';
    editEmail = '';
  }

  async function handleSaveProfile() {
    savingProfile = true;
    try {
      const updated = await apiClient.patch<any>('/auth/me', { full_name: editFullName.trim() || null });
      authStore.updateUser({ ...$authStore.user!, full_name: updated.full_name });
      notificationsStore.success('Perfil actualizado');
      cancelEditProfile();
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al guardar');
    } finally {
      savingProfile = false;
    }
  }

  // ── Change password ─────────────────────────────────────────────────────
  let changingPassword = false;
  let currentPassword = '';
  let newPassword = '';
  let confirmPassword = '';
  let saving = false;

  let showCurrent = false;
  let showNew = false;
  let showConfirm = false;

  // Password strength
  $: strength = (() => {
    if (!newPassword) return 0;
    let s = 0;
    if (newPassword.length >= 8) s++;
    if (/[A-Z]/.test(newPassword)) s++;
    if (/[0-9]/.test(newPassword)) s++;
    if (/[^A-Za-z0-9]/.test(newPassword)) s++;
    return s;
  })();
  const strengthColor = ['', 'bg-error', 'bg-warning', 'bg-info', 'bg-success'];
  const strengthLabel = ['', 'Muy débil', 'Débil', 'Buena', 'Fuerte'];

  $: passwordMismatch = confirmPassword.length > 0 && newPassword !== confirmPassword;
  $: canSubmit = currentPassword.length > 0 && newPassword.length >= 8 && newPassword === confirmPassword;

  function cancelChange() {
    changingPassword = false;
    currentPassword = ''; newPassword = ''; confirmPassword = '';
    showCurrent = false; showNew = false; showConfirm = false;
  }

  async function handleChangePassword() {
    if (!canSubmit) return;
    saving = true;
    try {
      await apiClient.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      });
      notificationsStore.success('Contraseña actualizada correctamente');
      cancelChange();
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al cambiar la contraseña');
    } finally {
      saving = false;
    }
  }
</script>

<svelte:head>
  <title>Mi Perfil - ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="max-w-2xl mx-auto space-y-4">
    <h1 class="text-2xl font-bold">Mi Perfil</h1>

    <!-- User info card -->
    <div class="bg-base-100 rounded-2xl border border-base-300 shadow-sm p-6">
      <div class="flex items-center gap-4 mb-6">
        <div class="w-16 h-16 rounded-2xl bg-primary text-primary-content flex items-center justify-center font-bold text-2xl flex-shrink-0">
          {$authStore.user?.full_name?.charAt(0).toUpperCase() || $authStore.user?.email?.charAt(0).toUpperCase()}
        </div>
        <div>
          <h2 class="text-xl font-bold">{$authStore.user?.full_name || 'Usuario'}</h2>
          <span class="badge badge-primary badge-sm capitalize mt-1">
            {$authStore.user?.role?.replace('_', ' ')}
          </span>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <p class="text-xs font-semibold text-base-content/50 uppercase tracking-wide mb-0.5">Email</p>
          <p class="text-sm">{$authStore.user?.email}</p>
        </div>
        <div>
          <p class="text-xs font-semibold text-base-content/50 uppercase tracking-wide mb-0.5">Nombre completo</p>
          <p class="text-sm">{$authStore.user?.full_name || 'No especificado'}</p>
        </div>
        <div>
          <p class="text-xs font-semibold text-base-content/50 uppercase tracking-wide mb-0.5">Estado de cuenta</p>
          {#if $authStore.user?.is_active}
            <span class="badge badge-success badge-sm">Activa</span>
          {:else}
            <span class="badge badge-error badge-sm">Inactiva</span>
          {/if}
        </div>
        <div>
          <p class="text-xs font-semibold text-base-content/50 uppercase tracking-wide mb-0.5">Email verificado</p>
          {#if $authStore.user?.is_verified}
            <span class="badge badge-success badge-sm">Verificado</span>
          {:else}
            <span class="badge badge-warning badge-sm">Pendiente</span>
          {/if}
        </div>
      </div>
    </div>

    <!-- Edit profile card -->
    <div class="bg-base-100 rounded-2xl border border-base-300 shadow-sm">
      <button
        class="w-full flex items-center justify-between px-6 py-4 text-left"
        on:click={() => { if (editingProfile) cancelEditProfile(); else startEditProfile(); }}>
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-base-200 flex items-center justify-center flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </div>
          <span class="font-semibold text-sm">Editar perfil</span>
        </div>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/40 transition-transform {editingProfile ? 'rotate-180' : ''}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {#if editingProfile}
        <div class="px-6 pb-6 border-t border-base-300 pt-4 space-y-4">

          <!-- Nombre -->
          <div class="form-control">
            <label class="label py-0.5" for="ep-fullname">
              <span class="label-text text-xs font-semibold">Nombre completo</span>
            </label>
            <input
              id="ep-fullname"
              type="text"
              class="input input-bordered input-sm"
              bind:value={editFullName}
              placeholder="Tu nombre completo"
              maxlength="255"
            />
          </div>

          <!-- Email (pendiente de verificación) -->
          <div class="form-control">
            <label class="label py-0.5" for="ep-email">
              <span class="label-text text-xs font-semibold">Correo electrónico</span>
              <span class="label-text-alt text-[10px] text-base-content/40">Requiere verificación</span>
            </label>
            <div class="relative">
              <input
                id="ep-email"
                type="email"
                class="input input-bordered input-sm w-full pr-24"
                bind:value={editEmail}
                placeholder="nuevo@correo.com"
                disabled
              />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-base-content/40 font-medium">Próximamente</span>
            </div>
            <p class="text-[10px] text-base-content/40 mt-1 ml-1">
              El cambio de correo requiere confirmación por email. Esta función estará disponible pronto.
            </p>
          </div>

          <div class="flex gap-2 justify-end pt-1">
            <button class="btn btn-ghost btn-sm" on:click={cancelEditProfile} disabled={savingProfile}>Cancelar</button>
            <button class="btn btn-primary btn-sm" on:click={handleSaveProfile} disabled={savingProfile}>
              {#if savingProfile}<span class="loading loading-spinner loading-xs"></span>{/if}
              Guardar cambios
            </button>
          </div>
        </div>
      {/if}
    </div>

    <!-- Change password card -->
    <div class="bg-base-100 rounded-2xl border border-base-300 shadow-sm">
      <!-- Header -->
      <button
        class="w-full flex items-center justify-between px-6 py-4 text-left"
        on:click={() => { if (changingPassword) cancelChange(); else changingPassword = true; }}>
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-base-200 flex items-center justify-center flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <span class="font-semibold text-sm">Cambiar contraseña</span>
        </div>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/40 transition-transform {changingPassword ? 'rotate-180' : ''}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Form -->
      {#if changingPassword}
        <div class="px-6 pb-6 border-t border-base-300 pt-4 space-y-4">

          <!-- Current password -->
          <div class="form-control">
            <label class="label py-0.5" for="cp-current">
              <span class="label-text text-xs font-semibold">Contraseña actual</span>
            </label>
            <div class="relative">
              {#if showCurrent}
                <input id="cp-current" type="text" class="input input-bordered input-sm w-full pr-10" bind:value={currentPassword} placeholder="Tu contraseña actual" autocomplete="current-password" />
              {:else}
                <input id="cp-current" type="password" class="input input-bordered input-sm w-full pr-10" bind:value={currentPassword} placeholder="Tu contraseña actual" autocomplete="current-password" />
              {/if}
              <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-base-content/40 hover:text-base-content/70 transition-colors" on:click={() => showCurrent = !showCurrent} tabindex="-1">
                {#if showCurrent}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                {:else}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                {/if}
              </button>
            </div>
          </div>

          <!-- New password -->
          <div class="form-control">
            <label class="label py-0.5" for="cp-new">
              <span class="label-text text-xs font-semibold">Nueva contraseña</span>
            </label>
            <div class="relative">
              {#if showNew}
                <input id="cp-new" type="text" class="input input-bordered input-sm w-full pr-10" bind:value={newPassword} placeholder="Mínimo 8 caracteres" autocomplete="new-password" />
              {:else}
                <input id="cp-new" type="password" class="input input-bordered input-sm w-full pr-10" bind:value={newPassword} placeholder="Mínimo 8 caracteres" autocomplete="new-password" />
              {/if}
              <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-base-content/40 hover:text-base-content/70 transition-colors" on:click={() => showNew = !showNew} tabindex="-1">
                {#if showNew}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                {:else}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                {/if}
              </button>
            </div>
            {#if newPassword.length > 0}
              <div class="mt-2 space-y-1">
                <div class="flex gap-1">
                  {#each [1,2,3,4] as i}
                    <div class="h-1 flex-1 rounded-full {i <= strength ? strengthColor[strength] : 'bg-base-300'} transition-all"></div>
                  {/each}
                </div>
                <p class="text-[10px] text-base-content/50">{strengthLabel[strength]}</p>
              </div>
            {/if}
          </div>

          <!-- Confirm password -->
          <div class="form-control">
            <label class="label py-0.5" for="cp-confirm">
              <span class="label-text text-xs font-semibold">Confirmar nueva contraseña</span>
            </label>
            <div class="relative">
              {#if showConfirm}
                <input id="cp-confirm" type="text" class="input input-sm w-full pr-10 {passwordMismatch ? 'input-error' : 'input-bordered'}" bind:value={confirmPassword} placeholder="Repite la nueva contraseña" autocomplete="new-password" />
              {:else}
                <input id="cp-confirm" type="password" class="input input-sm w-full pr-10 {passwordMismatch ? 'input-error' : 'input-bordered'}" bind:value={confirmPassword} placeholder="Repite la nueva contraseña" autocomplete="new-password" />
              {/if}
              <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-base-content/40 hover:text-base-content/70 transition-colors" on:click={() => showConfirm = !showConfirm} tabindex="-1">
                {#if showConfirm}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                {:else}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                {/if}
              </button>
            </div>
            {#if passwordMismatch}
              <p class="text-error text-xs mt-1 ml-1">Las contraseñas no coinciden</p>
            {/if}
          </div>

          <div class="flex gap-2 justify-end pt-1">
            <button class="btn btn-ghost btn-sm" on:click={cancelChange} disabled={saving}>Cancelar</button>
            <button class="btn btn-primary btn-sm" on:click={handleChangePassword} disabled={!canSubmit || saving}>
              {#if saving}<span class="loading loading-spinner loading-xs"></span>{/if}
              Guardar contraseña
            </button>
          </div>
        </div>
      {/if}
    </div>

  </div>
</div>
