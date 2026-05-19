<script lang="ts">
  import { onMount } from 'svelte';
  import { imageService } from '$lib/services/imageService';
  import { archiveService } from '$lib/services/archiveService';
  import { notificationsStore } from '$lib/stores/notifications';
  import ImageGrid from '$lib/components/viewer/ImageGrid.svelte';
  import ImageViewer from '$lib/components/viewer/ImageViewer.svelte';
  import type { Collection, Image } from '$lib/types';
  import type { CreateCollectionPayload, BulkUploadResult } from '$lib/services/archiveService';

  type Tab = 'colecciones' | 'subir' | 'masiva' | 'explorar';
  let activeTab: Tab = 'colecciones';

  // ── Collections ────────────────────────────────────────────────────────────
  let collections: Collection[] = [];
  let loadingCollections = true;
  let showColModal = false;
  let editingCol: Collection | null = null;
  let savingCol = false;
  let colForm = {
    name: '',
    description: '',
    photographer_name: '',
    origin_country: '',
    date_range_from: '',
    date_range_to: '',
    is_public: true,
    license: '',
    copyright_notes: '',
  };

  // Cover change
  let coverColId: number | null = null;
  let coverFile: File | null = null;
  let coverPreviewUrl: string | null = null;
  let savingCover = false;
  let coverInputEl: HTMLInputElement;

  // ── Delete confirmation ────────────────────────────────────────────────────
  type DeleteMode = 'collection' | 'images';
  let deleteTarget: { mode: DeleteMode; collection: Collection } | null = null;
  let deleteConfirmInput = '';
  let deleting = false;

  $: deleteNameMatch =
    deleteTarget !== null &&
    deleteConfirmInput.trim() === deleteTarget.collection.name.trim();

  // ── Single upload ──────────────────────────────────────────────────────────
  let uploadColId: number | null = null;
  let uploadFile: File | null = null;
  let uploadPreviewUrl: string | null = null;
  let uploadDragOver = false;
  let uploading = false;
  let uploadForm = { title: '', year: '', location: '', description: '', is_public: true, box: '', subdivision: '' };
  let uploadInputEl: HTMLInputElement;

  // ── Bulk upload ────────────────────────────────────────────────────────────
  let bulkColId: number | null = null;
  let bulkFiles: File[] = [];
  let bulkDragOver = false;
  let bulkUploading = false;
  let bulkDefaults = { year: '', location: '', is_public: true, box: '', subdivision: '' };
  let bulkResults: BulkUploadResult[] = [];
  let bulkInputEl: HTMLInputElement;

  // ── Explore ────────────────────────────────────────────────────────────────
  let exploreColId: number | null = null;
  let exploreSearch = '';
  let exploreImages: Image[] = [];
  let exploreTotal = 0;
  let explorePage = 0;
  let loadingExplore = false;
  let showViewer = false;
  let viewerImage: Image | null = null;

  const PER_PAGE = 24;
  $: exploreTotalPages = Math.ceil(exploreTotal / PER_PAGE);
  $: exploreFiltered = exploreSearch.trim()
    ? exploreImages.filter(
        img =>
          img.title.toLowerCase().includes(exploreSearch.toLowerCase()) ||
          (img.location ?? '').toLowerCase().includes(exploreSearch.toLowerCase())
      )
    : exploreImages;

  onMount(loadCollections);

  // ── Collections helpers ────────────────────────────────────────────────────

  async function loadCollections() {
    loadingCollections = true;
    try {
      const res = await archiveService.listAllCollections({ limit: 200 });
      collections = res.collections;
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al cargar colecciones');
    } finally {
      loadingCollections = false;
    }
  }

  function openCreate() {
    editingCol = null;
    colForm = {
      name: '',
      description: '',
      photographer_name: '',
      origin_country: '',
      date_range_from: '',
      date_range_to: '',
      is_public: true,
      license: '',
      copyright_notes: '',
    };
    showColModal = true;
  }

  function openEdit(col: Collection) {
    editingCol = col;
    colForm = {
      name: col.name,
      description: col.description ?? '',
      photographer_name: col.photographer_name ?? '',
      origin_country: col.origin_country ?? '',
      date_range_from: col.date_range_from ?? '',
      date_range_to: col.date_range_to ?? '',
      is_public: col.is_public,
      license: col.license ?? '',
      copyright_notes: col.copyright_notes ?? '',
    };
    showColModal = true;
  }

  async function saveCol() {
    if (!colForm.name.trim()) return;
    savingCol = true;
    try {
      const payload: CreateCollectionPayload = {
        name: colForm.name.trim(),
        description: colForm.description || undefined,
        photographer_name: colForm.photographer_name || undefined,
        origin_country: colForm.origin_country || undefined,
        date_range_from: colForm.date_range_from ? Number(colForm.date_range_from) : undefined,
        date_range_to: colForm.date_range_to ? Number(colForm.date_range_to) : undefined,
        is_public: colForm.is_public,
        license: colForm.license || undefined,
        copyright_notes: colForm.copyright_notes || undefined,
      };
      if (editingCol) {
        await archiveService.updateCollection(editingCol.id, payload);
        notificationsStore.success('Colección actualizada');
      } else {
        await archiveService.createCollection(payload);
        notificationsStore.success('Colección creada');
      }
      showColModal = false;
      await loadCollections();
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al guardar');
    } finally {
      savingCol = false;
    }
  }

  function startCoverChange(colId: number) {
    coverColId = colId;
    coverFile = null;
    coverPreviewUrl = null;
    coverInputEl?.click();
  }

  function onCoverChange(e: Event) {
    const f = (e.target as HTMLInputElement).files?.[0];
    if (!f) return;
    coverFile = f;
    coverPreviewUrl = URL.createObjectURL(f);
    (e.target as HTMLInputElement).value = '';
  }

  async function saveCover() {
    if (!coverColId || !coverFile) return;
    savingCover = true;
    try {
      await archiveService.setCollectionCover(coverColId, coverFile);
      notificationsStore.success('Portada actualizada');
      cancelCover();
      await loadCollections();
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al subir portada');
    } finally {
      savingCover = false;
    }
  }

  function cancelCover() {
    coverFile = null;
    coverPreviewUrl = null;
    coverColId = null;
  }

  // ── Single upload helpers ──────────────────────────────────────────────────

  function onUploadDrop(e: DragEvent) {
    e.preventDefault();
    uploadDragOver = false;
    const f = e.dataTransfer?.files?.[0];
    if (f?.type.startsWith('image/')) setUploadFile(f);
  }

  function setUploadFile(f: File) {
    uploadFile = f;
    uploadPreviewUrl = URL.createObjectURL(f);
    if (!uploadForm.title) uploadForm.title = f.name.replace(/\.[^.]+$/, '');
  }

  function onUploadFileChange(e: Event) {
    const f = (e.target as HTMLInputElement).files?.[0];
    if (f) setUploadFile(f);
    (e.target as HTMLInputElement).value = '';
  }

  async function submitUpload() {
    if (!uploadFile || !uploadColId) return;
    uploading = true;
    try {
      await archiveService.uploadSingle(uploadFile, {
        collection_id: uploadColId,
        title: uploadForm.title || undefined,
        year: uploadForm.year ? Number(uploadForm.year) : undefined,
        location: uploadForm.location || undefined,
        description: uploadForm.description || undefined,
        is_public: uploadForm.is_public,
        box: uploadForm.box || undefined,
        subdivision: uploadForm.subdivision || undefined,
      });
      notificationsStore.success('Fotografía subida correctamente');
      uploadFile = null;
      uploadPreviewUrl = null;
      uploadForm = { title: '', year: '', location: '', description: '', is_public: true, box: '', subdivision: '' };
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al subir fotografía');
    } finally {
      uploading = false;
    }
  }

  // ── Bulk upload helpers ────────────────────────────────────────────────────

  function onBulkDrop(e: DragEvent) {
    e.preventDefault();
    bulkDragOver = false;
    const files = Array.from(e.dataTransfer?.files ?? []).filter(f =>
      f.type.startsWith('image/')
    );
    bulkFiles = [...bulkFiles, ...files];
  }

  function onBulkFileChange(e: Event) {
    const files = Array.from((e.target as HTMLInputElement).files ?? []);
    bulkFiles = [...bulkFiles, ...files];
    (e.target as HTMLInputElement).value = '';
  }

  function removeBulkFile(i: number) {
    bulkFiles = bulkFiles.filter((_, idx) => idx !== i);
  }

  async function submitBulk() {
    if (!bulkFiles.length || !bulkColId) return;
    bulkUploading = true;
    bulkResults = [];
    try {
      const res = await archiveService.uploadBulk(bulkFiles, {
        collection_id: bulkColId,
        year: bulkDefaults.year ? Number(bulkDefaults.year) : undefined,
        location: bulkDefaults.location || undefined,
        is_public: bulkDefaults.is_public,
        box: bulkDefaults.box || undefined,
        subdivision: bulkDefaults.subdivision || undefined,
      });
      bulkResults = res.results;
      const s = res.succeeded;
      const f = res.failed;
      if (f === 0) {
        notificationsStore.success(`${s} fotografía${s !== 1 ? 's' : ''} subida${s !== 1 ? 's' : ''}`);
      } else {
        notificationsStore.error(`${s} subidas, ${f} con error`);
      }
      if (s > 0) bulkFiles = [];
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error en carga masiva');
    } finally {
      bulkUploading = false;
    }
  }

  // ── Explore helpers ────────────────────────────────────────────────────────

  async function loadExplore() {
    if (!exploreColId) return;
    loadingExplore = true;
    try {
      const res = await imageService.listImages({
        collection_id: exploreColId,
        skip: explorePage * PER_PAGE,
        limit: PER_PAGE,
      });
      exploreImages = res.images;
      exploreTotal = res.total;
    } catch {
      exploreImages = [];
      exploreTotal = 0;
    } finally {
      loadingExplore = false;
    }
  }

  function onExploreColChange() {
    explorePage = 0;
    exploreImages = [];
    exploreTotal = 0;
    exploreSearch = '';
    loadExplore();
  }

  async function explorePaginate(delta: number) {
    explorePage += delta;
    await loadExplore();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // ── Delete helpers ─────────────────────────────────────────────────────────

  function openDeleteCollection(col: Collection) {
    deleteTarget = { mode: 'collection', collection: col };
    deleteConfirmInput = '';
  }

  function openDeleteImages(col: Collection) {
    deleteTarget = { mode: 'images', collection: col };
    deleteConfirmInput = '';
  }

  function cancelDelete() {
    deleteTarget = null;
    deleteConfirmInput = '';
  }

  async function confirmDelete() {
    if (!deleteTarget || !deleteNameMatch) return;
    deleting = true;
    try {
      const { mode, collection } = deleteTarget;
      if (mode === 'collection') {
        await archiveService.deleteCollection(collection.id);
        notificationsStore.success(`Colección "${collection.name}" eliminada`);
        if (exploreColId === collection.id) {
          exploreColId = null;
          exploreImages = [];
          exploreTotal = 0;
        }
        await loadCollections();
      } else {
        await archiveService.deleteImagesByCollection(collection.id);
        notificationsStore.success(`Imágenes de "${collection.name}" eliminadas`);
        if (exploreColId === collection.id) {
          exploreImages = [];
          exploreTotal = 0;
        }
      }
      cancelDelete();
    } catch (e: any) {
      notificationsStore.error(e?.detail ?? 'Error al eliminar');
    } finally {
      deleting = false;
    }
  }
</script>

<svelte:head>
  <title>Archivo · ROGER</title>
</svelte:head>

<!-- Hidden file inputs -->
<input bind:this={coverInputEl} type="file" accept="image/*" class="hidden" on:change={onCoverChange} />
<input bind:this={uploadInputEl} type="file" accept="image/*" class="hidden" on:change={onUploadFileChange} />
<input bind:this={bulkInputEl} type="file" accept="image/*" multiple class="hidden" on:change={onBulkFileChange} />

<div class="container mx-auto px-4 sm:px-6 py-8 max-w-7xl">

  <header class="mb-6">
    <h1 class="text-3xl font-bold">Administración del Archivo</h1>
    <p class="text-base-content/60 mt-1 text-sm">Gestiona colecciones, sube fotografías y explora el acervo.</p>
  </header>

  <!-- Tabs -->
  <div role="tablist" class="tabs tabs-bordered tabs-lg mb-8">
    <button
      role="tab"
      class="tab {activeTab === 'colecciones' ? 'tab-active font-semibold' : ''}"
      on:click={() => activeTab = 'colecciones'}
    >
      Colecciones
    </button>
    <button
      role="tab"
      class="tab {activeTab === 'subir' ? 'tab-active font-semibold' : ''}"
      on:click={() => activeTab = 'subir'}
    >
      Subir foto
    </button>
    <button
      role="tab"
      class="tab {activeTab === 'masiva' ? 'tab-active font-semibold' : ''}"
      on:click={() => activeTab = 'masiva'}
    >
      Carga masiva
    </button>
    <button
      role="tab"
      class="tab {activeTab === 'explorar' ? 'tab-active font-semibold' : ''}"
      on:click={() => activeTab = 'explorar'}
    >
      Explorar
    </button>
  </div>

  <!-- ── Tab: Colecciones ── -->
  {#if activeTab === 'colecciones'}
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold">
        {loadingCollections ? 'Cargando…' : `${collections.length} colección${collections.length !== 1 ? 'es' : ''}`}
      </h2>
      <button class="btn btn-primary btn-sm gap-1" on:click={openCreate}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nueva colección
      </button>
    </div>

    {#if loadingCollections}
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each Array(6) as _}
          <div class="card bg-base-100 shadow">
            <div class="skeleton h-40 w-full rounded-t-2xl"></div>
            <div class="card-body p-4 space-y-2">
              <div class="skeleton h-5 w-2/3 rounded"></div>
              <div class="skeleton h-4 w-1/2 rounded"></div>
            </div>
          </div>
        {/each}
      </div>
    {:else if collections.length === 0}
      <div class="text-center py-20 text-base-content/50">
        <p class="text-lg">Sin colecciones. Crea la primera.</p>
      </div>
    {:else}
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each collections as col (col.id)}
          <div class="card bg-base-100 shadow hover:shadow-md transition-shadow">
            <!-- Cover image -->
            <figure class="relative h-40 bg-base-300 rounded-t-2xl overflow-hidden">
              {#if col.cover_image_path}
                <img
                  src="/storage/{col.cover_image_path}"
                  alt="Portada de {col.name}"
                  class="w-full h-full object-cover"
                />
              {:else}
                <div class="w-full h-full flex items-center justify-center text-base-content/30">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              {/if}
              <span class="absolute top-2 right-2 badge {col.is_public ? 'badge-success' : 'badge-neutral'} badge-sm">
                {col.is_public ? 'Pública' : 'Privada'}
              </span>
            </figure>

            <div class="card-body p-4">
              <h3 class="font-semibold text-base leading-tight">{col.name}</h3>
              {#if col.photographer_name || col.date_range_from}
                <p class="text-xs text-base-content/60">
                  {#if col.photographer_name}{col.photographer_name}{/if}
                  {#if col.photographer_name && col.date_range_from} · {/if}
                  {#if col.date_range_from}{col.date_range_from}{#if col.date_range_to}–{col.date_range_to}{/if}{/if}
                </p>
              {/if}

              <div class="card-actions mt-2 flex-wrap gap-1">
                <button class="btn btn-xs btn-ghost" on:click={() => openEdit(col)}>
                  Editar
                </button>
                <button class="btn btn-xs btn-ghost" on:click={() => startCoverChange(col.id)}>
                  Portada
                </button>
                <a
                  href="/colecciones/{col.id}"
                  class="btn btn-xs btn-ghost"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Ver
                </a>
                <button
                  class="btn btn-xs btn-error btn-outline ml-auto"
                  on:click={() => openDeleteCollection(col)}
                  aria-label="Eliminar colección {col.name}"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {/if}

  <!-- ── Tab: Subir foto ── -->
  {#if activeTab === 'subir'}
    <div class="max-w-2xl mx-auto space-y-6">

      <!-- Collection picker -->
      <div class="form-control">
        <label class="label" for="upload-col">
          <span class="label-text font-medium">Colección <span class="text-error">*</span></span>
        </label>
        <select
          id="upload-col"
          class="select select-bordered w-full"
          bind:value={uploadColId}
        >
          <option value={null}>Seleccionar colección…</option>
          {#each collections as col}
            <option value={col.id}>{col.name}</option>
          {/each}
        </select>
      </div>

      <!-- Drop zone -->
      <div
        role="button"
        tabindex="0"
        class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
          {uploadDragOver ? 'border-primary bg-primary/5' : 'border-base-300 hover:border-primary/50'}"
        on:click={() => uploadInputEl?.click()}
        on:keydown={e => e.key === 'Enter' && uploadInputEl?.click()}
        on:dragover|preventDefault={() => (uploadDragOver = true)}
        on:dragleave={() => (uploadDragOver = false)}
        on:drop={onUploadDrop}
        aria-label="Área de subida de fotografía"
      >
        {#if uploadPreviewUrl && uploadFile}
          <img
            src={uploadPreviewUrl}
            alt="Vista previa de {uploadFile.name}"
            class="mx-auto max-h-56 rounded-lg object-contain mb-3"
          />
          <p class="text-sm text-base-content/60">{uploadFile.name}</p>
          <p class="text-xs text-base-content/40 mt-1">Clic para cambiar</p>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-base-content/30 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p class="font-medium text-base-content/70">Arrastra una imagen o haz clic para seleccionar</p>
          <p class="text-sm text-base-content/40 mt-1">JPG, PNG, TIFF — máximo 50 MB</p>
        {/if}
      </div>

      <!-- Metadata form -->
      {#if uploadFile}
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="form-control sm:col-span-2">
            <label class="label" for="upload-title"><span class="label-text">Título</span></label>
            <input id="upload-title" type="text" class="input input-bordered" bind:value={uploadForm.title} placeholder="Título de la fotografía" />
          </div>
          <div class="form-control">
            <label class="label" for="upload-year"><span class="label-text">Año</span></label>
            <input id="upload-year" type="number" class="input input-bordered" bind:value={uploadForm.year} placeholder="1935" min="1800" max="2100" />
          </div>
          <div class="form-control">
            <label class="label" for="upload-location"><span class="label-text">Lugar</span></label>
            <input id="upload-location" type="text" class="input input-bordered" bind:value={uploadForm.location} placeholder="Antofagasta, Chile" />
          </div>
          <div class="form-control sm:col-span-2">
            <label class="label" for="upload-desc"><span class="label-text">Descripción</span></label>
            <textarea id="upload-desc" class="textarea textarea-bordered" rows="2" bind:value={uploadForm.description} placeholder="Descripción opcional"></textarea>
          </div>
          <div class="form-control">
            <label class="label" for="upload-box"><span class="label-text">Caja</span></label>
            <input id="upload-box" type="text" class="input input-bordered" bind:value={uploadForm.box} placeholder="caja-11" />
          </div>
          <div class="form-control">
            <label class="label" for="upload-sub"><span class="label-text">Subdivisión</span></label>
            <input id="upload-sub" type="text" class="input input-bordered" bind:value={uploadForm.subdivision} placeholder="1072-punta-arenas" />
          </div>
          <div class="form-control sm:col-span-2">
            <label class="label cursor-pointer justify-start gap-3">
              <input type="checkbox" class="checkbox" bind:checked={uploadForm.is_public} />
              <span class="label-text">Fotografía pública</span>
            </label>
          </div>
        </div>

        <button
          class="btn btn-primary w-full"
          on:click={submitUpload}
          disabled={!uploadColId || uploading}
        >
          {#if uploading}
            <span class="loading loading-spinner loading-sm"></span>
            Subiendo…
          {:else}
            Subir fotografía
          {/if}
        </button>
      {/if}

    </div>
  {/if}

  <!-- ── Tab: Carga masiva ── -->
  {#if activeTab === 'masiva'}
    <div class="max-w-3xl mx-auto space-y-6">

      <!-- Collection picker -->
      <div class="form-control">
        <label class="label" for="bulk-col">
          <span class="label-text font-medium">Colección <span class="text-error">*</span></span>
        </label>
        <select id="bulk-col" class="select select-bordered w-full" bind:value={bulkColId}>
          <option value={null}>Seleccionar colección…</option>
          {#each collections as col}
            <option value={col.id}>{col.name}</option>
          {/each}
        </select>
      </div>

      <!-- Shared defaults -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-base-200 rounded-xl">
        <p class="col-span-2 sm:col-span-4 text-sm font-medium text-base-content/70 mb-1">Valores compartidos (opcionales)</p>
        <div class="form-control">
          <label class="label" for="bulk-box"><span class="label-text text-sm">Caja</span></label>
          <input id="bulk-box" type="text" class="input input-bordered input-sm" bind:value={bulkDefaults.box} placeholder="caja-11" />
        </div>
        <div class="form-control">
          <label class="label" for="bulk-sub"><span class="label-text text-sm">Subdivisión</span></label>
          <input id="bulk-sub" type="text" class="input input-bordered input-sm" bind:value={bulkDefaults.subdivision} placeholder="1072-punta-arenas" />
        </div>
        <div class="form-control">
          <label class="label" for="bulk-year"><span class="label-text text-sm">Año</span></label>
          <input id="bulk-year" type="number" class="input input-bordered input-sm" bind:value={bulkDefaults.year} placeholder="1935" />
        </div>
        <div class="form-control">
          <label class="label" for="bulk-loc"><span class="label-text text-sm">Lugar</span></label>
          <input id="bulk-loc" type="text" class="input input-bordered input-sm" bind:value={bulkDefaults.location} placeholder="Antofagasta" />
        </div>
        <div class="form-control col-span-2 sm:col-span-4 justify-end">
          <label class="label cursor-pointer justify-start gap-2 pb-0">
            <input type="checkbox" class="checkbox checkbox-sm" bind:checked={bulkDefaults.is_public} />
            <span class="label-text text-sm">Fotografías públicas</span>
          </label>
        </div>
      </div>

      <!-- Drop zone -->
      <div
        role="button"
        tabindex="0"
        class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
          {bulkDragOver ? 'border-primary bg-primary/5' : 'border-base-300 hover:border-primary/50'}"
        on:click={() => bulkInputEl?.click()}
        on:keydown={e => e.key === 'Enter' && bulkInputEl?.click()}
        on:dragover|preventDefault={() => (bulkDragOver = true)}
        on:dragleave={() => (bulkDragOver = false)}
        on:drop={onBulkDrop}
        aria-label="Área de carga masiva"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto text-base-content/30 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p class="font-medium text-base-content/70">Arrastra imágenes o haz clic para seleccionar</p>
        <p class="text-sm text-base-content/40 mt-1">Selección múltiple permitida</p>
      </div>

      <!-- File list -->
      {#if bulkFiles.length > 0}
        <div>
          <p class="text-sm font-medium mb-2">{bulkFiles.length} archivo{bulkFiles.length !== 1 ? 's' : ''} seleccionado{bulkFiles.length !== 1 ? 's' : ''}</p>
          <div class="space-y-1 max-h-56 overflow-y-auto pr-1">
            {#each bulkFiles as file, i}
              <div class="flex items-center justify-between px-3 py-2 bg-base-200 rounded-lg text-sm">
                <span class="truncate flex-1 mr-2">{file.name}</span>
                <span class="text-base-content/40 shrink-0 mr-2">{(file.size / 1024 / 1024).toFixed(1)} MB</span>
                <button
                  class="btn btn-ghost btn-xs text-error"
                  on:click={() => removeBulkFile(i)}
                  aria-label="Eliminar {file.name}"
                >
                  ✕
                </button>
              </div>
            {/each}
          </div>
        </div>

        <button
          class="btn btn-primary w-full"
          on:click={submitBulk}
          disabled={!bulkColId || bulkUploading}
        >
          {#if bulkUploading}
            <span class="loading loading-spinner loading-sm"></span>
            Subiendo {bulkFiles.length} archivos…
          {:else}
            Subir {bulkFiles.length} fotografía{bulkFiles.length !== 1 ? 's' : ''}
          {/if}
        </button>
      {/if}

      <!-- Results -->
      {#if bulkResults.length > 0}
        <div>
          <p class="text-sm font-medium mb-2">
            Resultados:
            <span class="text-success">{bulkResults.filter(r => r.ok).length} ok</span>
            {#if bulkResults.some(r => !r.ok)}
              · <span class="text-error">{bulkResults.filter(r => !r.ok).length} con error</span>
            {/if}
          </p>
          <div class="overflow-x-auto">
            <table class="table table-xs">
              <thead>
                <tr>
                  <th>Archivo</th>
                  <th>Estado</th>
                  <th>ID</th>
                  <th>Error</th>
                </tr>
              </thead>
              <tbody>
                {#each bulkResults as r}
                  <tr class="{r.ok ? '' : 'text-error'}">
                    <td class="truncate max-w-xs">{r.filename}</td>
                    <td>
                      {#if r.ok}
                        <span class="badge badge-success badge-sm">ok</span>
                      {:else}
                        <span class="badge badge-error badge-sm">error</span>
                      {/if}
                    </td>
                    <td>{r.image_id ?? '—'}</td>
                    <td class="text-xs">{r.error ?? ''}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}

    </div>
  {/if}

  <!-- ── Tab: Explorar ── -->
  {#if activeTab === 'explorar'}
    <div class="space-y-5">

      <!-- Controls -->
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="form-control sm:w-64">
          <label class="sr-only" for="explore-col">Colección</label>
          <select
            id="explore-col"
            class="select select-bordered"
            bind:value={exploreColId}
            on:change={onExploreColChange}
          >
            <option value={null}>Seleccionar colección…</option>
            {#each collections as col}
              <option value={col.id}>{col.name}</option>
            {/each}
          </select>
        </div>

        {#if exploreColId}
          <div class="form-control flex-1">
            <label class="sr-only" for="explore-search">Buscar</label>
            <input
              id="explore-search"
              type="search"
              class="input input-bordered w-full"
              placeholder="Buscar por título o lugar…"
              bind:value={exploreSearch}
            />
          </div>
          {@const exploreCol = collections.find(c => c.id === exploreColId)}
          {#if exploreCol}
            <button
              class="btn btn-error btn-outline btn-sm shrink-0"
              on:click={() => openDeleteImages(exploreCol)}
            >
              Eliminar imágenes
            </button>
          {/if}
        {/if}
      </div>

      {#if exploreColId}
        {#if !loadingExplore && exploreTotal > 0}
          <p class="text-sm text-base-content/50">
            {exploreSearch ? `${exploreFiltered.length} de ` : ''}{exploreTotal} fotografía{exploreTotal !== 1 ? 's' : ''}
          </p>
        {/if}

        <ImageGrid
          images={exploreFiltered}
          loading={loadingExplore}
          error={null}
          onImageClick={(img) => { viewerImage = img; showViewer = true; }}
          onRetry={loadExplore}
        />

        {#if !loadingExplore && exploreTotal > PER_PAGE}
          <div class="flex items-center justify-center gap-3">
            <button
              class="btn btn-sm"
              on:click={() => explorePaginate(-1)}
              disabled={explorePage === 0}
            >
              Anterior
            </button>
            <span class="text-sm text-base-content/60">
              Página {explorePage + 1} de {exploreTotalPages}
            </span>
            <button
              class="btn btn-sm"
              on:click={() => explorePaginate(1)}
              disabled={explorePage >= exploreTotalPages - 1}
            >
              Siguiente
            </button>
          </div>
        {/if}
      {:else}
        <div class="text-center py-20 text-base-content/50">
          <p>Selecciona una colección para explorar sus fotografías.</p>
        </div>
      {/if}

    </div>
  {/if}

</div>

<!-- ── Modal: Delete confirmation ── -->
{#if deleteTarget}
  {@const col = deleteTarget.collection}
  {@const isFullDelete = deleteTarget.mode === 'collection'}
  <dialog class="modal modal-open" aria-labelledby="delete-modal-title">
    <div class="modal-box max-w-md">

      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-error/15 flex items-center justify-center shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
        </div>
        <h3 id="delete-modal-title" class="font-bold text-lg">
          {isFullDelete ? 'Eliminar colección' : 'Eliminar imágenes'}
        </h3>
      </div>

      <p class="text-sm text-base-content/70 mb-1">
        {#if isFullDelete}
          Se eliminarán permanentemente <strong>todas las imágenes</strong> y el registro de la colección
          <strong>"{col.name}"</strong>. Esta acción no se puede deshacer.
        {:else}
          Se eliminarán permanentemente <strong>todas las imágenes</strong> de la colección
          <strong>"{col.name}"</strong>. La colección en sí permanecerá. Esta acción no se puede deshacer.
        {/if}
      </p>

      <p class="text-sm text-base-content/50 mt-3 mb-2">
        Para confirmar, escribe el nombre de la colección:
      </p>
      <p class="font-mono text-sm bg-base-200 px-3 py-1.5 rounded mb-3 select-all">
        {col.name}
      </p>

      <input
        type="text"
        class="input input-bordered w-full {deleteConfirmInput && !deleteNameMatch ? 'input-error' : ''}"
        placeholder="Escribe el nombre exacto…"
        bind:value={deleteConfirmInput}
        on:keydown={e => e.key === 'Enter' && deleteNameMatch && confirmDelete()}
        autocomplete="off"
        spellcheck="false"
      />
      {#if deleteConfirmInput && !deleteNameMatch}
        <p class="text-xs text-error mt-1">El nombre no coincide</p>
      {/if}

      <div class="modal-action mt-5">
        <button class="btn btn-ghost" on:click={cancelDelete} disabled={deleting}>
          Cancelar
        </button>
        <button
          class="btn btn-error"
          on:click={confirmDelete}
          disabled={!deleteNameMatch || deleting}
        >
          {#if deleting}
            <span class="loading loading-spinner loading-sm"></span>
          {/if}
          {isFullDelete ? 'Eliminar colección' : 'Eliminar imágenes'}
        </button>
      </div>

    </div>
    <button class="modal-backdrop" on:click={cancelDelete} aria-label="Cerrar">
      <span class="sr-only">Cerrar</span>
    </button>
  </dialog>
{/if}

<!-- ── Modal: Create / Edit collection ── -->
{#if showColModal}
  <dialog class="modal modal-open" aria-labelledby="col-modal-title">
    <div class="modal-box max-w-2xl w-full">
      <h3 id="col-modal-title" class="font-bold text-lg mb-4">
        {editingCol ? 'Editar colección' : 'Nueva colección'}
      </h3>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <div class="form-control sm:col-span-2">
          <label class="label" for="col-name">
            <span class="label-text">Nombre <span class="text-error">*</span></span>
          </label>
          <input
            id="col-name"
            type="text"
            class="input input-bordered"
            bind:value={colForm.name}
            placeholder="Colección Robert Gerstmann"
            required
          />
        </div>

        <div class="form-control sm:col-span-2">
          <label class="label" for="col-desc"><span class="label-text">Descripción</span></label>
          <textarea
            id="col-desc"
            class="textarea textarea-bordered"
            rows="2"
            bind:value={colForm.description}
            placeholder="Descripción de la colección"
          ></textarea>
        </div>

        <div class="form-control">
          <label class="label" for="col-photo"><span class="label-text">Fotógrafo</span></label>
          <input id="col-photo" type="text" class="input input-bordered" bind:value={colForm.photographer_name} placeholder="Robert Gerstmann" />
        </div>

        <div class="form-control">
          <label class="label" for="col-country"><span class="label-text">País de origen</span></label>
          <input id="col-country" type="text" class="input input-bordered" bind:value={colForm.origin_country} placeholder="Chile" />
        </div>

        <div class="form-control">
          <label class="label" for="col-from"><span class="label-text">Fecha desde (año)</span></label>
          <input id="col-from" type="number" class="input input-bordered" bind:value={colForm.date_range_from} placeholder="1920" min="1800" max="2100" />
        </div>

        <div class="form-control">
          <label class="label" for="col-to"><span class="label-text">Fecha hasta (año)</span></label>
          <input id="col-to" type="number" class="input input-bordered" bind:value={colForm.date_range_to} placeholder="1960" min="1800" max="2100" />
        </div>

        <div class="form-control sm:col-span-2">
          <label class="label" for="col-license"><span class="label-text">Licencia</span></label>
          <input id="col-license" type="text" class="input input-bordered" bind:value={colForm.license} placeholder="CC BY-NC 4.0" />
        </div>

        <div class="form-control sm:col-span-2">
          <label class="label" for="col-copy"><span class="label-text">Notas de copyright</span></label>
          <textarea id="col-copy" class="textarea textarea-bordered" rows="2" bind:value={colForm.copyright_notes} placeholder="Notas adicionales de derechos"></textarea>
        </div>

        <div class="form-control sm:col-span-2">
          <label class="label cursor-pointer justify-start gap-3">
            <input type="checkbox" class="checkbox" bind:checked={colForm.is_public} />
            <span class="label-text">Colección pública (visible sin iniciar sesión)</span>
          </label>
        </div>

      </div>

      <div class="modal-action mt-6">
        <button class="btn btn-ghost" on:click={() => (showColModal = false)} disabled={savingCol}>
          Cancelar
        </button>
        <button
          class="btn btn-primary"
          on:click={saveCol}
          disabled={!colForm.name.trim() || savingCol}
        >
          {#if savingCol}
            <span class="loading loading-spinner loading-sm"></span>
          {/if}
          {editingCol ? 'Guardar cambios' : 'Crear colección'}
        </button>
      </div>
    </div>
    <button class="modal-backdrop" on:click={() => (showColModal = false)} aria-label="Cerrar">
      <span class="sr-only">Cerrar</span>
    </button>
  </dialog>
{/if}

<!-- ── Modal: Cover preview confirm ── -->
{#if coverPreviewUrl && coverColId}
  <dialog class="modal modal-open" aria-labelledby="cover-modal-title">
    <div class="modal-box max-w-sm">
      <h3 id="cover-modal-title" class="font-bold text-lg mb-3">Confirmar portada</h3>
      <img src={coverPreviewUrl} alt="Vista previa de portada" class="w-full rounded-lg object-cover max-h-64" />
      <p class="text-sm text-base-content/60 mt-2">
        Esta imagen se usará como portada de la colección.
      </p>
      <div class="modal-action">
        <button class="btn btn-ghost btn-sm" on:click={cancelCover} disabled={savingCover}>
          Cancelar
        </button>
        <button class="btn btn-primary btn-sm" on:click={saveCover} disabled={savingCover}>
          {#if savingCover}
            <span class="loading loading-spinner loading-xs"></span>
          {/if}
          Establecer portada
        </button>
      </div>
    </div>
    <button class="modal-backdrop" on:click={cancelCover} aria-label="Cerrar">
      <span class="sr-only">Cerrar</span>
    </button>
  </dialog>
{/if}

<!-- ImageViewer -->
{#if showViewer && viewerImage}
  <ImageViewer
    image={viewerImage}
    narratives={[]}
    on:close={() => { showViewer = false; viewerImage = null; }}
  />
{/if}
