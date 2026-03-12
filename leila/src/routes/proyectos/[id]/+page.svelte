<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { authStore } from '$lib/stores/auth';
  import { projectService, chatService } from '$lib/services';
  import { projectsStore } from '$lib/stores/projects';
  import { chatStore } from '$lib/stores/chat';
  import { notificationsStore } from '$lib/stores/notifications';
  import { apiClient } from '$lib/services/apiClient';
  import type { Project, ProjectMember, ProjectRole, SentInvitation } from '$lib/types';

  interface UserSuggestion { id: number; email: string; full_name: string | null; }

  let project: Project | null = null;
  let members: ProjectMember[] = [];
  let loading = true;
  let error: string | null = null;

  // Sent invitations
  let sentInvitations: SentInvitation[] = [];
  let loadingInvitations = false;

  // Tab state
  let activeTab: 'chat' | 'members' = 'chat';

  // Add member form
  let newMemberEmail = '';
  let addingMember = false;

  // Email autocomplete
  let emailSuggestions: UserSuggestion[] = [];
  let showSuggestions = false;
  let debounceTimer: ReturnType<typeof setTimeout>;
  let suggestionIndex = -1;

  // Edit mode
  let editing = false;
  let editName = '';
  let editDescription = '';
  let editStartDate = '';
  let editAiInstructions = '';
  let saving = false;

  // Chat
  let chatInput = '';
  let aiInput = '';
  let chatContainer: HTMLDivElement;
  let pollingInterval: ReturnType<typeof setInterval>;

  // PDF context
  let pdfContext: string | undefined = undefined;
  let pdfFilename = '';
  let uploadingPdf = false;
  let pdfInput: HTMLInputElement;

  $: projectId = Number($page.params.id);
  $: currentUserId = $authStore.user?.id;
  $: isOwner = project?.owner_id === currentUserId;
  $: myMembership = members.find(m => m.user_id === currentUserId);
  $: isLider = isOwner || myMembership?.role === 'lider';
  $: canEdit = isLider || myMembership?.role === 'investigador';
  $: messages = $chatStore.messages;
  $: sending = $chatStore.sending;

  onMount(async () => {
    await loadProject();
    await loadMessages();
    pollingInterval = setInterval(pollMessages, 5000);
  });

  onDestroy(() => {
    clearInterval(pollingInterval);
    chatStore.reset();
  });

  async function loadProject() {
    try {
      loading = true;
      error = null;
      const [proj, membersResp] = await Promise.all([
        projectService.getProject(projectId),
        projectService.listMembers(projectId)
      ]);
      project = proj;
      members = membersResp.members;
      projectsStore.setCurrentProject(proj);
      projectsStore.setMembers(membersResp.members);
    } catch (e: any) {
      error = e.detail || 'Error al cargar el proyecto';
    } finally {
      loading = false;
    }
  }

  async function loadMessages() {
    try {
      chatStore.setLoading(true);
      const resp = await chatService.listMessages(projectId, 0, 200);
      chatStore.setMessages(resp.messages);
      scrollToBottom();
    } catch (e: any) {
      chatStore.setError(e.detail || 'Error al cargar mensajes');
    } finally {
      chatStore.setLoading(false);
    }
  }

  async function pollMessages() {
    try {
      const resp = await chatService.listMessages(projectId, 0, 200);
      const prevCount = $chatStore.messages.length;
      chatStore.mergeNew(resp.messages);
      if ($chatStore.messages.length > prevCount) scrollToBottom();
    } catch {
      // silent poll failure
    }
  }

  function scrollToBottom() {
    setTimeout(() => {
      if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 50);
  }

  function startEdit() {
    if (!project) return;
    editName = project.name;
    editDescription = project.description || '';
    editStartDate = project.start_date || '';
    editAiInstructions = project.ai_instructions || '';
    editing = true;
  }

  function cancelEdit() { editing = false; }

  async function saveEdit() {
    if (!editName.trim()) {
      notificationsStore.warning('El nombre es obligatorio');
      return;
    }
    try {
      saving = true;
      const updated = await projectService.updateProject(projectId, {
        name: editName.trim(),
        description: editDescription.trim() || undefined,
        start_date: editStartDate || undefined,
        ai_instructions: editAiInstructions.trim() || undefined
      });
      project = updated;
      editing = false;
      notificationsStore.success('Proyecto actualizado');
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al actualizar');
    } finally {
      saving = false;
    }
  }

  async function loadSentInvitations() {
    try {
      loadingInvitations = true;
      const resp = await projectService.listProjectInvitations(projectId);
      sentInvitations = resp.invitations;
    } catch {
      sentInvitations = [];
    } finally {
      loadingInvitations = false;
    }
  }

  async function handleAddMember() {
    if (!newMemberEmail.trim()) {
      notificationsStore.warning('Ingresa el correo del usuario');
      return;
    }
    try {
      addingMember = true;
      await projectService.addMember(projectId, newMemberEmail.trim());
      newMemberEmail = '';
      emailSuggestions = [];
      showSuggestions = false;
      notificationsStore.success('Invitación enviada. El usuario deberá aceptarla para unirse.');
      await loadSentInvitations();
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al enviar invitación');
    } finally {
      addingMember = false;
    }
  }

  function onEmailInput() {
    clearTimeout(debounceTimer);
    suggestionIndex = -1;
    const q = newMemberEmail.trim();
    if (q.length < 2) { emailSuggestions = []; showSuggestions = false; return; }
    debounceTimer = setTimeout(async () => {
      try {
        const results = await apiClient.get<UserSuggestion[]>('/auth/users/search', { q });
        // Exclude already-members
        const memberIds = new Set(members.map(m => m.user_id));
        emailSuggestions = results.filter(u => !memberIds.has(u.id));
        showSuggestions = emailSuggestions.length > 0;
      } catch { emailSuggestions = []; showSuggestions = false; }
    }, 300);
  }

  function selectSuggestion(u: UserSuggestion) {
    newMemberEmail = u.email;
    emailSuggestions = [];
    showSuggestions = false;
    suggestionIndex = -1;
  }

  function onEmailKeydown(e: KeyboardEvent) {
    if (!showSuggestions) return;
    if (e.key === 'ArrowDown') { e.preventDefault(); suggestionIndex = Math.min(suggestionIndex + 1, emailSuggestions.length - 1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); suggestionIndex = Math.max(suggestionIndex - 1, -1); }
    else if (e.key === 'Enter' && suggestionIndex >= 0) { e.preventDefault(); selectSuggestion(emailSuggestions[suggestionIndex]); }
    else if (e.key === 'Escape') { showSuggestions = false; }
  }

  async function handleRemoveMember(member: ProjectMember) {
    if (member.user_id === project?.owner_id) {
      notificationsStore.warning('No se puede remover al propietario');
      return;
    }
    if (!confirm('¿Remover este miembro del proyecto?')) return;
    try {
      await projectService.removeMember(projectId, member.user_id);
      members = members.filter(m => m.user_id !== member.user_id);
      projectsStore.setMembers(members);
      notificationsStore.success('Miembro removido');
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al remover miembro');
    }
  }

  async function handleSendMessage() {
    if (!chatInput.trim() || sending) return;
    const content = chatInput.trim();
    chatInput = '';
    try {
      chatStore.setSending(true);
      const msg = await chatService.sendMessage(projectId, content);
      chatStore.addMessage(msg);
      scrollToBottom();
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al enviar mensaje');
      chatInput = content;
    } finally {
      chatStore.setSending(false);
    }
  }

  async function handleAskAI() {
    if (!aiInput.trim() || sending) return;
    const question = aiInput.trim();
    aiInput = '';
    try {
      chatStore.setSending(true);
      const resp = await chatService.askAI(projectId, question, pdfContext);
      chatStore.addMessage(resp.user_message);
      chatStore.addMessage(resp.ai_message);
      scrollToBottom();
    } catch (e: any) {
      notificationsStore.error(e.detail || e.message || 'Error al consultar la IA');
      aiInput = question;
    } finally {
      chatStore.setSending(false);
    }
  }

  async function handlePdfUpload(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    try {
      uploadingPdf = true;
      const resp = await chatService.uploadPdfContext(projectId, file);
      pdfContext = resp.text;
      pdfFilename = resp.filename;
      notificationsStore.success(`PDF cargado: ${resp.filename} (${resp.pages} págs., ${resp.char_count} caracteres)`);
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al procesar el PDF');
    } finally {
      uploadingPdf = false;
      input.value = '';
    }
  }

  function clearPdfContext() {
    pdfContext = undefined;
    pdfFilename = '';
  }

  function onChatKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); }
  }

  function onAiKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAskAI(); }
  }

  function getRoleBadge(role: ProjectRole): string {
    const map: Record<ProjectRole, string> = {
      lider: 'badge-primary', investigador: 'badge-accent',
      colaborador: 'badge-info', observador: 'badge-ghost'
    };
    return map[role] ?? '';
  }

  function formatDate(d?: string) {
    return d ? new Date(d).toLocaleDateString('es-CL') : '-';
  }

  function formatTime(d: string) {
    return new Date(d).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
  }
</script>

<svelte:head>
  <title>{project?.name || 'Proyecto'} - ROGER</title>
</svelte:head>

<div class="max-w-4xl mx-auto">
  <div class="mb-4">
    <a href="/proyectos" class="btn btn-ghost btn-sm gap-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Volver
    </a>
  </div>

  {#if loading}
    <div class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

  {:else if error}
    <div class="alert alert-error">
      <span>{error}</span>
      <button class="btn btn-sm" on:click={loadProject}>Reintentar</button>
    </div>

  {:else if project}

    <!-- Project header card -->
    <div class="card bg-base-100 shadow-lg border border-base-300 mb-4">
      <div class="card-body py-4">
        {#if !editing}
          <div class="flex items-start justify-between">
            <div>
              <h1 class="text-2xl font-bold">{project.name}</h1>
              {#if project.description}
                <p class="text-base-content/60 mt-1 text-sm">{project.description}</p>
              {/if}
              <div class="flex gap-3 mt-2 text-xs text-base-content/40">
                {#if project.start_date}<span>Inicio: {formatDate(project.start_date)}</span>{/if}
                <span class="badge {project.is_active ? 'badge-success' : 'badge-ghost'} badge-xs">
                  {project.is_active ? 'Activo' : 'Inactivo'}
                </span>
              </div>
            </div>
            {#if canEdit}
              <button class="btn btn-ghost btn-sm" on:click={startEdit}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Editar
              </button>
            {/if}
          </div>
        {:else}
          <!-- Edit form -->
          <div class="space-y-3">
            <div class="form-control">
              <label class="label py-1" for="edit-name"><span class="label-text font-semibold text-sm">Nombre *</span></label>
              <input id="edit-name" type="text" class="input input-bordered input-sm" bind:value={editName} required />
            </div>
            <div class="form-control">
              <label class="label py-1" for="edit-desc"><span class="label-text font-semibold text-sm">Descripción</span></label>
              <textarea id="edit-desc" class="textarea textarea-bordered textarea-sm" bind:value={editDescription}></textarea>
            </div>
            <div class="form-control">
              <label class="label py-1" for="edit-start"><span class="label-text font-semibold text-sm">Fecha de inicio</span></label>
              <input id="edit-start" type="date" class="input input-bordered input-sm" bind:value={editStartDate} />
            </div>
            {#if isLider}
            <div class="form-control">
              <label class="label py-1" for="edit-ai-instructions">
                <span class="label-text font-semibold text-sm">Instrucciones para la IA</span>
                <span class="label-text-alt text-base-content/40">Solo visibles para la IA</span>
              </label>
              <textarea
                id="edit-ai-instructions"
                class="textarea textarea-bordered textarea-sm"
                rows="3"
                placeholder="Ej: En este proyecto, 'planta madre' se refiere a la instalación central de tratamiento…"
                bind:value={editAiInstructions}
              ></textarea>
            </div>
            {/if}
            <div class="flex gap-2 justify-end">
              <button class="btn btn-ghost btn-sm" on:click={cancelEdit}>Cancelar</button>
              <button class="btn btn-primary btn-sm" on:click={saveEdit} disabled={saving}>
                {#if saving}<span class="loading loading-spinner loading-xs"></span>{/if}
                Guardar
              </button>
            </div>
          </div>
        {/if}
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs tabs-boxed mb-4">
      <button class="tab gap-2" class:tab-active={activeTab === 'chat'}
        on:click={() => { activeTab = 'chat'; scrollToBottom(); }}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        Chat
        {#if messages.length > 0}<span class="badge badge-sm badge-primary">{messages.length}</span>{/if}
      </button>
      <button class="tab gap-2" class:tab-active={activeTab === 'members'}
        on:click={() => { activeTab = 'members'; if (isLider) loadSentInvitations(); }}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        Miembros ({members.length})
      </button>
    </div>

    <!-- ===== CHAT TAB ===== -->
    {#if activeTab === 'chat'}
      <div class="card bg-base-100 shadow-lg border border-base-300">
        <div class="card-body p-4 flex flex-col" style="height:520px">

          <!-- Messages scroll area -->
          <div bind:this={chatContainer} class="flex-1 overflow-y-auto space-y-3 pr-1">
            {#if $chatStore.loading}
              <div class="flex justify-center py-10">
                <span class="loading loading-spinner text-primary"></span>
              </div>

            {:else if messages.length === 0}
              <div class="flex flex-col items-center justify-center h-full text-center text-base-content/40 py-16">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14 mb-3 opacity-25" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p class="font-medium">No hay mensajes aún</p>
                <p class="text-sm mt-1">Escribe el primer mensaje o pregunta a la IA</p>
              </div>

            {:else}
              {#each messages as msg (msg.id)}
                {#if msg.message_type === 'ai'}
                  <!-- AI bubble — left -->
                  <div class="flex gap-2 items-start">
                    <div class="w-8 h-8 rounded-full bg-secondary/20 text-secondary flex items-center justify-center flex-shrink-0">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2h-2" />
                      </svg>
                    </div>
                    <div class="max-w-[78%]">
                      <p class="text-xs text-secondary font-semibold mb-0.5">
                        Asistente IA · {formatTime(msg.created_at)}
                      </p>
                      <div class="bg-secondary/10 rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm whitespace-pre-wrap">
                        {msg.content}
                      </div>
                    </div>
                  </div>

                {:else if msg.user_id === currentUserId}
                  <!-- Own message — right -->
                  <div class="flex gap-2 items-start justify-end">
                    <div class="max-w-[78%]">
                      <p class="text-xs text-primary font-semibold mb-0.5 text-right">
                        Tú · {formatTime(msg.created_at)}
                      </p>
                      <div class="bg-primary text-primary-content rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm whitespace-pre-wrap">
                        {msg.content}
                      </div>
                    </div>
                    <div class="w-8 h-8 rounded-full bg-primary text-primary-content flex items-center justify-center flex-shrink-0 text-sm font-bold">
                      {$authStore.user?.full_name?.charAt(0).toUpperCase() ?? '?'}
                    </div>
                  </div>

                {:else}
                  <!-- Other member — left -->
                  <div class="flex gap-2 items-start">
                    <div class="w-8 h-8 rounded-full bg-base-300 flex items-center justify-center flex-shrink-0 text-sm font-bold">
                      {msg.sender_name?.charAt(0).toUpperCase() ?? '?'}
                    </div>
                    <div class="max-w-[78%]">
                      <p class="text-xs font-semibold mb-0.5 text-base-content/60">
                        {msg.sender_name ?? 'Miembro'} · {formatTime(msg.created_at)}
                      </p>
                      <div class="bg-base-200 rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm whitespace-pre-wrap">
                        {msg.content}
                      </div>
                    </div>
                  </div>
                {/if}
              {/each}
            {/if}
          </div>

          <!-- Input area -->
          <div class="border-t pt-3 mt-2 space-y-2">
            <!-- Chat input -->
            <div class="flex gap-2">
              <input
                type="text"
                placeholder="Escribe un mensaje… (Enter para enviar)"
                class="input input-bordered input-sm flex-1"
                bind:value={chatInput}
                on:keydown={onChatKeydown}
                disabled={sending}
              />
              <button class="btn btn-primary btn-sm" on:click={handleSendMessage}
                disabled={sending || !chatInput.trim()}>
                {#if sending}
                  <span class="loading loading-spinner loading-xs"></span>
                {:else}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                {/if}
              </button>
            </div>

            <!-- PDF context indicator -->
            {#if pdfContext}
              <div class="flex items-center gap-2 text-xs bg-secondary/10 text-secondary rounded px-2 py-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span class="truncate flex-1">Contexto PDF: <strong>{pdfFilename}</strong></span>
                <button class="btn btn-ghost btn-xs text-error p-0 h-auto min-h-0" on:click={clearPdfContext} title="Quitar PDF">✕</button>
              </div>
            {/if}

            <!-- AI input -->
            <div class="flex gap-2">
              <input
                type="text"
                placeholder="Pregunta a la IA… (Enter para enviar)"
                class="input input-bordered input-sm flex-1 border-secondary/50"
                bind:value={aiInput}
                on:keydown={onAiKeydown}
                disabled={sending}
              />
              <!-- PDF upload button -->
              <input
                type="file"
                accept=".pdf"
                class="hidden"
                bind:this={pdfInput}
                on:change={handlePdfUpload}
              />
              <button class="btn btn-ghost btn-sm" title="Subir PDF como contexto"
                on:click={() => pdfInput.click()} disabled={uploadingPdf}>
                {#if uploadingPdf}
                  <span class="loading loading-spinner loading-xs"></span>
                {:else}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                {/if}
              </button>
              <button class="btn btn-secondary btn-sm gap-1" on:click={handleAskAI}
                disabled={sending || !aiInput.trim()}>
                {#if sending}
                  <span class="loading loading-spinner loading-xs"></span>
                {:else}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2h-2" />
                  </svg>
                  IA
                {/if}
              </button>
            </div>
          </div>
        </div>
      </div>
    {/if}

    <!-- ===== MEMBERS TAB ===== -->
    {#if activeTab === 'members'}
      <div class="card bg-base-100 shadow-lg border border-base-300">
        <div class="card-body">

          {#if isLider}
            <form on:submit|preventDefault={handleAddMember}
              class="flex gap-3 mb-6 p-4 bg-base-200 rounded-lg flex-wrap items-start">
              <div class="form-control flex-1 min-w-[200px] relative">
                <input
                  type="text"
                  placeholder="correo@ejemplo.com"
                  class="input input-bordered input-sm"
                  bind:value={newMemberEmail}
                  on:input={onEmailInput}
                  on:keydown={onEmailKeydown}
                  on:blur={() => setTimeout(() => { showSuggestions = false; }, 150)}
                  autocomplete="off"
                  required
                />
                {#if showSuggestions}
                  <ul class="absolute top-full left-0 right-0 z-50 mt-1 bg-base-100 border border-base-300 rounded-box shadow-lg overflow-hidden">
                    {#each emailSuggestions as u, i}
                      <li>
                        <button type="button"
                          class="w-full text-left px-3 py-2 text-sm hover:bg-base-200 transition-colors"
                          class:bg-base-200={i === suggestionIndex}
                          on:mousedown|preventDefault={() => selectSuggestion(u)}>
                          <span class="font-medium">{u.email}</span>
                          {#if u.full_name}<span class="text-base-content/50 ml-1">— {u.full_name}</span>{/if}
                        </button>
                      </li>
                    {/each}
                  </ul>
                {/if}
              </div>
              <button type="submit" class="btn btn-primary btn-sm" disabled={addingMember}>
                {#if addingMember}<span class="loading loading-spinner loading-xs"></span>{/if}
                Invitar
              </button>
            </form>
          {/if}

          {#if members.length === 0}
            <p class="text-center text-base-content/50 py-6">No hay miembros registrados</p>
          {:else}
            <div class="overflow-x-auto">
              <table class="table">
                <thead>
                  <tr>
                    <th>Usuario</th>
                    <th>Rol</th>
                    <th>Agregado</th>
                    {#if isLider}<th></th>{/if}
                  </tr>
                </thead>
                <tbody>
                  {#each members as member (member.id)}
                    <tr>
                      <td>
                        <span class="font-mono text-sm">#{member.user_id}</span>
                        {#if member.user_id === project.owner_id}
                          <span class="badge badge-warning badge-xs ml-1">Owner</span>
                        {/if}
                        {#if member.user_id === currentUserId}
                          <span class="badge badge-info badge-xs ml-1">Tú</span>
                        {/if}
                      </td>
                      <td>
                        <span class="badge {getRoleBadge(member.role)} badge-sm capitalize">
                          {member.role}
                        </span>
                      </td>
                      <td class="text-sm text-base-content/50">{formatDate(member.created_at)}</td>
                      {#if isLider}
                        <td>
                          {#if member.user_id !== project.owner_id}
                            <button class="btn btn-ghost btn-xs text-error"
                              on:click={() => handleRemoveMember(member)} title="Remover">
                              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          {/if}
                        </td>
                      {/if}
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {/if}

          <!-- Sent invitations (leader only) -->
          {#if isLider}
            <div class="mt-6">
              <h3 class="font-semibold text-sm mb-2 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Invitaciones enviadas
              </h3>
              {#if loadingInvitations}
                <div class="flex justify-center py-4">
                  <span class="loading loading-spinner loading-sm text-primary"></span>
                </div>
              {:else if sentInvitations.length === 0}
                <p class="text-sm text-base-content/40 py-3">No hay invitaciones enviadas</p>
              {:else}
                <div class="overflow-x-auto">
                  <table class="table table-sm">
                    <thead>
                      <tr>
                        <th>Correo invitado</th>
                        <th>Estado</th>
                        <th>Enviado</th>
                      </tr>
                    </thead>
                    <tbody>
                      {#each sentInvitations as inv (inv.id)}
                        <tr>
                          <td class="text-sm">{inv.invited_email}</td>
                          <td>
                            {#if inv.status === 'pending'}
                              <span class="badge badge-warning badge-sm">Pendiente</span>
                            {:else if inv.status === 'accepted'}
                              <span class="badge badge-success badge-sm">Aceptada</span>
                            {:else}
                              <span class="badge badge-ghost badge-sm">Rechazada</span>
                            {/if}
                          </td>
                          <td class="text-sm text-base-content/50">{formatDate(inv.created_at)}</td>
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                </div>
              {/if}
            </div>
          {/if}

        </div>
      </div>
    {/if}

  {/if}
</div>
