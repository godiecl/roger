<script lang="ts">
  let message = "Describe la imagen TA-LTA-BRC-016.jpg";
  let loading = false;
  let response: any = null;
  let error = "";

  const API_URL = `${import.meta.env.VITE_API_URL}/roger/chat`;

  async function sendMessage() {
    console.log("CLICK ENVIAR");
    console.log("API_URL:", API_URL);
    console.log("message:", message);

    if (!message.trim()) {
      console.log("Mensaje vacío");
      return;
    }

    loading = true;
    error = "";
    response = null;

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message })
      });

      console.log("status:", res.status);

      const data = await res.json();
      console.log("data:", data);

      if (!res.ok) {
        throw new Error(data.error || data.detail || `Error ${res.status}`);
      }

      response = data;
    } catch (err: any) {
      console.error("ERROR:", err);
      error = err.message || "Error al consultar ROGER";
    } finally {
      loading = false;
    }
  }
</script>

<section class="min-h-screen bg-gray-50 px-8 py-10">
  <div class="mx-auto max-w-4xl rounded-2xl bg-white p-8 shadow-lg">
    <h1 class="mb-2 text-3xl font-bold text-gray-900">ROGER IA</h1>
    <p class="mb-6 text-gray-600">
      Consulta el archivo patrimonial usando lenguaje natural.
    </p>

    <textarea
      bind:value={message}
      rows="5"
      class="w-full rounded-xl border border-gray-300 p-4 text-gray-800 outline-none focus:border-blue-600"
      placeholder="Ej: Describe la imagen TA-LTA-BRC-016.jpg"
    />

    <button
        type="button"
        on:click={sendMessage}
        disabled={loading}
        class="mt-4 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
        >
        {loading ? "Consultando..." : "Enviar"}
    </button>

    {#if error}
      <div class="mt-6 rounded-xl bg-red-100 p-4 text-red-700">
        {error}
      </div>
    {/if}

    {#if response}
      <div class="mt-6 rounded-xl bg-gray-100 p-5">
        <h2 class="mb-3 text-xl font-bold text-gray-900">Respuesta</h2>

        <p><strong>Herramienta:</strong> {response.tool_used}</p>

        {#if response.result?.caption_en}
          <p class="mt-3">
            <strong>Descripción:</strong> {response.result.caption_en}
          </p>
        {/if}

        {#if response.result?.results}
          <div class="mt-4">
            <strong>Resultados:</strong>
            <ul class="mt-2 list-disc pl-6">
              {#each response.result.results as item}
                <li>
                  {item.image_name}
                  {#if item.score}
                    — score: {item.score.toFixed(3)}
                  {/if}
                </li>
              {/each}
            </ul>
          </div>
        {/if}

        <details class="mt-4">
          <summary class="cursor-pointer font-semibold">Ver JSON completo</summary>
          <pre class="mt-3 overflow-auto rounded-lg bg-gray-900 p-4 text-sm text-green-300">{JSON.stringify(response, null, 2)}</pre>
        </details>
      </div>
    {/if}
  </div>
</section>