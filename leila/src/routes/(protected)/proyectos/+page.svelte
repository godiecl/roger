<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth';
  import { projectService } from '$lib/services';
  import { projectsStore } from '$lib/stores/projects';
  import { notificationsStore } from '$lib/stores/notifications';
  import type { Project } from '$lib/types';

  let loading = true;
  let error: string | null = null;

  $: projects = $projectsStore.projects;
  $: currentUserId = $authStore.user?.id;

  onMount(async () => {
    await loadProjects();
  });

  async function loadProjects() {
    try {
      loading = true;
      error = null;
      const response = await projectService.listProjects();
      projectsStore.setProjects(response.projects);
    } catch (e: any) {
      error = e.detail || 'Error al cargar proyectos';
      notificationsStore.error(error!);
    } finally {
      loading = false;
    }
  }

  async function handleDelete(project: Project) {
    if (!confirm(`¿Estás seguro de eliminar "${project.name}"? Esta acción no se puede deshacer.`)) {
      return;
    }

    try {
      await projectService.deleteProject(project.id);
      projectsStore.removeProject(project.id);
      notificationsStore.success('Proyecto eliminado');
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al eliminar proyecto');
    }
  }

  function formatDate(dateStr?: string): string {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('es-CL');
  }
</script>

<svelte:head>
  <title>Mis Proyectos - ROGER</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-4 sm:px-6 py-8">
  <!-- Header -->
  <div class="flex items-center justify-between mb-8">
    <div>
      <h1 class="text-3xl font-bold">Mis Proyectos</h1>
      <p class="text-base-content/60 mt-1">Gestiona tus grupos de trabajo e investigación</p>
    </div>
    <a href="/proyectos/nuevo" class="btn btn-primary">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
      Crear Proyecto
    </a>
  </div>

  <!-- Loading -->
  {#if loading}
    <div class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

  <!-- Error -->
  {:else if error}
    <div class="alert alert-error">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{error}</span>
      <button class="btn btn-sm" on:click={loadProjects}>Reintentar</button>
    </div>

  <!-- Empty -->
  {:else if projects.length === 0}
    <div class="text-center py-16">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-base-content/30 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
      <h2 class="text-xl font-semibold mb-2">No tienes proyectos</h2>
      <p class="text-base-content/60 mb-6">Crea un proyecto para comenzar a colaborar con otros investigadores</p>
      <a href="/proyectos/nuevo" class="btn btn-primary">Crear mi primer proyecto</a>
    </div>

  <!-- Project List -->
  {:else}
    <div class="grid gap-4">
      {#each projects as project (project.id)}
        <div class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow border border-base-300">
          <div class="card-body">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <a href="/proyectos/{project.id}" class="card-title text-lg hover:text-primary transition-colors">
                  {project.name}
                </a>
                {#if project.description}
                  <p class="text-base-content/60 text-sm mt-1">{project.description}</p>
                {/if}
                <div class="flex gap-4 mt-3 text-sm text-base-content/50">
                  {#if project.start_date}
                    <span>Inicio: {formatDate(project.start_date)}</span>
                  {/if}
                  {#if project.end_date}
                    <span>Fin: {formatDate(project.end_date)}</span>
                  {/if}
                </div>
              </div>

              <div class="flex items-center gap-2">
                {#if project.is_active}
                  <span class="badge badge-success badge-sm">Activo</span>
                {:else}
                  <span class="badge badge-ghost badge-sm">Inactivo</span>
                {/if}

                {#if project.owner_id === currentUserId}
                  <span class="badge badge-primary badge-sm">Owner</span>
                  <button
                    class="btn btn-ghost btn-sm btn-square text-error"
                    on:click|stopPropagation={() => handleDelete(project)}
                    title="Eliminar proyecto"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                {/if}
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
