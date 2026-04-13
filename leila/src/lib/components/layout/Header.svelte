<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { authStore, isAuthenticated } from '$lib/stores/auth';
  import { invitationsStore, pendingCount } from '$lib/stores/invitations';
  import { invitationService } from '$lib/services/invitationService';
  import ThemeToggle from '$lib/components/common/ThemeToggle.svelte';
  import { locale, t, switchLocale, LOCALES } from '$lib/stores/locale';

  let isMenuOpen = false;

  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }

  function handleLogout() {
    invitationsStore.reset();
    authStore.logout();
  }

  async function loadInvitations() {
    if (!$isAuthenticated) return;
    try {
      invitationsStore.setLoading(true);
      const resp = await invitationService.listPending();
      invitationsStore.setPending(resp.invitations);
    } catch {
      // silent — not critical
    } finally {
      invitationsStore.setLoading(false);
    }
  }

  onMount(() => {
    loadInvitations();
  });

  $: if ($isAuthenticated) loadInvitations();
</script>

<header class="sticky top-0 z-50 bg-base-100/90 backdrop-blur-sm border-b border-base-content/10">
  <!-- Top Bar -->
  <div class="bg-neutral text-neutral-content">
    <div class="container mx-auto px-4">
      <div class="flex justify-end items-center h-8 text-xs">
        <a href="/ayuda" class="hover:text-neutral-content/70 px-3 transition-colors">{$t.topbar.help}</a>
        <a href="/contacto" class="hover:text-neutral-content/70 px-3 transition-colors">{$t.topbar.contact}</a>
        <div class="dropdown dropdown-end">
          <button
            tabindex="0"
            class="hover:text-neutral-content/70 px-3 transition-colors flex items-center gap-1.5 font-semibold"
            aria-label="Cambiar idioma"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
            <span class="uppercase text-xs" translate="no">{$locale}</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 opacity-60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          <!-- svelte-ignore a11y-no-noninteractive-tabindex -->
          <ul tabindex="0" role="menu" class="dropdown-content menu menu-sm bg-neutral text-neutral-content shadow-lg rounded-box mt-1 w-36 p-1 z-[999]">
            {#each LOCALES as lang}
              <li>
                <button
                  class="flex items-center gap-2 w-full {$locale === lang.code ? 'font-bold opacity-100' : 'opacity-70 hover:opacity-100'}"
                  on:click={() => switchLocale(lang.code)}
                >
                  <span class="uppercase text-xs w-6" translate="no">{lang.code}</span>
                  <span translate="no">{lang.label}</span>
                  {#if $locale === lang.code}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 ml-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                    </svg>
                  {/if}
                </button>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    </div>
  </div>

  <!-- Main Header -->
  <div class="bg-transparent">
    <div class="container mx-auto px-4 py-3">
      <div class="flex items-center justify-between">
        <!-- Logo and Branding -->
        <a href="/" class="flex items-center gap-3 hover:opacity-90 transition-opacity">
          <div class="rounded-lg overflow-hidden bg-base-100 p-1">
            <img src="/images/ucn.png" alt="UCN" class="h-12 w-auto object-contain" />
          </div>
          <div>
            <div class="text-xs text-base-content/50 uppercase tracking-widest font-semibold" translate="no">Universidad Católica del Norte</div>
            <div class="text-lg font-bold text-base-content" translate="no">Fondo Robert Gerstmann</div>
          </div>
        </a>

        <!-- Search and User Actions -->
        <div class="hidden md:flex items-center gap-2">
          <ThemeToggle />
          <div class="form-control">
            <div class="join">
              <input type="text" placeholder={$t.search.placeholder} class="input input-bordered join-item w-64 focus:outline-primary" />
              <button class="btn btn-primary join-item btn-search-animated">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </div>

          {#if $isAuthenticated}
            <div class="dropdown dropdown-end">
              <button class="btn btn-ghost gap-2 normal-case">
                <div class="avatar placeholder relative">
                  <div class="w-8 h-8 rounded-full bg-primary text-primary-content">
                    <span class="text-sm font-semibold">
                      {$authStore.user?.full_name?.charAt(0).toUpperCase() || $authStore.user?.email?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  {#if $pendingCount > 0}
                    <span class="absolute -top-1 -right-1 badge badge-error badge-xs text-white font-bold min-w-[16px] h-4 flex items-center justify-center text-[10px] px-1">
                      {$pendingCount}
                    </span>
                  {/if}
                </div>
                <div class="text-left hidden md:block">
                  <div class="text-sm font-semibold">{$authStore.user?.full_name || $authStore.user?.email}</div>
                  <div class="text-xs text-base-content/50 capitalize">{$authStore.user?.role?.replace('_', ' ')}</div>
                </div>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <ul class="menu menu-sm dropdown-content mt-3 z-10 p-2 shadow-lg bg-base-100 rounded-box w-64 border border-base-300">
                <li class="menu-title px-4 py-3 border-b border-base-300">
                  <div>
                    <div class="text-sm font-semibold text-base-content">{$authStore.user?.full_name}</div>
                    <div class="text-xs text-base-content/50">{$authStore.user?.email}</div>
                    <div class="badge badge-primary badge-sm mt-1 capitalize">{$authStore.user?.role?.replace('_', ' ')}</div>
                  </div>
                </li>
                <li><a href="/profile">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {$t.auth.profile}
                </a></li>
                <li><a href="/proyectos">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  {$t.auth.projects}
                </a></li>
                {#if $authStore.user?.role === 'curador' || $authStore.user?.role === 'administrador'}
                  <li><a href="/admin">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    {$t.auth.admin}
                  </a></li>
                {/if}
                {#if $pendingCount > 0}
                  <div class="divider my-0"></div>
                  <li>
                    <a href="/proyectos" class="flex items-center gap-3 px-3 py-2.5 text-warning hover:bg-warning/10">
                      <div class="relative flex-shrink-0">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                        <span class="absolute -top-1.5 -right-1.5 badge badge-error badge-xs text-white font-bold min-w-[14px] h-3.5 text-[9px] px-0.5">
                          {$pendingCount}
                        </span>
                      </div>
                      <div class="min-w-0">
                        <p class="text-xs font-semibold leading-tight">
                          {$pendingCount === 1 ? '1 invitación pendiente' : `${$pendingCount} invitaciones pendientes`}
                        </p>
                        <p class="text-[10px] text-base-content/40 leading-tight mt-0.5">Ver en Mis Proyectos →</p>
                      </div>
                    </a>
                  </li>
                {/if}
                <div class="divider my-0"></div>
                <li><button on:click={handleLogout} class="text-error">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  {$t.auth.logout}
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

        <!-- Mobile Actions -->
        <div class="flex items-center gap-1 lg:hidden">
          <ThemeToggle />
          <button class="btn btn-ghost btn-circle" on:click={toggleMenu} aria-label="Menú">
            {#if isMenuOpen}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            {/if}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Navigation Bar -->
  <div class="border-t border-base-content/10 hidden lg:block">
    <div class="container mx-auto px-4">
      <ul class="menu menu-horizontal p-0 gap-1">
        <li>
          <a href="/" class="rounded-full font-semibold hover:bg-primary/10 hover:text-primary text-sm" class:bg-primary={$page.url.pathname === '/'} class:text-primary-content={$page.url.pathname === '/'}>
            {$t.nav.home}
          </a>
        </li>
        <li>
          <a href="/colecciones" class="rounded-full font-semibold hover:bg-primary/10 hover:text-primary text-sm" class:bg-primary={$page.url.pathname === '/colecciones'} class:text-primary-content={$page.url.pathname === '/colecciones'}>
            {$t.nav.collections}
          </a>
        </li>
        <li>
          <a href="/mapa" class="rounded-full font-semibold hover:bg-primary/10 hover:text-primary text-sm" class:bg-primary={$page.url.pathname === '/mapa'} class:text-primary-content={$page.url.pathname === '/mapa'}>
            {$t.nav.map}
          </a>
        </li>
        <li>
          <a href="/investigacion" class="rounded-full font-semibold hover:bg-primary/10 hover:text-primary text-sm" class:bg-primary={$page.url.pathname === '/investigacion'} class:text-primary-content={$page.url.pathname === '/investigacion'}>
            {$t.nav.research}
          </a>
        </li>
        <li>
          <a href="/sobre-roger" class="rounded-full font-semibold hover:bg-primary/10 hover:text-primary text-sm" class:bg-primary={$page.url.pathname === '/sobre-roger'} class:text-primary-content={$page.url.pathname === '/sobre-roger'}>
            {$t.nav.about}
          </a>
        </li>
      </ul>
    </div>
  </div>

  <!-- Mobile Menu Drawer -->
  {#if isMenuOpen}
    <div class="lg:hidden bg-base-100 border-b border-base-content/10 shadow-lg">
      <ul class="menu p-4 gap-1 text-base font-semibold">
        <li><a href="/" class="rounded-lg" on:click={toggleMenu}>{$t.nav.home}</a></li>
        <li><a href="/colecciones" class="rounded-lg" on:click={toggleMenu}>{$t.nav.collections}</a></li>
        <li><a href="/mapa" class="rounded-lg" on:click={toggleMenu}>{$t.nav.map}</a></li>
        <li><a href="/investigacion" class="rounded-lg" on:click={toggleMenu}>{$t.nav.research}</a></li>
        <li><a href="/sobre-roger" class="rounded-lg" on:click={toggleMenu}>{$t.nav.about}</a></li>
        {#if $isAuthenticated}
          <div class="divider my-1"></div>
          <li><a href="/proyectos" class="rounded-lg" on:click={toggleMenu}>Mis Proyectos</a></li>
          <li><a href="/profile" class="rounded-lg" on:click={toggleMenu}>Mi Perfil</a></li>
          <li>
            <button class="rounded-lg text-error" on:click={() => { handleLogout(); toggleMenu(); }}>
              {$t.auth.logout}
            </button>
          </li>
        {:else}
          <div class="divider my-1"></div>
          <li><a href="/login" class="btn btn-primary rounded-lg" on:click={toggleMenu}>{$t.auth.login}</a></li>
        {/if}
      </ul>
    </div>
  {/if}
</header>
