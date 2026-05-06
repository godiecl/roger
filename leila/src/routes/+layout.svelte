<script lang="ts">
  import { onMount } from 'svelte';
  import Layout from '$lib/components/layout/Layout.svelte';
  import Toast from '$lib/components/common/Toast.svelte';
  import { enforceHttps } from '$lib/config/security';
  import '../app.css';

  // Enforce HTTPS in production
  onMount(() => {
    enforceHttps();
  });
</script>

<Layout>
  <slot />
</Layout>

<Toast />
