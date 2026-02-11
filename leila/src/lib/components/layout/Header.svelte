<script lang="ts">
  import { page } from '$app/stores';
  import { authStore, isAuthenticated } from '$lib/stores/auth';

  let isMenuOpen = false;

  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }

  function handleLogout() {
    authStore.logout();
  }
</script>

<header class="sticky top-0 z-50 bg-base-100 shadow-sm">
  <!-- Top Bar -->
  <div class="bg-slate-600 text-white">
    <div class="container mx-auto px-4">
      <div class="flex justify-end items-center h-8 text-xs">
        <a href="/help" class="hover:text-slate-200 px-3 transition-colors">Ayuda</a>
        <a href="/contact" class="hover:text-slate-200 px-3 transition-colors">Contacto</a>
        <a href="/en" class="hover:text-slate-200 px-3 transition-colors">English</a>
      </div>
    </div>
  </div>

  <!-- Main Header -->
  <div class="bg-base-100 border-b border-base-300">
    <div class="container mx-auto px-4 py-4">
      <div class="flex items-center justify-between">
        <!-- Logo and Branding -->
        <a href="/" class="flex items-center gap-3 hover:opacity-90 transition-opacity">
          <div class="avatar">
            <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
          </div>
          <div>
            <div class="text-xs text-slate-500 uppercase tracking-wide">Universidad Católica del Norte</div>
            <div class="text-lg font-bold text-slate-800">Fondo Roberto Gerstmann</div>
          </div>
        </a>

        <!-- Search and User Actions -->
        <div class="hidden md:flex items-center gap-3">
          <div class="form-control">
            <div class="join">
              <input type="text" placeholder="Buscar en el archivo..." class="input input-bordered join-item w-64 focus:outline-primary" />
              <button class="btn btn-primary join-item">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </div>

          {#if $isAuthenticated}
            <div class="dropdown dropdown-end">
              <button class="btn btn-ghost gap-2 normal-case">
                <div class="avatar placeholder">
                  <div class="w-8 h-8 rounded-full bg-primary text-primary-content">
                    <span class="text-sm font-semibold">
                      {$authStore.user?.full_name?.charAt(0).toUpperCase() || $authStore.user?.email?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                </div>
                <div class="text-left hidden md:block">
                  <div class="text-sm font-semibold">{$authStore.user?.full_name || $authStore.user?.email}</div>
                  <div class="text-xs text-slate-500 capitalize">{$authStore.user?.role?.replace('_', ' ')}</div>
                </div>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <ul class="menu menu-sm dropdown-content mt-3 z-10 p-2 shadow-lg bg-base-100 rounded-box w-64 border border-base-300">
                <li class="menu-title px-4 py-3 border-b border-base-300">
                  <div>
                    <div class="text-sm font-semibold text-slate-800">{$authStore.user?.full_name}</div>
                    <div class="text-xs text-slate-500">{$authStore.user?.email}</div>
                    <div class="badge badge-primary badge-sm mt-1 capitalize">{$authStore.user?.role?.replace('_', ' ')}</div>
                  </div>
                </li>
                <li><a href="/profile">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  Mi Perfil
                </a></li>
                {#if $authStore.user?.role === 'curador' || $authStore.user?.role === 'administrador'}
                  <li><a href="/admin">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Administración
                  </a></li>
                {/if}
                <div class="divider my-0"></div>
                <li><button on:click={handleLogout} class="text-error">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Cerrar sesión
                </button></li>
              </ul>
            </div>
          {:else}
            <a href="/login" class="btn btn-primary btn-sm">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Iniciar sesión
            </a>
          {/if}
        </div>

        <!-- Mobile Menu Button -->
        <button class="btn btn-ghost lg:hidden" on:click={toggleMenu}>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Navigation Bar -->
  <div class="bg-primary text-primary-content">
    <div class="container mx-auto px-4">
      <ul class="menu menu-horizontal hidden lg:flex p-0">
        <li>
          <a href="/" class="rounded-none hover:bg-primary-focus" class:bg-primary-focus={$page.url.pathname === '/'}>
            Inicio
          </a>
        </li>
        <li>
          <a href="/gallery" class="rounded-none hover:bg-primary-focus" class:bg-primary-focus={$page.url.pathname === '/gallery'}>
            Colecciones Digitales
          </a>
        </li>
        <li>
          <a href="/map" class="rounded-none hover:bg-primary-focus" class:bg-primary-focus={$page.url.pathname === '/map'}>
            Mapa
          </a>
        </li>
        <li>
          <a href="/research" class="rounded-none hover:bg-primary-focus" class:bg-primary-focus={$page.url.pathname === '/research'}>
            Investigación
          </a>
        </li>
        <li>
          <a href="/about" class="rounded-none hover:bg-primary-focus" class:bg-primary-focus={$page.url.pathname === '/about'}>
            Acerca del Proyecto
          </a>
        </li>
      </ul>
    </div>
  </div>

  <!-- Mobile Menu Drawer -->
  {#if isMenuOpen}
    <div class="lg:hidden bg-base-100 border-b border-base-300">
      <ul class="menu p-4">
        <li><a href="/" on:click={toggleMenu}>Inicio</a></li>
        <li><a href="/gallery" on:click={toggleMenu}>Colecciones Digitales</a></li>
        <li><a href="/map" on:click={toggleMenu}>Mapa</a></li>
        <li><a href="/research" on:click={toggleMenu}>Investigación</a></li>
        <li><a href="/about" on:click={toggleMenu}>Acerca del Proyecto</a></li>
        {#if !$isAuthenticated}
          <li><a href="/login" on:click={toggleMenu}>Iniciar sesión</a></li>
        {/if}
      </ul>
    </div>
  {/if}
</header>
