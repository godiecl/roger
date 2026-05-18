<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { projectService, type ProjectPhotographLink } from '$lib/services/projectService';
  import { clusterService, type ClusteringJob } from '$lib/services/clusterService';
  import { notificationsStore } from '$lib/stores/notifications';
  import type { Project } from '$lib/types';

  $: projectId = Number($page.params.id);

  let project: Project | null = null;
  let photos: ProjectPhotographLink[] = [];
  let recentJobs: ClusteringJob[] = [];
  let loading = true;
  let error: string | null = null;
  let removingId: number | null = null;

  onMount(async () => {
    try {
      const [proj, photosRes, jobsRes] = await Promise.all([
        projectService.getProject(projectId),
        projectService.listProjectPhotographs(projectId, { limit: 200 }),
        clusterService.list({ limit: 10 }),
      ]);
      project = proj;
      photos = photosRes.items;
      // Filtrar clusters cuyo job involucra alguna foto del proyecto
      const projectPhotoIds = new Set(photos.map((p) => p.photograph_id));
      recentJobs = jobsRes.jobs.filter((j) =>
        j.photograph_ids.some((id) => projectPhotoIds.has(id)),
      );
    } catch (e: any) {
      error = e?.detail || e?.message || 'No se pudo cargar el proyecto';
    } finally {
      loading = false;
    }
  });

  async function removePhoto(photographId: number) {
    removingId = photographId;
    try {
      await projectService.detachPhotograph(projectId, photographId);
      photos = photos.filter((p) => p.photograph_id !== photographId);
      notificationsStore.success('Fotografía desvinculada');
    } catch (e: any) {
      notificationsStore.error(e?.detail || 'No se pudo desvincular');
    } finally {
      removingId = null;
    }
  }
</script>

<svelte:head>
  <title>{project ? `${project.name} · Fotografías` : 'Fotografías del proyecto'}</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-6xl">
  <header class="mb-6">
    <a href="/proyectos?p={projectId}" class="text-sm text-base-content/60 hover:text-base-content inline-flex items-center gap-1 mb-3">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Volver al proyecto
    </a>
    <h1 class="text-3xl font-bold">{project?.name ?? 'Proyecto'}</h1>
    <p class="text-base-content/60 mt-1">
      Fotografías y agrupaciones asociadas a este proyecto.
    </p>
  </header>

  {#if loading}
    <div class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if error}
    <div class="alert alert-error"><span>{error}</span></div>
  {:else}
    <section class="mb-10">
      <h2 class="text-xl font-semibold mb-3">
        Fotografías asociadas
        <span class="badge badge-neutral ml-2">{photos.length}</span>
      </h2>

      {#if photos.length === 0}
        <p class="text-base-content/60">
          Aún no hay fotografías asociadas. Selecciónalas desde el <a href="/archivo" class="link link-primary">archivo</a> y usa "Añadir a proyecto".
        </p>
      {:else}
        <div class="overflow-x-auto">
          <table class="table table-zebra">
            <thead>
              <tr>
                <th>Foto #</th>
                <th>Añadida</th>
                <th>Por</th>
                <th>Nota</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {#each photos as link (link.id)}
                <tr>
                  <td class="font-mono">{link.photograph_id}</td>
                  <td class="text-sm">{new Date(link.added_at).toLocaleDateString()}</td>
                  <td class="text-sm text-base-content/60">{link.added_by ?? '—'}</td>
                  <td class="text-sm">{link.notes ?? '—'}</td>
                  <td class="text-right">
                    <button
                      class="btn btn-xs btn-ghost text-error"
                      on:click={() => removePhoto(link.photograph_id)}
                      disabled={removingId === link.photograph_id}
                    >
                      Quitar
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </section>

    <section>
      <h2 class="text-xl font-semibold mb-3">
        Agrupaciones recientes
        <span class="badge badge-neutral ml-2">{recentJobs.length}</span>
      </h2>

      {#if recentJobs.length === 0}
        <p class="text-base-content/60">
          No hay agrupaciones que incluyan fotografías de este proyecto. Genera una desde un cajón en el archivo.
        </p>
      {:else}
        <div class="grid gap-3 sm:grid-cols-2">
          {#each recentJobs as job (job.id)}
            <a
              href="/archivo/clusters/{job.id}"
              class="card bg-base-100 shadow hover:shadow-md transition-all"
            >
              <div class="card-body p-4">
                <div class="flex items-start justify-between gap-2">
                  <h3 class="font-semibold">Agrupación #{job.id}</h3>
                  <span class="badge badge-sm">{job.algorithm}</span>
                </div>
                <p class="text-sm text-base-content/60">
                  {job.n_clusters} cluster{job.n_clusters !== 1 ? 's' : ''} ·
                  {job.photograph_ids.length} fotos
                </p>
                {#if job.created_at}
                  <p class="text-xs text-base-content/50">
                    {new Date(job.created_at).toLocaleString()}
                  </p>
                {/if}
              </div>
            </a>
          {/each}
        </div>
      {/if}
    </section>
  {/if}
</div>
