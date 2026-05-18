<script lang="ts">
  import { tick } from 'svelte';
  import { fade } from 'svelte/transition';
  import { projectService } from '$lib/services/projectService';
  import type { Project } from '$lib/types';

  export let open: boolean = false;
  export let photographIds: number[] = [];
  export let onClose: () => void = () => {};
  export let onAttached: (project: Project, added: number, skipped: number) => void = () => {};

  let projects: Project[] = [];
  let loading = false;
  let error: string | null = null;
  let selectedProjectId: number | null = null;
  let notes = '';
  let attaching = false;

  let dialog: HTMLDivElement;
  let previouslyFocused: HTMLElement | null = null;

  $: if (open) handleOpen();
  $: if (!open) previouslyFocused = null;

  async function handleOpen() {
    previouslyFocused = (document.activeElement as HTMLElement) ?? null;
    await load();
    await tick();
    focusFirst();
  }

  async function load() {
    if (projects.length > 0) return;
    loading = true;
    error = null;
    try {
      const res = await projectService.listProjects(0, 100);
      projects = res.projects.filter((p) => p.is_active);
    } catch (e: any) {
      error = e?.detail || 'No se pudo cargar la lista de proyectos';
    } finally {
      loading = false;
    }
  }

  function focusFirst() {
    if (!dialog) return;
    const focusables = getFocusables();
    if (focusables.length > 0) focusables[0].focus();
  }

  function getFocusables(): HTMLElement[] {
    if (!dialog) return [];
    return Array.from(
      dialog.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
      ),
    ).filter((el) => !el.hasAttribute('disabled') && el.offsetParent !== null);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      e.preventDefault();
      close();
      return;
    }
    if (e.key !== 'Tab') return;
    const focusables = getFocusables();
    if (focusables.length === 0) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    const active = document.activeElement as HTMLElement;
    if (e.shiftKey && active === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && active === last) {
      e.preventDefault();
      first.focus();
    }
  }

  async function attach() {
    if (!selectedProjectId || photographIds.length === 0) return;
    attaching = true;
    error = null;
    try {
      const res = await projectService.attachPhotographs(
        selectedProjectId,
        photographIds,
        notes.trim() || undefined,
      );
      const project = projects.find((p) => p.id === selectedProjectId)!;
      onAttached(project, res.added, res.skipped);
      close();
    } catch (e: any) {
      error = e?.detail || 'No se pudieron asociar las fotografías';
    } finally {
      attaching = false;
    }
  }

  function close() {
    selectedProjectId = null;
    notes = '';
    error = null;
    onClose();
    if (previouslyFocused && typeof previouslyFocused.focus === 'function') {
      // Defer focus return until after Svelte unmounts the modal
      setTimeout(() => previouslyFocused?.focus(), 0);
    }
  }

  function handleBackdrop(e: MouseEvent) {
    if (e.target === e.currentTarget) close();
  }
</script>

{#if open}
  <div
    class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
    on:click={handleBackdrop}
    on:keydown={handleKeydown}
    role="presentation"
    transition:fade={{ duration: 150 }}
  >
    <div
      bind:this={dialog}
      class="bg-base-100 rounded-2xl shadow-2xl max-w-md w-full max-h-[85vh] flex flex-col"
      role="dialog"
      aria-modal="true"
      aria-labelledby="project-picker-title"
      aria-describedby="project-picker-desc"
    >
      <header class="p-5 border-b border-base-200">
        <h2 id="project-picker-title" class="text-xl font-bold">Añadir a proyecto</h2>
        <p id="project-picker-desc" class="text-sm text-base-content/60 mt-1">
          {photographIds.length} {photographIds.length === 1 ? 'fotografía' : 'fotografías'} seleccionadas
        </p>
      </header>

      <div class="p-5 overflow-y-auto flex-1">
        {#if loading}
          <div class="flex justify-center py-8" aria-live="polite" aria-busy="true">
            <span class="loading loading-spinner loading-md" aria-label="Cargando proyectos"></span>
          </div>
        {:else if error}
          <div class="alert alert-error" role="alert">
            <span>{error}</span>
          </div>
        {:else if projects.length === 0}
          <p class="text-center text-base-content/60 py-8">
            No tienes proyectos activos. Crea uno desde la sección de Proyectos.
          </p>
        {:else}
          <fieldset class="space-y-2">
            <legend class="sr-only">Selecciona el proyecto destino</legend>
            {#each projects as project (project.id)}
              <label
                class="flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors hover:bg-base-200 focus-within:ring-2 focus-within:ring-primary"
                class:border-primary={selectedProjectId === project.id}
                class:bg-primary={selectedProjectId === project.id}
                class:bg-opacity-5={selectedProjectId === project.id}
              >
                <input
                  type="radio"
                  name="project"
                  class="radio radio-primary mt-1"
                  value={project.id}
                  bind:group={selectedProjectId}
                />
                <span class="flex-1 min-w-0">
                  <span class="block font-medium truncate">{project.name}</span>
                  {#if project.description}
                    <span class="block text-sm text-base-content/60 line-clamp-2 mt-0.5">{project.description}</span>
                  {/if}
                </span>
              </label>
            {/each}
          </fieldset>

          <div class="form-control mt-4">
            <label class="label" for="attach-notes">
              <span class="label-text text-sm">Nota (opcional)</span>
            </label>
            <textarea
              id="attach-notes"
              class="textarea textarea-bordered text-sm"
              rows="2"
              maxlength="500"
              placeholder="Contexto o razón de la selección…"
              bind:value={notes}
            ></textarea>
          </div>
        {/if}
      </div>

      <footer class="p-4 border-t border-base-200 flex justify-end gap-2">
        <button class="btn btn-ghost min-h-[44px]" on:click={close} disabled={attaching}>
          Cancelar
        </button>
        <button
          class="btn btn-primary min-h-[44px]"
          on:click={attach}
          disabled={!selectedProjectId || attaching || projects.length === 0}
        >
          {#if attaching}
            <span class="loading loading-spinner loading-sm" aria-hidden="true"></span>
            <span class="sr-only">Asociando…</span>
          {/if}
          Añadir
        </button>
      </footer>
    </div>
  </div>
{/if}

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-clamp: 2;
    overflow: hidden;
  }
</style>
