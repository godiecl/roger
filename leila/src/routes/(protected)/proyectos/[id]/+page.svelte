<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  onMount(() => goto(`/proyectos?p=${$page.params.id}`, { replaceState: true }));
</script>
