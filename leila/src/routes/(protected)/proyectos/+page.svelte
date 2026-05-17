<script lang="ts">
  import { onMount, onDestroy, tick } from 'svelte';
  import { authStore } from '$lib/stores/auth';
  import { projectService, chatService } from '$lib/services';
  import { projectsStore } from '$lib/stores/projects';
  import { invitationsStore, pendingCount } from '$lib/stores/invitations';
  import { invitationService } from '$lib/services/invitationService';
  import { notificationsStore } from '$lib/stores/notifications';
  import { apiClient } from '$lib/services/apiClient';
  import type { Project, ProjectMember, ProjectRole, SentInvitation } from '$lib/types';

  interface UserSuggestion { id: number; email: string; full_name: string | null; }

  // ── View state ────────────────────────────────────────────────────────
  let view: 'workspace' | 'new' | 'invitations' = 'workspace';
  let rightPanelOpen = true;
  let rightTab: 'chat' | 'members' = 'chat';
  let mobileShowSidebar = false;
  let mobileShowRight = false;

  // Inline delete confirmation (evita confirm() del navegador)
  let confirmDeleteId: number | null = null;

  // ── Projects list ─────────────────────────────────────────────────────
  let projectsLoading = true;
  let projectsError: string | null = null;

  $: projects = $projectsStore.projects;
  $: currentUserId = $authStore.user?.id;
  $: ownedCount = projects.filter(p => p.owner_id === currentUserId).length;

  // ── Selected project ──────────────────────────────────────────────────
  let selectedProjectId: number | null = null;
  let selectedProject: Project | null = null;
  let members: ProjectMember[] = [];
  let projectLoading = false;
  let projectError: string | null = null;

  // ── Edit project ──────────────────────────────────────────────────────
  let editing = false;
  let editName = '';
  let editDescription = '';
  let editStartDate = '';
  let editAiInstructions = '';
  let saving = false;

  // ── Members ───────────────────────────────────────────────────────────
  let newMemberEmail = '';
  let addingMember = false;
  let emailSuggestions: UserSuggestion[] = [];
  let showSuggestions = false;
  let debounceTimer: ReturnType<typeof setTimeout>;
  let suggestionIndex = -1;
  let sentInvitations: SentInvitation[] = [];

  // ── Messages ──────────────────────────────────────────────────────────
  let messages: any[] = [];
  let chatInput = '';
  let aiInput = '';
  let groupChatContainer: HTMLDivElement;
  let aiChatContainer: HTMLDivElement;
  let pollingInterval: ReturnType<typeof setInterval> | null = null;
  let sendingMsg = false;

  // ── AI ────────────────────────────────────────────────────────────────
  let aiThinking = false;
  let typewriterMsgId: number | null = null;
  let typewriterContent = '';
  let typewriterTimer: ReturnType<typeof setInterval> | null = null;
  let aiUsedThisHour = 0;
  $: aiRemaining = Math.max(0, 10 - aiUsedThisHour);

  // ── PDF ───────────────────────────────────────────────────────────────
  let pdfContext: string | undefined = undefined;
  let pdfFilename = '';
  let uploadingPdf = false;
  let pdfInput: HTMLInputElement;

  // ── Create form ───────────────────────────────────────────────────────
  let newName = '';
  let newDescription = '';
  let newStartDate = '';
  let newAiInstructions = '';
  let creating = false;
  const today = new Date().toISOString().split('T')[0];

  // ── Derived ───────────────────────────────────────────────────────────
  $: isOwner = selectedProject?.owner_id === currentUserId;
  $: myMembership = members.find(m => m.user_id === currentUserId);
  $: isLider = isOwner || myMembership?.role === 'lider';
  $: canEdit = isLider || myMembership?.role === 'investigador';

  $: groupMessages = messages.filter((m: any, i: number) => {
    if (m.message_type !== 'user') return false;
    const next = messages[i + 1] as any;
    return !(next?.message_type === 'ai');
  });

  $: aiConversation = (() => {
    const pairs: Array<{ question: any | null; answer: any }> = [];
    for (let i = 0; i < messages.length; i++) {
      const m = messages[i] as any;
      if (m.message_type === 'ai') {
        const prev = messages[i - 1] as any;
        pairs.push({ question: prev?.message_type === 'user' ? prev : null, answer: m });
      }
    }
    return pairs;
  })();

  // ── Lifecycle ─────────────────────────────────────────────────────────
  onMount(async () => {
    await Promise.all([loadProjects(), loadInvitations()]);
    // Fetch real AI usage from backend
    try {
      const usage = await apiClient.get<{ used: number; limit: number }>('/projects/ai-usage');
      aiUsedThisHour = usage.used;
    } catch { /* non-critical, default stays 0 */ }
    // Preseleccionar proyecto si viene ?p=ID en la URL (ej. redirect desde /proyectos/[id])
    const preselect = new URLSearchParams(window.location.search).get('p');
    if (preselect) {
      const id = parseInt(preselect, 10);
      if (!isNaN(id)) await selectProject(id);
    }
  });

  onDestroy(() => {
    stopPolling();
    if (typewriterTimer) clearInterval(typewriterTimer);
  });

  // ── Projects ──────────────────────────────────────────────────────────
  async function loadProjects() {
    try {
      projectsLoading = true; projectsError = null;
      const resp = await projectService.listProjects();
      projectsStore.setProjects(resp.projects);
    } catch (e: any) {
      projectsError = e.detail || 'Error al cargar proyectos';
    } finally { projectsLoading = false; }
  }

  async function loadInvitations() {
    try {
      invitationsStore.setLoading(true);
      const resp = await invitationService.listPending();
      invitationsStore.setPending(resp.invitations);
    } catch { } finally { invitationsStore.setLoading(false); }
  }

  // ── Select project inline ─────────────────────────────────────────────
  async function selectProject(id: number) {
    if (selectedProjectId === id && view === 'workspace') return;
    stopPolling();
    clearTypewriter();
    selectedProjectId = id;
    selectedProject = null;
    members = [];
    messages = [];
    editing = false;
    view = 'workspace';
    pdfContext = undefined;
    pdfFilename = '';
    mobileShowSidebar = false;
    mobileShowRight = false;
    await loadProjectData(id);
    startPolling(id);
  }

  async function loadProjectData(id: number) {
    try {
      projectLoading = true; projectError = null;
      const [proj, membersResp, msgResp] = await Promise.all([
        projectService.getProject(id),
        projectService.listMembers(id),
        chatService.listMessages(id, 0, 200)
      ]);
      selectedProject = proj;
      members = membersResp.members;
      messages = msgResp.messages;
      await tick();
      scrollToAiBottom();
      scrollToGroupBottom();
    } catch (e: any) {
      projectError = e.detail || 'Error al cargar el proyecto';
    } finally { projectLoading = false; }
  }

  function startPolling(id: number) {
    pollingInterval = setInterval(async () => {
      try {
        const resp = await chatService.listMessages(id, 0, 200);
        const maxId = messages.length > 0 ? Math.max(...messages.map((m: any) => m.id)) : 0;
        const newOnes = resp.messages.filter((m: any) => m.id > maxId);
        if (newOnes.length > 0) {
          messages = [...messages, ...newOnes];
          await tick();
          scrollToGroupBottom();
        }
      } catch { }
    }, 5000);
  }

  function stopPolling() {
    if (pollingInterval) { clearInterval(pollingInterval); pollingInterval = null; }
  }

  // ── Scroll ────────────────────────────────────────────────────────────
  function scrollToAiBottom() {
    setTimeout(() => { if (aiChatContainer) aiChatContainer.scrollTop = aiChatContainer.scrollHeight; }, 50);
  }
  function scrollToGroupBottom() {
    setTimeout(() => { if (groupChatContainer) groupChatContainer.scrollTop = groupChatContainer.scrollHeight; }, 50);
  }

  // ── Edit ──────────────────────────────────────────────────────────────
  function startEdit() {
    if (!selectedProject) return;
    editName = selectedProject.name;
    editDescription = selectedProject.description || '';
    editStartDate = selectedProject.start_date || '';
    editAiInstructions = (selectedProject as any).ai_instructions || '';
    editing = true;
  }

  async function saveEdit() {
    if (!editName.trim()) { notificationsStore.warning('El nombre es obligatorio'); return; }
    try {
      saving = true;
      const updated = await projectService.updateProject(selectedProjectId!, {
        name: editName.trim(),
        description: editDescription.trim() || undefined,
        start_date: editStartDate || undefined,
        ai_instructions: editAiInstructions.trim() || undefined
      });
      selectedProject = updated;
      projectsStore.setProjects(projects.map(p => p.id === selectedProjectId ? updated : p));
      editing = false;
      notificationsStore.success('Proyecto actualizado');
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al actualizar');
    } finally { saving = false; }
  }

  // ── Create ────────────────────────────────────────────────────────────
  async function handleCreate() {
    if (!newName.trim()) { notificationsStore.warning('El nombre es obligatorio'); return; }
    try {
      creating = true;
      const project = await projectService.createProject({
        name: newName.trim(),
        description: newDescription.trim() || undefined,
        start_date: newStartDate || undefined,
        ai_instructions: newAiInstructions.trim() || undefined
      });
      projectsStore.addProject(project);
      notificationsStore.success(`Proyecto "${project.name}" creado`);
      newName = ''; newDescription = ''; newStartDate = ''; newAiInstructions = '';
      await selectProject(project.id);
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al crear proyecto');
    } finally { creating = false; }
  }

  // ── Delete ────────────────────────────────────────────────────────────
  function requestDelete(project: Project, e: MouseEvent) {
    e.stopPropagation();
    confirmDeleteId = project.id;
  }

  async function confirmDelete(project: Project, e: MouseEvent) {
    e.stopPropagation();
    confirmDeleteId = null;
    try {
      await projectService.deleteProject(project.id);
      projectsStore.removeProject(project.id);
      if (selectedProjectId === project.id) {
        selectedProjectId = null; selectedProject = null;
        messages = []; members = []; stopPolling();
      }
      notificationsStore.success('Proyecto eliminado');
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al eliminar');
    }
  }

  function cancelDelete(e: MouseEvent) {
    e.stopPropagation();
    confirmDeleteId = null;
  }

  // ── Members ───────────────────────────────────────────────────────────
  async function loadSentInvitations() {
    if (!selectedProjectId) return;
    try {
      const resp = await projectService.listProjectInvitations(selectedProjectId);
      sentInvitations = resp.invitations;
    } catch { sentInvitations = []; }
  }

  async function handleAddMember() {
    if (!newMemberEmail.trim()) return;
    try {
      addingMember = true;
      await projectService.addMember(selectedProjectId!, newMemberEmail.trim());
      newMemberEmail = ''; emailSuggestions = []; showSuggestions = false;
      notificationsStore.success('Invitación enviada');
      await loadSentInvitations();
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al invitar');
    } finally { addingMember = false; }
  }

  function onEmailInput() {
    clearTimeout(debounceTimer); suggestionIndex = -1;
    const q = newMemberEmail.trim();
    if (q.length < 2) { emailSuggestions = []; showSuggestions = false; return; }
    debounceTimer = setTimeout(async () => {
      try {
        const results = await apiClient.get<UserSuggestion[]>('/auth/users/search', { q });
        const memberIds = new Set(members.map(m => m.user_id));
        emailSuggestions = results.filter(u => !memberIds.has(u.id));
        showSuggestions = emailSuggestions.length > 0;
      } catch { emailSuggestions = []; showSuggestions = false; }
    }, 300);
  }

  function selectSuggestion(u: UserSuggestion) {
    newMemberEmail = u.email; emailSuggestions = []; showSuggestions = false; suggestionIndex = -1;
  }

  function onEmailKeydown(e: KeyboardEvent) {
    if (!showSuggestions) return;
    if (e.key === 'ArrowDown') { e.preventDefault(); suggestionIndex = Math.min(suggestionIndex + 1, emailSuggestions.length - 1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); suggestionIndex = Math.max(suggestionIndex - 1, -1); }
    else if (e.key === 'Enter' && suggestionIndex >= 0) { e.preventDefault(); selectSuggestion(emailSuggestions[suggestionIndex]); }
    else if (e.key === 'Escape') { showSuggestions = false; }
  }

  let confirmRemoveMemberId: number | null = null;

  async function handleRemoveMember(member: ProjectMember) {
    if (member.user_id === selectedProject?.owner_id) { notificationsStore.warning('No se puede remover al propietario'); return; }
    if (confirmRemoveMemberId !== member.user_id) { confirmRemoveMemberId = member.user_id; return; }
    confirmRemoveMemberId = null;
    try {
      await projectService.removeMember(selectedProjectId!, member.user_id);
      members = members.filter(m => m.user_id !== member.user_id);
      notificationsStore.success('Miembro removido');
    } catch (e: any) { notificationsStore.error(e.detail || 'Error al remover'); }
  }

  // ── Group chat ────────────────────────────────────────────────────────
  async function handleSendMessage() {
    if (!chatInput.trim() || sendingMsg) return;
    const content = chatInput.trim(); chatInput = '';
    try {
      sendingMsg = true;
      const msg = await chatService.sendMessage(selectedProjectId!, content);
      messages = [...messages, msg];
      await tick(); scrollToGroupBottom();
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al enviar mensaje');
      chatInput = content;
    } finally { sendingMsg = false; }
  }

  function onChatKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); }
  }

  // ── AI chat ───────────────────────────────────────────────────────────
  function clearTypewriter() {
    if (typewriterTimer) { clearInterval(typewriterTimer); typewriterTimer = null; }
    typewriterMsgId = null; typewriterContent = '';
  }

  function startTypewriter(msgId: number, content: string) {
    clearTypewriter();
    typewriterMsgId = msgId; typewriterContent = ''; let i = 0;
    typewriterTimer = setInterval(() => {
      i += 3;
      typewriterContent = content.slice(0, i);
      scrollToAiBottom();
      if (i >= content.length) { clearTypewriter(); }
    }, 18);
  }

  async function handleAskAI() {
    if (!aiInput.trim() || sendingMsg) return;
    const question = aiInput.trim(); aiInput = '';
    aiUsedThisHour++;
    try {
      sendingMsg = true; aiThinking = true;
      const resp = await chatService.askAI(selectedProjectId!, question, pdfContext);
      messages = [...messages, resp.user_message, resp.ai_message];
      aiThinking = false;
      await tick(); scrollToAiBottom();
      startTypewriter(resp.ai_message.id, resp.ai_message.content);
    } catch (e: any) {
      aiThinking = false;
      aiUsedThisHour = Math.max(0, aiUsedThisHour - 1);
      notificationsStore.error(e.detail || e.message || 'Error al consultar la IA');
      aiInput = question;
    } finally { sendingMsg = false; }
  }

  function onAiKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAskAI(); }
  }

  async function handlePdfUpload(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0]; if (!file) return;
    try {
      uploadingPdf = true;
      const resp = await chatService.uploadPdfContext(selectedProjectId!, file);
      pdfContext = resp.text; pdfFilename = resp.filename;
      notificationsStore.success(`PDF: ${resp.filename}`);
    } catch (e: any) {
      notificationsStore.error(e.detail || 'Error al procesar PDF');
    } finally { uploadingPdf = false; input.value = ''; }
  }

  // ── Invitations ───────────────────────────────────────────────────────
  async function handleAccept(id: number) {
    try {
      await invitationService.accept(id);
      invitationsStore.remove(id);
      notificationsStore.success('Te has unido al proyecto');
      await loadProjects();
    } catch (e: any) { notificationsStore.error(e.detail || 'Error al aceptar'); }
  }

  async function handleDecline(id: number) {
    try {
      await invitationService.decline(id);
      invitationsStore.remove(id);
      notificationsStore.success('Invitación rechazada');
    } catch (e: any) { notificationsStore.error(e.detail || 'Error al rechazar'); }
  }

  // ── Helpers ───────────────────────────────────────────────────────────
  function getRoleBadge(role: ProjectRole): string {
    const map: Record<ProjectRole, string> = { lider: 'badge-primary', investigador: 'badge-accent', colaborador: 'badge-info', observador: 'badge-ghost' };
    return map[role] ?? '';
  }
  function getRoleLabel(role: string | undefined): string {
    const map: Record<string, string> = { lider: 'Líder', investigador: 'Investigador', colaborador: 'Colaborador', observador: 'Observador' };
    return map[role ?? ''] ?? (role || 'Observador');
  }
  function formatTime(d: string) { return new Date(d).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' }); }
  function initials(name: string) { return name.charAt(0).toUpperCase(); }
</script>

<svelte:head>
  <title>{selectedProject?.name || 'Proyectos'} - ROGER</title>
</svelte:head>

<div class="flex h-[calc(100svh-8rem)] overflow-hidden bg-base-200/30 relative">

  <!-- Mobile sidebar backdrop -->
  {#if mobileShowSidebar}
    <div
      class="fixed inset-0 z-30 bg-black/40 lg:hidden"
      on:click={() => mobileShowSidebar = false}
      role="presentation"
    ></div>
  {/if}

  <!-- Mobile right drawer backdrop -->
  {#if mobileShowRight}
    <div
      class="fixed inset-0 z-30 bg-black/40 lg:hidden"
      on:click={() => mobileShowRight = false}
      role="presentation"
    ></div>
  {/if}

  <!-- ══════════════════════════════════════════════════════════════════ -->
  <!-- LEFT SIDEBAR                                                        -->
  <!-- ══════════════════════════════════════════════════════════════════ -->
  <aside class="{mobileShowSidebar ? 'flex fixed inset-y-0 left-0 z-40 shadow-2xl' : 'hidden md:flex'} w-60 flex-shrink-0 bg-base-100 border-r border-base-300 flex-col select-none">

    <!-- Sidebar header -->
    <div class="px-3 py-3 border-b border-base-300">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div class="min-w-0">
          <p class="text-sm font-bold leading-tight">Chat interactivo</p>
          <p class="text-[10px] text-base-content/40">Asistente IA por proyecto</p>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="px-3 pt-3 pb-1 space-y-1">
      <!-- New project button -->
      <button
        class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-semibold transition-all
          {view === 'new' ? 'bg-primary text-primary-content' : 'hover:bg-base-200 text-base-content/70 hover:text-base-content'}
          {ownedCount >= 3 ? 'opacity-40 cursor-not-allowed' : ''}"
        on:click={() => {
          if (ownedCount >= 3) { notificationsStore.warning('Has alcanzado el límite de 3 proyectos propios'); return; }
          view = 'new'; selectedProjectId = null; selectedProject = null; stopPolling();
        }}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
        </svg>
        <span>Nuevo proyecto</span>
        <span class="ml-auto text-[10px] opacity-50">{ownedCount}/3</span>
      </button>

      <!-- Invitations button -->
      <button
        class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-semibold transition-all
          {view === 'invitations' ? 'bg-primary text-primary-content' : 'hover:bg-base-200 text-base-content/70 hover:text-base-content'}"
        on:click={() => { view = 'invitations'; selectedProjectId = null; selectedProject = null; stopPolling(); }}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <span>Invitaciones</span>
        {#if $pendingCount > 0}
          <span class="ml-auto badge badge-warning badge-xs font-bold">{$pendingCount}</span>
        {/if}
      </button>
    </div>

    <!-- Divider -->
    <div class="px-3 py-2">
      <p class="text-[10px] font-bold uppercase tracking-widest text-base-content/30 px-1">Mis proyectos</p>
    </div>

    <!-- Project list -->
    <nav class="flex-1 overflow-y-auto px-2 space-y-0.5 pb-2">
      {#if projectsLoading}
        <div class="flex justify-center py-6">
          <span class="loading loading-spinner loading-sm text-primary/40"></span>
        </div>
      {:else if projectsError}
        <p class="text-xs text-error px-3 py-2">{projectsError}</p>
      {:else if projects.length === 0}
        <p class="text-xs text-base-content/30 px-3 py-3 text-center">Sin proyectos aún</p>
      {:else}
        {#each projects as project (project.id)}
          <!-- Confirmar eliminación inline -->
          {#if confirmDeleteId === project.id}
            <div class="flex items-center gap-1 px-2 py-2 rounded-lg bg-error/10 border border-error/20">
              <span class="flex-1 text-xs text-error font-semibold truncate">¿Eliminar?</span>
              <button
                class="btn btn-error btn-xs rounded-md h-6 min-h-0 px-2"
                on:click={e => confirmDelete(project, e)}>Sí</button>
              <button
                class="btn btn-ghost btn-xs rounded-md h-6 min-h-0 px-2"
                on:click={cancelDelete}>No</button>
            </div>
          {:else}
          <div
            class="group relative flex items-center gap-2 px-2 py-2 rounded-lg cursor-pointer transition-all
              {selectedProjectId === project.id && view === 'workspace'
                ? 'bg-primary/10 text-primary'
                : 'hover:bg-base-200 text-base-content/70 hover:text-base-content'}"
            on:click={() => selectProject(project.id)}
            role="button"
            tabindex="0"
            on:keydown={e => e.key === 'Enter' && selectProject(project.id)}>

            <!-- Avatar -->
            <div class="w-7 h-7 rounded-md flex-shrink-0 flex items-center justify-center text-xs font-bold
              {selectedProjectId === project.id && view === 'workspace' ? 'bg-primary text-primary-content' : 'bg-base-300 text-base-content/60'}">
              {initials(project.name)}
            </div>

            <!-- Name -->
            <span class="flex-1 text-sm font-medium truncate min-w-0" title={project.name}>{project.name}</span>

            <!-- Owner badge + delete -->
            <div class="flex items-center gap-1 flex-shrink-0">
              {#if project.owner_id === currentUserId}
                <button
                  class="flex sm:opacity-0 sm:group-hover:opacity-100 w-5 h-5 items-center justify-center rounded text-error/50 hover:text-error hover:bg-error/10 transition-opacity"
                  on:click={e => requestDelete(project, e)}
                  title="Eliminar">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              {/if}
            </div>

          </div>
          {/if}
        {/each}
      {/if}
    </nav>

    <!-- Bottom: AI quota -->
    <div class="px-4 py-3 border-t border-base-300">
      <div class="flex items-center justify-between mb-1.5">
        <p class="text-[10px] text-base-content/40 font-semibold uppercase tracking-wide">Consultas IA</p>
        <p class="text-[10px] text-base-content/50 font-bold">{aiUsedThisHour}/10 esta hora</p>
      </div>
      <div class="flex gap-0.5">
        {#each {length: 10} as _, i}
          <div class="flex-1 h-1.5 rounded-full transition-colors {i < aiUsedThisHour ? (aiUsedThisHour >= 9 ? 'bg-error' : aiUsedThisHour >= 6 ? 'bg-warning' : 'bg-primary') : 'bg-base-300'}"></div>
        {/each}
      </div>
      {#if aiRemaining === 0}
        <p class="text-[10px] text-error mt-1">Sin consultas disponibles</p>
      {:else}
        <p class="text-[10px] text-base-content/30 mt-1">{aiRemaining} consultas restantes</p>
      {/if}
    </div>

  </aside>

  <!-- ══════════════════════════════════════════════════════════════════ -->
  <!-- CENTER: AI WORKSPACE                                               -->
  <!-- ══════════════════════════════════════════════════════════════════ -->
  <div class="flex-1 flex flex-col min-w-0 overflow-hidden">

    <!-- Mobile top bar (hamburger + título + botón equipo) -->
    <div class="lg:hidden flex-shrink-0 bg-base-100 border-b border-base-300 px-3 py-2 flex items-center gap-2">
      <button
        class="btn btn-ghost btn-xs btn-square"
        on:click={() => mobileShowSidebar = true}
        title="Proyectos">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <span class="text-sm font-semibold truncate flex-1">{selectedProject?.name || 'Proyectos'}</span>
      {#if selectedProject}
        <button
          class="btn btn-ghost btn-xs gap-1"
          on:click={() => mobileShowRight = true}
          title="Equipo">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0" />
          </svg>
          <span class="text-xs">Equipo</span>
        </button>
      {/if}
    </div>

    <!-- ─ NEW PROJECT FORM ─────────────────────────────────────────── -->
    {#if view === 'new'}
      <div class="flex-1 overflow-y-auto">
        <div class="max-w-xl mx-auto px-6 py-8">
          <div class="mb-6">
            <h1 class="text-xl font-bold">Nuevo proyecto</h1>
            <p class="text-sm text-base-content/50 mt-0.5">Puedes tener hasta 3 proyectos propios</p>
          </div>
          <div class="bg-base-100 rounded-2xl border border-base-300 p-6 shadow-sm">
            <form on:submit|preventDefault={handleCreate} class="space-y-4">
              <div class="form-control">
                <label class="label py-1" for="new-name">
                  <span class="label-text font-semibold text-sm">Nombre *</span>
                </label>
                <input id="new-name" type="text" placeholder="Ej: Expedición Sacambaya 1928"
                  class="input input-bordered" bind:value={newName} maxlength="255" required />
              </div>
              <div class="form-control">
                <label class="label py-1" for="new-desc">
                  <span class="label-text font-semibold text-sm">Descripción</span>
                </label>
                <textarea id="new-desc" placeholder="Describe el objetivo del proyecto…"
                  class="textarea textarea-bordered h-24 resize-none" bind:value={newDescription}></textarea>
              </div>
              <div class="form-control">
                <label class="label py-1" for="new-date">
                  <span class="label-text font-semibold text-sm">Fecha de inicio</span>
                </label>
                <input id="new-date" type="date" class="input input-bordered" bind:value={newStartDate} min={today} />
              </div>
              <div class="form-control">
                <label class="label py-1" for="new-ai">
                  <span class="label-text font-semibold text-sm">Contexto para la IA</span>
                  <span class="label-text-alt text-[11px] text-base-content/40">Opcional</span>
                </label>
                <textarea
                  id="new-ai"
                  class="textarea textarea-bordered h-28 resize-none text-sm"
                  placeholder="Ej: Este proyecto investiga el Fondo Fotográfico Robert Gerstmann (1896–1964), fotógrafo alemán que documentó Chile y Bolivia entre 1924 y 1964. Las imágenes abarcan paisajes, comunidades indígenas y expediciones a zonas como Isla de Pascua y la Antártica. Publicaciones clave: 'Chile: 280 grabados en cobre' (1932) y 'Bolivia' (1928)."
                  bind:value={newAiInstructions}
                ></textarea>
                <p class="text-[11px] text-base-content/40 mt-1 px-1">Este texto se entrega a la IA en cada consulta para dar contexto específico al proyecto.</p>
              </div>
              {#if ownedCount >= 2}
                <div class="alert bg-warning/10 border-warning/20 text-sm py-2.5">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  {ownedCount === 2 ? 'Este será tu último proyecto disponible.' : 'Has alcanzado el límite máximo.'}
                </div>
              {/if}
              <div class="flex gap-3 justify-end pt-1">
                <button type="button" class="btn btn-ghost btn-sm" on:click={() => view = 'workspace'}>Cancelar</button>
                <button type="submit" class="btn btn-primary btn-sm" disabled={creating || !newName.trim()}>
                  {#if creating}<span class="loading loading-spinner loading-xs"></span>{/if}
                  Crear proyecto
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

    <!-- ─ INVITATIONS ───────────────────────────────────────────────── -->
    {:else if view === 'invitations'}
      <div class="flex-1 overflow-y-auto">
        <div class="max-w-xl mx-auto px-6 py-8">
          <div class="mb-6">
            <h1 class="text-xl font-bold">Invitaciones pendientes</h1>
            <p class="text-sm text-base-content/50 mt-0.5">Proyectos a los que has sido invitado</p>
          </div>
          {#if $invitationsStore.loading}
            <div class="flex justify-center py-16"><span class="loading loading-spinner text-primary"></span></div>
          {:else if $invitationsStore.pending.length === 0}
            <div class="flex flex-col items-center py-20 text-center">
              <div class="w-14 h-14 rounded-2xl bg-base-300 flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-base-content/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <p class="text-sm font-semibold text-base-content/50">Sin invitaciones pendientes</p>
            </div>
          {:else}
            <div class="space-y-3">
              {#each $invitationsStore.pending as inv (inv.id)}
                <div class="bg-base-100 rounded-2xl border border-base-300 p-4 shadow-sm">
                  <div class="flex items-center gap-3 mb-3">
                    <div class="w-10 h-10 rounded-xl bg-secondary/10 text-secondary flex items-center justify-center font-bold flex-shrink-0">
                      {inv.project_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p class="font-bold text-sm">{inv.project_name}</p>
                      <p class="text-xs text-base-content/40">Invitado por {inv.invited_by_email}</p>
                    </div>
                  </div>
                  <div class="flex gap-2">
                    <button class="btn btn-success btn-sm flex-1 rounded-xl" on:click={() => handleAccept(inv.id)}>Aceptar</button>
                    <button class="btn btn-ghost btn-sm flex-1 rounded-xl text-error" on:click={() => handleDecline(inv.id)}>Rechazar</button>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>

    <!-- ─ WORKSPACE (no project selected) ──────────────────────────── -->
    {:else if !selectedProjectId}
      <div class="flex-1 flex flex-col items-center justify-center text-center px-8">
        <div class="w-20 h-20 rounded-3xl bg-primary/8 flex items-center justify-center mb-5">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-primary/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <h2 class="text-lg font-bold text-base-content/50 mb-2">Selecciona un proyecto</h2>
        <p class="text-sm text-base-content/30 max-w-xs">Haz clic en un proyecto del panel izquierdo para cargar su espacio de trabajo con el asistente IA.</p>
        {#if projects.length === 0 && !projectsLoading}
          <button class="btn btn-primary btn-sm mt-6"
            on:click={() => { view = 'new'; selectedProjectId = null; selectedProject = null; }}>
            Crear primer proyecto
          </button>
        {/if}
      </div>

    <!-- ─ WORKSPACE (project loading) ──────────────────────────────── -->
    {:else if projectLoading}
      <div class="flex-1 flex items-center justify-center">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

    <!-- ─ WORKSPACE (project error) ────────────────────────────────── -->
    {:else if projectError}
      <div class="flex-1 flex items-center justify-center p-8">
        <div class="alert alert-error max-w-sm">
          <span>{projectError}</span>
          <button class="btn btn-sm" on:click={() => selectedProjectId && loadProjectData(selectedProjectId)}>Reintentar</button>
        </div>
      </div>

    <!-- ─ WORKSPACE (project loaded) ───────────────────────────────── -->
    {:else if selectedProject}

      <!-- Project top bar -->
      <div class="flex-shrink-0 bg-base-100 border-b border-base-300 px-4 py-2.5 flex items-center gap-3">
        {#if editing}
          <div class="flex-1 min-w-0">
            <p class="font-bold text-sm">Editando: {selectedProject.name}</p>
          </div>
        {:else}
          <div class="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center font-bold text-sm flex-shrink-0">
            {initials(selectedProject.name)}
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-sm truncate">{selectedProject.name}</p>
            {#if selectedProject.description}
              <p class="text-xs text-base-content/40 truncate">{selectedProject.description}</p>
            {/if}
          </div>
          <div class="flex items-center gap-1 flex-shrink-0">
            {#if isOwner}
              <span class="badge badge-primary badge-xs">Dueño</span>
            {:else}
              <span class="badge badge-ghost badge-xs">{getRoleLabel(myMembership?.role ?? 'observador')}</span>
            {/if}
            {#if canEdit}
              <button class="btn btn-ghost btn-xs btn-square" on:click={startEdit} title="Editar proyecto">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            {/if}
          </div>
          <!-- Toggle right panel -->
          <button
            class="btn btn-ghost btn-xs btn-square ml-1"
            on:click={() => rightPanelOpen = !rightPanelOpen}
            title="{rightPanelOpen ? 'Ocultar' : 'Mostrar'} panel de equipo">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {#if rightPanelOpen}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              {:else}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              {/if}
            </svg>
          </button>
        {/if}
      </div>

      <!-- Edit form (full central area) -->
      {#if editing}
        <div class="flex-1 overflow-y-auto flex flex-col items-center justify-center px-6 py-8">
          <div class="w-full max-w-lg bg-base-100 rounded-2xl border border-base-300 shadow-sm p-6">
            <h2 class="text-base font-bold mb-4">Editar proyecto</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="form-control col-span-2 sm:col-span-1">
                <label class="label py-0.5" for="ep-name"><span class="label-text text-xs font-semibold">Nombre *</span></label>
                <input id="ep-name" type="text" class="input input-bordered input-sm" bind:value={editName} />
              </div>
              <div class="form-control col-span-2">
                <label class="label py-0.5" for="ep-desc"><span class="label-text text-xs font-semibold">Descripción</span></label>
                <input id="ep-desc" type="text" class="input input-bordered input-sm" bind:value={editDescription} placeholder="Descripción breve del proyecto" />
              </div>
              {#if isLider}
                <div class="form-control col-span-2">
                  <label class="label py-0.5" for="ep-ai">
                    <span class="label-text text-xs font-semibold">Instrucciones para la IA</span>
                    <span class="label-text-alt text-[10px] text-base-content/40">Solo las ve la IA</span>
                  </label>
                  <textarea
                    id="ep-ai"
                    class="textarea textarea-bordered textarea-sm resize-none h-24 text-sm"
                    placeholder="Ej: En este proyecto 'planta madre' se refiere a la instalación central…"
                    bind:value={editAiInstructions}
                  ></textarea>
                </div>
              {/if}
            </div>
            <div class="flex gap-2 justify-end mt-5">
              <button class="btn btn-ghost btn-sm" on:click={() => editing = false}>Cancelar</button>
              <button class="btn btn-primary btn-sm" on:click={saveEdit} disabled={saving || !editName.trim()}>
                {#if saving}<span class="loading loading-spinner loading-xs"></span>{/if}
                Guardar cambios
              </button>
            </div>
          </div>
        </div>
      {/if}

      <!-- AI chat area -->
      <div class="flex-1 overflow-y-auto px-4 py-4 space-y-6" class:hidden={editing} bind:this={aiChatContainer}>

        {#if aiConversation.length === 0 && !aiThinking}
          <div class="flex flex-col items-center justify-center h-full text-center py-12">
            <div class="w-16 h-16 rounded-2xl bg-primary/8 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <p class="font-semibold text-base-content/50">Asistente IA listo</p>
            <p class="text-sm text-base-content/30 mt-1 max-w-xs">Haz tu primera consulta. Puedes adjuntar un PDF para dar contexto adicional.</p>
          </div>
        {:else}
          {#each aiConversation as pair (pair.answer.id)}
            <!-- User question -->
            {#if pair.question}
              <div class="flex justify-end">
                <div class="max-w-[72%] bg-primary text-primary-content rounded-2xl rounded-tr-sm px-4 py-2.5 shadow-sm">
                  <p class="text-sm whitespace-pre-wrap leading-relaxed">{pair.question.content}</p>
                  <p class="text-[10px] opacity-50 mt-1 text-right">{formatTime(pair.question.created_at)}</p>
                </div>
              </div>
            {/if}
            <!-- AI answer -->
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5
                {aiThinking && pair.answer.id === aiConversation[aiConversation.length - 1]?.answer.id ? 'animate-pulse' : ''}">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div class="flex-1 max-w-[82%]">
                <div class="bg-base-100 border border-base-300 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                  <p class="text-sm whitespace-pre-wrap leading-relaxed">
                    {typewriterMsgId === pair.answer.id ? typewriterContent : pair.answer.content}
                  </p>
                </div>
                <p class="text-[10px] text-base-content/30 mt-1 ml-1">{formatTime(pair.answer.created_at)}</p>
              </div>
            </div>
          {/each}

          <!-- AI thinking indicator -->
          {#if aiThinking}
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0 animate-pulse">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div class="bg-base-100 border border-base-300 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-primary/60 animate-bounce" style="animation-delay:0ms"></span>
                <span class="w-2 h-2 rounded-full bg-primary/60 animate-bounce" style="animation-delay:150ms"></span>
                <span class="w-2 h-2 rounded-full bg-primary/60 animate-bounce" style="animation-delay:300ms"></span>
              </div>
            </div>
          {/if}
        {/if}
      </div>

      <!-- AI input bar -->
      <div class="flex-shrink-0 bg-base-100 border-t border-base-300 px-4 py-3" class:hidden={editing}>
        <!-- PDF indicator -->
        {#if pdfContext}
          <div class="flex items-center gap-2 mb-2 px-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-error flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span class="text-xs text-base-content/50 truncate">{pdfFilename}</span>
            <button class="btn btn-ghost btn-xs btn-square ml-auto" aria-label="Quitar PDF" on:click={() => { pdfContext = undefined; pdfFilename = ''; }}>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        {/if}

        <div class="flex items-end gap-2">
          <!-- PDF upload -->
          <input type="file" accept=".pdf" class="hidden" bind:this={pdfInput} on:change={handlePdfUpload} />
          <button
            class="btn btn-ghost btn-sm btn-square flex-shrink-0 {uploadingPdf ? 'loading' : ''}"
            on:click={() => pdfInput?.click()}
            disabled={uploadingPdf}
            title="Adjuntar PDF">
            {#if !uploadingPdf}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            {/if}
          </button>

          <!-- Input -->
          <textarea
            class="textarea textarea-bordered flex-1 resize-none text-sm leading-relaxed min-h-[42px] max-h-32"
            placeholder="{aiRemaining > 0 ? 'Consulta al asistente IA…' : 'Sin consultas disponibles esta hora'}"
            bind:value={aiInput}
            on:keydown={onAiKeydown}
            disabled={sendingMsg || aiRemaining === 0}
            rows="1"
          ></textarea>

          <!-- Send -->
          <button
            class="btn btn-primary btn-sm flex-shrink-0 h-[42px] px-4"
            on:click={handleAskAI}
            disabled={!aiInput.trim() || sendingMsg || aiRemaining === 0}>
            {#if sendingMsg}
              <span class="loading loading-spinner loading-xs"></span>
            {:else}
              <!-- Robot icon -->
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <rect x="3" y="11" width="18" height="10" rx="2" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 3a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm0 4v4"/>
                <circle cx="8.5" cy="16" r="1" fill="currentColor" stroke="none"/>
                <circle cx="15.5" cy="16" r="1" fill="currentColor" stroke="none"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 19.5h6"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 14h-1m19 0h1"/>
              </svg>
            {/if}
          </button>
        </div>
      </div>
    {/if}
  </div>

  <!-- ══════════════════════════════════════════════════════════════════ -->
  <!-- RIGHT PANEL: GROUP CHAT + MEMBERS                                  -->
  <!-- ══════════════════════════════════════════════════════════════════ -->
  {#if selectedProject && (rightPanelOpen || mobileShowRight)}
    <aside class="{mobileShowRight ? 'flex fixed right-0 inset-y-0 z-40 shadow-2xl' : 'hidden'} {rightPanelOpen ? 'lg:flex' : 'lg:hidden'} w-72 flex-shrink-0 bg-base-100 border-l border-base-300 flex-col min-w-0">

      <!-- Tabs + cierre mobile -->
      <div class="flex border-b border-base-300 flex-shrink-0 items-center">
        <button
          class="flex-1 py-2.5 text-xs font-bold uppercase tracking-wide transition-colors
            {rightTab === 'chat' ? 'text-primary border-b-2 border-primary' : 'text-base-content/40 hover:text-base-content/70'}"
          on:click={() => { rightTab = 'chat'; }}>
          Equipo
        </button>
        <button
          class="flex-1 py-2.5 text-xs font-bold uppercase tracking-wide transition-colors
            {rightTab === 'members' ? 'text-primary border-b-2 border-primary' : 'text-base-content/40 hover:text-base-content/70'}"
          on:click={() => { rightTab = 'members'; if (isLider) loadSentInvitations(); }}>
          Miembros
          <span class="ml-1 text-[10px] opacity-50">({members.length})</span>
        </button>
        <!-- Cerrar drawer (solo mobile) -->
        <button
          class="lg:hidden btn btn-ghost btn-xs btn-square mr-1 flex-shrink-0"
          on:click={() => mobileShowRight = false}
          title="Cerrar">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- ─ GROUP CHAT ─────────────────────────────────────────────── -->
      {#if rightTab === 'chat'}
        <div class="flex-1 overflow-y-auto px-3 py-3 space-y-2.5" bind:this={groupChatContainer}>
          {#if groupMessages.length === 0}
            <div class="flex flex-col items-center justify-center h-full text-center py-8">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-base-content/20 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p class="text-xs text-base-content/30">Sin mensajes aún.<br/>Sé el primero en escribir.</p>
            </div>
          {:else}
            {#each groupMessages as msg (msg.id)}
              <div class="flex {msg.user_id === currentUserId ? 'justify-end' : 'justify-start'}">
                <div class="max-w-[85%] {msg.user_id === currentUserId ? 'bg-primary text-primary-content rounded-2xl rounded-tr-sm' : 'bg-base-200 rounded-2xl rounded-tl-sm'} px-3 py-2 shadow-sm">
                  {#if msg.user_id !== currentUserId}
                    <p class="text-[10px] font-bold opacity-50 mb-0.5">{msg.sender_name || 'Miembro'}</p>
                  {/if}
                  <p class="text-xs whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                  <p class="text-[9px] opacity-40 mt-0.5 {msg.user_id === currentUserId ? 'text-right' : ''}">{formatTime(msg.created_at)}</p>
                </div>
              </div>
            {/each}
          {/if}
        </div>

        <!-- Group chat input -->
        <div class="flex-shrink-0 border-t border-base-300 px-3 py-2.5">
          <div class="flex items-end gap-2">
            <textarea
              class="textarea textarea-bordered textarea-sm flex-1 resize-none text-sm min-h-[36px] max-h-20"
              placeholder="Mensaje al equipo…"
              bind:value={chatInput}
              on:keydown={onChatKeydown}
              disabled={sendingMsg}
              rows="1"
            ></textarea>
            <button
              class="btn btn-primary btn-sm btn-square h-9 w-9 flex-shrink-0"
              on:click={handleSendMessage}
              disabled={!chatInput.trim() || sendingMsg}>
              <!-- Telegram-style paper plane -->
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22 2L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
              </svg>
            </button>
          </div>
        </div>

      <!-- ─ MEMBERS ────────────────────────────────────────────────── -->
      {:else}
        <div class="flex-1 overflow-y-auto">
          <!-- Add member (lider only) -->
          {#if isLider}
            <div class="px-3 pt-3 pb-2 border-b border-base-300">
              <div class="relative">
                <input
                  type="email"
                  class="input input-bordered input-sm w-full pr-20 text-xs"
                  placeholder="Ingresar correo"
                  bind:value={newMemberEmail}
                  on:input={onEmailInput}
                  on:keydown={onEmailKeydown}
                  autocomplete="off"
                />
                <button
                  class="btn btn-primary btn-xs absolute right-1 top-1/2 -translate-y-1/2"
                  on:click={handleAddMember}
                  disabled={!newMemberEmail.trim() || addingMember}>
                  {#if addingMember}<span class="loading loading-spinner loading-xs"></span>{:else}Invitar{/if}
                </button>
                {#if showSuggestions}
                  <ul class="absolute z-20 top-full left-0 right-0 mt-1 bg-base-100 border border-base-300 rounded-xl shadow-lg overflow-hidden">
                    {#each emailSuggestions as su, i (su.id)}
                      <li>
                        <button
                          class="w-full text-left px-3 py-2 text-xs hover:bg-base-200 transition-colors {i === suggestionIndex ? 'bg-base-200' : ''}"
                          on:click={() => selectSuggestion(su)}>
                          <span class="font-medium">{su.email}</span>
                          {#if su.full_name}<span class="text-base-content/40 ml-1">— {su.full_name}</span>{/if}
                        </button>
                      </li>
                    {/each}
                  </ul>
                {/if}
              </div>
            </div>
          {/if}

          <!-- Members list -->
          <div class="px-3 py-2 space-y-1">
            {#each members as member (member.id)}
              <div class="flex items-center gap-2 py-1.5 group">
                <div class="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0
                  {member.user_id === selectedProject?.owner_id ? 'bg-primary text-primary-content' : 'bg-base-300 text-base-content/60'}">
                  {(member.user_full_name || member.user_email || '?').charAt(0).toUpperCase()}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-semibold truncate" title={member.user_full_name || member.user_email}>
                    {member.user_full_name || member.user_email || `#${member.user_id}`}
                    {#if member.user_id === currentUserId}<span class="text-[9px] text-primary font-bold ml-1">(tú)</span>{/if}
                  </p>
                  <span class="badge {getRoleBadge(member.role)} badge-xs">{getRoleLabel(member.role)}</span>
                </div>
                {#if isLider && member.user_id !== selectedProject?.owner_id}
                  {#if confirmRemoveMemberId === member.user_id}
                    <div class="flex gap-1 flex-shrink-0">
                      <button class="btn btn-error btn-xs h-5 min-h-0 px-1.5 text-[10px]"
                        on:click={() => handleRemoveMember(member)}>Sí</button>
                      <button class="btn btn-ghost btn-xs h-5 min-h-0 px-1.5 text-[10px]"
                        on:click={() => confirmRemoveMemberId = null}>No</button>
                    </div>
                  {:else}
                    <button
                      class="flex sm:opacity-0 sm:group-hover:opacity-100 btn btn-ghost btn-xs btn-square text-error/50 hover:text-error transition-opacity"
                      on:click={() => handleRemoveMember(member)}
                      title="Remover">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  {/if}
                {/if}
              </div>
            {/each}
          </div>

          <!-- Sent invitations -->
          {#if isLider && sentInvitations.length > 0}
            <div class="px-3 pt-2 pb-3 border-t border-base-300">
              <p class="text-[10px] font-bold uppercase tracking-wide text-base-content/30 mb-1.5">Invitaciones enviadas</p>
              {#each sentInvitations as inv (inv.id)}
                <div class="flex items-center gap-2 py-1">
                  <div class="w-1.5 h-1.5 rounded-full bg-warning flex-shrink-0"></div>
                  <p class="text-xs text-base-content/50 truncate">{inv.invited_email}</p>
                  <span class="badge badge-warning badge-xs ml-auto">Pendiente</span>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/if}

    </aside>
  {/if}

</div>
