<script lang="ts">
  import { goto } from '$app/navigation';
  import { projectService } from '$lib/services';
  import { projectsStore } from '$lib/stores/projects';
  import { notificationsStore } from '$lib/stores/notifications';

  let name = '';
  let description = '';
  let startDate = '';
  let loading = false;

  const today = new Date().toISOString().split('T')[0];

  async function handleSubmit() {
    if (!name.trim()) {
      notificationsStore.warning('El nombre del proyecto es obligatorio');
      return;
    }

    if (startDate && startDate < today) {
      notificationsStore.error('La fecha de inicio no puede ser anterior a hoy');
      return;
    }

    try {
      loading = true;
      const project = await projectService.createProject({
        name: name.trim(),
        description: description.trim() || undefined,
        start_date: startDate || undefined
      });

      projectsStore.addProject(project);
      notificationsStore.success(`Proyecto "${project.name}" creado`);
      goto(`/proyectos/${project.id}`);
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al crear proyecto');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Crear Proyecto - ROGER</title>
</svelte:head>

<div class="max-w-2xl mx-auto px-4 sm:px-6 py-8">
  <div class="mb-6">
    <a href="/proyectos" class="btn btn-ghost btn-sm gap-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Volver a proyectos
    </a>
  </div>

  <div class="card bg-base-100 shadow-lg border border-base-300">
    <div class="card-body">
      <h1 class="card-title text-2xl mb-4">Crear Proyecto</h1>

      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-control mb-4">
          <label class="label" for="name">
            <span class="label-text font-semibold">Nombre del proyecto *</span>
          </label>
          <input
            id="name"
            type="text"
            placeholder="Ej: Investigación Norte de Chile"
            class="input input-bordered"
            bind:value={name}
            maxlength="255"
            required
          />
        </div>

        <div class="form-control mb-4">
          <label class="label" for="description">
            <span class="label-text font-semibold">Descripción</span>
          </label>
          <textarea
            id="description"
            placeholder="Describe el objetivo del proyecto..."
            class="textarea textarea-bordered h-24"
            bind:value={description}
          ></textarea>
        </div>

        <div class="form-control mb-6">
          <label class="label" for="start-date">
            <span class="label-text font-semibold">Fecha de inicio</span>
          </label>
          <input
            id="start-date"
            type="date"
            class="input input-bordered"
            bind:value={startDate}
            min={today}
          />
        </div>

        <div class="flex gap-3 justify-end">
          <a href="/proyectos" class="btn btn-ghost">Cancelar</a>
          <button type="submit" class="btn btn-primary" disabled={loading || !name.trim()}>
            {#if loading}
              <span class="loading loading-spinner loading-sm"></span>
            {/if}
            Crear Proyecto
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
