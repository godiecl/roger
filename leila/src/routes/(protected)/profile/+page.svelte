<script lang="ts">
  import { authStore } from '$lib/stores/auth';
</script>

<svelte:head>
  <title>Mi Perfil - ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Mi Perfil</h1>

    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <div class="flex items-center gap-4 mb-6">
          <div class="avatar placeholder">
            <div class="w-20 h-20 rounded-full bg-primary text-primary-content">
              <span class="text-3xl font-bold">
                {$authStore.user?.full_name?.charAt(0).toUpperCase() || $authStore.user?.email?.charAt(0).toUpperCase()}
              </span>
            </div>
          </div>
          <div>
            <h2 class="text-2xl font-bold">{$authStore.user?.full_name || 'Usuario'}</h2>
            <div class="badge badge-primary badge-lg capitalize mt-2">
              {$authStore.user?.role?.replace('_', ' ')}
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text font-semibold">Email</span>
            </label>
            <div class="text-lg">{$authStore.user?.email}</div>
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text font-semibold">Nombre completo</span>
            </label>
            <div class="text-lg">{$authStore.user?.full_name || 'No especificado'}</div>
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text font-semibold">Estado de cuenta</span>
            </label>
            <div>
              {#if $authStore.user?.is_active}
                <span class="badge badge-success">Activa</span>
              {:else}
                <span class="badge badge-error">Inactiva</span>
              {/if}
            </div>
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text font-semibold">Email verificado</span>
            </label>
            <div>
              {#if $authStore.user?.is_verified}
                <span class="badge badge-success">Verificado</span>
              {:else}
                <span class="badge badge-warning">Pendiente</span>
              {/if}
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <div class="card-actions justify-end">
          <button class="btn btn-outline">Editar perfil</button>
          <button class="btn btn-outline btn-error">Cambiar contraseña</button>
        </div>
      </div>
    </div>
  </div>
</div>
