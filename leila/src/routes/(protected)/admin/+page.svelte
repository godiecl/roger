<script lang="ts">
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/services/apiClient';
  import { notificationsStore } from '$lib/stores/notifications';
  import { authStore } from '$lib/stores/auth';
  import { getRoleLabel, roleBadge } from '$lib/utils/roles';

  $: currentUserId = $authStore.user?.id;

  interface AdminUser {
    id: number;
    email: string;
    username: string;
    full_name: string | null;
    company: string | null;
    role: string;
    is_active: boolean;
    is_verified: boolean;
  }

  let users: AdminUser[] = [];
  let loading = true;
  let error = '';
  let togglingId: number | null = null;
  let changingRoleId: number | null = null;
  let searchQuery = '';

  // ── Ordenación ───────────────────────────────────────────────────────────
  let sortKey: 'role' | 'is_active' | null = null;
  let sortAsc = true;

  function toggleSort(key: 'role' | 'is_active') {
    if (sortKey === key) {
      sortAsc = !sortAsc;
    } else {
      sortKey = key;
      sortAsc = true;
    }
    currentPage = 1;
  }

  $: sorted = (() => {
    if (!sortKey) return filtered;
    return [...filtered].sort((a, b) => {
      let valA: string | number;
      let valB: string | number;
      if (sortKey === 'role') {
        valA = getRoleLabel(a.role);
        valB = getRoleLabel(b.role);
      } else {
        valA = a.is_active ? 0 : 1;
        valB = b.is_active ? 0 : 1;
      }
      if (valA < valB) return sortAsc ? -1 : 1;
      if (valA > valB) return sortAsc ? 1 : -1;
      return 0;
    });
  })();

  // ── Paginación ────────────────────────────────────────────────────────────
  const PAGE_SIZE = 10;
  let currentPage = 1;

  $: {
    searchQuery;
    sortKey;
    currentPage = 1;
  }

  $: totalPages = Math.ceil(sorted.length / PAGE_SIZE);
  $: paginated = sorted.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  // ── Create user modal ─────────────────────────────────────────────────────
  let showCreateModal = false;
  let creating = false;
  let createEmail = '';
  let createUsername = '';
  let createFullName = '';
  let createCompany = '';
  let createPassword = '';
  let createRole = 'usuario_estandar';
  let showCreatePassword = false;

  const roleOptions = [
    { value: 'usuario_estandar', label: 'Explorador' },
    { value: 'investigador', label: 'Investigador' },
    { value: 'curador', label: 'Curador' },
    { value: 'administrador', label: 'Administrador' },
  ];

  function openCreateModal() {
    createEmail = ''; createUsername = ''; createFullName = '';
    createPassword = ''; createCompany = ''; createRole = 'usuario_estandar'; showCreatePassword = false;
    showCreateModal = true;
  }

  function closeCreateModal() {
    showCreateModal = false;
  }

  async function handleCreateUser() {
    if (!createEmail.trim() || !createUsername.trim() || createPassword.length < 8) return;
    creating = true;
    try {
      const created = await apiClient.post<AdminUser>('/auth/admin/users', {
        email: createEmail.trim(),
        username: createUsername.trim(),
        full_name: createFullName.trim() || null,
        company: createCompany.trim() || null,
        password: createPassword,
        role: createRole,
      });
      users = [...users, created];
      notificationsStore.success(`Usuario ${created.email} creado correctamente`);
      closeCreateModal();
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al crear usuario');
    } finally {
      creating = false;
    }
  }

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

  async function changeRole(user: AdminUser, newRole: string) {
    if (newRole === user.role) return;
    changingRoleId = user.id;
    try {
      const updated = await apiClient.patch<AdminUser>(`/auth/admin/users/${user.id}/role?role=${encodeURIComponent(newRole)}`, {});
      users = users.map(u => u.id === updated.id ? updated : u);
      notificationsStore.success(`Rol de ${updated.email} cambiado a ${getRoleLabel(updated.role)}`);
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al cambiar rol');
    } finally {
      changingRoleId = null;
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
      <div class="flex gap-2">
        <button class="btn btn-primary btn-sm" on:click={openCreateModal}>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Nuevo usuario
        </button>
        <button class="btn btn-ghost btn-sm" on:click={loadUsers} disabled={loading}>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 {loading ? 'animate-spin' : ''}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Actualizar
        </button>
      </div>
    </div>

    <!-- Stats -->
    {#if !loading && !error}
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
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
          <thead>
            <tr class="bg-base-200/70 border-b border-base-300">
              <th class="py-3 px-4 text-xs font-semibold text-base-content/40 uppercase tracking-wider">Usuario</th>
              <th class="py-3 px-4 text-xs font-semibold text-base-content/40 uppercase tracking-wider">Correo</th>
              <th class="py-3 px-4 text-xs font-semibold text-base-content/40 uppercase tracking-wider">Empresa</th>
              <th class="py-3 px-4">
                <button class="flex items-center gap-1 text-xs font-semibold text-base-content/40 uppercase tracking-wider hover:text-base-content/70 transition-colors" on:click={() => toggleSort('role')}>
                  Rol
                  <span class="text-[10px]">{sortKey === 'role' ? (sortAsc ? '↑' : '↓') : '↕'}</span>
                </button>
              </th>
              <th class="py-3 px-4 text-center">
                <button class="flex items-center gap-1 text-xs font-semibold text-base-content/40 uppercase tracking-wider hover:text-base-content/70 transition-colors mx-auto" on:click={() => toggleSort('is_active')}>
                  Estado
                  <span class="text-[10px]">{sortKey === 'is_active' ? (sortAsc ? '↑' : '↓') : '↕'}</span>
                </button>
              </th>
              <th class="py-3 px-4 text-xs font-semibold text-base-content/40 uppercase tracking-wider text-right">Acción</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-base-200">
            {#each paginated as user (user.id)}
              <tr class="hover:bg-base-200/30 transition-colors">

                <!-- Usuario -->
                <td class="py-3 px-4">
                  <div class="flex items-center gap-3 {!user.is_active ? 'opacity-40' : ''}">
                    <div class="w-9 h-9 rounded-xl flex items-center justify-center font-bold text-sm flex-shrink-0
                      {user.is_active ? 'bg-primary/10 text-primary' : 'bg-base-300 text-base-content/30'}">
                      {(user.full_name || user.email).charAt(0).toUpperCase()}
                    </div>
                    <div class="min-w-0">
                      <p class="text-sm font-semibold leading-tight truncate {!user.is_active ? 'text-base-content/40' : ''}">{user.full_name || user.username}</p>
                    </div>
                  </div>
                </td>

                <!-- Correo -->
                <td class="py-3 px-4">
                  <a href="mailto:{user.email}"
                    class="text-sm text-primary hover:underline underline-offset-2 truncate block max-w-[180px]"
                    title={user.email}>
                    {user.email}
                  </a>
                </td>

                <!-- Empresa -->
                <td class="py-3 px-4">
                  {#if user.company}
                    <span class="text-sm text-base-content/70 truncate block max-w-[140px]" title={user.company}>{user.company}</span>
                  {:else}
                    <span class="text-base-content/25 text-xs italic">Sin empresa</span>
                  {/if}
                </td>

                <!-- Rol -->
                <td class="py-3 px-4">
                  {#if user.id === currentUserId}
                    <span class="badge badge-sm {roleBadge[user.role] ?? 'badge-ghost'}">
                      {getRoleLabel(user.role)}
                    </span>
                  {:else}
                    <select
                      class="select select-xs select-bordered max-w-[130px]"
                      value={user.role}
                      disabled={changingRoleId === user.id}
                      on:change={(e) => changeRole(user, e.currentTarget.value)}>
                      {#each roleOptions as opt}
                        <option value={opt.value}>{opt.label}</option>
                      {/each}
                    </select>
                  {/if}
                </td>

                <!-- Estado -->
                <td class="py-3 px-4 text-center">
                  {#if user.is_active}
                    <span class="badge badge-success badge-sm gap-1">
                      <span class="w-1.5 h-1.5 rounded-full bg-success-content/70 inline-block"></span>
                      Activo
                    </span>
                  {:else}
                    <span class="badge badge-error badge-sm gap-1">
                      <span class="w-1.5 h-1.5 rounded-full bg-error-content/70 inline-block"></span>
                      Inactivo
                    </span>
                  {/if}
                </td>

                <!-- Acción -->
                <td class="py-3 px-4 text-right">
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

      <!-- Paginador -->
      {#if totalPages > 1}
        <div class="flex items-center justify-between mt-2">
          <p class="text-xs text-base-content/40">
            Mostrando {(currentPage - 1) * PAGE_SIZE + 1}–{Math.min(currentPage * PAGE_SIZE, sorted.length)} de {sorted.length}
          </p>
          <div class="join">
            <button
              class="join-item btn btn-xs btn-ghost"
              disabled={currentPage === 1}
              on:click={() => currentPage--}>
              ‹
            </button>
            {#each Array.from({ length: totalPages }, (_, i) => i + 1) as p}
              <button
                class="join-item btn btn-xs {currentPage === p ? 'btn-primary' : 'btn-ghost'}"
                on:click={() => currentPage = p}>
                {p}
              </button>
            {/each}
            <button
              class="join-item btn btn-xs btn-ghost"
              disabled={currentPage === totalPages}
              on:click={() => currentPage++}>
              ›
            </button>
          </div>
        </div>
      {/if}

    {/if}

  </div>
</div>

<!-- Create user modal -->
{#if showCreateModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center px-4" role="dialog" aria-modal="true">
    <!-- Backdrop -->
    <button
      class="absolute inset-0 bg-black/40 backdrop-blur-sm w-full h-full cursor-default"
      on:click={closeCreateModal}
      on:keydown={(e) => e.key === 'Escape' && closeCreateModal()}
      aria-label="Cerrar modal"
      tabindex="-1"
    ></button>
    <div class="relative bg-base-100 rounded-2xl border border-base-300 shadow-xl w-full max-w-md p-6 space-y-4">

      <div class="flex items-center justify-between">
        <h2 class="text-lg font-bold">Crear usuario</h2>
        <button class="btn btn-ghost btn-sm btn-circle" on:click={closeCreateModal} aria-label="Cerrar">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Email -->
      <div class="form-control">
        <label class="label py-0.5" for="cu-email">
          <span class="label-text text-xs font-semibold">Correo electrónico</span>
        </label>
        <input id="cu-email" type="email" class="input input-bordered input-sm" bind:value={createEmail} placeholder="correo@ejemplo.com" />
      </div>

      <!-- Username -->
      <div class="form-control">
        <label class="label py-0.5" for="cu-username">
          <span class="label-text text-xs font-semibold">Nombre de usuario</span>
        </label>
        <input id="cu-username" type="text" class="input input-bordered input-sm" bind:value={createUsername} placeholder="usuario123" />
      </div>

      <!-- Full name -->
      <div class="form-control">
        <label class="label py-0.5" for="cu-fullname">
          <span class="label-text text-xs font-semibold">Nombre completo <span class="text-base-content/40 font-normal">(opcional)</span></span>
        </label>
        <input id="cu-fullname" type="text" class="input input-bordered input-sm" bind:value={createFullName} placeholder="Nombre Apellido" />
      </div>

      <!-- Company -->
      <div class="form-control">
        <label class="label py-0.5" for="cu-company">
          <span class="label-text text-xs font-semibold">Empresa / Institución <span class="text-base-content/40 font-normal">(opcional)</span></span>
        </label>
        <input id="cu-company" type="text" class="input input-bordered input-sm" bind:value={createCompany} placeholder="Universidad, empresa u organización" />
      </div>

      <!-- Role -->
      <div class="form-control">
        <label class="label py-0.5" for="cu-role">
          <span class="label-text text-xs font-semibold">Rol</span>
        </label>
        <select id="cu-role" class="select select-bordered select-sm" bind:value={createRole}>
          {#each roleOptions as opt}
            <option value={opt.value}>{opt.label}</option>
          {/each}
        </select>
      </div>

      <!-- Password -->
      <div class="form-control">
        <label class="label py-0.5" for="cu-password">
          <span class="label-text text-xs font-semibold">Contraseña temporal</span>
        </label>
        <div class="relative">
          {#if showCreatePassword}
            <input id="cu-password" type="text" class="input input-bordered input-sm w-full pr-10" bind:value={createPassword} placeholder="Mínimo 8 caracteres" />
          {:else}
            <input id="cu-password" type="password" class="input input-bordered input-sm w-full pr-10" bind:value={createPassword} placeholder="Mínimo 8 caracteres" />
          {/if}
          <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-base-content/40 hover:text-base-content/70 transition-colors" on:click={() => showCreatePassword = !showCreatePassword} tabindex="-1">
            {#if showCreatePassword}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
            {/if}
          </button>
        </div>
        <p class="text-[10px] text-base-content/40 mt-1 ml-1">Se enviará al usuario por correo electrónico.</p>
      </div>

      <div class="flex gap-2 justify-end pt-1">
        <button class="btn btn-ghost btn-sm" on:click={closeCreateModal} disabled={creating}>Cancelar</button>
        <button
          class="btn btn-primary btn-sm"
          on:click={handleCreateUser}
          disabled={creating || !createEmail.trim() || !createUsername.trim() || createPassword.length < 8}>
          {#if creating}<span class="loading loading-spinner loading-xs"></span>{/if}
          Crear usuario
        </button>
      </div>

    </div>
  </div>
{/if}
