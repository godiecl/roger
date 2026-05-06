<script lang="ts">
  import { onMount } from 'svelte';

  const themes = [
    { id: 'lofi',      label: 'Lofi',      icon: '○' },
    { id: 'dark',      label: 'Dark',      icon: '●' },
    { id: 'nord',      label: 'Nord',      icon: '❄' },
    { id: 'cupcake',   label: 'Cupcake',   icon: '🧁' },
    { id: 'luxury',    label: 'Luxury',    icon: '◆' },
    { id: 'corporate', label: 'Corporate', icon: '▣' },
    { id: 'retro',     label: 'Retro',     icon: '◉' },
  ];

  let currentTheme = 'lofi';

  onMount(() => {
    currentTheme = localStorage.getItem('roger-theme') || 'lofi';
  });

  function setTheme(theme: string) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('roger-theme', theme);
  }
</script>

<div class="dropdown dropdown-end">
  <button
    tabindex="0"
    class="btn btn-ghost btn-circle"
    aria-label="Cambiar tema"
    title="Cambiar tema"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
    </svg>
  </button>

  <ul
    tabindex="0"
    class="dropdown-content menu p-2 shadow-xl bg-base-100 rounded-box w-40 border border-base-content/10 mt-2 z-[100]"
  >
    {#each themes as theme}
      <li>
        <button
          class="flex items-center gap-2 text-sm font-semibold w-full text-left {currentTheme === theme.id ? 'active' : ''}"
          on:click={() => setTheme(theme.id)}
        >
          <span class="text-base">{theme.icon}</span>
          {theme.label}
          {#if currentTheme === theme.id}
            <span class="ml-auto text-primary">✓</span>
          {/if}
        </button>
      </li>
    {/each}
  </ul>
</div>
