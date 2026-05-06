<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { apiClient } from '$lib/services/apiClient';

  let status: 'loading' | 'success' | 'error' = 'loading';
  let message = '';

  onMount(async () => {
    const token = $page.url.searchParams.get('token');
    if (!token) {
      status = 'error';
      message = 'El enlace no es valido.';
      return;
    }
    try {
      const resp = await apiClient.get<{ message: string }>(`/auth/me/confirm-email-change?token=${encodeURIComponent(token)}`);
      message = resp.message;
      status = 'success';
      setTimeout(() => goto('/login'), 3000);
    } catch (e: any) {
      status = 'error';
      message = e.detail || 'El enlace es invalido o ha expirado.';
    }
  });
</script>

<svelte:head>
  <title>Confirmar correo - ROGER</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-base-200 px-4">
  <div class="bg-base-100 rounded-2xl border border-base-300 shadow-sm p-8 max-w-md w-full text-center space-y-4">

    {#if status === 'loading'}
      <span class="loading loading-spinner loading-lg text-primary"></span>
      <p class="text-sm text-base-content/60">Verificando enlace...</p>

    {:else if status === 'success'}
      <div class="w-14 h-14 rounded-2xl bg-success/10 flex items-center justify-center mx-auto">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 class="text-xl font-bold">Correo actualizado</h1>
      <p class="text-sm text-base-content/60">{message}</p>
      <p class="text-xs text-base-content/40">Redirigiendo al inicio de sesion...</p>

    {:else}
      <div class="w-14 h-14 rounded-2xl bg-error/10 flex items-center justify-center mx-auto">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <h1 class="text-xl font-bold">Enlace no valido</h1>
      <p class="text-sm text-base-content/60">{message}</p>
      <a href="/login" class="btn btn-primary btn-sm">Ir al inicio de sesion</a>
    {/if}

  </div>
</div>
