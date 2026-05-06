<script lang="ts">
  import { apiClient } from '$lib/services/apiClient';

  let name = '';
  let email = '';
  let company = '';
  let subject = '';
  let message = '';
  let sent = false;
  let sending = false;
  let errorMsg = '';

  async function handleSubmit(e: Event) {
    e.preventDefault();
    sending = true;
    errorMsg = '';
    try {
      await apiClient.post('/auth/contact', {
        name: name.trim(),
        email: email.trim(),
        company: company.trim() || undefined,
        subject,
        message: message.trim(),
      });
      sent = true;
    } catch (err: any) {
      errorMsg = err.detail || 'Error al enviar el mensaje. Intenta de nuevo.';
    } finally {
      sending = false;
    }
  }
</script>

<svelte:head>
  <title>Contacto — ROGER</title>
  <meta name="description" content="Ponte en contacto con el equipo del proyecto ROGER — Archivo fotográfico de Robert Gerstmann, UCN." />
</svelte:head>

<div class="min-h-screen bg-base-100">

  <!-- Header -->
  <section class="bg-neutral text-neutral-content py-16">
    <div class="container mx-auto px-4 max-w-3xl text-center">
      <h1 class="text-4xl font-bold mb-4">Contáctanos</h1>
      <p class="text-neutral-content/70 text-lg max-w-xl mx-auto">
        ¿Tienes fotografías de Gerstmann, deseas colaborar con el proyecto o simplemente quieres saber más? Escríbenos.
      </p>
    </div>
  </section>

  <div class="container mx-auto px-4 max-w-5xl py-16">
    <div class="grid md:grid-cols-2 gap-12">

      <!-- Información de contacto -->
      <div class="space-y-8">
        <div>
          <h2 class="text-2xl font-bold text-base-content mb-6">Información de contacto</h2>
          <div class="space-y-5">
            {#each [
              {
                icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-2 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
                label: 'Institución',
                value: 'Universidad Católica del Norte',
                sub: 'Facultad de Humanidades — Escuela de Periodismo',
              },
              {
                icon: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z',
                label: 'Dirección',
                value: 'Av. Angamos 0610, Antofagasta',
                sub: 'Chile',
              },
              {
                icon: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
                label: 'Correo electrónico',
                value: 'archivo.roger@ucn.cl',
                sub: 'Respuesta dentro de 3 días hábiles',
              },
            ] as info}
              <div class="flex gap-4">
                <div class="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={info.icon} />
                  </svg>
                </div>
                <div>
                  <p class="text-xs text-base-content/40 uppercase tracking-wide font-semibold">{info.label}</p>
                  <p class="text-base-content font-medium">{info.value}</p>
                  <p class="text-sm text-base-content/50">{info.sub}</p>
                </div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Motivos frecuentes -->
        <div class="bg-base-200 rounded-2xl p-6">
          <h3 class="font-bold text-base-content mb-4">Motivos frecuentes de contacto</h3>
          <ul class="space-y-2">
            {#each [
              'Aportar fotografías o documentos históricos al archivo',
              'Colaboración académica o institucional',
              'Solicitar acceso a colecciones para investigación',
              'Prensa y medios de comunicación',
              'Consultas técnicas sobre la plataforma',
            ] as item}
              <li class="flex items-center gap-2 text-sm text-base-content/70">
                <div class="w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0"></div>
                {item}
              </li>
            {/each}
          </ul>
        </div>
      </div>

      <!-- Formulario -->
      <div>
        {#if sent}
          <div class="flex flex-col items-center justify-center h-full text-center gap-4 py-16">
            <div class="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-base-content">Mensaje enviado</h3>
            <p class="text-base-content/60 text-sm max-w-xs">Gracias por escribirnos. Te responderemos a la brevedad posible.</p>
            <button class="btn btn-ghost btn-sm mt-2" on:click={() => { sent = false; name = ''; email = ''; company = ''; subject = ''; message = ''; errorMsg = ''; }}>
              Enviar otro mensaje
            </button>
          </div>
        {:else}
          <form on:submit={handleSubmit} class="space-y-5">
            <h2 class="text-2xl font-bold text-base-content mb-6">Envíanos un mensaje</h2>

            <div class="form-control">
              <label class="label pb-1" for="name">
                <span class="label-text font-medium">Nombre completo</span>
              </label>
              <input id="name" type="text" class="input input-bordered w-full" placeholder="Tu nombre" bind:value={name} required />
            </div>

            <div class="form-control">
              <label class="label pb-1" for="email">
                <span class="label-text font-medium">Correo electrónico</span>
              </label>
              <input id="email" type="email" class="input input-bordered w-full" placeholder="tu@email.com" bind:value={email} required />
            </div>

            <div class="form-control">
              <label class="label pb-1" for="company">
                <span class="label-text font-medium">Empresa / Institución <span class="text-base-content/40 font-normal text-xs">(opcional)</span></span>
              </label>
              <input id="company" type="text" class="input input-bordered w-full" placeholder="Universidad, empresa u organización" bind:value={company} />
            </div>

            <div class="form-control">
              <label class="label pb-1" for="subject">
                <span class="label-text font-medium">Asunto</span>
              </label>
              <select id="subject" class="select select-bordered w-full" bind:value={subject} required>
                <option value="" disabled selected>Selecciona un motivo</option>
                <option>Aportar fotografías o documentos al archivo</option>
                <option>Colaboración académica</option>
                <option>Investigación y acceso a colecciones</option>
                <option>Prensa y comunicaciones</option>
                <option>Consulta técnica</option>
                <option>Otro</option>
              </select>
            </div>

            <div class="form-control">
              <label class="label pb-1" for="message">
                <span class="label-text font-medium">Mensaje</span>
              </label>
              <textarea id="message" class="textarea textarea-bordered w-full h-36 resize-none" placeholder="Cuéntanos en qué podemos ayudarte..." bind:value={message} required></textarea>
            </div>

            {#if errorMsg}
              <div class="alert alert-error py-2 px-3 text-sm rounded-xl">
                <span>{errorMsg}</span>
              </div>
            {/if}

            <button type="submit" class="btn btn-primary w-full gap-2 rounded-xl" disabled={sending}>
              {#if sending}
                <span class="loading loading-spinner loading-sm"></span>
                Enviando...
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Enviar mensaje
              {/if}
            </button>
          </form>
        {/if}
      </div>

    </div>
  </div>
</div>
