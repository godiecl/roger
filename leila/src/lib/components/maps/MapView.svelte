<script lang="ts">
  import { onMount, onDestroy, tick, createEventDispatcher } from 'svelte';
  import { afterNavigate } from '$app/navigation';
  import { browser } from '$app/environment';
  import type { PhotoPin } from '$lib/types';

  export let pins: PhotoPin[] = [];
  export let selectedId: number | null = null;

  const dispatch = createEventDispatcher<{ select: PhotoPin }>();

  let mapEl: HTMLDivElement;
  let mapInstance: any = null;
  let L: any = null;
  let markerMap = new Map<number, any>();
  let resizeObserver: ResizeObserver | null = null;

  onMount(async () => {
    if (!browser) return;

    await tick();

    const leaflet = await import('leaflet');
    L = leaflet.default;

    mapInstance = L.map(mapEl, {
      center: [-35.5, -71.0],
      zoom: 5,
      minZoom: 4,
      zoomControl: false,
      attributionControl: true,
      worldCopyJump: false,
      maxBounds: [[-90, -180], [90, 180]],
      maxBoundsViscosity: 1.0
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution:
        '© <a href="https://openstreetmap.org" target="_blank">OpenStreetMap</a> · © <a href="https://carto.com" target="_blank">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 20,
      noWrap: true
    }).addTo(mapInstance);

    L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);

    renderMarkers();


    resizeObserver = new ResizeObserver(() => {
      mapInstance?.invalidateSize();
    });
    resizeObserver.observe(mapEl);
  });

  afterNavigate(() => {
    if (!mapInstance) return;
    requestAnimationFrame(() => mapInstance.invalidateSize());
  });

  function makePinIcon(isSelected: boolean) {
    const bg = isSelected ? '#ea580c' : '#1d4ed8';
    const shadow = isSelected ? 'rgba(234,88,12,0.4)' : 'rgba(29,78,216,0.3)';
    return L.divIcon({
      className: '',
      html: `<div style="
          width:36px;height:36px;
          background:${bg};
          border-radius:50% 50% 50% 0;
          transform:rotate(-45deg);
          border:3px solid white;
          box-shadow:0 2px 10px ${shadow};
          display:flex;align-items:center;justify-content:center;
          transition:background 0.2s;
        ">
          <svg style="transform:rotate(45deg);width:17px;height:17px"
            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>
        </div>`,
      iconSize: [36, 36],
      iconAnchor: [18, 36],
      popupAnchor: [0, -38]
    });
  }

  function renderMarkers() {
    if (!mapInstance || !L) return;

    markerMap.forEach((m) => m.remove());
    markerMap.clear();

    pins.forEach((pin) => {
      const marker = L.marker([pin.lat, pin.lng], {
        icon: makePinIcon(pin.id === selectedId)
      }).addTo(mapInstance);

      const tagsHtml = pin.tags
        .slice(0, 3)
        .map(
          (t) =>
            `<span style="display:inline-block;background:#dbeafe;color:#1e40af;padding:1px 8px;border-radius:99px;font-size:11px;font-weight:600;margin:2px 2px 0 0">${t}</span>`
        )
        .join('');

      marker.bindPopup(
        `<div style="font-family:'Urbanist',system-ui,sans-serif;min-width:200px;padding:2px 0">
          <p style="font-weight:700;font-size:14px;margin:0 0 3px;color:#111827">${pin.title}</p>
          <p style="color:#6b7280;font-size:12px;margin:0 0 8px">${pin.location} · ${pin.year}</p>
          <div>${tagsHtml}</div>
        </div>`,
        { maxWidth: 260, className: 'roger-popup' }
      );

      marker.on('click', () => dispatch('select', pin));
      markerMap.set(pin.id, marker);
    });
  }

  // Cuando cambian los pins, re-renderizar
  $: {
    pins;
    selectedId;
    if (mapInstance && L) renderMarkers();
  }

  // Cuando se selecciona un pin, volar a él
  $: if (mapInstance && selectedId !== null) {
    const m = markerMap.get(selectedId);
    if (m) {
      m.openPopup();
      mapInstance.flyTo(m.getLatLng(), Math.max(mapInstance.getZoom(), 9), {
        duration: 0.9,
        easeLinearity: 0.3
      });
    }
  }

  onDestroy(() => {
    resizeObserver?.disconnect();
    if (mapInstance) mapInstance.remove();
  });
</script>

<div bind:this={mapEl} style="width:100%;height:100%" />

<style>
  :global(.roger-popup .leaflet-popup-content-wrapper) {
    border-radius: 10px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.14);
    border: 1px solid #e5e7eb;
  }
  :global(.roger-popup .leaflet-popup-tip) {
    background: white;
  }
  :global(.leaflet-attribution-flag) {
    display: none !important;
  }
</style>
