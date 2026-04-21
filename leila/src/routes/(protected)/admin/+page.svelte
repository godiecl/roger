<script lang="ts">
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/services/apiClient';
  import { notificationsStore } from '$lib/stores/notifications';
  import { authStore } from '$lib/stores/auth';

  $: currentUserId = $authStore.user?.id;

  interface AdminUser {
    id: number;
    email: string;
    username: string;
    full_name: string | null;
    role: string;
    is_active: boolean;
    is_verified: boolean;
  }

  let users: AdminUser[] = [];
  let loading = true;
  let error = '';
  let togglingId: number | null = null;
  let searchQuery = '';

  $: filtered = users.filter(u =>
    u.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (u.full_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.username.toLowerCase().includes(searchQuery.toLowerCase())
  );

  async function loadUsers() {
    loading = true;
    error = '';
    try {
      const resp = await apiClient.get<{ total: number; users: AdminUser[] }>('/auth/admin/users');
      users = resp.users;
    } catch (e: any) {
      error = e.detail || 'Error al cargar usuarios';
    } finally {
      loading = false;
    }
  }

  async function toggleActive(user: AdminUser) {
    togglingId = user.id;
    try {
      const updated = await apiClient.patch<AdminUser>(`/auth/admin/users/${user.id}/toggle-active`, {});
      users = users.map(u => u.id === updated.id ? updated : u);
      notificationsStore.success(updated.is_active ? `${updated.email} habilitado` : `${updated.email} deshabilitado`);
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al cambiar estado');
    } finally {
      togglingId = null;
    }
  }

  const roleLabel: Record<string, string> = {
    administrador: 'Administrador',
    curador: 'Curador',
    investigador: 'Investigador',
    usuario_estandar: 'Usuario',
  };

  const roleBadge: Record<string, string> = {
    administrador: 'badge-error',
    curador: 'badge-warning',
    investigador: 'badge-info',
    usuario_estandar: 'badge-ghost',
  };

  onMount(loadUsers);
</script>

<svelte:head>
  <title>Administración - ROGER</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="max-w-4xl mx-auto space-y-4">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Administración</h1>
        <p class="text-sm text-base-content/50 mt-0.5">Control de usuarios del sistema</p>
      </div>
      <button class="btn btn-ghost btn-sm" on:click={loadUsers} disabled={loading}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 {loading ? 'animate-spin' : ''}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Actualizar
      </button>
    </div>

    <!-- Stats -->
    {#if !loading && !error}
      <div class="grid grid-cols-3 gap-3">
        <div class="bg-base-100 rounded-2xl border border-base-300 p-4 text-center">
          <p class="text-2xl font-bold">{users.length}</p>
          <p class="text-xs text-base-content/50 mt-0.5">Total usuarios</p>
        </div>
        <div class="bg-base-100 rounded-2xl border border-base-300 p-4 text-center">
          <p class="text-2xl font-bold text-success">{users.filter(u => u.is_active).length}</p>
          <p class="text-xs text-base-content/50 mt-0.5">Habilitados</p>
        </div>
        <div class="bg-base-100 rounded-2xl border border-base-300 p-4 text-center">
          <p class="text-2xl font-bold text-error">{users.filter(u => !u.is_active).length}</p>
          <p class="text-xs text-base-content/50 mt-0.5">Deshabilitados</p>
        </div>
      </div>
    {/if}

    <!-- Search -->
    <div class="relative">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-base-content/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        type="text"
        class="input input-bordered input-sm w-full pl-9"
        placeholder="Buscar por nombre, correo o usuario..."
        bind:value={searchQuery}
      />
    </div>

    <!-- Content -->
    {#if loading}
      <div class="flex justify-center py-16">
        <span class="loading loading-spinner text-primary"></span>
      </div>

    {:else if error}
      <div class="alert alert-error">
        <span>{error}</span>
        <button class="btn btn-sm" on:click={loadUsers}>Reintentar</button>
      </div>

    {:else if filtered.length === 0}
      <div class="flex flex-col items-center py-16 text-center text-base-content/40">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <p class="text-sm font-semibold">Sin resultados</p>
      </div>

    {:else}
      <div class="bg-base-100 rounded-2xl border border-base-300 shadow-sm overflow-hidden">
        <table class="table table-sm w-full">
          <thead class="bg-base-200/60">
            <tr>
              <th class="text-xs font-semibold text-base-content/50 uppercase tracking-wide">Usuario</th>
              <th class="text-xs font-semibold text-base-content/50 uppercase tracking-wide">Correo</th>
              <th class="text-xs font-semibold text-base-content/50 uppercase tracking-wide">Rol</th>
              <th class="text-xs font-semibold text-base-content/50 uppercase tracking-wide">Estado</th>
              <th class="text-xs font-semibold text-base-content/50 uppercase tracking-wide text-right">Acción</th>
            </tr>
          </thead>
          <tbody>
            {#each filtered as user (user.id)}
              <tr class="hover:bg-base-200/40 transition-colors {!user.is_active ? 'opacity-60' : ''}">
                <td>
                  <div class="flex items-center gap-2.5">
                    <div class="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm flex-shrink-0
                      {user.is_active ? 'bg-primary/10 text-primary' : 'bg-base-300 text-base-content/40'}">
                      {(user.full_name || user.email).charAt(0).toUpperCase()}
                    </div>
                    <div class="min-w-0">
                      <p class="text-sm font-semibold truncate">{user.full_name || '—'}</p>
                      <p class="text-[10px] text-base-content/40">@{user.username}</p>
                    </div>
                  </div>
                </td>
                <td class="text-sm text-base-content/70">{user.email}</td>
                <td>
                  <span class="badge badge-sm {roleBadge[user.role] ?? 'badge-ghost'}">
                    {roleLabel[user.role] ?? user.role}
                  </span>
                </td>
                <td>
                  {#if user.is_active}
                    <span class="badge badge-success badge-sm">Habilitado</span>
                  {:else}
                    <span class="badge badge-error badge-sm">Deshabilitado</span>
                  {/if}
                </td>
                <td class="text-right">
                  {#if user.id === currentUserId}
                    <span class="text-[10px] text-base-content/30 italic">Tu cuenta</span>
                  {:else}
                    <button
                      class="btn btn-xs {user.is_active ? 'btn-error btn-outline' : 'btn-success btn-outline'}"
                      on:click={() => toggleActive(user)}
                      disabled={togglingId === user.id}>
                      {#if togglingId === user.id}
                        <span class="loading loading-spinner loading-xs"></span>
                      {:else if user.is_active}
                        Deshabilitar
                      {:else}
                        Habilitar
                      {/if}
                    </button>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}

  </div>
</div>
